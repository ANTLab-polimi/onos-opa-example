import matplotlib.pyplot as plt
import networkx as nx
from config import *
from utils import json_get_req
import logging


class TopoManager(object):
    def __init__(self):
        self.G = nx.Graph()
        self.pos = None
        self.hosts = []
        self.devices = []
        self.deviceId_to_chassisId = {}
        self.retrieve_topo_from_ONOS()

    def retrieve_topo_from_ONOS(self):
        logging.info("Retrieving Topology...")
        reply = json_get_req('http://%s:%d/onos/v1/devices' % (ONOS_IP, ONOS_PORT))
        if 'devices' not in reply:
            return
        for dev in reply['devices']:
            # id is 'of:00000000000000a1', chassisID is 'a1'
            self.deviceId_to_chassisId[dev['id']] = dev['chassisId']
            self.G.add_node(dev['id'], type='device')
            self.devices.append(dev['id'])

        reply = json_get_req('http://%s:%d/onos/v1/links' % (ONOS_IP, ONOS_PORT))
        if 'links' not in reply:
            return
        for link in reply['links']:
            n1 = link['src']['device']
            n2 = link['dst']['device']
            if 'annotations' in link and 'bandwidth' in link['annotations']:
                    bw = int(link['annotations']['bandwidth']) * 1e6
            else:
                bw = DEFAULT_CAPACITY
            self.G.add_edge(n1, n2, **{'bandwidth': bw})

        reply = json_get_req('http://%s:%d/onos/v1/hosts' % (ONOS_IP, ONOS_PORT))
        if 'hosts' not in reply:
            return
        for host in reply['hosts']:
            self.G.add_node(host['id'], type='host')
            for location in host['locations']:
                self.G.add_edge(host['id'], location['elementId'],  **{'bandwidth': DEFAULT_ACCESS_CAPACITY})
            self.hosts.append(host['id'])

        self.pos = nx.fruchterman_reingold_layout(self.G)

    def draw_topo(self, block=True):
        plt.figure()
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.hosts, node_shape='o', node_color='w')
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.devices, node_shape='s', node_color='b')
        nx.draw_networkx_labels(self.G.subgraph(self.hosts), self.pos, font_color='k')
        nx.draw_networkx_labels(self.G.subgraph(self.devices), self.pos, font_color='w',
                                labels=self.deviceId_to_chassisId)
        nx.draw_networkx_edges(self.G, self.pos)
        plt.show(block=block)
