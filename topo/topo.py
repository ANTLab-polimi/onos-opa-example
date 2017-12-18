#!/usr/bin/env python

from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink


class CustomTopo(Topo):
    def __init__(self, bw=1e3, **opts):
        super(CustomTopo, self).__init__(**opts)

        s = [self.addSwitch('s%d' % n) for n in range(1, 4)]
        h = [self.addHost('h%d' % n) for n in range(1, 5)]

        self.addLink(s[0], s[1], bw=bw)
        self.addLink(s[0], s[2], bw=bw)
        self.addLink(s[2], s[1], bw=bw)

        self.addLink(h[0], s[0], bw=bw)
        self.addLink(h[1], s[0], bw=bw)
        self.addLink(h[2], s[1], bw=bw)
        self.addLink(h[3], s[1], bw=bw)


if __name__ == '__main__':
    net = Mininet(topo=CustomTopo(),
                  controller=RemoteController,
                  cleanup=True,
                  autoSetMacs=True,
                  autoStaticArp=True,
                  link=TCLink)
    net.start()
    CLI(net)
    net.stop()
