import networkx as nx
from utils import json_get_req
from config import *
import matplotlib.pyplot as plt


class TopoManager(object):
    def __init__(self):
        self.G = nx.Graph()
        self.hosts = []
        self.devices = []
        self.device_id_to_chassisid = {}

        # device's id is 'of:00000000000000a1', device's chassisID is 'a1'
        reply = json_get_req("http://%s:%d/onos/v1/devices" % (ONOS_IP, ONOS_PORT))
        if 'devices' not in reply:
            return
        for dev in reply['devices']:
            self.device_id_to_chassisid[dev['id']] = dev['chassisId']
            self.G.add_node(dev['id'], type='device')
            self.devices.append(dev['id'])

        reply = json_get_req("http://%s:%d/onos/v1/links" % (ONOS_IP, ONOS_PORT))
        if 'links' not in reply:
            return
        for link in reply['links']:
            n1 = link['src']['device']
            n2 = link['dst']['device']
            # TODO should we add information about ConnectPoint?
            self.G.add_edge(n1, n2)

        reply = json_get_req("http://%s:%d/onos/v1/hosts" % (ONOS_IP, ONOS_PORT))
        if 'hosts' not in reply:
            return
        for host in reply['hosts']:
            # hostname = TopoManager.multi_ip_hostname(host['ipAddresses']) if host['ipAddresses'] != [] else host['id']
            hostname = host['id']
            self.G.add_node(hostname, type='host')
            n1 = hostname
            for location in host['locations']:
                n2 = location['elementId']
                self.G.add_edge(n1, n2)
            self.hosts.append(hostname)

        self.pos = nx.fruchterman_reingold_layout(self.G)

        # TODO how to get link capacities from ONOS?
        self.capacity_dict = {link: 1e6 for link in
                              [e for e in self.G.edges() if e[0] in self.devices and e[1] in self.devices]}

    @staticmethod
    def multi_ip_hostname(ip_list):
        if len(ip_list) == 1:
            return ip_list[0]
        else:
            return "\n".join(sorted(ip_list))

    def draw_topo(self, block=True):
        plt.figure()
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.hosts, node_shape='o', node_color='w')
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=self.devices, node_shape='s', node_color='b')
        nx.draw_networkx_labels(self.G.subgraph(self.hosts), self.pos, font_color='k')
        nx.draw_networkx_labels(self.G.subgraph(self.devices), self.pos, font_color='w',
                                labels=self.device_id_to_chassisid)
        nx.draw_networkx_edges(self.G, self.pos)
        plt.show(block=block)

    def shortestPath(self, from_el, to_el):
        return nx.shortest_path(self.G, from_el, to_el)
