#!/usr/bin/env python3
"""
Test script to set the office miner to high mode.
Starts the heater service temporarily on port 5001 for testing.
"""

import time
import requests
import subprocess
import signal
import sys
import os

PORT = 5001
BASE_URL = f"http://localhost:{PORT}"

def start_service():
    """Start the heater service on a custom port."""
    # Modify the service to use PORT 5001
    print(f"Starting heater service on port {PORT}...")

    # Start the service in a subprocess
    env = os.environ.copy()
    process = subprocess.Popen(
        ['./venv/bin/python', '-c', f"""
from heaterService import app
app.run(host='0.0.0.0', port={PORT})
"""],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd='/Users/darrin/git/bHeater-Python'
    )

    # Wait for service to start
    print("Waiting for service to start...")
    time.sleep(3)

    return process

def test_set_heater(heater_name, action):
    """Test setting a heater configuration."""
    url = f"{BASE_URL}/set_heater"
    payload = {
        "heaterName": heater_name,
        "action": action
    }

    print(f"\nTesting: Set '{heater_name}' to '{action}' mode")
    print(f"URL: {url}")
    print(f"Payload: {payload}")

    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print(f"✓ SUCCESS: {heater_name} configuration set to {action} mode")
            return True
        else:
            print(f"✗ FAILED: {response.json().get('error', 'Unknown error')}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"✗ ERROR: {str(e)}")
        return False

def main():
    """Main test function."""
    print("="*80)
    print("Office Miner Test - Setting to HIGH mode")
    print("="*80)

    # Start the service
    process = start_service()

    try:
        # Test the office miner
        success = test_set_heater("office", "high")

        print("\n" + "="*80)
        if success:
            print("TEST PASSED")
        else:
            print("TEST FAILED")
        print("="*80)

    finally:
        # Stop the service
        print("\nStopping heater service...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        print("Service stopped.")

if __name__ == "__main__":
    main()
