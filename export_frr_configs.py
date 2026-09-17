import subprocess
import os

backup_dir = "./frr_backups"
os.makedirs(backup_dir, exist_ok=True)

namespaces = ["router-ns", "router2"]

for ns in namespaces:
    # Save running config to file inside namespace first
    subprocess.run(["sudo", "ip", "netns", "exec", ns, "vtysh", "--vty_socket", f"/run/frr-{ns}", "-c", "write memory"], check=True)
    
    # Copy the config file out to host backup directory
    # (Assuming standard FRR config path or pulling via vtysh)
    result = subprocess.run(
        ["sudo", "ip", "netns", "exec", ns, "cat", "/etc/frr/frr.conf"],
        capture_output=True, text=True, check=True
    )
    
    backup_path = os.path.join(backup_dir, f"{ns}_frr.conf")
    with open(backup_path, "w") as f:
        f.write(result.stdout)
    print(f"Exported configuration for {ns} to {backup_path}")

