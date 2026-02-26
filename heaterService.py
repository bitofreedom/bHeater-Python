from flask import Flask, request, jsonify, send_from_directory
import paramiko
import logging
import os
import json
from utils import transfer_file_to_remote_host  # Import the utility function

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SSH Configuration
SSH_USERNAME = "root"  # Replace with your SSH username
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")  # Path to your SSH private key

# Named commands
NAMED_COMMANDS = {
    "start": "/etc/init.d/bosminer start",
    "stop": "/etc/init.d/bosminer stop"
}

# Path to the heaters JSON file
HEATERS_JSON_PATH = "./heaters.json"

def execute_remote_command(host, command):
    """
    Execute a command on a remote host using SSH key authentication.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the host
        client.connect(
            hostname=host,
            username=SSH_USERNAME,
            key_filename=SSH_KEY_PATH,
            timeout=10
        )

        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()

        # Capture output and errors
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        return {
            "host": host,
            "command": command,
            "exit_code": exit_code,
            "output": output,
            "error": error
        }

    except paramiko.AuthenticationException:
        logger.error(f"Authentication failed for {host}")
        return {"error": "Authentication failed"}
    except paramiko.SSHException as e:
        logger.error(f"SSH connection failed to {host}: {str(e)}")
        return {"error": f"SSH connection failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Error connecting to {host}: {str(e)}")
        return {"error": f"Connection error: {str(e)}"}
    finally:
        client.close()

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

@app.route("/execute", methods=["POST"])
def execute_command():
    """
    API endpoint to execute a command on a remote host.
    """
    data = request.json

    # Validate input
    if not data or "host" not in data or "command" not in data:
        return jsonify({"error": "Missing 'host' or 'command' in request body"}), 400

    host = data["host"]
    command_name = data["command"]

    # Check if the command is in the named commands list
    if command_name not in NAMED_COMMANDS:
        return jsonify({
            "error": f"Invalid command. Available commands: {list(NAMED_COMMANDS.keys())}"
        }), 400

    # Get the actual command to execute
    command = NAMED_COMMANDS[command_name]
    logger.info(f"Executing command on {host}: {command}")

    # Execute the command
    result = execute_remote_command(host, command)

    # Only return 500 if there's an actual error message
    if result.get("error"):  # Check if "error" key has a non-empty value
        return jsonify(result), 500

    return jsonify(result), 200

@app.route("/commands", methods=["GET"])
def list_commands():
    """
    API endpoint to list available named commands.
    """
    return jsonify({
        "available_commands": NAMED_COMMANDS
    }), 200

@app.route("/heaters", methods=["GET"])
def list_heaters():
    """
    API endpoint to list available heaters from the JSON file.
    """
    try:
        # Load the heaters JSON file
        with open(HEATERS_JSON_PATH, 'r') as file:
            heaters = json.load(file)
        return jsonify(heaters), 200
    except FileNotFoundError:
        logger.error(f"Heaters JSON file not found at {HEATERS_JSON_PATH}")
        return jsonify({"error": "Heaters data not found"}), 404
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in {HEATERS_JSON_PATH}")
        return jsonify({"error": "Invalid heaters data format"}), 500
    except Exception as e:
        logger.error(f"Error reading heaters data: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/set_heater", methods=["POST"])
def set_heater():
    """
    API endpoint to set the heater configuration based on the selected action and miner type.
    """
    data = request.json

    # Validate input
    if not data or "heaterName" not in data or "action" not in data:
        return jsonify({"error": "Missing 'heaterName' or 'action' in request body"}), 400

    heater_name = data["heaterName"]
    action = data["action"]

    # Load the heaters JSON file to get the heater details
    try:
        with open(HEATERS_JSON_PATH, 'r') as file:
            heaters = json.load(file)
    except FileNotFoundError:
        logger.error(f"Heaters JSON file not found at {HEATERS_JSON_PATH}")
        return jsonify({"error": "Heaters data not found"}), 404
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in {HEATERS_JSON_PATH}")
        return jsonify({"error": "Invalid heaters data format"}), 500
    except Exception as e:
        logger.error(f"Error reading heaters data: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    # Find the selected heater
    selected_heater = next((heater for heater in heaters if heater["heaterName"] == heater_name), None)
    if not selected_heater:
        return jsonify({"error": f"Heater '{heater_name}' not found"}), 404

    # Determine the local file path based on the action and miner type
    miner_type = selected_heater.get("type", "default")  # Default to 'default' if type is not specified
    if action == "low":
        local_file_path = f"bosminerConfig/bosminer-{miner_type}-low.toml"
    elif action == "medium":
        local_file_path = f"bosminerConfig/bosminer-{miner_type}-medium.toml"
    elif action == "high":
        local_file_path = f"bosminerConfig/bosminer-{miner_type}-high.toml"
    else:
        return jsonify({"error": "Invalid action. Valid actions are 'low', 'medium', 'high'"}), 400

    # Set the remote file path
    remote_file_path = "/etc/bosminer.toml"

    # Call the transfer_file_to_remote_host function
    try:
        transfer_file_to_remote_host(
            local_file_path=local_file_path,
            remote_file_path=remote_file_path,
            hostname=selected_heater["hostname"]
        )
        return jsonify({"message": f"Heater '{heater_name}' configuration updated to '{action}' mode for type '{miner_type}'"}), 200
    except Exception as e:
        logger.error(f"Error transferring file to heater '{heater_name}': {str(e)}")
        return jsonify({"error": f"Failed to update heater configuration: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)