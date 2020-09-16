from ctypes import *
import pprint
import socket


class CAEN_Controller:
    def __init__(self, system_type, hostname, username, password, link_type=0):
        self.MAX_CHANNEL_NAME_LENGHT = 12  # This is hardcoded at this time in the CAEN C-API
        self.MAX_PARAM_LENGTH = 10  # this too is hardcoded and needed for nasty pointer indexing caused by the char ** they like to use
        self.PARAM_TYPE = {0: "numeric", 1: "onoff", 2: "chstatus", 3: "bdstatus", 4: "binary", 5: "string", 6: "enum"}
        try:
            self.libcaenhvwrapper_so = cdll.LoadLibrary('libcaenhvwrapper.so')
        except:
            print("Could not load CAEN's C library : libcaenhvwrapper.so")
            print("It needs to be in in one of the directories listed in your LD_LIBRARY_PATH environment variable")
            exit(1)

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

    def check_return_code(self, return_code):
        if hex(return_code) != hex(0):
            print("Could not connect to HVPS : %s, ERROR code : %i" % (self.ip_address, return_code))
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
            c_channel_params_num = (c_int * 1)()
            c_channel_info_list = c_char_p()
            channel_name = self. get_channel_names(slot, [my_channel])
            return_code = self.libcaenhvwrapper_so.CAENHV_GetChParamInfo(self.handle, slot, my_channel, byref(c_channel_info_list), c_channel_params_num)
            self.check_return_code(return_code)

            num_parameters_for_channel = c_channel_params_num[0]
            channel_parameter_list = []
            for i in range(0, num_parameters_for_channel - 1):  # For this we must do weird pointer indexing
                parameter_dict = {}
                pointer_to_param = cast(c_channel_info_list, c_void_p).value + (i * self.MAX_PARAM_LENGTH)  # So we cast to type void_p then incriment the pointer value to move to the next actual value
                channel_parameter_list.append(cast(pointer_to_param, POINTER(c_char * self.MAX_PARAM_LENGTH)).contents.value)  # then we need to cast back to an array and deference the pointer and get the array value..

                property_type = c_void_p()
                return_code = self.libcaenhvwrapper_so.CAENHV_GetChParamProp(self.handle, slot, my_channel, channel_parameter_list[-1], "Type".encode('utf-8'), byref(property_type))
                self.check_return_code(return_code)

                my_property_type = 0
                if property_type.value is not None:  # I don't know why it comes out as None instead of 0 but whatever..
                    my_property_type = property_type.value

                c_channels_list = (c_ushort * 1)(*[my_channel])
                param_value = (c_void_p * 1)()
                return_code = self.libcaenhvwrapper_so.CAENHV_GetChParam(self.handle, slot, channel_parameter_list[-1], 1, c_channels_list, byref(param_value))
                self.check_return_code(return_code)

                cast_param_value = 0
                if self.PARAM_TYPE[my_property_type] == "numeric":
                    cast_param_value = cast(param_value, POINTER(c_float)).contents.value
                elif self.PARAM_TYPE[my_property_type] == "onoff" or self.PARAM_TYPE[my_property_type] == "chstatus":
                    cast_param_value = cast(param_value, POINTER(c_int)).contents.value
                    # if (cast_param_value & (1<<n)):  # Checks if bit n is set to 1
                parameter_dict = {"parameter": channel_parameter_list[-1].decode('utf-8'), "type": self.PARAM_TYPE[my_property_type], "value": cast_param_value}
                full_channel_parameters_list.append(parameter_dict)
            channel_info_dict = {"chan_name": channel_name[0], "chan_num": my_channel, "chan_info": full_channel_parameters_list}
            all_channels_info_list.append(channel_info_dict)
#            print(channel_info_dict)
#                print("Channel NAme:",channel_name[0], "Property:", channel_parameter_list[-1].decode('utf-8'), "Value:", cast_param_value, "Type:", self.PARAM_TYPE[my_property_type])
            # channel_info_list.append(something..)
        return all_channels_info_list

    def get_board_info(self, slot):
        c_board_info_list = (c_char_p * 12)()
        self.libcaenhvwrapper_so.CAENHV_GetBdParamInfo(self.handle, slot, c_board_info_list)
        for i in c_board_info_list:
            print(i)
        return

    def channel_status(handle, channels):
        slot = 0  # No clue here at the moment, will figure this one out eventually, maybe when I actually have the hardware and am not coding blind
        print("get status...")
        slot = 0
        list = (c_float * 1)()
        channels_list=[1]
        parameter_name='Pon'
        p_parm = parameter_name.encode('utf-8')
        nb_channels = 5
        c_channels_list = (c_ushort * 1)(*channels_list)
        c_parameter_values_list = (c_int * 1)()
        somelist = []
        # Parameter list to grab, V0Set, I0Set, Rup, RDWn, Vmon, Imon, Status, Pw
        # I think I may have to do seveal of these calls to return all the information, this might be one of those parts I need to leave until after
        # we get the hardware
        libcaenhvwrapper_so.CAENHV_GetChParam(handle, 0, "Pon", 1, [1], byref(somelist))
        #for c_parameter_value in c_parameter_values_list:
        #    parameter_values_list.append(c_parameter_value)
        #pprint.pprint(parameter_values_list)
        return 0  # Will return something nice soon enough

    def get_system_property(handle):
        mine =''
        #b_char = .encode('utf-8')

        libcaenhvwrapper_so.CAENHV_GetSysProp(handle, )

    def get_system_property_list(handle):
        prop_name_list = POINTER(POINTER(c_char)) #c_char_p()
        num_prop = c_ushort()
        #prop_name_list = c_wchar_p("")

        #NumProp = 0
        print(handle)
        myreturn = libcaenhvwrapper_so.CAENHV_GetSysPropList(handle=handle, NumProp=byref(num_prop), PropNameList=byref(prop_name_list))
        print("Got here 2", myreturn)
        print(NumProp, prop_name_list)
        return

    def set_channel_parameters(handle, channels, action):
        slot = 0
        print("Setting stuff to bias or unbias")
        # We will want to check if we are biasing or unbiasing and what the current state of the system is.
        # We want to catch things like bias'ing an already biased detector as there is no reason to tempt fate.
        parameter_name='Pw'  # this is the parameter to turn the power on or off (1 = on; 0 = off I think)
        # Also set RDWn and Rup

        if action == "BIAS":
            print("We're going to bias!")
            libcaenhvwrapper_so.CAENHV_SetChParam(handle, c_ushort(slot), parameter_name, c_ushort(nb_channels), c_channels_list, cast([1], c_void_p))
        elif action == "UNBIAS":
            print("Woo! We're going to unbias!")
            libcaenhvwrapper_so.CAENHV_SetChParam(handle, c_ushort(slot), parameter_name, c_ushort(nb_channels), c_channels_list, cast([0], c_void_p))
