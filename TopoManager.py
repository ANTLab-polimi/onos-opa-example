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
        super(FakeTopoManager, self).__init__()

'''
http://onosvm.local:8181/onos/v1/devices
{"devices":[{"id":"of:000000000000000c","type":"SWITCH","available":true,"role":"MASTER","mfr":"Nicira, Inc.","hw":"Open vSwitch","sw":"2.5.2","serial":"None","driver":"ovs","chassisId":"c","annotations":{"managementAddress":"127.0.0.1","protocol":"OF_13","channelId":"127.0.0.1:58268"}},{"id":"of:000000000000000d","type":"SWITCH","available":true,"role":"MASTER","mfr":"Nicira, Inc.","hw":"Open vSwitch","sw":"2.5.2","serial":"None","driver":"ovs","chassisId":"d","annotations":{"managementAddress":"127.0.0.1","protocol":"OF_13","channelId":"127.0.0.1:58272"}},{"id":"of:000000000000000b","type":"SWITCH","available":true,"role":"MASTER","mfr":"Nicira, Inc.","hw":"Open vSwitch","sw":"2.5.2","serial":"None","driver":"ovs","chassisId":"b","annotations":{"managementAddress":"127.0.0.1","protocol":"OF_13","channelId":"127.0.0.1:58262"}},{"id":"of:000000000000000e","type":"SWITCH","available":true,"role":"MASTER","mfr":"Nicira, Inc.","hw":"Open vSwitch","sw":"2.5.2","serial":"None","driver":"ovs","chassisId":"e","annotations":{"managementAddress":"127.0.0.1","protocol":"OF_13","channelId":"127.0.0.1:58266"}},{"id":"of:0000000000000001","type":"SWITCH","available":true,"role":"MASTER","mfr":"Nicira, Inc.","hw":"Open vSwitch","sw":"2.5.2","serial":"None","driver":"ovs","chassisId":"1","annotations":{"managementAddress":"127.0.0.1","protocol":"OF_13","channelId":"127.0.0.1:58264"}},{"id":"of:0000000000000002","type":"SWITCH","available":true,"role":"MASTER","mfr":"Nicira, Inc.","hw":"Open vSwitch","sw":"2.5.2","serial":"None","driver":"ovs","chassisId":"2","annotations":{"managementAddress":"127.0.0.1","protocol":"OF_13","channelId":"127.0.0.1:58270"}}]}

http://onosvm.local:8181/onos/v1/links
{"links":[{"src":{"port":"1","device":"of:000000000000000d"},"dst":{"port":"4","device":"of:0000000000000001"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"2","device":"of:000000000000000e"},"dst":{"port":"5","device":"of:0000000000000002"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"1","device":"of:000000000000000b"},"dst":{"port":"2","device":"of:0000000000000001"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"2","device":"of:000000000000000c"},"dst":{"port":"3","device":"of:0000000000000002"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"2","device":"of:0000000000000002"},"dst":{"port":"2","device":"of:000000000000000b"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"4","device":"of:0000000000000002"},"dst":{"port":"2","device":"of:000000000000000d"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"3","device":"of:0000000000000001"},"dst":{"port":"1","device":"of:000000000000000c"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"5","device":"of:0000000000000001"},"dst":{"port":"1","device":"of:000000000000000e"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"1","device":"of:0000000000000002"},"dst":{"port":"1","device":"of:0000000000000001"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"1","device":"of:000000000000000e"},"dst":{"port":"5","device":"of:0000000000000001"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"2","device":"of:000000000000000d"},"dst":{"port":"4","device":"of:0000000000000002"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"1","device":"of:000000000000000c"},"dst":{"port":"3","device":"of:0000000000000001"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"2","device":"of:000000000000000b"},"dst":{"port":"2","device":"of:0000000000000002"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"1","device":"of:0000000000000001"},"dst":{"port":"1","device":"of:0000000000000002"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"2","device":"of:0000000000000001"},"dst":{"port":"1","device":"of:000000000000000b"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"3","device":"of:0000000000000002"},"dst":{"port":"2","device":"of:000000000000000c"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"5","device":"of:0000000000000002"},"dst":{"port":"2","device":"of:000000000000000e"},"type":"DIRECT","state":"ACTIVE"},{"src":{"port":"4","device":"of:0000000000000001"},"dst":{"port":"1","device":"of:000000000000000d"},"type":"DIRECT","state":"ACTIVE"}]}

http://onosvm.local:8181/onos/v1/hosts
{"hosts":[{"id":"00:00:00:00:00:01/None","mac":"00:00:00:00:00:01","vlan":"None","configured":false,"ipAddresses":["10.0.0.1"],"locations":[{"elementId":"of:000000000000000b","port":"3"}]},{"id":"00:00:00:00:00:08/None","mac":"00:00:00:00:00:08","vlan":"None","configured":false,"ipAddresses":["10.0.0.8"],"locations":[{"elementId":"of:000000000000000c","port":"4"}]}]}
'''