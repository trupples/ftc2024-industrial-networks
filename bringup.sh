#!/bin/bash -x

# Set up switch (bridge config)

scp ./configure_network.sh analog@kuiper-switch:
ssh analog@kuiper-switch -- 'sudo -S /home/analog/configure_network.sh'

# Set up network

ETH0_MAC=e4:5f:01:6d:7c:2a # Make sure it is different from the one automatically taken by eth1
ETH0_IP=169.254.12.34      # Ditto
SWITCH_IP=169.254.207.82 #$(getent hosts kuiper-switch | cut -d' ' -f1)

sudo ip link set eth0 down
sudo ip link set eth0 address $ETH0_MAC
sudo ip link set eth0 up
sudo ip address add $ETH0_IP/16 dev eth0
sudo ip route del 169.254.0.0/16 # Delete previous routes
sudo ip route add 169.254.0.0/16 via $ETH0_IP dev eth0

