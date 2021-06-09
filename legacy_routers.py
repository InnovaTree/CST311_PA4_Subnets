#!/usr/bin/python

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
    # Change - moved switches ahead of routers
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)

    # Change - add ip address of r5-eth0
    r5 = net.addHost('r5', cls=Node, ip='10.0.2.1/24')
    r5.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Change - add ip address of r4-eth0
    r4 = net.addHost('r4', cls=Node, ip='192.168.1.2/30')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Change - add ip address of r3-eth0
    r3 = net.addHost('r3', cls=Node, ip='10.0.1.1/24')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')

    info('*** Add hosts\n')

    # Change - add IP address of h1 and h2
    h1 = net.addHost('h1', cls=Host, ip='10.0.1.100/24',
                     defaultRoute='via 10.0.1.1')
    h2 = net.addHost('h2', cls=Host, ip='10.0.2.100/24',
                     defaultRoute='via 10.0.2.1')

    info('*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s2)

    net.addLink(s2, r5)
    net.addLink(s1, r3)

    # Change - add IP address of router-eth1
    net.addLink(r3, r4, intfName1='r3-eth1',
                params1={'ip': '192.168.1.1/30'})

    # Change - add IP address of router-eth1
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

    info('*** Adding static routes for R3, R4, R5\n')

    r3.cmd('ip route add 10.0.2.0/24 via 192.168.1.2 dev r3-eth1')
    r3.cmd('ip route add 192.168.1.4/30 via 192.168.1.2 dev r3-eth1')

    r4.cmd('ip route add 10.0.2.0/24 via 192.168.1.6 dev r4-eth1')
    r4.cmd('ip route add 10.0.1.0/24 via 192.168.1.1 dev r4-eth0')

    r5.cmd('ip route add 10.0.1.0/24 via 192.168.1.5 dev r5-eth1')
    r5.cmd('ip route add 192.168.1.0/30 via 192.168.1.5 dev r5-eth1')


    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
