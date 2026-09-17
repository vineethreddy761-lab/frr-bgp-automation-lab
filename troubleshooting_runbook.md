
---

# Complete Lab & Troubleshooting Master Notes

## 1. Environment Topology & Addressing

* **Hypervisor / OS:** Ubuntu Linux running in VirtualBox, managed via Git Bash / terminal.
* **Network Namespaces:**
* `router-ns` (AS `65001`, Router ID/Interface IP: `192.168.100.10/24`)
* `router2` (AS `65002`, Router ID/Interface IP: `192.168.100.20/24`)


* **FRR VTY Socket Paths:**
* `router-ns`: `/run/frr-router-ns`
* `router2`: `/run/frr-router2`



---

## 2. Phase-by-Phase Troubleshooting & Error Fixes

### A. The "Configure Command Not Found" Error

* **What Happened:** You tried running BGP/FRR routing commands like `configure terminal` or `ip prefix-list` directly in the Linux bash shell.
* **Error Output:**
```text
configure: command not found
Object "prefix-list" is unknown, try "ip help".

```


* **The Fix:** You must enter the FRR interactive CLI (`vtysh`) inside the correct network namespace first:
```bash
sudo ip netns exec router-ns vtysh --vty_socket /run/frr-router-ns

```



---

### B. Namespace VTY Socket Isolation & Cross-Contamination

* **What Happened:** Running generic `vtysh` commands without specifying a socket path caused commands to hit the global host daemon instead of the isolated namespace router (`router-ns` or `router2`).
* **The Fix:** Always explicitly supply the `--vty_socket` flag and namespace execution wrapper:
```bash
sudo ip netns exec router-ns vtysh --vty_socket /run/frr-router-ns -c "show ip bgp summary"
sudo ip netns exec router2 vtysh --vty_socket /run/frr-router2 -c "show ip bgp summary"

```



---

### C. BGP Instance Name & AS Mismatch

* **What Happened:** When attempting to modify or re-declare BGP parameters, FRR threw errors because an active runtime instance with a conflicting AS number was already running.
* **Error Output:**
```text
BGP instance name and AS number mismatch
BGP instance is already running; AS is 65001

```


* **The Fix:** Explicitly tear down the existing BGP router process before re-declaring the correct AS:
```vtysh
configure terminal
no router bgp 65001
router bgp 65002
bgp router-id 192.168.100.20
neighbor 192.168.100.10 remote-as 65001
neighbor 192.168.100.10 update-source 192.168.100.20
address-family ipv4 unicast
neighbor 192.168.100.10 activate
end
write memory

```



---

### D. Missing BGP Prefixes / 0 Advertised Routes

* **What Happened:** The BGP peer state showed as `Established`, but `show ip bgp` or neighbor statistics showed `0 accepted` or missing prefixes.
* **The Fix:** Ensure that local subnets are actively injected into the BGP table using the `network` statement under the IPv4 unicast address-family:
```vtysh
configure terminal
router bgp 65001
  address-family ipv4 unicast
    network 192.168.10.0/24
  end-address-family
end
write memory

```



---

### E. Implementing Prefix-Lists and Route-Maps

* **Goal:** Filter incoming/outgoing BGP advertisements so only permitted networks are accepted.
* **Configuration Steps:**
1. **Create the Prefix-List:**
```vtysh
configure terminal
ip prefix-list PL-FILTER permit 192.168.10.0/24

```


2. **Create the Route-Map:**
```vtysh
route-map RM-BGP-POLICY permit 10
  match ip address prefix-list PL-FILTER
end

```


3. **Apply the Route-Map to the BGP Neighbor:**
```vtysh
router bgp 65001
  address-family ipv4 unicast
    neighbor 192.168.100.20 route-map RM-BGP-POLICY in
  end-address-family
end
write memory

```




* **Verification Command:**
```vtysh
show ip bgp neighbors 192.168.100.20

```


*(Look for line: `Route map for incoming advertisements is *RM-BGP-POLICY` and `Inbound filtered: 1`)*

---

## 3. Layer 3 Connectivity & Diagnostic Commands

* **Ping Test Across Namespace:**
```bash
sudo ip netns exec router-ns ping -c 3 192.168.100.20

```


* **Verify TCP Port 179 (BGP Port) Reachability:**
```bash
sudo ip netns exec router-ns nc -zv 192.168.100.20 179

```


* **Check Route Tables:**
```bash
sudo ip netns exec router-ns ip route show

```



---

## 4. Automation & Monitoring Python Scripts

### A. Health Monitor Script (`bgp_monitor.py`)

```python
#!/usr/bin/env python3

import subprocess
import sys

def run_cmd(command):
    try:
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}\n{e.stderr.strip()}", file=sys.stderr)
        return None

def check_router_ns_bgp():
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

```

### B. Master Pipeline Automation Script (`pipeline.py`)

```python
#!/usr/bin/env python3

import subprocess
import sys
import time

def run_cmd(command, description=""):
    if description:
        print(f"[*] {description}...")
    try:
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {command}\n{e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

def configure_routers():
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

    run_cmd('sudo ip netns exec router-ns vtysh --vty_socket /run/frr-router-ns -c "clear ip bgp *"', "Clearing BGP sessions")
    time.sleep(2)

def run_health_monitor():
    print("\n--- Running BGP Health Monitor ---")
    result = subprocess.run(["python3", "bgp_monitor.py"])
    sys.exit(result.returncode)

if __name__ == "__main__":
    print("=== Starting Network Automation Pipeline ===")
    configure_routers()
    print("[SUCCESS] All router configurations applied successfully.")
    run_healt_monitor()
