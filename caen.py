from ctypes import *
import pprint

def init(caen_system_info_dict):
    handle = c_int()
    print(handle.value)
    b_ip = caen_system_info_dict["ip_address"].encode('utf-8')
    return_code = libcaenhvwrapper_so.CAENHV_InitSystem(c_int(caen_system_info_dict["system_type"]),
                                                        c_int(caen_system_info_dict["link_type"]),
                                                        b_ip,
                                                        '',
                                                        '',
                                                        handle=pointer(handle))
    print("INIT RETURN CODE : ", hex(return_code))
    print("Handle Value : ", handle.value)
    #print(libcaenhvwrapper_so.CAENHV_DeinitSystem(handle))

    return handle


def deinit(handle):
    return libcaenhvwrapper_so.CAENHV_DeinitSystem(handle)


#res = libcaenhv.get_channel_parameter(handle=handle, slot=0, parameter_name='V0Set', nb_channels=5, channels_list=[1,2,3,4,5], parameter_values_list=parameter_values_list)
# 		list = (c_float * nb_channels)()
def get_channel_name(handle):
    channels_list = [1]
    MAX_CH_NAME = 12
    slot = 0
    nb_channels = 1
    c_channels_list = (c_ushort * nb_channels)(*channels_list)
    c_channel_names = ((c_char * MAX_CH_NAME) * len(channels_list))()
    print(hex(libcaenhvwrapper_so.CAENHV_GetChName(handle=handle, slot=c_ushort(slot), ChNum=c_ushort(nb_channels), ChList=c_channels_list, ChNameList=byref(c_channel_names))))
    pprint.pprint(c_channel_names)
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


libcaenhvwrapper_so = cdll.LoadLibrary('libcaenhvwrapper.so')
