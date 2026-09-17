# FRR BGP Automation Lab

A network automation and routing lab designed to test, manage, and monitor BGP peering sessions across isolated Linux network namespaces using FRRouting (FRR), Python, Terraform, and Ansible.

---

## Architecture and Topology

This lab simulates a multi-AS routing environment on a single Linux host using network namespaces:
* router-ns (AS 65001): Primary routing instance running FRR, managing route advertisement and prefix filtering.
* router2 (AS 65002): Secondary routing instance communicating via virtual Ethernet (veth) peer interfaces.
* Automation Layer: Python scripts and configuration pipelines to deploy settings, flush stale sessions, and perform health checks.

---

## Directory Layout

~/frr-bgp-automation-lab/
├── ansible/                  # Ansible playbooks and roles for configuration management
├── terraform/                # Infrastructure provisioning and drift verification templates
├── pipeline.py               # Master end-to-end automation execution script
├── bgp_monitor.py            # Real-time BGP health and session monitor
└── project.md                # Comprehensive project runbook and technical notes

---

## Prerequisites

* Linux environment (Ubuntu/Debian recommended) with iproute2 and root/sudo privileges.
* FRRouting (FRR) version 10.5.1 or higher installed.
* Python 3.x for execution scripts.
* Terraform with local/mock provider support for lab infrastructure testing.

---

## Quick Start and Usage

### 1. Clone and Navigate
cd ~/frr-bgp-automation-lab

### 2. Run BGP Health Monitoring
To verify active BGP peer states, prefix counts, and daemon responsiveness:
python3 bgp_monitor.py

### 3. Execute the Automation Pipeline
To push routing configurations and validate connectivity:
python3 pipeline.py

---

## Troubleshooting Namespace Sockets

When executing vtysh commands against FRR inside isolated namespaces, target the specific socket path:
* router-ns: /run/frr-router-ns
* router2: /run/frr-router2

Example:
sudo ip netns exec router-ns vtysh --vty_socket /run/frr-router-ns -c "show ip bgp summary"

---

## License

This project is open-source and intended for network automation research, lab testing, and educational purposes.
