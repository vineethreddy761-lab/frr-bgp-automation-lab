#!/usr/bin/env bash
# Network Topology & Bonding Simulation Script

echo "[INFO] Setting up virtual network namespaces and dummy interfaces..."

# Create dummy interfaces to simulate external network links or Telco peers
sudo ip link add dummy1 type dummy
sudo ip link add dummy2 type dummy

sudo ip addr add 192.168.100.1/24 dev dummy1
sudo ip addr add 192.168.200.1/24 dev dummy2

sudo ip link set dummy1 up
sudo ip link set dummy2 up

echo "[INFO] Network topology simulation interfaces created successfully."
ip -o addr show dev dummy1
ip -o addr show dev dummy2
