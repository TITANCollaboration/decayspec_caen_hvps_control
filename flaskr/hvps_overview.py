from flask import Blueprint, redirect, render_template, request, session, url_for
# from asset_tracker_restapi import asset_tracker_restapi
from hvps_ctrl import process_config_file
from hvps import HVPS_Class
from pprint import pprint

bp = Blueprint("hvps_overview", __name__)


@bp.route("/", methods=['GET', 'POST'])
def index():
    crate_info_list = []
    channel_short_info_list = []
    caen_system_info_list = process_config_file()
    HVPS = HVPS_Class(caen_system_info_list)
    crate_info_list = HVPS.get_all_crates_info()
    for my_crate in crate_info_list:
        channel_short_info_list.append({'device_name': my_crate['device_name']})
        channel_name_list = []
        for my_slot in range(0, my_crate['num_of_slots']):
            for my_channel in HVPS.status_all_channels(my_crate['device_name'])[0][my_slot]:
                channel_name_list.append(my_channel['chan_name'])
        channel_short_info_list[-1].update({'channel_names': channel_name_list})
    return render_template('hvps_overview.html', channel_short_info_list=channel_short_info_list)


@bp.route("/select_channel", methods=['GET', 'POST'])
def select_channel():
    channel_name = request.form["chan_name"]
    print(channel_name)
    return render_template('hvps_overview.html')
