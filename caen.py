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


libcaenhvwrapper_so = cdll.LoadLibrary('libcaenhvwrapper.so')
