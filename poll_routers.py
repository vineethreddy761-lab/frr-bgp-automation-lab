import subprocess
import json

namespaces = ["router-ns", "router2"]

for ns in namespaces:
    print(f"--- Polling BGP Summary for {ns} ---")
    cmd = f"sudo ip netns exec {ns} vtysh --vty_socket /run/frr-{ns} -c 'show ip bgp summary json'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        print(json.dumps(data, indent=2))
    else:
        print(f"Could not fetch data for {ns}: {result.stderr}")
