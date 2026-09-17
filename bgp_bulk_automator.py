import subprocess

subnets = ["192.168.30.0/24", "192.168.40.0/24"]

for subnet in subnets:
    full_cmd = [
        "sudo", "ip", "netns", "exec", "router-ns",
        "vtysh", "--vty_socket", "/run/frr-router-ns",
        "-c", "configure terminal",
        "-c", "router bgp 65001",
        "-c", "address-family ipv4 unicast",
        "-c", f"network {subnet}",
        "-c", "exit-address-family",
        "-c", "end"
    ]
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    print(f"Advertised {subnet}: {result.stdout.strip()}")
