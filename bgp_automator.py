import subprocess

def run_vtysh_command(namespace, command):
    router_cmd = "router bgp 65001" if namespace == "router-ns" else "router bgp 65002"
    full_cmd = [
        "sudo", "ip", "netns", "exec", namespace,
        "vtysh", "--vty_socket", f"/run/frr-{namespace}",
        "-c", "configure terminal",
        "-c", router_cmd,
        "-c", "address-family ipv4 unicast",
        "-c", command,
        "-c", "exit-address-family",
        "-c", "end"
    ]
    result = subprocess.run(full_cmd, capture_output=True, text=True)
    return result.stdout

# Example: Advertise a new subnet from router-ns
print(run_vtysh_command("router-ns", "network 192.168.20.0/24"))
