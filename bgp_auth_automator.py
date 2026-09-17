import subprocess

def configure_md5(namespace, local_as, neighbor_ip, password):
    commands = [
        "configure terminal",
        f"router bgp {local_as}",
        f"neighbor {neighbor_ip} password {password}",
        "end",
        "write memory"
    ]
    
    vtysh_args = ["sudo", "ip", "netns", "exec", namespace, "vtysh", "--vty_socket", f"/run/frr-{namespace}"]
    for cmd in commands:
        vtysh_args.extend(["-c", cmd])
        
    result = subprocess.run(vtysh_args, capture_output=True, text=True)
    return result.stdout

# Configure MD5 between router-ns and router2
print("Configuring router-ns...")
print(configure_md5("router-ns", 65001, "192.168.100.20", "SecretBGPPassword123"))

print("Configuring router2...")
print(configure_md5("router2", 65002, "192.168.100.10", "SecretBGPPassword123"))
