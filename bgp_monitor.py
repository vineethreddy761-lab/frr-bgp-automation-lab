#!/usr/bin/env python3

import subprocess
import sys

def run_cmd(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\n{e.stderr.strip()}", file=sys.stderr)
        return None

def check_router_ns_bgp():
    """Check BGP summary for router-ns (AS 65001) using its specific vty socket."""
    cmd = 'sudo ip netns exec router-ns vtysh --vty_socket /run/frr-router-ns -c "show ip bgp summary"'
    output = run_cmd(cmd)
    if not output:
        return "ERROR", "Failed to fetch router-ns BGP summary."
    
    for line in output.splitlines():
        if "192.168.100.20" in line:
            parts = line.split()
            state_pfx = parts[-2] if len(parts) >= 10 else "Unknown"
            if state_pfx not in ["Idle", "Active", "Connect", "OpenSent", "OpenConfirm"]:
                return "OK", f"router-ns Peer 192.168.100.20 State/Prefix: {state_pfx}"
            return "DOWN", f"router-ns Peer State is {state_pfx}"
    return "DOWN", "router-ns BGP session peer not found."

def check_router2_bgp():
    """Check BGP summary for router2 inside router-ns (AS 65002)."""
    cmd = 'sudo ip netns exec router2 vtysh --vty_socket /run/frr-router2 -c "show ip bgp summary"'
    output = run_cmd(cmd)
    if not output:
        return "ERROR", "Failed to fetch router2 BGP summary."
    
    for line in output.splitlines():
        if "192.168.100.10" in line:
            parts = line.split()
            state_pfx = parts[-2] if len(parts) >= 10 else "Unknown"
            if state_pfx not in ["Idle", "Active", "Connect", "OpenSent", "OpenConfirm"]:
                return "OK", f"Router2 Peer 192.168.100.10 State/Prefix: {state_pfx}"
            return "DOWN", f"Router2 Peer State is {state_pfx}"
    return "DOWN", "Router2 BGP session peer not found."

if __name__ == "__main__":
    print("--- BGP Health Monitor ---")
    
    status1, msg1 = check_router_ns_bgp()
    print(f"[{status1}] {msg1}")
    
    status2, msg2 = check_router2_bgp()
    print(f"[{status2}] {msg2}")
    
    if status1 != "OK" or status2 != "OK":
        sys.exit(1)
    else:
        print("\nAll BGP sessions are healthy and established.")
        sys.exit(0)
