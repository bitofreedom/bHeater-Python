import paramiko
import os

# SSH Configuration
SSH_USERNAME = "root"  # Replace with your SSH username
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")  # Path to your SSH private key

def transfer_file_to_remote_host(local_file_path, remote_file_path, hostname, minerId):
    """
    Transfers a file from the local machine to a remote host using SFTP with private key-based authentication.
    Includes a minerId parameter for additional functionality.

    :param local_file_path: Path to the local file to be transferred.
    :param remote_file_path: Path to the remote file (including filename) where the file will be saved.
    :param hostname: Hostname or IP address of the remote host.
    :param minerId: An identifier for the miner (can be used for logging or dynamic path generation).
    """
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the private key
        private_key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH)

        # Connect to the remote host using the private key
        ssh.connect(hostname, username=SSH_USERNAME, pkey=private_key)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        # Update config file with minerId and save to temporary location
        replace_miner_id_in_toml(local_file_path, minerId)

        # TODO - update previous function to return the new file path
        new_local_file_path = "./tmpFile/newConfigTmp.toml"

        # Transfer the file
        sftp.put(new_local_file_path, remote_file_path)
        print(f"File {new_local_file_path} transferred to {remote_file_path} on {hostname} (Miner ID: {minerId})")

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()

    except Exception as e:
        print(f"An error occurred (Miner ID: {minerId}): {e}")

def replace_miner_id_in_toml(file_path, minerId):
    """
    Replaces occurrences of '{minerId}' in a .toml file with the provided minerId value.
    Saves the updated content to a new file named 'newConfigTmp.toml' in the ./tmpFile directory.

    :param file_path: Path to the input .toml file.
    :param minerId: The value to replace '{minerId}' with.
    """
    try:
        # Ensure the input file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        # Read the content of the .toml file
        with open(file_path, 'r') as file:
            content = file.read()

        # Replace all occurrences of '{minerId}' with the provided minerId
        updated_content = content.replace('{minerId}', minerId)

        # Ensure the ./tmpFile directory exists
        tmp_dir = "./tmpFile"
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        # Define the path for the new file in the ./tmpFile directory
        new_file_path = os.path.join(tmp_dir, 'newConfigTmp.toml')

        # Write the updated content to the new file
        with open(new_file_path, 'w') as new_file:
            new_file.write(updated_content)

        print(f"Updated .toml file saved as {new_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    local_file_path = "./bosminerConfig/bosminer-default.toml"  # Replace with your local file path
    remote_file_path = "/etc/bosminer.toml"  # Replace with your remote file path
    hostname = "192.168.24.206"  # Replace with your remote host's IP or hostname
    minerId = "s9b1"  # Replace with your miner ID

    transfer_file_to_remote_host(local_file_path, remote_file_path, hostname, minerId)