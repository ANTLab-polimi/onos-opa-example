import matplotlib.pyplot as plt
import networkx as nx
from config import *
from utils import json_get_req


class TopoManager(object):
    def __init__(self):
        self.G = nx.Graph()
        self.hosts = []
        self.devices = []
        self.deviceId_to_chassisId = {}

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


class FakeTopoManager(TopoManager):
    def __init__(self):
        self.G = nx.Graph()
        self.hosts = []
        self.devices = []
        self.deviceId_to_chassisId = {}

        reply = {u'devices': [{u'available': True, u'chassisId': u'c', u'driver': u'ovs', u'sw': u'2.5.2', u'hw': u'Open vSwitch', u'annotations': {u'managementAddress': u'127.0.0.1', u'channelId': u'127.0.0.1:42522', u'protocol': u'OF_13'}, u'mfr': u'Nicira, Inc.', u'role': u'MASTER', u'serial': u'None', u'type': u'SWITCH', u'id': u'of:000000000000000c'}, {u'available': True, u'chassisId': u'd', u'driver': u'ovs', u'sw': u'2.5.2', u'hw': u'Open vSwitch', u'annotations': {u'managementAddress': u'127.0.0.1', u'channelId': u'127.0.0.1:42526', u'protocol': u'OF_13'}, u'mfr': u'Nicira, Inc.', u'role': u'MASTER', u'serial': u'None', u'type': u'SWITCH', u'id': u'of:000000000000000d'}, {u'available': True, u'chassisId': u'b', u'driver': u'ovs', u'sw': u'2.5.2', u'hw': u'Open vSwitch', u'annotations': {u'managementAddress': u'127.0.0.1', u'channelId': u'127.0.0.1:42516', u'protocol': u'OF_13'}, u'mfr': u'Nicira, Inc.', u'role': u'MASTER', u'serial': u'None', u'type': u'SWITCH', u'id': u'of:000000000000000b'}, {u'available': True, u'chassisId': u'e', u'driver': u'ovs', u'sw': u'2.5.2', u'hw': u'Open vSwitch', u'annotations': {u'managementAddress': u'127.0.0.1', u'channelId': u'127.0.0.1:42520', u'protocol': u'OF_13'}, u'mfr': u'Nicira, Inc.', u'role': u'MASTER', u'serial': u'None', u'type': u'SWITCH', u'id': u'of:000000000000000e'}, {u'available': True, u'chassisId': u'1', u'driver': u'ovs', u'sw': u'2.5.2', u'hw': u'Open vSwitch', u'annotations': {u'managementAddress': u'127.0.0.1', u'channelId': u'127.0.0.1:42518', u'protocol': u'OF_13'}, u'mfr': u'Nicira, Inc.', u'role': u'MASTER', u'serial': u'None', u'type': u'SWITCH', u'id': u'of:0000000000000001'}, {u'available': True, u'chassisId': u'2', u'driver': u'ovs', u'sw': u'2.5.2', u'hw': u'Open vSwitch', u'annotations': {u'managementAddress': u'127.0.0.1', u'channelId': u'127.0.0.1:42524', u'protocol': u'OF_13'}, u'mfr': u'Nicira, Inc.', u'role': u'MASTER', u'serial': u'None', u'type': u'SWITCH', u'id': u'of:0000000000000002'}]}
        if 'devices' not in reply:
            return
        for dev in reply['devices']:
            # id is 'of:00000000000000a1', chassisID is 'a1'
            self.deviceId_to_chassisId[dev['id']] = dev['chassisId']
            self.G.add_node(dev['id'], type='device')
            self.devices.append(dev['id'])

        reply = {u'links': [{u'src': {u'device': u'of:000000000000000e', u'port': u'1'}, u'dst': {u'device': u'of:0000000000000001', u'port': u'5'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:000000000000000e', u'port': u'2'}, u'dst': {u'device': u'of:0000000000000002', u'port': u'5'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:000000000000000d', u'port': u'1'}, u'dst': {u'device': u'of:0000000000000001', u'port': u'4'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:000000000000000d', u'port': u'2'}, u'dst': {u'device': u'of:0000000000000002', u'port': u'4'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:000000000000000c', u'port': u'1'}, u'dst': {u'device': u'of:0000000000000001', u'port': u'3'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:000000000000000b', u'port': u'1'}, u'dst': {u'device': u'of:0000000000000001', u'port': u'2'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:000000000000000c', u'port': u'2'}, u'dst': {u'device': u'of:0000000000000002', u'port': u'3'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:000000000000000b', u'port': u'2'}, u'dst': {u'device': u'of:0000000000000002', u'port': u'2'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000002', u'port': u'2'}, u'dst': {u'device': u'of:000000000000000b', u'port': u'2'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000002', u'port': u'3'}, u'dst': {u'device': u'of:000000000000000c', u'port': u'2'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000001', u'port': u'2'}, u'dst': {u'device': u'of:000000000000000b', u'port': u'1'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000001', u'port': u'3'}, u'dst': {u'device': u'of:000000000000000c', u'port': u'1'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000002', u'port': u'4'}, u'dst': {u'device': u'of:000000000000000d', u'port': u'2'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000002', u'port': u'5'}, u'dst': {u'device': u'of:000000000000000e', u'port': u'2'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000001', u'port': u'4'}, u'dst': {u'device': u'of:000000000000000d', u'port': u'1'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000001', u'port': u'5'}, u'dst': {u'device': u'of:000000000000000e', u'port': u'1'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000002', u'port': u'1'}, u'dst': {u'device': u'of:0000000000000001', u'port': u'1'}, u'type': u'DIRECT', u'state': u'ACTIVE'}, {u'src': {u'device': u'of:0000000000000001', u'port': u'1'}, u'dst': {u'device': u'of:0000000000000002', u'port': u'1'}, u'type': u'DIRECT', u'state': u'ACTIVE'}]}
        if 'links' not in reply:
            return
        for link in reply['links']:
            n1 = link['src']['device']
            n2 = link['dst']['device']
            if 'annotations' in link and 'bandwidth' in link['annotations']:
                    bw = int(link['annotations']['bandwidth']) * 1e6
            else:
                bw = DEFAULT_CAPACITY
            self.G.add_edge(n1, n2, {'bandwidth': bw})

        reply = {u'hosts': [{u'configured': False, u'vlan': u'None', u'locations': [{u'port': u'3', u'elementId': u'of:000000000000000b'}], u'mac': u'00:00:00:00:00:01', u'ipAddresses': [u'10.0.0.1'], u'id': u'00:00:00:00:00:01/None'}, {u'configured': False, u'vlan': u'None', u'locations': [{u'port': u'4', u'elementId': u'of:000000000000000c'}], u'mac': u'00:00:00:00:00:08', u'ipAddresses': [u'10.0.0.8'], u'id': u'00:00:00:00:00:08/None'}]}
        if 'hosts' not in reply:
            return
        for host in reply['hosts']:
            self.G.add_node(host['id'], type='host')
            for location in host['locations']:
                self.G.add_edge(host['id'], location['elementId'],  {'bandwidth': DEFAULT_ACCESS_CAPACITY})
            self.hosts.append(host['id'])

        self.pos = nx.fruchterman_reingold_layout(self.G)
