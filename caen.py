from ctypes import *
import pprint
import socket


class CAEN_Controller:
    def __init__(self, system_type, hostname, username, password, link_type=0):
        self.MAX_CHANNEL_NAME_LENGHT = 12  # This is hardcoded at this time in the CAEN C-API
        self.MAX_PARAM_LENGTH = 10  # this too is hardcoded and needed for nasty pointer indexing caused by the char ** they like to use
        self.libcaenhvwrapper_so = cdll.LoadLibrary('libcaenhvwrapper.so')

        self.system_type = system_type
        self.hostname = hostname
        self.username = username
        self.password = password
        self.link_type = link_type

        self.ip_address = socket.gethostbyname(hostname).encode('utf-8')  # We need to pass the IP addresss to the C API, and we need it in utf8
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
        channel_info_list = []
        for my_channel in channels:
            c_channel_params_num = (c_int * 1)()
            c_channel_info_list = c_char_p()

            return_code = self.libcaenhvwrapper_so.CAENHV_GetChParamInfo(self.handle, slot, my_channel, byref(c_channel_info_list), c_channel_params_num)
            self.check_return_code(return_code)

            num_parameters_for_channel = c_channel_params_num[0]
            channel_parameter_list = []
            for i in range(0, num_parameters_for_channel - 1):  # For this we must do weird pointer indexing
                pointer_to_param = cast(c_channel_info_list, c_void_p).value + (i * self.MAX_PARAM_LENGTH)  # So we cast to type void_p then incriment the pointer value to move to the next actual value
                cast(pointer_to_param, POINTER(c_char * self.MAX_PARAM_LENGTH)).contents.value.decode("utf-8")  # then we need to cast back to an array and deference the pointer and get the array value..
                return_code = self.libcaenhvwrapper_so.CAENHV_GetChParamInfo(self.handle, slot, my_channel,)
            print(channel_parameter_list)
        return

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
