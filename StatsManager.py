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

        # Since for a same flow we receive many flow stats (possibly one for each switch), we keep just the most recent
        for app_stat in stat_list:
            for intents in app_stat['intents']:
                for intentKey, stats in intents.items():
                    for stat in stats:
                        flow_id = (intentKey, app_stat['id'], app_stat['name'])
                        if flow_id not in filtered_stats or \
                                (flow_id in filtered_stats and stat['life'] > filtered_stats[flow_id]['life']):
                            filtered_stats[flow_id] = stat

        # For each flow we check if a stat relative to a previous polling round is already available
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


'''
http://onosvm.local:8181/onos/v1/imr/intentStats
{"statistics":[{"id":71,"name":"org.onosproject.ifwd","intents":[{"00:00:00:00:00:08/None00:00:00:00:00:01/None":[{"id":"41939772554358923","tableId":0,"appId":"org.onosproject.net.intent","groupId":0,"priority":100,"timeout":0,"isPermanent":true,"deviceId":"of:0000000000000001","state":"ADDED","life":78,"packets":77,"bytes":7546,"liveType":"UNKNOWN","lastSeen":1511447769975,"treatment":{"instructions":[{"type":"OUTPUT","port":"2"}],"deferred":[]},"selector":{"criteria":[{"type":"IN_PORT","port":3},{"type":"ETH_DST","mac":"00:00:00:00:00:01"},{"type":"ETH_SRC","mac":"00:00:00:00:00:08"}]}},{"id":"41939773468048931","tableId":0,"appId":"org.onosproject.net.intent","groupId":0,"priority":100,"timeout":0,"isPermanent":true,"deviceId":"of:000000000000000b","state":"ADDED","life":78,"packets":77,"bytes":7546,"liveType":"UNKNOWN","lastSeen":1511447769983,"treatment":{"instructions":[{"type":"OUTPUT","port":"3"}],"deferred":[]},"selector":{"criteria":[{"type":"IN_PORT","port":1},{"type":"ETH_DST","mac":"00:00:00:00:00:01"},{"type":"ETH_SRC","mac":"00:00:00:00:00:08"}]}},{"id":"41939774073666626","tableId":0,"appId":"org.onosproject.net.intent","groupId":0,"priority":100,"timeout":0,"isPermanent":true,"deviceId":"of:000000000000000c","state":"ADDED","life":78,"packets":77,"bytes":7546,"liveType":"UNKNOWN","lastSeen":1511447769992,"treatment":{"instructions":[{"type":"OUTPUT","port":"1"}],"deferred":[]},"selector":{"criteria":[{"type":"IN_PORT","port":4},{"type":"ETH_DST","mac":"00:00:00:00:00:01"},{"type":"ETH_SRC","mac":"00:00:00:00:00:08"}]}}]},{"00:00:00:00:00:01/None00:00:00:00:00:08/None":[{"id":"41939774100762928","tableId":0,"appId":"org.onosproject.net.intent","groupId":0,"priority":100,"timeout":0,"isPermanent":true,"deviceId":"of:000000000000000c","state":"ADDED","life":78,"packets":77,"bytes":7546,"liveType":"UNKNOWN","lastSeen":1511447769992,"treatment":{"instructions":[{"type":"OUTPUT","port":"4"}],"deferred":[]},"selector":{"criteria":[{"type":"IN_PORT","port":2},{"type":"ETH_DST","mac":"00:00:00:00:00:08"},{"type":"ETH_SRC","mac":"00:00:00:00:00:01"}]}},{"id":"41939771925797092","tableId":0,"appId":"org.onosproject.net.intent","groupId":0,"priority":100,"timeout":0,"isPermanent":true,"deviceId":"of:0000000000000002","state":"ADDED","life":78,"packets":77,"bytes":7546,"liveType":"UNKNOWN","lastSeen":1511447769984,"treatment":{"instructions":[{"type":"OUTPUT","port":"3"}],"deferred":[]},"selector":{"criteria":[{"type":"IN_PORT","port":2},{"type":"ETH_DST","mac":"00:00:00:00:00:08"},{"type":"ETH_SRC","mac":"00:00:00:00:00:01"}]}},{"id":"41939772159200305","tableId":0,"appId":"org.onosproject.net.intent","groupId":0,"priority":100,"timeout":0,"isPermanent":true,"deviceId":"of:000000000000000b","state":"ADDED","life":78,"packets":77,"bytes":7546,"liveType":"UNKNOWN","lastSeen":1511447769983,"treatment":{"instructions":[{"type":"OUTPUT","port":"2"}],"deferred":[]},"selector":{"criteria":[{"type":"IN_PORT","port":3},{"type":"ETH_DST","mac":"00:00:00:00:00:08"},{"type":"ETH_SRC","mac":"00:00:00:00:00:01"}]}}]}]}]}
'''