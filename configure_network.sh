#!/bin/bash

ip link delete br0 type bridge

ip link add name br0 type bridge
ip link set eth0 down
ip link set eth1 down
ip link set eth0 master br0
ip link set eth1 master br0
ip link set eth0 up
ip link set eth1 up
ip link set br0 up
ip addr add 192.254.0.1/16 dev br0
ip route add 169.254.0.0/16 dev br0
echo 1 | tee /proc/sys/net/ipv4/ip_forward
echo GATA DISTRACTIA
