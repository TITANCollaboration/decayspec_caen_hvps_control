from ctypes import c_int, c_float, c_void_p, c_char_p, c_char, c_ushort, pointer, cdll, cast, POINTER, byref
import pprint
import socket
import sys


class CAEN_Controller:
    def __init__(self, system_type, hostname, username, password, device_name, link_type=0):
        self.MAX_CHANNEL_NAME_LENGHT = 12  # This is hardcoded at this time in the CAEN C-API
        self.MAX_PARAM_LENGTH = 10  # this too is hardcoded and needed for nasty pointer indexing caused by the char ** they like to use
        self.PARAM_TYPE = {0: "numeric", 1: "onoff", 2: "chstatus", 3: "bdstatus", 4: "binary", 5: "string", 6: "enum"}
        try:
            self.libcaenhvwrapper_so = cdll.LoadLibrary('libcaenhvwrapper.so')
        except:
            print("Could not load CAEN's C library : libcaenhvwrapper.so")
            print("It needs to be in in one of the directories listed in your LD_LIBRARY_PATH environment variable")
            exit(1)
        self.device_name = device_name
        self.system_type = system_type
        self.hostname = hostname
        self.username = username
        self.password = password
        self.link_type = link_type
        try:
            self.ip_address = socket.gethostbyname(hostname).encode('utf-8')  # We need to pass the IP addresss to the C API, and we need it in utf8
        except:
            print("Could not get the IP address for the hostname :%s", (hostname))
            print("Or the IP address is improperly formatted")
        self.handle = c_int()
        self.init()

    def check_return_code(self, return_code):
        if hex(return_code) != hex(0):
            print("Problem communicating with HVPS, check SLOT # and Channel # : %s, ERROR code : %s" % (self.ip_address, hex(return_code)))
            # print(cast(self.libcaenhvwrapper_so.CAENHV_GetError(self.handle), c_char_p).raw)  # this didn't work the first time, maybe i'll come back to it
            print("Calling Function:", sys._getframe(1).f_code.co_name)
            exit(1)
        else:
            return return_code

    def init(self):
        #  Initialize the connection to the HVPS and return the handle as a pointer to a structure if successful.
        return_code = self.libcaenhvwrapper_so.CAENHV_InitSystem(c_int(self.system_type),
                                                                 c_int(self.link_type),
                                                                 self.ip_address,
                                                                 self.username,
                                                                 self.password,
                                                                 pointer(self.handle))
        self.check_return_code(return_code)
        print("Initialized Connection to : %s" % (self.hostname))

    def deinit(self):
        # De-initilize the connection to the HVPS.
        return_code = self.libcaenhvwrapper_so.CAENHV_DeinitSystem(self.handle)
        return return_code

    def get_channel_paramters(self, slot, channel):
        full_channel_parameters_list = []
        c_channel_info_list = c_char_p()
        c_channel_params_num = (c_int * 1)()

        return_code = self.libcaenhvwrapper_so.CAENHV_GetChParamInfo(self.handle, slot, channel, byref(c_channel_info_list), c_channel_params_num)
        self.check_return_code(return_code)

        num_parameters_for_channel = c_channel_params_num[0]
        channel_parameter_list = []
        for i in range(0, num_parameters_for_channel - 1):  # For this we must do weird pointer indexing
            parameter_dict = {}
            pointer_to_param = cast(c_channel_info_list, c_void_p).value + (i * self.MAX_PARAM_LENGTH)  # So we cast to type void_p then incriment the pointer value to move to the next actual value
            channel_parameter_list.append(cast(pointer_to_param, POINTER(c_char * self.MAX_PARAM_LENGTH)).contents.value)  # then we need to cast back to an array and deference the pointer and get the array value..

            property_type = c_void_p()
            return_code = self.libcaenhvwrapper_so.CAENHV_GetChParamProp(self.handle, slot, channel, channel_parameter_list[-1], "Type".encode('utf-8'), byref(property_type))
            self.check_return_code(return_code)

            my_property_type = 0
            if property_type.value is not None:  # I don't know why it comes out as None instead of 0 but whatever..
                my_property_type = property_type.value
            parameter_dict = {"parameter": channel_parameter_list[-1].decode('utf-8'), "type": self.PARAM_TYPE[my_property_type], "value": None}
            full_channel_parameters_list.append(parameter_dict)
        return full_channel_parameters_list

    def get_channel_names(self, slot, list_of_channels):
        # Get a list of all the channel names on a SLOT given a list of channels
        channel_names = []
        num_of_channels = len(list_of_channels)
        c_channels_list = (c_ushort * num_of_channels)(*list_of_channels)
        c_channel_names = (c_char * self.MAX_CHANNEL_NAME_LENGHT * num_of_channels)()  # Setup multidimentional array c_channel_names[num_channels][MaxLength]

        return_code = self.libcaenhvwrapper_so.CAENHV_GetChName(self.handle, slot, num_of_channels, c_channels_list, c_channel_names)
        self.check_return_code(return_code)

        for channel_name in c_channel_names:
            channel_names.append(channel_name.value.decode("utf-8"))
        return channel_names

    def get_all_info_for_channels(self, slot, channels):
        all_channels_info_list = []
        for my_channel in channels:
            full_channel_parameters_list = []
            channel_info_dict = {}
            channel_name = self. get_channel_names(slot, [my_channel])

            full_channel_parameters_list = self.get_channel_paramters(slot, my_channel)
            for my_parameter in full_channel_parameters_list:
                c_channels_list = (c_ushort * 1)(*[my_channel])
                param_value = (c_void_p * 1)()
                return_code = self.libcaenhvwrapper_so.CAENHV_GetChParam(self.handle, slot, my_parameter["parameter"].encode('utf-8'), 1, c_channels_list, byref(param_value))
                self.check_return_code(return_code)

                cast_param_value = 0
                if my_parameter["type"] == "numeric":  # Check what type of value we should be getting and cast the c_void_p accordingly
                    cast_param_value = cast(param_value, POINTER(c_float)).contents.value
                elif my_parameter["type"] == "onoff" or my_parameter["type"] == "chstatus":
                    cast_param_value = cast(param_value, POINTER(c_int)).contents.value
                    # if (cast_param_value & (1<<n)):  # Checks if bit n is set to 1

                my_parameter["value"] = cast_param_value

            channel_info_dict = {"chan_name": channel_name[0], "chan_num": my_channel, "slot": slot, "chan_info": full_channel_parameters_list}
            all_channels_info_list.append(channel_info_dict)
        return all_channels_info_list

    def set_channel_name(self, slot, channel, channel_name):
        #  Change the name of a single channel, I know the API allows multiple but I just don't care
        #  !! THIS IS UNTESTED UNTIL I FLIP THE HVPS TO REMOTE FROM LOCAL
        c_channels_list = (c_ushort * 1)(*[channel])

        return_code = self.libcaenhvwrapper_so.CAENHV_SetChName(self.handle, slot, 1, c_channels_list, channel_name.encode('utf-8'))
        self.check_return_code(return_code)
        return

    def set_channel_parameter(self, slot, channel, parameter, new_value):
        #  !! THIS IS UNTESTED UNTIL I FLIP THE HVPS TO REMOTE FROM LOCAL
        c_channels_list = (c_ushort * 1)(*[channel])
        c_new_value = c_float(new_value)

        return_code = self.libcaenhvwrapper_so.CAENHV_SetChParam(self.handle, slot, parameter.encode('utf-8'), 1, c_channels_list, c_new_value)
        self.check_return_code(return_code)
        return

    def get_crate_info(self):
        #  Used to get number of slots and channels in a crate.  It grabs other things as well but they aren't super useful
        c_num_of_slots = c_ushort()
        c_num_of_channels = POINTER(c_ushort)()
        c_description_list = c_char_p()
        c_model_list = c_char_p()
        c_serial_num_list = POINTER(c_ushort)()
        c_firmware_release_min_list = c_char_p()
        c_firmware_releae_max_list = c_char_p()
        return_code = self.libcaenhvwrapper_so.CAENHV_GetCrateMap(self.handle,
                                                                  byref(c_num_of_slots),
                                                                  byref(c_num_of_channels),
                                                                  byref(c_model_list),
                                                                  byref(c_description_list),
                                                                  byref(c_serial_num_list),
                                                                  byref(c_firmware_release_min_list),
                                                                  byref(c_firmware_releae_max_list))

        self.check_return_code(return_code)
        crate_info_dict = {"num_of_slots": c_num_of_slots.value, "num_of_channels": c_num_of_channels.contents.value, "model": c_model_list.value.decode('utf-8')}
        return crate_info_dict
