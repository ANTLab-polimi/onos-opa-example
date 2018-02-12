from config import *
from utils import json_get_req
from pprint import pprint
import logging
from utils import bps_to_human_string


class StatsManager(object):
    def __init__(self, verbose=VERBOSE):
        self.last_stat = {}
        self.tm_store = []
        self.verbose = verbose

    @staticmethod
    def bitrate(old_stat, current_stat):
        delta_bytes = current_stat['bytes'] - old_stat['bytes']
        delta_time = current_stat['life'] - old_stat['life']
        return 1.0 * 8 * delta_bytes / delta_time if delta_time > 0 and delta_bytes >= 0 else None

    def add_stats(self, stat_list):
        tm = {}
        filtered_stats = {}

        # For a same flow we might receive many flow stats (possibly one for each switch) with different "life" values:
        # in some cases the differences are due to potential ONOS asynchrony in receiving stats event from a given
        # switch, in other cases a big difference might be due to a re-routing (some flow rules might persist, others
        # might be added as brand new with a 0-valued life).
        # Currently we are keeping the with biggest "life" value: in case of coexsistence of old+new rules this means
        # keeping the oldest, in case of all new rules this means the most updated.
        for app_stat in stat_list:
            for intents in app_stat['intents']:
                for intentKey, stats in intents.items():
                    for stat in stats:
                        flow_id = (intentKey, app_stat['id'], app_stat['name'])
                        if flow_id not in filtered_stats or \
                                (flow_id in filtered_stats and stat['life'] > filtered_stats[flow_id]['life']):
                            filtered_stats[flow_id] = stat

        # For each flow we check if a stat related to a previous polling round is available
        for flow_id, stat in filtered_stats.items():
            if flow_id in self.last_stat:
                bitrate = self.bitrate(self.last_stat[flow_id], stat)
                if bitrate is not None:
                    tm[flow_id] = bitrate
            self.last_stat[flow_id] = stat

        self.tm_store.append(tm)
        if self.verbose:
            pprint({flow_id: bps_to_human_string(tm[flow_id]) for flow_id in tm})

    def poll_stats(self):
        logging.info("Polling Traffic Matrices...")
        reply = json_get_req('http://%s:%d/onos/v1/imr/imr/intentStats' % (ONOS_IP, ONOS_PORT))
        if 'statistics' not in reply:
            return
        self.add_stats(reply['statistics'])

    def get_tm_store(self):
        return self.tm_store
