import networkx as nx
from utils import json_get_req
from config import *
import matplotlib.pyplot as plt


class TopoManager(object):
    def __init__(self):
        self.G = nx.DiGraph()
        self.hosts = []
        self.devices = []
        self.deviceId_to_chassisId = {}
        self.link_capacities = {}

        # device's id is 'of:00000000000000a1', device's chassisID is 'a1'
        reply = json_get_req("http://%s:%d/onos/v1/devices" % (ONOS_IP, ONOS_PORT))
        if 'devices' not in reply:
            return
        for dev in reply['devices']:
            self.deviceId_to_chassisId[dev['id']] = dev['chassisId']
            self.G.add_node(dev['id'], type='device')
            self.devices.append(dev['id'])

        reply = json_get_req("http://%s:%d/onos/v1/links" % (ONOS_IP, ONOS_PORT))
        if 'links' not in reply:
            return
        for link in reply['links']:
            n1 = link['src']['device']
            n2 = link['dst']['device']
            if 'annotations' in link:
                if 'bandwidth' in link['annotations']:
                    self.link_capacities[n1, n2] = int(link['annotations']['bandwidth'])*1e6
            else:
                self.link_capacities[n1, n2] = DEFAULT_CAPACITY
            self.G.add_edge(n1, n2)

        reply = json_get_req("http://%s:%d/onos/v1/hosts" % (ONOS_IP, ONOS_PORT))
        if 'hosts' not in reply:
            return
        for host in reply['hosts']:
            self.G.add_node(host['id'], type='host')
            for location in host['locations']:
                self.G.add_edge(host['id'], location['elementId'])
                self.G.add_edge(location['elementId'], host['id'])
                self.link_capacities[host['id'], location['elementId']] = DEFAULT_CAPACITY
                self.link_capacities[location['elementId'], host['id']] = DEFAULT_CAPACITY
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

    def shortestPath(self, from_el, to_el, weight):
        return nx.shortest_path(self.G, from_el, to_el, weight)


class FakeTopoManager(TopoManager):
    def __init__(self):
        self.G = nx.DiGraph()
        self.hosts = []
        self.devices = []
        self.deviceId_to_chassisId = {}
        self.link_capacities = {}

        # device's id is 'of:00000000000000a1', device's chassisID is 'a1'
        # reply = json_get_req("http://%s:%d/onos/v1/devices" % (ONOS_IP, ONOS_PORT))
        reply = {'devices': [{u'available': True, u'chassisId': u'3', u'sw': u'2.5.2', u'hw': u'Open vSwitch', u'annotations': {u'managementAddress': u'127.0.0.1', u'channelId': u'127.0.0.1:57710', u'protocol': u'OF_13'}, u'mfr': u'Nicira, Inc.', u'role': u'MASTER', u'serial': u'None', u'type': u'SWITCH', u'id': u'of:0000000000000003'}, {u'available': True, u'chassisId': u'1', u'sw': u'2.5.2', u'hw': u'Open vSwitch', u'annotations': {u'managementAddress': u'127.0.0.1', u'channelId': u'127.0.0.1:57708', u'protocol': u'OF_13'}, u'mfr': u'Nicira, Inc.', u'role': u'MASTER', u'serial': u'None', u'type': u'SWITCH', u'id': u'of:0000000000000001'}, {u'available': True, u'chassisId': u'2', u'sw': u'2.5.2', u'hw': u'Open vSwitch', u'annotations': {u'managementAddress': u'127.0.0.1', u'channelId': u'127.0.0.1:57712', u'protocol': u'OF_13'}, u'mfr': u'Nicira, Inc.', u'role': u'MASTER', u'serial': u'None', u'type': u'SWITCH', u'id': u'of:0000000000000002'}]}
        if 'devices' not in reply:
            return
        for dev in reply['devices']:
            self.deviceId_to_chassisId[dev['id']] = dev['chassisId']
            self.G.add_node(dev['id'], type='device')
            self.devices.append(dev['id'])

        # reply = json_get_req("http://%s:%d/onos/v1/links" % (ONOS_IP, ONOS_PORT))
        reply = {u'links': [{u'src': {u'device': u'of:0000000000000002', u'port': u'3'}, u'dst': {u'device': u'of:0000000000000003', u'port': u'2'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000002', u'port': u'2'}, u'dst': {u'device': u'of:0000000000000001', u'port': u'2'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000003', u'port': u'2'}, u'dst': {u'device': u'of:0000000000000002', u'port': u'3'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000001', u'port': u'2'}, u'dst': {u'device': u'of:0000000000000002', u'port': u'2'}, u'type': u'DIRECT', u'state': u'ACTIVE'}]}
        if 'links' not in reply:
            return
        for link in reply['links']:
            n1 = link['src']['device']
            n2 = link['dst']['device']
            if 'annotations' in link:
                if 'bandwidth' in link['annotations']:
                    self.link_capacities[n1, n2] = int(link['annotations']['bandwidth'])*1e6
            else:
                self.link_capacities[n1, n2] = DEFAULT_CAPACITY
            self.G.add_edge(n1, n2)

        # reply = json_get_req("http://%s:%d/onos/v1/hosts" % (ONOS_IP, ONOS_PORT))
        reply = {u'hosts': [{u'configured': False, u'vlan': u'None', u'mac': u'00:00:00:00:00:01', u'locations': [{u'port': u'1', u'elementId': u'of:0000000000000001'}], u'ipAddresses': [], u'id': u'00:00:00:00:00:01/None'}, {u'configured': False, u'vlan': u'None', u'mac': u'00:00:00:00:00:02', u'locations': [{u'port': u'1', u'elementId': u'of:0000000000000002'}], u'ipAddresses': [], u'id': u'00:00:00:00:00:02/None'}, {u'configured': False, u'vlan': u'None', u'mac': u'00:00:00:00:00:03', u'locations': [{u'port': u'1', u'elementId': u'of:0000000000000003'}], u'ipAddresses': [], u'id': u'00:00:00:00:00:03/None'}]}
        if 'hosts' not in reply:
            return
        for host in reply['hosts']:
            self.G.add_node(host['id'], type='host')
            for location in host['locations']:
                self.G.add_edge(host['id'], location['elementId'])
                self.G.add_edge(location['elementId'], host['id'])
                self.link_capacities[host['id'], location['elementId']] = DEFAULT_CAPACITY
                self.link_capacities[location['elementId'], host['id']] = DEFAULT_CAPACITY
            self.hosts.append(host['id'])

        self.pos = nx.fruchterman_reingold_layout(self.G)
