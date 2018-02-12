import json
import networkx as nx
from config import ONOS_IP, ONOS_PORT, VERBOSE
from utils import json_get_req, json_post_req, bps_to_human_string
from pprint import pprint
import logging


class IMRManager(object):
    def __init__(self, verbose=VERBOSE):
        self.intentKey_to_inOutElements = {}
        self.verbose = verbose
        self.retrieve_monitored_intents_from_ONOS()

    def retrieve_monitored_intents_from_ONOS(self):
        logging.info("Retrieving Monitored Intents...")
        reply = json_get_req('http://%s:%d/onos/v1/imr/imr/monitoredIntents' % (ONOS_IP, ONOS_PORT))
        if 'response' not in reply:
            return
        for apps in reply['response']:
            for intent in apps['intents']:
                if self.verbose:
                    print intent
                flow_id = (intent['key'], apps['id'], apps['name'])
                if len(intent['inElements']) == 1 and len(intent['outElements']) == 1:
                    self.intentKey_to_inOutElements[flow_id] = (intent['inElements'][0], intent['outElements'][0])
                else:
                    print 'Intent with multiple inElements/outElements are not currently supported :('

    def get_monitored_intents(self):
        return set(self.intentKey_to_inOutElements.keys())

    def reroute_monitored_intents(self, tm, topoManager):
        reroute_msg = {'routingList': []}

        topo = topoManager.G.copy()

        # iterate over flows (sorted by amount, in decreasing order)
        for flow_id, amount in sorted(tm.items(), key=lambda x: x[1], reverse=True):
            intent_key, app_id, app_name = flow_id
            in_elem, out_elem = self.intentKey_to_inOutElements[flow_id]
            if self.verbose:
                print '\nTrying to route %s for demand %s -> %s' % (bps_to_human_string(amount), in_elem, out_elem)

            # build a reduced_topo keeping just links with enough capacity to accomodate the current demand
            reduced_topo = reduced_capacity_topo(topo, amount)
            try:
                path = nx.shortest_path(reduced_topo, in_elem, out_elem)
                if self.verbose:
                    print 'Found path %s' % path
                # update the topology
                topo = reduced_capacity_on_path(topo, amount, path)
                reroute_msg['routingList'].append(
                    {'key': intent_key, 'appId': {'id': app_id, 'name': app_name},
                     'paths': [{'path': path, 'weight': 1.0}]}
                )
            except nx.NetworkXNoPath:
                if self.verbose:
                    print 'No path found'

        if self.verbose:
            logging.info('reroute_msg config:')
            pprint(reroute_msg)
        json_post_req(('http://%s:%d/onos/v1/imr/imr/reRouteIntents' % (ONOS_IP, ONOS_PORT)), json.dumps(reroute_msg))


def reduced_capacity_on_path(topo, amount, path):
    reduced_topo = topo.copy()
    for link in zip(path, path[1:]):
        if reduced_topo[link[0]][link[1]]['bandwidth'] - amount <= 0:
            reduced_topo.remove_edge(link[0], link[1])
        else:
            reduced_topo[link[0]][link[1]]['bandwidth'] -= amount
    return reduced_topo


def reduced_capacity_topo(topo, amount):
    reduced_topo = topo.copy()
    for u, v, data in reduced_topo.edges(data=True):
        if data['bandwidth'] - amount < 0:
            reduced_topo.remove_edge(u, v)
        else:
            data['bandwidth'] -= amount
    return reduced_topo
