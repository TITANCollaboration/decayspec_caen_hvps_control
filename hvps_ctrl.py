# *************************************************************************************
#   By: Jon Ringuette
#   Created: March 23 2020 - During the great plague
#   Purpose: Provide a wrapper for CAEN's C library to control the CAEN HVPS which biases
#            the HPGe's (8pi's and ULGe)
# *************************************************************************************

import argparse
import configparser
from configobj import ConfigObj
import sys
import os
from hvps import HVPS_Class
from pprint import pprint
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

def process_config_file_test(config_file="hvps_test.cfg"):
    config_dict = ConfigObj("hvps_test.cfg")
    #pprint(config_dict.keys())
    #for mykey in config_dict.keys():
    #    if mykey.startswith('HVPS_'):
    #        print(config_dict[mykey].keys())
    return config_dict

def process_config_file(config_file="hvps.cfg"):
    caen_system_info_list = []
    caen_global_params_dict = {}

    config = configparser.RawConfigParser()

    if not os.path.exists(config_file):
        print("Could not read config file : %s" % (config_file))
        exit(1)
    config.read(config_file)
    for section in config.sections():
        # Read in HVPS information
        if section == "GLOBAL":
            caen_global_params_dict["default_slot"] = int(getConfigEntry(config, section, 'default_slot', reqd=False, remove_spaces=True))
            caen_global_params_dict["max_ramp_rate"] = float(getConfigEntry(config, section, 'max_ramp_rate', reqd=False, remove_spaces=True))
            caen_global_params_dict["max_bias_voltage"] = float(getConfigEntry(config, section, 'max_bias_voltage', reqd=True, remove_spaces=True))
            caen_system_info_dict = {}
            caen_system_info_dict["device_name"] = section
            caen_system_info_dict["system_type"] = int(getConfigEntry(config, section, 'caen_system_type', reqd=True, remove_spaces=True))
            caen_system_info_dict["link_type"] = int(getConfigEntry(config, section, 'caen_link_type', reqd=True, remove_spaces=True))
            caen_system_info_dict["hostname"] = getConfigEntry(config, section, 'caen_hostname', reqd=True, remove_spaces=True)
            caen_system_info_dict["username"] = getConfigEntry(config, section, 'caen_username', reqd=True, remove_spaces=True)
            caen_system_info_dict["password"] = getConfigEntry(config, section, 'caen_password', reqd=True, remove_spaces=True)
            caen_system_info_list.append(caen_system_info_dict)

        else:
            enabled = getConfigEntry(config, section, 'enabled', reqd=True, remove_spaces=True)
            if enabled == "True":
                channel_num = int(getConfigEntry(config, section, 'channel_num', reqd=True, remove_spaces=True))
                enabled = getConfigEntry(config, section, 'enabled', reqd=True, remove_spaces=True)
        #     detector_name = getConfigEntry(config, channel_section, 'detector_name', reqd=True, remove_spaces=True)
        #     detector_position = int(getConfigEntry(config, channel_section, 'detector_position', reqd=True, remove_spaces=True))
                max_bias_voltage = float(getConfigEntry(config, section, 'max_bias_voltage', reqd=True, remove_spaces=True))
                if max_bias_voltage > caen_global_params_dict["max_bias_voltage"]:
                    print("Max Bias Voltage for channel", channel_num, "is greater than global max_bias_voltage allowed in config.")
                    exit(1)
                ramp_rate = float(getConfigEntry(config, section, 'ramp_rate', reqd=True, remove_spaces=True))
                if ramp_rate > caen_global_params_dict["max_ramp_rate"]:
                    print("Ramp rate for channel", channel_num, "is greater than global max_ramp_rate allowed in config.")
                    exit(1)
             #hvps_channel_list.append(HVPS_Channel(channel_num, enabled, detector_name, detector_position, max_bias_voltage, ramp_rate))

    return caen_system_info_list, caen_global_params_dict


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


def find_channel_in_config(channel, config_dict_hvps):
    channel_entry = None
    pprint(config_dict_hvps)
    for my_channel_key in config_dict_hvps.keys():
        if my_channel_key.startswith('CH_'):
            if (config_dict_hvps[my_channel_key]['channel_num'] == channel) and config_dict_hvps[my_channel_key]['Enabled'].upper() == "True".upper():
                channel_entry = config_dict_hvps[my_channel_key]
    return channel_entry


def compare_voltage(channel, my_new_bias_voltage, ramp_rate, HVPS, my_slot, max_ramp_rate):
    perform_bias = False
    new_bias_voltage = int(my_new_bias_voltage)
    channel_status_list = HVPS[0].status_channel(None, my_slot, int(channel))
    current_voltage = int(next(item for item in channel_status_list[0][0]['chan_info'] if item['parameter'] == 'VSet')['value'])

    if current_voltage >= int(new_bias_voltage):
        print("Channel:", channel, "is already set to bias voltage:", current_voltage)
        exit(1)
    else:
        print("You are about to change the BIAS voltage for :")
        print("Channel:", channel)
        print("Current BIAS voltage:", current_voltage)
        print("New BIAS voltage:", new_bias_voltage)
        print("At voltage ramp rate (V/sec):", max_ramp_rate)
        input_response = input("Please Confirm This Change (y/n) : ")
        if input_response == 'y':
            perform_bias = True
    return perform_bias


def get_max_voltage_ramp_rate(config_dict, channel_entry):
    my_ramp_rate = 0
    if int(channel_entry['ramp_rate']) < int(config_dict['max_ramp_rate']):
        my_ramp_rate = int(channel_entry['ramp_rate'])
    else:
        my_ramp_rate = int(config_dict['max_ramp_rate'])
    return int(my_ramp_rate)


def bias(args, config_dict, HVPS, my_slot, default_hvps_key):
    max_ramp_rate = 0
    if (args.bias_voltage is None) and (args.channel_selected is not None):
        channel_entry = find_channel_in_config(args.channel_selected, config_dict[default_hvps_key])
        if channel_entry is not None:
            print(channel_entry)
            max_ramp_rate = get_max_voltage_ramp_rate(config_dict, channel_entry)
            if compare_voltage(channel_entry['channel_num'], channel_entry['max_bias_voltage'], max_ramp_rate, HVPS, my_slot, max_ramp_rate) is True:
                HVPS[0].set_channel_param(args.hvps_name, my_slot, int(args.channel_selected), 'RUp', max_ramp_rate)
                time.sleep(1)
                HVPS[0].bias_channel(args.hvps_name, my_slot, int(args.channel_selected), int(channel_entry['max_bias_voltage']))

        else:
            print("Must specify a BIAS voltage via --bias_voltage or put an entry for the channel in the config file and ensure Enabled is True")
            exit(1)
    elif args.channel_selected is None:
        print("Must specify --channel")
        exit(1)
    else:

        HVPS[0].bias_channel(args.hvps_name, my_slot, int(args.channel_selected), int(args.bias_voltage))


def process_cli_args(args, config_dict):
    default_hvps_key = None
    HVPS = []
    if "default_slot" in config_dict.keys():
        my_slot = int(config_dict["default_slot"])
    else:
        my_slot = args.slot_selected

    for mykey in config_dict.keys():
        if mykey.startswith('HVPS_'):
            default_hvps_key = mykey
            HVPS.append(HVPS_Class(config_dict[mykey]))

    if args.action == "status":
        chan_status = []

        if args.channel_selected is None:
            args.channel_selected = "ALL"

        if args.channel_selected.upper() == "ALL":
            HVPS[0].status_all_channels(args.hvps_name)
        else:
            channel_status_list = HVPS[0].status_channel(args.hvps_name, my_slot, int(args.channel_selected))
            HVPS[0].show_channel_status(channel_status_list)
    elif args.action == "bias":
        bias(args, config_dict, HVPS, my_slot, default_hvps_key)
    elif args.action == "unbias":
        if args.channel_selected is None:
            print("Must specify --channel")
        else:
            HVPS[0].unbias_channel(args.hvps_name, my_slot, int(args.channel_selected))
    elif args.action == "set_param":
        if args.channel_selected is None:
            print("Must specify --channel")
        else:
            HVPS[0].set_channel_param(args.hvps_name, my_slot, int(args.channel_selected), args.param, args.param_value)
    #elif args.action == "set_name":
    #    if args.channel_selected is None:
    #        print("Must specify --slot and --channel")
    #    else:
    #        HVPS[0].set_channel_name(args.hvps_name, my_slot, int(args.channel_selected), "j1")
    del HVPS[0]
    #print("Time 2")  # Uncommented this and the next line to try init'ing again.  This should work if CAEN ever fixes their CApi which they promised back in Nov2020
    #HVPS = HVPS_Class(caen_system_info_list)

    return


def main():
    parser = argparse.ArgumentParser(description='HVPS Controller', usage='%(prog)s --action [bias, unbias, status, set_name] --channel [channel num]')
    parser.add_argument('--hvps_name', dest='hvps_name', default=None, required=False)

    parser.add_argument('--action', choices=('bias', 'unbias', 'status', 'bias_all', 'unbias_all', 'set_param'), required=False)

    parser.add_argument('--param', dest='param', choices=('ISet', 'RUp', 'RDwn', 'PDwn', 'IMRange', 'Trip'), required=False, default=None,
                        help="Specify parameter to modify for channel, must specify with --action set_param")
    parser.add_argument('--param_value', dest='param_value', required=False, type=int, default=None,
                        help="Specify parameter value, must specify --action set_param and --param")
    parser.add_argument('--bias_voltage', dest='bias_voltage', type=int, required=False, default=None,
                        help="Specify new bias voltage for a channel")

    parser.add_argument('--slot', dest='slot_selected', type=int, required=False, default=None,
                        help="Specify slot to take action against")

    parser.add_argument('--channel', dest='channel_selected', required=False, default=None,
                        help="Specify channel to take action against, specify channel number or ALL")

    parser.add_argument('--config_file', dest='config_file', required=False,
                        help="Specify the complete path to the config file, by default we'll use hvps.cfg")

    parser.add_argument('--force', action='store_true', required=False, help="If used than no confirmation will be asked.. !!BE CAREFUL!!")

    parser.set_defaults(config_file="hvps.cfg")
    args, unknown = parser.parse_known_args()
    # print(args)
    config_dict = process_config_file_test(args.config_file)

    #caen_system_info_list, caen_global_params_dict = process_config_file(args.config_file)
    #hvps_channel_action = process_cli_args(args, caen_system_info_list, caen_global_params_dict)
    process_cli_args(args, config_dict)


if __name__ == "__main__":
    main()
