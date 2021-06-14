"""
NAMES: Larry Chiem, Ian Rowe, Raymond Shum, Nicholas Stankovich
DUE DATE: June 19, 2021
ASSIGNMENT: Team Programming Assignment #4
DESCRIPTION: This script is modified from the original MiniEdit Level 2
Script provided in the assignment spec sheet. The topology contains 3
routers (r3, r4, r5), two switches (s1, s2) and two hosts (h1, h2). The
goal is to implement a network such that h1 can successfully ping h2 and
vice versa.

There are four total subnets, holding interfaces (within parenthesis):

    - 10.0.1.0/24 (h1-eth0, IP: 10.0.1.100) (r3-eth0, IP: 10.0.1.1)
    - 192.168.1.0/30 (r3-eth1, IP: 192.168.1.1) (r4-eth0, IP: 192.168.1.2)
    - 192.168.1.4/30 (r4-eth1, IP: 192.168.1.5) (r5-eth1, IP: 192.168.1.6)
    - 10.0.2.0/24 (h2-eth0, IP: 10.0.2.100) (r5-eth0, IP: 10.0.2.1)

The 10.0.1.0/24 and 10.0.2.0/24 subnets consist of a host interface connected
to a switch interface and a second switch interface connecting to a router
interface.

The 192.168.1.0/30 and 192.168.1.4/30 subnets each consist of two directly
connected router interfaces (point to point links).
"""

# !/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call


def myNetwork():
    net = Mininet(topo=None,
                  build=False,
                  ipBase='10.0.0.0/24')

    info('*** Adding controller\n')
    c0 = net.addController(name='c0',
                           controller=Controller,
                           protocol='tcp',
                           port=6633)

    info('*** Add switches\n')
    # [Change] Moved switches ahead of routers as per instructions
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)

    # [Change] Set IP address and mask of r5-eth0
    r5 = net.addHost('r5', cls=Node, ip='10.0.2.1/24')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')

    # [Change] Set IP address and mask of r4-eth0
    r4 = net.addHost('r4', cls=Node, ip='192.168.1.2/30')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')

    # [Change] Set IP address and mask of r3-eth0
    r3 = net.addHost('r3', cls=Node, ip='10.0.1.1/24')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')

    info('*** Add hosts\n')

    # [Change] Set IP address, mask and default route of h1 and h2
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.100/24',
                     defaultRoute='via 10.0.1.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.2.100/24',
                     defaultRoute='via 10.0.2.1')

    info('*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s2)

    net.addLink(s2, r5)
    net.addLink(s1, r3)

    # [Change] Set IP address and mask of r3-eth1
    net.addLink(r3, r4, intfName1='r3-eth1',
                params1={'ip': '192.168.1.1/30'})

    # [Change] Set IP address and mask of r4-eth1 and r5-eth1
    net.addLink(r4, r5, intfName1='r4-eth1',
                params1={'ip': '192.168.1.5/30'},
                intfName2='r5-eth1',
                params2={'ip': '192.168.1.6/30'})

    info('*** Starting network\n')
    net.build()

    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')
    net.get('s2').start([c0])
    net.get('s1').start([c0])

    info('*** Post configure switches and hosts\n')

    # [Change] Added section to configure routing tables of r3, r4, r5
    info('*** Adding static routes for R3, R4, R5\n')

    # Configured routing table of r3
    # Added route to 10.0.2.0/24 (subnet of r5-eth0 and h2-eth0)
    # Added route to 192.168.1.4/30 (subnet of r4-eth1 and r5-eth1)
    r3.cmd('ip route add 10.0.2.0/24 via 192.168.1.2 dev r3-eth1')
    r3.cmd('ip route add 192.168.1.4/30 via 192.168.1.2 dev r3-eth1')

    # Configured routing table of r4
    # Added route to 10.0.2.0/24 (subnet of r5-eth0 and h2-eth0)
    # Added route to 10.0.1.0/24 (subnet of h1-eth0 and r3-eth0)
    r4.cmd('ip route add 10.0.2.0/24 via 192.168.1.6 dev r4-eth1')
    r4.cmd('ip route add 10.0.1.0/24 via 192.168.1.1 dev r4-eth0')

    # Configured routing table of r5
    # Added route to 10.0.1.0/24 (subnet of r5-eth0 and h2-eth0)
    # Added route to 192.168.1.0/30 (subnet of r3-eth1 and r4-eth0)
    r5.cmd('ip route add 10.0.1.0/24 via 192.168.1.5 dev r5-eth1')
    r5.cmd('ip route add 192.168.1.0/30 via 192.168.1.5 dev r5-eth1')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
