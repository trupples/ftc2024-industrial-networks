from scapy.all import *
import argparse
import time
from netifaces import ifaddresses, AF_INET
from matplotlib import pyplot as plt
import matplotlib as mpl
import matplotlib.axes as axes
import numpy as np

mpl.use('TkAgg')
plt.style.use('dark_background')

parser = argparse.ArgumentParser(
    description='Graphical network packet tracer for industrial networks demo')
parser.add_argument('-i', '--iface', default='eth0',
                    help='Network interface to sniff. Multiple interfaces can be specified as a comma-separated list')
args = vars(parser.parse_args())

class IFace:
    def __init__(self, iface):
        self.iface = iface
        self.addr = ifaddresses(iface)[AF_INET][0]['addr']
        self.stats = [0, 0]
    
    def pkt(self, pkt):
        if pkt.sniffed_on != self.iface:
            return
    
        if IP in pkt and pkt[IP].src == self.addr:
            self.stats[1] += 1
        elif IP in pkt and pkt[IP].dst == self.addr:
            self.stats[0] += 1
    
    def reset_count(self):
        self.stats = [0, 0]
    
    def __repr__(self):
        return f'{self.iface} ({self.addr}) incoming={self.stats[0]} outgoing={self.stats[1]}'

    def __str__(self):
        return f'{self.iface} incoming={self.stats[0]} outgoing={self.stats[1]}'

ifaces = {
    iface: IFace(iface) for iface in args['iface'].split(',')
}
print(f'{ifaces=}')
print(f'{[repr(ifaces[i]) for i in ifaces]=}')

fig, (ax1, ax2) = plt.subplots(2, 1)

ax1 : axes.Axes = ax1
ax2 : axes.Axes = ax2

ax1.set_title('Incoming packets')
swio_incoming, = ax1.plot([0, 0], [0, 0], color='#e5aa09', label='SWIO (eth0)')
max_incoming, = ax1.plot([0, 0], [0, 0], color='#0982e5', label='MAX (eth1)')
ax1.set_ybound(0, 150)
ax1.grid()
ax1.legend()

ax2.set_title('Outgoing packets')
swio_outgoing, = ax2.plot([0, 0], [0, 0], color='#e5aa09', label='SWIO (eth0)')
max_outgoing, = ax2.plot([0, 0], [0, 0], color='#0982e5', label='MAX (eth1)')
ax2.set_ybound(0, 100)
ax2.grid()
ax2.legend()

ts = [0]
si = [0]
so = [0]
mi = [0]
mo = [0]

fig.tight_layout()
plt.show(block=False)

def process_pkt(pkt):
    ifaces[pkt.sniffed_on].pkt(pkt)

    return None

def sniff_thread(*args):
    sniff(iface=list(ifaces.keys()), prn=process_pkt)

Thread(target=sniff_thread).start()

first = time.time()
last = first

while True:
    t = time.time()
    dt = t - last
    last = t
    t -= first
    print(f'{t=} {dt=}', end=' ')
    for name, iface in ifaces.items():
        print(f'| {iface} {ifaces["eth0"].stats=} {ifaces["eth1"].stats=}', end=' ')
    print()

    ts.append(t)
    si.append(ifaces['eth0'].stats[0] / dt)
    so.append(ifaces['eth0'].stats[1] / dt)
    mi.append(ifaces['eth1'].stats[0] / dt)
    mo.append(ifaces['eth1'].stats[1] / dt)

    swio_incoming.set_data(ts, si)
    swio_outgoing.set_data(ts, so)
    max_incoming.set_data(ts, mi)
    max_outgoing.set_data(ts, mo)
    
    for name, iface in ifaces.items():
        iface.reset_count()
    
    ax1.set_xbound(t - 10, t)
    ax2.set_xbound(t - 10, t)


    plt.pause(0.1)

