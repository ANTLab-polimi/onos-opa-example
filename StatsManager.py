from config import *
from utils import json_get_req


class StatsManager(object):
    def __init__(self):
        self.last_stat = {}
        self.tm_store = []

    @staticmethod
    def bitrate(old_stat, current_stat):
        delta_bytes = current_stat['bytes'] - old_stat['bytes']
        delta_time = current_stat['life'] - old_stat['life']
        return 1.0 * 8 * delta_bytes / delta_time if delta_time > 0 else None

    def add_stats(self, stat_list):
        tm = {}
        filtered_stats = {}

        # Keep just the more recent per-flow stat
        for app_stat in stat_list:
            for intents in app_stat['intents']:
                for (intentKey, stats) in intents.items():
                    for stat in stats:
                        flow_id = (intentKey, app_stat['id'], app_stat['name'])
                        if flow_id not in filtered_stats or \
                                (flow_id in filtered_stats and stat['life'] > filtered_stats[flow_id]['life']):
                            filtered_stats[flow_id] = stat

        for flow_id, stat in filtered_stats.items():
            if flow_id in self.last_stat:
                bitrate = self.bitrate(self.last_stat[flow_id], stat)
                if bitrate is not None:
                    tm[flow_id] = bitrate
            self.last_stat[flow_id] = stat

        self.tm_store.append(tm)
        print tm

    def poll_stats(self):
        reply = json_get_req('http://%s:%d/onos/v1/imr/intentStats' % (ONOS_IP, ONOS_PORT))
        if 'statistics' not in reply:
            return
        self.add_stats(reply['statistics'])

    def get_tm_store(self):
        return self.tm_store


class FakeStatsManager(StatsManager):
    def __init__(self):
        super(FakeStatsManager, self).__init__()
        '''
        self.rand = [[Stats(0, 10, 10, 0, 'key1', 0, 'appName')],
                     [Stats(5, 15, 10, 0, 'key1', 0, 'appName')],
                     [Stats(25, 20, 10, 0, 'key2', 0, 'appName')],
                     [Stats(35, 21, 10, 0, 'key2', 0, 'appName'), Stats(35, 150, 10, 0, 'key1', 0, 'appName')]]'''

    def poll_stats(self):
        if len(self.rand) == 0:
            return
        reply = {'response': self.rand.pop(0)}
        if 'response' not in reply:
            return
        self.add_stats(reply['response'])
