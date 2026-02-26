#!/usr/bin/env python3
"""
Connectivity test tool for Bitcoin heater miners.
Tests SSH access to each miner defined in heaters.json.
"""

import json
import paramiko
import os
from datetime import datetime
from typing import Dict, List

# SSH Configuration
SSH_USERNAME = "root"
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")
CONNECTION_TIMEOUT = 5  # seconds

def test_ssh_connection(hostname: str, ip_address: str) -> Dict:
    """
    Test SSH connection to a miner using both hostname.local and IP address.

    Returns:
        Dictionary with connection status and details
    """
    result = {
        "hostname": hostname,
        "ip_address": ip_address,
        "hostname_status": "FAIL",
        "ip_status": "FAIL",
        "error": None,
        "auth_method": None
    }

    # Try hostname.local first
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            hostname=f"{hostname}.local",
            username=SSH_USERNAME,
            key_filename=SSH_KEY_PATH,
            timeout=CONNECTION_TIMEOUT,
            banner_timeout=CONNECTION_TIMEOUT
        )

        # Test command execution
        stdin, stdout, stderr = client.exec_command("echo 'test'")
        exit_code = stdout.channel.recv_exit_status()

        if exit_code == 0:
            result["hostname_status"] = "SUCCESS"
            result["auth_method"] = "SSH Key"

        client.close()

    except paramiko.AuthenticationException:
        result["error"] = "Authentication failed - SSH key not authorized"
    except paramiko.SSHException as e:
        result["error"] = f"SSH error: {str(e)}"
    except Exception as e:
        result["error"] = f"Connection error: {str(e)}"

    # Try IP address if hostname failed
    if result["hostname_status"] == "FAIL":
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                hostname=ip_address,
                username=SSH_USERNAME,
                key_filename=SSH_KEY_PATH,
                timeout=CONNECTION_TIMEOUT,
                banner_timeout=CONNECTION_TIMEOUT
            )

            # Test command execution
            stdin, stdout, stderr = client.exec_command("echo 'test'")
            exit_code = stdout.channel.recv_exit_status()

            if exit_code == 0:
                result["ip_status"] = "SUCCESS"
                result["auth_method"] = "SSH Key"
                result["error"] = None  # Clear error if IP works

            client.close()

        except Exception as e:
            # Keep the original error if both fail
            if result["error"] is None:
                result["error"] = f"IP connection error: {str(e)}"

    return result

def test_all_miners(heaters_json_path: str = "./heaters.json") -> List[Dict]:
    """
    Test connectivity to all miners defined in heaters.json.

    Returns:
        List of test results for each miner
    """
    try:
        with open(heaters_json_path, 'r') as file:
            heaters = json.load(file)
    except FileNotFoundError:
        print(f"ERROR: Heaters JSON file not found at {heaters_json_path}")
        return []
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON format in {heaters_json_path}")
        return []

    results = []

    print(f"\n{'='*80}")
    print(f"Bitcoin Heater Miner Connectivity Test")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing {len(heaters)} miners...")
    print(f"{'='*80}\n")

    for heater in heaters:
        heater_name = heater.get("heaterName", "Unknown")
        hostname = heater.get("hostname", "")
        ip_address = heater.get("ipAddress", "")
        location = heater.get("location", "Unknown")
        miner_type = heater.get("type", "Unknown")

        print(f"Testing: {heater_name} ({location})")
        print(f"  Type: {miner_type}")
        print(f"  Hostname: {hostname}.local")
        print(f"  IP Address: {ip_address}")

        result = test_ssh_connection(hostname, ip_address)
        result["heater_name"] = heater_name
        result["location"] = location
        result["type"] = miner_type
        results.append(result)

        # Print immediate result
        if result["hostname_status"] == "SUCCESS":
            print(f"  ✓ Status: SUCCESS (via hostname)")
        elif result["ip_status"] == "SUCCESS":
            print(f"  ✓ Status: SUCCESS (via IP address)")
        else:
            print(f"  ✗ Status: FAILED")
            if result["error"]:
                print(f"    Error: {result['error']}")

        print()

    return results

def print_summary(results: List[Dict]):
    """
    Print a summary of all connectivity tests.
    """
    print(f"\n{'='*80}")
    print("CONNECTIVITY TEST SUMMARY")
    print(f"{'='*80}\n")

    online_count = sum(1 for r in results if r["hostname_status"] == "SUCCESS" or r["ip_status"] == "SUCCESS")
    offline_count = len(results) - online_count

    print(f"Total Miners: {len(results)}")
    print(f"Online: {online_count}")
    print(f"Offline: {offline_count}")
    print()

    # Online miners
    if online_count > 0:
        print("ONLINE MINERS:")
        print(f"{'Heater Name':<20} {'Location':<15} {'Type':<10} {'Method':<15}")
        print(f"{'-'*20} {'-'*15} {'-'*10} {'-'*15}")
        for result in results:
            if result["hostname_status"] == "SUCCESS" or result["ip_status"] == "SUCCESS":
                method = "hostname" if result["hostname_status"] == "SUCCESS" else "IP address"
                print(f"{result['heater_name']:<20} {result['location']:<15} {result['type']:<10} {method:<15}")
        print()

    # Offline miners
    if offline_count > 0:
        print("OFFLINE MINERS:")
        print(f"{'Heater Name':<20} {'Location':<15} {'Error':<50}")
        print(f"{'-'*20} {'-'*15} {'-'*50}")
        for result in results:
            if result["hostname_status"] == "FAIL" and result["ip_status"] == "FAIL":
                error_msg = result["error"][:47] + "..." if len(result["error"]) > 50 else result["error"]
                print(f"{result['heater_name']:<20} {result['location']:<15} {error_msg:<50}")
        print()

    print(f"{'='*80}")

    # Recommendations
    if offline_count > 0:
        print("\nRECOMMENDATIONS:")
        auth_failures = sum(1 for r in results if "Authentication failed" in str(r.get("error", "")))
        timeout_failures = sum(1 for r in results if "timed out" in str(r.get("error", "")).lower())

        if auth_failures > 0:
            print(f"  • {auth_failures} miner(s) failed authentication - run ssh-copy-id to add SSH key:")
            for result in results:
                if "Authentication failed" in str(result.get("error", "")):
                    print(f"    ssh-copy-id root@{result['hostname']}.local")

        if timeout_failures > 0:
            print(f"  • {timeout_failures} miner(s) timed out - check if they are powered on and network accessible")

def main():
    """
    Main function to run connectivity tests.
    """
    # Check if SSH key exists
    if not os.path.exists(SSH_KEY_PATH):
        print(f"ERROR: SSH private key not found at {SSH_KEY_PATH}")
        print("Generate a key pair with: ssh-keygen -t rsa -b 4096")
        return

    results = test_all_miners()

    if results:
        print_summary(results)

        # Save results to file
        output_file = "connectivity_test_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results
            }, f, indent=2)
        print(f"\nDetailed results saved to: {output_file}")

if __name__ == "__main__":
    main()
