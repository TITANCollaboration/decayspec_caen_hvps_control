from ctypes import *


def init(caen_system_info_dict):
    handle = c_int()
    return_code = libcaenhvwrapper_so.CAENHV_InitSystem(caen_system_info_dict["system_type"],
                                                        caen_system_info_dict["link_type"],
                                                        caen_system_info_dict["ip_address"],
                                                        caen_system_info_dict["username"],
                                                        caen_system_info_dict["password"],
                                                        handle=byref(handle))
    return return_code, handle


def deinit(handle):
    return libcaenhvwrapper_so.CAENHV_DeinitSystem(handle)


def channel_status(handle, channels):
    slot = 0  # No clue here at the moment, will figure this one out eventually, maybe when I actually have the hardware and am not coding blind
    print("get status...")
    # Parameter list to grab, V0Set, I0Set, Rup, RDWn, Vmon, Imon, Status, Pw
    # I think I may have to do seveal of these calls to return all the information, this might be one of those parts I need to leave until after
    # we get the hardware
    libcaenhvwrapper_so.CAENHV_GetChParam(handle, c_ushort(slot), parameter_name, c_ushort(len(channels)), c_channels_list, cast(c_parameter_values_list, c_void_p))
    for c_parameter_value in c_parameter_values_list:
        parameter_values_list.append(c_parameter_value)

    return 0  # Will return something nice soon enough


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
