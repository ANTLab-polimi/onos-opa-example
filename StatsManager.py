from config import *
from utils import json_get_req


class StatsManager(object):
    def __init__(self):
        self.last_stat = {}
        self.TMs = []

    @staticmethod
    def bitrate(old_stat, current_stat):
        delta_bytes = current_stat['bytes'] - old_stat['bytes']
        delta_time = current_stat['life'] - old_stat['life']
        print 'birate'
        print 'old', old_stat
        print 'current', current_stat
        return 1.0 * 8 * delta_bytes / delta_time if delta_time > 0 else 0

    @staticmethod
    def flow_id(stat):
        return stat['key'], stat['appId'], stat['appName']

    def add_stats(self, stat_list):
        TM = {}
        filtered_stats = {}

        # Keep just the more recent per-flow stat
        for stat in stat_list:
            if self.flow_id(stat) not in filtered_stats or \
                    (self.flow_id(stat) in filtered_stats and stat['life'] > filtered_stats[self.flow_id(stat)]['life']):
                filtered_stats[self.flow_id(stat)] = stat

        for stat in filtered_stats.values():
            if self.flow_id(stat) in self.last_stat:
                TM[self.flow_id(stat)] = self.bitrate(self.last_stat[self.flow_id(stat)], stat)
            self.last_stat[self.flow_id(stat)] = stat

        self.TMs.append(TM)
        print TM

    def poll_stats(self):
        reply = json_get_req("http://%s:%d/onos/v1/imr/intentStats" % (ONOS_IP, ONOS_PORT))
        if 'response' not in reply:
            return
        self.add_stats(reply['response'])

    def get_TMs(self):
        return self.TMs


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
