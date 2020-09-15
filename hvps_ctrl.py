# *************************************************************************************
#   By: Jon Ringuette
#   Created: March 23 2020 - During the great plague
#   Purpose: Provide a wrapper for CAEN's C library to control the CAEN HVPS which biases
#            the HPGe's (8pi's and ULGe)
# *************************************************************************************

import argparse
import configparser
import sys
import os
from hvps import HVPS_Channel
import pprint
from caen import CAEN_Controller
from ctypes import *
import time


def getConfigEntry(config, heading, item, reqd=False, remove_spaces=True, default_val=''):
    #  Just a helper function to process config file lines, strip out white spaces and check if requred etc.
    if config.has_option(heading, item):
        if remove_spaces:
            config_item = config.get(heading, item).replace(" ", "")
        else:
            config_item = config.get(heading, item)
    elif reqd:
        print("The required config file setting \'%s\' under [%s] is missing") % (item, heading)
        sys.exit(1)
    else:
        config_item = default_val
    return config_item

# *************************************************************************************
# process_config_file:
# Process config file using the configparser library
# *************************************************************************************


def process_config_file(config_file):
    hvps_channel_list = []
    caen_system_info_dict = {}
    config = configparser.RawConfigParser()

    if os.path.exists(config_file):
        config.read(config_file)

        for channel_section in config.sections():
            # Read in Beam information
            if channel_section == "SYSTEM":
                caen_system_info_dict["system_type"] = int(getConfigEntry(config, channel_section, 'caen_system_type', reqd=True, remove_spaces=True))
                caen_system_info_dict["link_type"] = int(getConfigEntry(config, channel_section, 'caen_link_type', reqd=True, remove_spaces=True))
                caen_system_info_dict["hostname"] = getConfigEntry(config, channel_section, 'caen_hostname', reqd=True, remove_spaces=True)
                caen_system_info_dict["username"] = getConfigEntry(config, channel_section, 'caen_username', reqd=True, remove_spaces=True)
                caen_system_info_dict["password"] = getConfigEntry(config, channel_section, 'caen_password', reqd=True, remove_spaces=True)
            else:
                channel_num = int(getConfigEntry(config, channel_section, 'channel_num', reqd=True, remove_spaces=True))
                enabled = getConfigEntry(config, channel_section, 'enabled', reqd=True, remove_spaces=True)
                detector_name = getConfigEntry(config, channel_section, 'detector_name', reqd=True, remove_spaces=True)
                detector_position = int(getConfigEntry(config, channel_section, 'detector_position', reqd=True, remove_spaces=True))
                max_bias_voltage = int(getConfigEntry(config, channel_section, 'max_bias_voltage', reqd=True, remove_spaces=True))
                ramp_rate = int(getConfigEntry(config, channel_section, 'ramp_rate', reqd=True, remove_spaces=True))

                hvps_channel_list.append(HVPS_Channel(channel_num, enabled, detector_name, detector_position, max_bias_voltage, ramp_rate))
    #    initMacroMachine(system_objects, work_dir, g4_macro_filename)
    return hvps_channel_list, caen_system_info_dict


def find_channel_num_or_det_name(channel_selection, hvps_channel_list):
    for chan_obj in hvps_channel_list:
        try:
            if chan_obj.channel_num == int(channel_selection):
                return chan_obj
        except:
             print("Your channel selection must be a number from 0-15")
    print("!! Could not find the channel # you specified.  Please make sure it is between 0-15 and is specified in the hvps.cfg file")
    sys.exit(1)


def confirm_channel(chan_obj, action):
    print("-------------------------------------")
    print("Channel Number : %i " % chan_obj.channel_num)
    print("Detector Name : %s" % chan_obj.detector_name)
    print("Detector Position : %i" % chan_obj.detector_position)
    print("MAX BIAS VOLTAGE : %i V" % chan_obj.max_bias_voltage)
    print("RAMP RATE : %i V/sec" % chan_obj.ramp_rate)
    print("-------------------------------------")
    print("Current status : ")  # Put some current status here..., will need to pass this in
    user_confirmation_input = input("Are you sure you want to %s this channel? YES/NO : " % action.upper())
    if user_confirmation_input.upper() == "YES":
        print("Ok, Let's do it!!")
    else:
        print("Could not confirm action, exiting ...")
        sys.exit(1)


def process_cli_args(args, hvps_channel_list, caen_system_info_dict):
    myslot = 0
    pprint.pprint(caen_system_info_dict)
    #print(caen.deinit(0))
    #system_type, hostname, username, password, link_type=0):
    CC = CAEN_Controller(caen_system_info_dict["system_type"], caen_system_info_dict["hostname"], caen_system_info_dict["username"], caen_system_info_dict["password"], caen_system_info_dict["link_type"])
    CC.init()
    #CC.get_channel_names(myslot, [0, 1, 3])
    #CC.get_board_info(myslot)
    CC.get_all_info_for_channels(myslot, [0])
    CC.deinit()
    #caen.deinit(handle)
 #caen.channel_status(handle, 1)
    #print("Hello", caen.deinit(handle))
    #caen.channel_status(handle, 1)
    #caen.get_system_property_list(handle)
#    if (args.action == "bias") or (args.action == "unbias"):
#        chan_obj = find_channel_num_or_det_name(args.channel_selected, hvps_channel_list)
#        print("Lets Bias or Unbias!")
#        confirm_channel(chan_obj, args.action)
#        chan_obj.bias_channel(caen_system_info_dict)
#
#    if args.action == "status":
#        chan_status = []
#        print("Lets get status!")
#        if args.channel_selected.upper() == "ALL":
#            for mychan in hvps_channel_list:
#                mychan_num = mychan.channel_num
#                chan_obj = find_channel_num_or_det_name(mychan_num, hvps_channel_list)
#                chan_status.append(chan_obj.status_channel(caen_system_info_dict))
#
#        chan_obj = find_channel_num_or_det_name(args.channel_selected, hvps_channel_list)
#        chan_status.append(chan_obj.status_channel(caen_system_info_dict))
#

def main():
    parser = argparse.ArgumentParser(description='HVPS Controller', usage='%(prog)s --action [bias, unbias, status] --channel [channel num]')

    parser.add_argument('--action', choices=('bias', 'unbias', 'status'), required=False)

    parser.add_argument('--channel', dest='channel_selected', required=False,
                        help="Specify channel to take action against, specify channel number or ALL")

    parser.add_argument('--config_file', dest='config_file', required=False,
                        help="Specify the complete path to the config file, by default we'll use hvps.cfg")

    parser.add_argument('--force', action='store_true', required=False, help="If used than no confirmation will be asked.. !!BE CAREFUL!!")

    parser.set_defaults(config_file="hvps.cfg")
    args, unknown = parser.parse_known_args()
    print(args)
    hvps_channel_list, caen_system_info_dict = process_config_file(args.config_file)
    hvps_channel_action = process_cli_args(args, hvps_channel_list, caen_system_info_dict)
    #print(hvps_channel_list, hvps_channel_action)


if __name__ == "__main__":
    main()
