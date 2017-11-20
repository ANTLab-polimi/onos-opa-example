from config import *
from utils import json_get_req
from Stats import Stats


class StatsManager(object):
    def __init__(self):
        self.last_stats = {}
        self.TMs = []
        self.rand = [[Stats(0, 10, 10, 0, 'key1', 0, 'appName')],
                     [Stats(5, 15, 10, 0, 'key1', 0, 'appName')],
                     [Stats(25, 20, 10, 0, 'key2', 0, 'appName')],
                     [Stats(35, 21, 10, 0, 'key2', 0, 'appName'), Stats(35, 150, 10, 0, 'key1', 0, 'appName')]]

    def add_stats(self, stat_list):
        TM = {}
        for stat in stat_list:
            if stat.intentKey in self.last_stats:
                TM[stat.intentKey] = self.bitrate(self.last_stats[stat.intentKey], stat)
            self.last_stats[stat.intentKey] = stat
        self.TMs.append(TM)

    def get_TM_samples(self):
        reply = json_get_req("http://%s:%d/onos/v1/imr/intentStats" % (ONOS_IP, ONOS_PORT))
        if 'response' not in reply:
            return
        self.add_stats(reply['response'])

    @staticmethod
    def bitrate(old_stat, current_stat):
        delta_bytes = current_stat.bytes - old_stat.bytes
        delta_time = current_stat.ts - old_stat.ts
        return 1.0*delta_bytes/delta_time if delta_time > 0 else 0


class FakeStatsManager(StatsManager):
    def __init__(self):
        super(FakeStatsManager, self).__init__()
        self.rand = [[Stats(0, 10, 10, 0, 'key1', 0, 'appName')],
                     [Stats(5, 15, 10, 0, 'key1', 0, 'appName')],
                     [Stats(25, 20, 10, 0, 'key2', 0, 'appName')],
                     [Stats(35, 21, 10, 0, 'key2', 0, 'appName'), Stats(35, 150, 10, 0, 'key1', 0, 'appName')]]

    def get_TM_samples(self):
        if len(self.rand) == 0:
            return
        reply = {'response': self.rand.pop(0)}
        if 'response' not in reply:
            return
        self.add_stats(reply['response'])
