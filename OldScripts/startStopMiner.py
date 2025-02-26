import sys
import requests
import json

# List of supported commands
SUPPORTED_COMMANDS = ["start", "stop"]

# Check if the required arguments are provided
if len(sys.argv) != 3:
    print("Usage: python startStopMiner.py <host> <command>")
    print(f"Supported commands: {SUPPORTED_COMMANDS}")
    sys.exit(1)

# Assign the arguments to variables
host = sys.argv[1]
command = sys.argv[2]

# Validate the command
if command not in SUPPORTED_COMMANDS:
    print(f"Error: Unsupported command '{command}'. Supported commands: {SUPPORTED_COMMANDS}")
    sys.exit(1)

# Define the payload
payload = {
    "host": host,
    "command": command
}

# Define the URL
url = "http://localhost:5000/execute"

# Send the POST request
try:
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    
    # Pretty-print the JSON response
    try:
        response_json = response.json()
        print("Response Body:")
        print(json.dumps(response_json, indent=4))
    except json.JSONDecodeError:
        print(f"Response Body (raw): {response.text}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")