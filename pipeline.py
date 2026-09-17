#!/usr/bin/env python3

import subprocess
import sys
import time

def run_cmd(command, description=""):
    """Run a shell command with status logging."""
    if description:
        print(f"[*] {description}...")
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
        print(f"[ERROR] Command failed: {command}\n{e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def configure_routers():
    # 1. Configure router-ns (AS 65001)
    run_cmd(
        '''sudo ip netns exec router-ns vtysh --vty_socket /run/frr-router-ns <<EOF
configure terminal
router bgp 65001
bgp router-id 192.168.100.10
neighbor 192.168.100.20 remote-as 65002
neighbor 192.168.100.20 update-source 192.168.100.10
address-family ipv4 unicast
neighbor 192.168.100.20 activate
network 192.168.10.0/24
end
write memory
EOF''',
        "Configuring router-ns (AS 65001)"
    )

    # 2. Configure router2 (AS 65002)
    run_cmd(
        '''sudo ip netns exec router2 vtysh --vty_socket /run/frr-router2 <<EOF
configure terminal
router bgp 65002
bgp router-id 192.168.100.20
neighbor 192.168.100.10 remote-as 65001
neighbor 192.168.100.10 update-source 192.168.100.20
address-family ipv4 unicast
neighbor 192.168.100.10 activate
end
write memory
EOF''',
        "Configuring router2 (AS 65002)"
    )

    # 3. Clear sessions to force immediate sync
    run_cmd('sudo ip netns exec router-ns vtysh --vty_socket /run/frr-router-ns -c "clear ip bgp *"', "Clearing BGP sessions")
    time.sleep(2) # Give a moment for the handshake

def run_health_monitor():
    print("\n--- Running BGP Health Monitor ---")
    result = subprocess.run(["python3", "bgp_monitor.py"])
    sys.exit(result.returncode)

if __name__ == "__main__":
    print("=== Starting Network Automation Pipeline ===")
    configure_routers()
    print("[SUCCESS] All router configurations applied successfully.")
    run_health_monitor()
