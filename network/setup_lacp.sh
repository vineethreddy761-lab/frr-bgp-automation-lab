#!/usr/bin/env bash
echo "[INFO] Loading bonding kernel module..."
sudo modprobe bonding

echo "[INFO] Creating bond0 interface with LACP (mode 4)..."
sudo ip link add bond0 type bond
sudo ip link set bond0 type bond mode 4 xmit_hash_policy layer3+4

echo "[INFO] Bond interface created successfully."
ip link show bond0
