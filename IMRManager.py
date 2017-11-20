import json
import operator
from config import ONOS_IP, ONOS_PORT
from utils import json_get_req, json_post_req
import networkx as nx

class IMRManager ():
    def __init__(self, topology):
        self.intentKey_to_inOutElements = {}
        self.topology = topology

        # reply = json_get_req("http://%s:%d/onos/v1/imr/monitoredIntents" % (ONOS_IP, ONOS_PORT))
        reply = {'response': [{'intentKey': 'key1', 'appId': 0, 'appName': 'testApp',
                               'inElement': u'00:00:00:00:00:01/None', 'outElement': u'00:00:00:00:00:02/None'},
                              {'intentKey': 'key2', 'appId': 0, 'appName': 'testApp',
                               'inElement': u'00:00:00:00:00:01/None', 'outElement': u'00:00:00:00:00:03/None'}]}

        if 'response' not in reply:
            return
        for intent in reply['response']:
            self.intentKey_to_inOutElements[intent['intentKey']] = (intent['inElement'], intent['outElement'])

    def monitoredIntents(self):
        return self.intentKey_to_inOutElements.keys()

    def reRouteMonitoredIntents(self, worst_TM):
        reRouting = {"routingList": []}

        residual_topo = self.topology.G.copy()
        residual_capacities = self.topology.link_capacities.copy()
        nx.set_edge_attributes(residual_topo, 'weight', self.inverse_capacity(residual_capacities))
        for intentKey, amount in sorted(worst_TM.items(), key=operator.itemgetter(1), reverse=True):
            dem = self.intentKey_to_inOutElements[intentKey]
            print 'Path', dem[0], dem[1]

            try:
                path = nx.shortest_path(residual_topo, dem[0], dem[1], 'weight')
                print path
                for link in zip(path, path[1:]):
                    if link[0] not in self.topology.hosts and link[1] not in self.topology.hosts:
                        residual_capacities[link] -= amount
                        residual_capacities[link[1], link[0]] -= amount
                        if residual_capacities[link] <= 0:
                            del residual_capacities[link]
                            del residual_capacities[link[1], link[0]]
                            residual_topo.remove_edge(link[0], link[1])
                            residual_topo.remove_edge(link[1], link[0])
                nx.set_edge_attributes(residual_topo, 'residual', self.inverse_capacity(residual_capacities))
                '''pos = nx.fruchterman_reingold_layout(residual_topo)
                nx.draw_networkx(residual_topo, pos)
                nx.draw_networkx_edge_labels(residual_topo, pos, residual_capacities)
                import matplotlib.pyplot as plt
                plt.show()'''
                current_reroute = {}
                current_reroute["key"] = intentKey
                current_reroute["paths"] = []
                current_reroute["paths"].append({})
                current_reroute["paths"][0]["path"] = path
                current_reroute["paths"][0]["weight"] = 1.0
                reRouting["routingList"].append(current_reroute)
            except nx.NetworkXNoPath:
                print 'No path between %s and %s' % (dem[0], dem[1])
        print "ReRouting config:"
        print reRouting
        json_post_req(("http://%s:%d/onos/v1/imr/reRouteIntents" % (ONOS_IP, ONOS_PORT)), json.dumps(reRouting))

    @staticmethod
    def inverse_capacity(d):
        return {k: 1.0 / v for k, v in d.items()}