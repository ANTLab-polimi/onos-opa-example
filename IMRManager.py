import json
import operator
import networkx as nx
from config import ONOS_IP, ONOS_PORT
from utils import json_get_req, json_post_req
from StatsManager import StatsManager


class IMRManager(object):
    def __init__(self, topo):
        self.intentKey_to_inOutElements = {}
        self.topo = topo

        reply = json_get_req("http://%s:%d/onos/v1/imr/monitoredIntents" % (ONOS_IP, ONOS_PORT))
        if 'response' not in reply:
            return
        for intent in reply['response']:
            self.intentKey_to_inOutElements[StatsManager.flow_id(intent)] = (intent['inElement'], intent['outElement'])

    def monitoredIntents(self):
        return set(self.intentKey_to_inOutElements.keys())

    def reRouteMonitoredIntents(self, worst_TM):
        reroute_msg = {"routingList": []}

        topo = self.topo.G.copy()
        
        # for each flow (sorted by amount, in decreasing order)
        for flow_id, amount in sorted(worst_TM.items(), key=operator.itemgetter(1), reverse=True):
            dem = self.intentKey_to_inOutElements[flow_id]
            print '\nTrying to route %d bps for demand %s -> %s' % (amount, dem[0], dem[1])
            # compute the shortest path on the residual graph
            reduced_topo = self.reduced_capacity_topo(topo, amount)
            try:
                path = nx.shortest_path(reduced_topo, dem[0], dem[1])
                print 'Found path %s' % path
                # if a path is found, update the residual capacity
                topo = self.reduced_capacity_on_path(topo, amount, path)
                reroute_msg["routingList"].append(
                    {'key': flow_id[0], 'appId': {'id': flow_id[1], 'name': flow_id[2]},
                     'paths': [{'path': path, 'weight': 1.0}]}
                )
            except nx.NetworkXNoPath:
                print 'No path found'

        print "reroute_msg config:"
        print reroute_msg
        json_post_req(("http://%s:%d/onos/v1/imr/reRouteIntents" % (ONOS_IP, ONOS_PORT)), json.dumps(reroute_msg))

    @staticmethod
    def reduced_capacity_topo(topo, amount):
        reduced_topo = topo.copy()
        for u, v, data in reduced_topo.edges(data=True):
            if data['bandwidth'] - amount < 0:
                reduced_topo.remove_edge(u, v)
            else:
                data['bandwidth'] -= amount
        return reduced_topo

    @staticmethod
    def reduced_capacity_on_path(topo, amount, path):
        reduced_topo = topo.copy()
        for link in zip(path, path[1:]):
            if reduced_topo[link[0]][link[1]]['bandwidth'] - amount <= 0:
                reduced_topo.remove_edge(link[0], link[1])
            else:
                reduced_topo[link[0]][link[1]]['bandwidth'] -= amount
        return reduced_topo


class FakeIMRManager(IMRManager):
    def __init__(self, topo):
        self.intentKey_to_inOutElements = {}
        self.topo = topo

        reply = {'response': [{'key': 'key1', 'appId': 0, 'appName': 'testApp',
                               'inElement': u'00:00:00:00:00:01/None', 'outElement': u'00:00:00:00:00:08/None'},
                              {'key': 'key2', 'appId': 0, 'appName': 'testApp',
                               'inElement': u'00:00:00:00:00:08/None', 'outElement': u'00:00:00:00:00:01/None'}]}

        if 'response' not in reply:
            return
        for intent in reply['response']:
            self.intentKey_to_inOutElements[intent['key']] = (intent['inElement'], intent['outElement'])
