from caen import CAEN_Controller as CC
from pprint import pprint

# *************************************************************************************
# HVPS_Channel
# Setup a class of objects that represent one channel on the HVPS
# This allows one to easily create a list of these objects which can represent all the
# channels on the HVPS
# *************************************************************************************


class HVPS_Class:
    def __init__(self, caen_system_info_list, max_bias_voltage=12, max_ramp_rate=1):
        self.max_bias_voltage = max_bias_voltage
        self.max_ramp_rate = max_ramp_rate
        self.hvps_systems_objects_list = []
        self.caen_system_info_list = caen_system_info_list

        self.init_all_hvps()

    def __del__(self):
        self.deinit_all_hvps()

    def init_all_hvps(self):
        for caen_system_info_dict in self.caen_system_info_list:
            self.hvps_systems_objects_list.append(CC(caen_system_info_dict["system_type"],
                                                     caen_system_info_dict["hostname"],
                                                     caen_system_info_dict["username"],
                                                     caen_system_info_dict["password"],
                                                     caen_system_info_dict["device_name"],
                                                     caen_system_info_dict["link_type"]))

        return 0

    def deinit_all_hvps(self):
        for hvps_device in self.hvps_systems_objects_list:
            hvps_device.deinit()

    def get_object_entry_for_hvps_by_name(self, hvps_name):
        if len(self.hvps_systems_objects_list) == 1 and hvps_name is None:
            hvps_entry = self.hvps_systems_objects_list[0]
        else:
            hvps_entry = next((hvps_entry for hvps_entry in self.hvps_systems_objects_list if hvps_entry.device_name == hvps_name), None)
        return hvps_entry

    def bias_channel(self, hvps_name, slot, channel, bias_voltage):
        # Probably need to turn channel on but will worry about that in a bit
        hvps_entry = self.get_object_entry_for_hvps_by_name(hvps_name)
        print("BIAS - DEVICE:", hvps_entry.device_name, " CHANNEL:", channel, "SLOT:", slot)
        hvps_entry.set_channel_parameter(slot, channel, 'VSet', bias_voltage)

    def unbias_channel(self, hvps_name, slot, channel):
        hvps_entry = self.get_object_entry_for_hvps_by_name(hvps_name)
        print("UNBIAS - DEVICE:", hvps_entry.device_name, "CHANNEL:", channel, "SLOT:", slot)
        hvps_entry.set_channel_parameter(slot, channel, 'VSet', 0)

    def get_channel_parameters(self, hvps_name, slot, channel):
        hvps_entry = self.get_object_entry_for_hvps_by_name(hvps_name)
        parameter_list = hvps_entry.get_channel_paramters(slot, channel)
        return parameter_list

    def status_channel(self, hvps_name, slot, channel):
        channel_status_list = []
        hvps_entry = self.get_object_entry_for_hvps_by_name(hvps_name)
        channel_status_list.append(hvps_entry.get_all_info_for_channels(slot, [channel]))
        return channel_status_list

    def get_all_crate_channel_statuses(self, my_hpvs_crate):
        channel_status_list = []
        crate_info_dict = my_hpvs_crate.get_crate_info()
        for my_slot in range(0, crate_info_dict['num_of_slots']):
            channel_status_list.append(my_hpvs_crate.get_all_info_for_channels(my_slot,  list(range(0, crate_info_dict['num_of_channels']))))
        return channel_status_list

    def status_all_channels(self, hvps_name):
        channel_status_list = []
        if hvps_name is not None:
            hvps_entry = next((hvps_entry for hvps_entry in self.hvps_systems_objects_list if hvps_entry.device_name == hvps_name), None)
            if hvps_entry is None:
                print("Could not find HVPS name:", hvps_name)
                exit(1)
            channel_status_list.append(self.get_all_crate_channel_statuses(hvps_entry))
        else:
            for my_hvps in self.hvps_systems_objects_list:
                channel_status_list.append(self.get_all_crate_channel_statuses(my_hvps))
        return channel_status_list
