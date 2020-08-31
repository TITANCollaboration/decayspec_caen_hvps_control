import caen

# *************************************************************************************
# HVPS_Channel
# Setup a class of objects that represent one channel on the HVPS
# This allows one to easily create a list of these objects which can represent all the
# channels on the HVPS
# *************************************************************************************


class HVPS_Channel:
    def __init__(self, channel_num, enabled, detector_name, detector_position, max_bias_voltage, ramp_rate):
        self.channel_num = channel_num
        self.enabled = enabled
        self.detector_name = detector_name
        self.detector_position = detector_position
        self.max_bias_voltage = max_bias_voltage
        self.ramp_rate = ramp_rate

    def bias_channel(self, caen_system_info_dict):
        return_code, handle = caen.init(caen_system_info_dict)
        caen.set_channel_parameters(handle, self.channel_num, action="BIAS")
        print("Bias channel!")

    def unbias_channel(self, caen_system_info_dict):
        return_code, handle = caen.init(caen_system_info_dict)
        caen.set_channel_parameters(handle, self.channel_num, action="UNBIAS")
        print("Unbias channel")

    def status_channel(self, caen_system_info_dict):
        return_code, handle = caen.init(caen_system_info_dict)
        print("This is my status")
