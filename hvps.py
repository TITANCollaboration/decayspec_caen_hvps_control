from caen import CAEN_Controller as CC
from pprint import pprint

# *************************************************************************************
# HVPS_Channel
# Setup a class of objects that represent one channel on the HVPS
# This allows one to easily create a list of these objects which can represent all the
# channels on the HVPS
# *************************************************************************************


class HVPS_Class:
    def __init__(self, caen_system_info_dict, max_bias_voltage=12, max_ramp_rate=1):
        self.max_bias_voltage = max_bias_voltage
        self.max_ramp_rate = max_ramp_rate
        self.hvps_systems_objects_list = []
        self.caen_system_info_dict = caen_system_info_dict
        self.init_hvps()

    def __del__(self):
        self.deinit_all_hvps()

    def init_hvps(self):
#        for caen_system_info_dict in self.caen_system_info_list:
        self.hvps_systems_objects_list.append(CC(int(self.caen_system_info_dict["system_type"]),
                                                 self.caen_system_info_dict["hostname"],
                                                 self.caen_system_info_dict["username"],
                                                 self.caen_system_info_dict["password"],
                                                 self.caen_system_info_dict["device_name"],
                                                 int(self.caen_system_info_dict["link_type"])))

        return 0

    def deinit_all_hvps(self):
        for hvps_device in self.hvps_systems_objects_list:
            hvps_device.deinit()

    def decode_chstatus(self, chstatus):
        chstatus_dict = {'on': 0, 'rup': 0, 'rdown': 0, 'overcurrent': 0, 'overvoltage': 0, 'undervoltage': 0, 'ext_trip': 0, 'maxv': 0,
                         'ext_disable': 0, 'int_trip': 0, 'calibration_error': 0, 'unplugged': 0, 'overvoltage_protection': 0,
                         'power_fail': 0, 'temp_error': 0}

#        if (chstatus & (1<<n)):  # Checks if bit n is set to 1
        chstatus_dict['on'] = chstatus & (1<<0)  # bit 0
        chstatus_dict['rup'] = chstatus & (1<<1)  # bit 1
        chstatus_dict['rdown'] = chstatus & (1<<2)  # bit 2
        chstatus_dict['overcurrent'] = chstatus & (1<<3)  # bit 3
        chstatus_dict['overvoltage'] = chstatus & (1<<4)  # bit 4
        chstatus_dict['undervoltage'] = chstatus & (1<<5)  # bit 5
        chstatus_dict['ext_trip'] = chstatus & (1<<6)  # bit 6
        chstatus_dict['maxv'] = chstatus & (1<<7)  # bit 7
        chstatus_dict['ext_disable'] = chstatus & (1<<8)  # bit 8
        chstatus_dict['int_trip'] = chstatus & (1<<9)  # bit 9
        chstatus_dict['calibration_error'] = chstatus & (1<<10)  # bit 10
        chstatus_dict['unplugged'] = chstatus & (1<<11)  # bit 11
        chstatus_dict['overvoltage_protection'] = chstatus & (1<<13)  # bit 13
        chstatus_dict['power_fail'] = chstatus & (1<<14)  # bit 14
        chstatus_dict['temp_error'] = chstatus & (1<<15)  # bit 15

        return chstatus_dict

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

    def set_channel_param(self, hvps_name, slot, channel, param, param_value):
        # Probably need to turn channel on but will worry about that in a bit
        hvps_entry = self.get_object_entry_for_hvps_by_name(hvps_name)
        print("DEVICE:", hvps_entry.device_name, " CHANNEL:", channel, "SLOT:", slot, "Parameter:", param, "=", param_value)
        hvps_entry.set_channel_parameter(slot, channel, param, param_value)

    def unbias_channel(self, hvps_name, slot, channel):
        hvps_entry = self.get_object_entry_for_hvps_by_name(hvps_name)
        print("UNBIAS - DEVICE:", hvps_entry.device_name, "CHANNEL:", channel, "SLOT:", slot)
        hvps_entry.set_channel_parameter(slot, channel, 'VSet', 0)

    def get_channel_parameters(self, hvps_name, slot, channel):
        hvps_entry = self.get_object_entry_for_hvps_by_name(hvps_name)
        parameter_list = hvps_entry.get_channel_paramters(slot, channel)
        #print(parameter_list)
        return parameter_list

    def show_channel_status(self, channel_status_list):
        for channel_dict in channel_status_list[0]:
            print("Slot:", channel_dict['slot'], end=' | ')
            print("Channel Name:", channel_dict['chan_name'], end=' | ')
            print("Channel#:", channel_dict['chan_num'], end=' | ')
            for channel_params in channel_dict['chan_info']:
                print(channel_params['parameter'], ':', channel_params['value'],  end=' | ')
            print('')

    def status_channel(self, hvps_name, slot, channel):
        channel_status_list = []
        hvps_entry = self.get_object_entry_for_hvps_by_name(hvps_name)
        channel_status_list.append(hvps_entry.get_all_info_for_channels(slot, [channel]))
        self.show_channel_status(channel_status_list)
        return channel_status_list

    def set_channel_name(self, hvps_name, slot, channel, channel_name):
        hvps_entry = self.get_object_entry_for_hvps_by_name(hvps_name)
        hvps_entry.set_channel_name(slot, channel, channel_name)
        return

    def get_all_crates_info(self):
        crate_info_list = []
        for hvps_entry in self.hvps_systems_objects_list:
            device_info_dict = {"device_name": hvps_entry.device_name, "hostname": hvps_entry.hostname}  # Throw in a couple extra pieces of data
            device_info_dict.update(hvps_entry.get_crate_info())  # combine dict's
            crate_info_list.append(device_info_dict)
        return crate_info_list

    def get_all_channel_names(self):
        full_list_of_channel_names = []
        crate_info_list = self.get_all_crates_info()
        print(crate_info_list)
        device_and_channel_dict = {}
        for my_crate in crate_info_list:
            list_of_channel_names = []
            hvps_entry = self.get_object_entry_for_hvps_by_name(my_crate['device_name'])
            for my_slot in range(0, my_crate['num_of_slots']):
                print("Got here2")
                list_of_channel_names.extend(hvps_entry.get_channel_names(my_slot, list(range(0, my_crate['num_of_channels']))))
            device_and_channel_dict = {'device_name': my_crate['device_name'], 'channel_names': list_of_channel_names}
            full_list_of_channel_names.append(device_and_channel_dict)
        return full_list_of_channel_names

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
        for hvps_entry in channel_status_list:
            self.show_channel_status(hvps_entry)
        return channel_status_list

    def find_channel_by_name(self, chan_name):
        return
