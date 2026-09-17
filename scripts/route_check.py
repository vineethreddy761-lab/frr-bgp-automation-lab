import subprocess
import sys

def check_route(destination):
    print(f"Checking route for destination: {destination}")
    try:
        result = subprocess.run(["ip", "route", "get", destination], capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Failed to resolve route: {e}", file=sys.stderr)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "192.168.40.1"
    check_route(target)
