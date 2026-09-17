Here is the complete, comprehensive, and updated `project.md` file containing all your project components, Terraform modules, Ansible roles, CI/CD pipelines, Gitea setup, and the complete Multi-AS BGP routing lab, troubleshooting logs, and Python automation scripts (`pipeline.py` and `bgp_monitor.py`).

You can save this directly to your project file as your master lab and exam notes:

```markdown
# Project Documentation: Multi-Cloud Automated Hybrid Connectivity & Infrastructure Platform

## 1. Project Overview
This project establishes a comprehensive, open-source infrastructure and network automation platform designed to align with the Opcito Infrastructure / Network Automation Engineer role. It bridges modular Infrastructure as Code (IaC), custom provider concepts, automated CI/CD workflows, and advanced network routing, network namespaces, and troubleshooting scenarios.

---

## 2. Environment & Architecture
- Environment: Ubuntu Linux VirtualBox environment accessed via Git Bash.
- Core Stack: Terraform (Modules & Custom Providers), Ansible, Go, Python, Linux Networking, FRRouting (FRR), and local Git CI/CD workflows.

### Directory Layout
```text
~/frr-bgp-automation-lab/
├── ansible/
│   └── roles/
│       └── network_config/
│           ├── tasks/main.yml
│           └── handlers/main.yml
├── modules/
│   ├── compute/
│   │   └── main.tf
│   └── vpc/
│       └── main.tf
├── playbooks/
│   └── site.yml
├── provider-mock/
│   └── main.go
├── scripts/
│   ├── lab_operations.sh
│   └── route_check.py
├── pipeline.py
├── bgp_monitor.py
├── main.tf
└── terraform.tfstate

```

---

## 3. Core Modules & Configuration

### A. Root Terraform Configuration (`main.tf`)

```hcl
terraform {
  required_version = ">= 1.0.0"
}

variable "project_name" {
  type    = string
  default = "opt-network-automation"
}

module "vpc" {
  source   = "./modules/vpc"
  vpc_cidr = "192.168.40.0/24"
}

module "compute" {
  source        = "./modules/compute"
  instance_name = "app-node-01"
  subnet_cidr   = module.vpc.vpc_network
}

output "project_info" {
  value = "Project ${var.project_name} workspace ready!"
}

output "vpc_output" {
  value = module.vpc.vpc_network
}

output "compute_output" {
  value = module.compute.compute_summary
}

```

### B. Custom VPC Module (`modules/vpc/main.tf`)

```hcl
variable "vpc_cidr" {
  type    = string
  default = "192.168.10.0/24"
}

output "vpc_network" {
  value = "Configured virtual network CIDR: ${var.vpc_cidr}"
}

```

### C. Compute Module Configuration (`modules/compute/main.tf`)

```hcl
variable "instance_name" {
  type    = string
  default = "app-node-01"
}

variable "subnet_cidr" {
  type    = string
}

output "compute_summary" {
  value = "Provisioned compute instance ${var.instance_name} attached to network subnet ${var.subnet_cidr}"
}

```

### D. Ansible Playbook (`playbooks/site.yml`)

```yaml
---
- name: Configure Network Automation Lab Nodes
  hosts: localhost
  connection: local
  gather_facts: yes
  tasks:
    - name: Ensure lab directories exist
      file:
        path: "{{ item }}"
        state: directory
        mode: "0755"
      loop:
        - /tmp/lab_configs
        - /tmp/lab_logs

    - name: Write system diagnostic info
      copy:
        content: "Lab automation configuration executed successfully on inventory host.\n"
        dest: /tmp/lab_configs/status.txt

```

---

## 4. Advanced Engineering Components

### A. Custom Terraform Provider Architecture (Go-based)

* **Concept:** Designed using the Terraform Plugin Framework in Go to handle CRUD operations against proprietary Telco APIs or internal application endpoints.
* **Implementation Strategy:** Defines resource schemas, state tracking, and REST client calls to manage resources declaratively via Terraform syntax.

### B. State Management & Drift Detection Workflow

* **State Locking:** Utilizes remote backend storage with encryption and locking mechanisms to prevent concurrent modification collisions.
* **Drift Resolution:** When manual changes occur via CLI/UI, drift is diagnosed using `terraform plan -refresh-only`, and unauthorized drifts are remediated by enforcing the declared state through `terraform apply`.

### C. Advanced Network Troubleshooting & Routing Lab

* **Top-Down vs. Bottom-Up Debugging:** Implemented diagnostic processes spanning Layer 2 (ARP/neighbor tables, LACP bonding/hash policies), Layer 3 (IP routing tables, subnet route lookups using `ip route get`), and Layer 4/Application layers (`tcpdump`, `ss`, `nc`).
* **DNS & Hosts Verification:** Managing `/etc/hosts` lookups and diagnosing BIND9/Port 53 unreachability using `dig` and response code analysis (`NXDOMAIN`, `SERVFAIL`, `REFUSED`).

---

## 5. CI/CD Pipeline & GitLab Integration (`.gitlab-ci.yml`)

```yaml
stages:
  - validate
  - plan
  - apply

variables:
  TF_ROOT: ${CI_PROJECT_DIR}

cache:
  paths:
    - ${TF_ROOT}/.terraform

before_script:
  - cd ${TF_ROOT}
  - terraform --version

validate:
  stage: validate
  script:
    - terraform fmt -check
    - terraform init -backend=false
    - terraform validate

plan:
  stage: plan
  script:
    - terraform init
    - terraform plan -out=tfplan
  artifacts:
    name: tfplan
    expire_in: 7 days
    paths:
      - ${TF_ROOT}/tfplan

apply:
  stage: apply
  script:
    - terraform init
    - terraform apply -input=false tfplan
  dependencies:
    - plan
  when: manual

```

---

## 6. Daily Operations & Execution Scripts (`scripts/lab_operations.sh`)

```bash
#!/usr/bin/env bash
# Lab Operations & Drift Verification Script

echo "[INFO] Starting infrastructure health check and drift verification..."

# 1. Run Terraform check for configuration drift
cd ~/frr-bgp-automation-lab
terraform plan -refresh-only

# 2. Check interface and routing states
echo "[INFO] Inspecting network route path and interfaces..."
ip route get 8.8.8.8
ip link show

# 3. Verify socket listeners (Top-Down check)
echo "[INFO] Checking active socket listeners..."
ss -tulpn | head -n 10

echo "[INFO] Lab operational check completed successfully."

```

---

## 7. LACP Link Aggregation & Bonding (`network/setup_lacp.sh`)

```bash
#!/usr/bin/env bash
# LACP Bonding Simulation Script

echo "[INFO] Loading bonding kernel module..."
sudo modprobe bonding

echo "[INFO] Creating bond0 interface with LACP (mode 4)..."
sudo ip link add bond0 type bond
sudo ip link set bond0 type bond mode 4 xmit_hash_policy layer3+4

echo "[INFO] Bond interface created successfully."
ip link show bond0

```

---

## 8. VirtualBox Namespace Routing & Firewall Troubleshooting Lab

### A. Environment Validation & Inter-VLAN Routing

* **Network Namespaces Setup:** Configured isolated namespaces (`router-ns` and `router2`) connected via virtual Ethernet pairs (`veth`) to simulate multi-subnet routing without requiring cloud VPCs.
* **IPv4 Forwarding:** Enabled packet routing across the router namespace:
```bash
sudo ip netns exec router-ns sysctl -w net.ipv4.ip_forward=1

```


* **Default Gateways:** Configured default routes on client nodes pointing to the respective router interface IPs.
* **Verification:** Successfully verified end-to-end packet delivery between subnets with 0% packet loss.

### B. Packet Tracing & Firewall Drop Simulation (`iptables`)

* **Route Inspection:** Evaluated the Linux kernel's route and next-hop selection using:
```bash
ip route get <destination-ip>

```


* **Security Group / Firewall Simulation:** Simulated a network block or security policy restriction by inserting an explicit `iptables` drop rule inside the router's FORWARD chain:
```bash
sudo ip netns exec router-ns iptables -A FORWARD -s 192.168.10.10 -d 192.168.20.20 -j DROP

```


* **Drop Verification:** Confirmed that traffic is successfully blocked when active, and verified immediate restoration of connectivity upon deleting the rule (`iptables -D`).

---

## 9. Advanced Multi-AS BGP Routing & FRR Lab

### A. Topology & Addressing Scheme

* **Router 1 (`router-ns`)**:
* **AS Number:** `65001`
* **Router ID / Peering IP:** `192.168.100.10`
* **VTY Socket Path:** `/run/frr-router-ns`
* **Advertised Prefix:** `192.168.10.0/24`


* **Router 2 (`router2`)**:
* **AS Number:** `65002`
* **Router ID / Peering IP:** `192.168.100.20`
* **VTY Socket Path:** `/run/frr-router2`



### B. Route Maps & Prefix Filtering Configuration

To control prefix propagation and filter updates inbound/outbound:

```vtysh
configure terminal
ip prefix-list PL-FILTER permit 192.168.10.0/24
route-map RM-BGP-POLICY permit 10
  match ip address prefix-list PL-FILTER
end
write memory

```

Applying the route map to a neighbor under BGP address-family:

```vtysh
configure terminal
router bgp 65001
  address-family ipv4 unicast
    neighbor 192.168.100.20 route-map RM-BGP-POLICY in
  end-address-family
end
write memory

```

---

## 10. Troubleshooting Log & Key Errors Handled

### 1. BGP Instance Name / AS Mismatch

* **Error:** `BGP instance is already running; AS is 65001`
* **Root Cause:** Trying to re-configure an active FRR session with a conflicting AS number.
* **Fix:** Explicitly clear out the old instance before re-declaring:
```vtysh
configure terminal
no router bgp 65001
router bgp 65002
...

```



### 2. VTY Socket Cross-Contamination

* **Issue:** Running generic `vtysh` commands modified global host sockets instead of isolated network namespaces.
* **Fix:** Always explicitly specify namespace-specific sockets:
```bash
sudo ip netns exec router-ns vtysh --vty_socket /run/frr-router-ns -c "show ip bgp summary"

```



### 3. BFD Session Stalls

* **Issue:** Having `neighbor ... bfd` enabled on one side while missing on the peer keeps the BGP session stuck in `Active`.
* **Fix:** Ensure matching BFD configurations on both nodes or remove the unconfigured `bfd` statement.

---

## 11. Python Automation Scripts

### A. Master Orchestration Pipeline (`pipeline.py`)

```python
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
        '''sudo ip netns exec router-ns vtysh --vty_socket /run/frr-router-ns <<EOF """Check """Run "192.168.100.20" "Clearing "Configuring "ERROR", "Failed "__main__": "bgp_monitor.py"]) "clear # #!/usr/bin/env ### '''sudo (AS (`bgp_monitor.py`) ) )" *"', ---") --vty_socket -c /run/frr-router-ns /run/frr-router2 192.168.10.0/24 192.168.100.10 192.168.100.20 2. 3. 65001 65001) 65001)" 65002 65002) 65002)" <<EOF All Automation B. BGP Clear Configure EOF''', Health Monitor Network None Pipeline="==" Running Starting __name__="=" ``` ```python a activate address-family and applied as bgp check="True" check_router_ns_bgp(): cmd="sudo ip netns exec router-ns vtysh --vty_socket /run/frr-router-ns -c " command command, command: configurations configure configure_routers() def e: end except exec executing fetch file="sys.stderr)" for force if immediate import in ip ipv4 its len(parts) line line: memory neighbor netns network not output="run_cmd(cmd)" output.""" output.splitlines(): output: parts="line.split()" print("="==" print("[SUCCESS] print("\n--- print(f"Error python3 remote-as result="subprocess.run(" result.stdout.strip() return router router-id router-ns router2 run_cmd( run_cmd('sudo run_cmd(command): run_health_monitor() run_health_monitor(): sessions sessions") shell="True," show socket.""" specific state_pfx="parts[-2]" stderr="subprocess.PIPE," stdout="subprocess.PIPE," subprocess subprocess.CalledProcessError successfully.") summary summary"" summary." sync sys sys.exit(result.returncode) terminal text="True," time.sleep(2) to try: unicast update-source using vty vtysh write {command}\n{e.stderr.strip()}",>= 10 else "Unknown"
            if state_pfx not in ["Idle", "Active", "Connect", "OpenSent", "OpenConfirm"]:
                return "OK", f"router-ns Peer 192.168.100.20 State/Prefix: {state_pfx}"
            return "DOWN", f"router-ns Peer State is {state_pfx}"
    return "DOWN", "router-ns BGP session peer not found."

def check_router2_bgp():
    """Check BGP summary for router2 inside namespace (AS 65002)."""
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

---

## 12. Gitea Initial Configuration & Setup Reference

### A. Core Installation Parameters

* **Service Port:** Hosted locally on port `3000` (`Gitea HTTP Listen Port`).
* **Configuration File Path:** All configuration options write directly into `/etc/gitea/app.ini`.
* **Database Backends:** Supports MySQL, PostgreSQL, MSSQL, SQLite3, or TiDB (MySQL protocol).

### B. Setup Sections & Fields

* **General Settings:**
* *Site Title:* Enterprise/Company name.
* *Repository Root Path:* Directory where remote Git repositories are stored.
* *Git LFS Root Path:* Storage path for files tracked by Git LFS.
* *Server Domain & Base URL:* Address configuration for HTTP(S) cloning and notifications.


* **Administrator Account:**
* Optional during setup; the first registered user automatically becomes the system administrator.



```

```
