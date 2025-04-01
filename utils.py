import paramiko
import os

# SSH Configuration
SSH_USERNAME = "root"  # Replace with your SSH username
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")  # Path to your SSH private key

def transfer_file_to_remote_host(local_file_path, remote_file_path, hostname):
    """
    Transfers a file from the local machine to a remote host using SFTP with private key-based authentication.

    :param local_file_path: Path to the local file to be transferred.
    :param remote_file_path: Path to the remote file (including filename) where the file will be saved.
    :param hostname: Hostname of the remote host.
    """
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the private key
        private_key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH)

        # Connect to the remote host using the private key
        ssh.connect(f"{hostname}.local", username=SSH_USERNAME, pkey=private_key)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        # Update config file with hostname and save to temporary location
        replace_host_name_in_toml(local_file_path, hostname)

        # TODO - update previous function to return the new file path
        new_local_file_path = "./tmpFile/newConfigTmp.toml"

        # Transfer the file
        sftp.put(new_local_file_path, remote_file_path)
        print(f"File {new_local_file_path} transferred to {remote_file_path} on {hostname}")

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()

    except Exception as e:
        print(f"An error occurred (HostName: {hostname}): {e}")

def replace_host_name_in_toml(file_path, hostname):
    """
    Replaces occurrences of '{hostname}' in a .toml file with the provided hostname value.
    Saves the updated content to a new file named 'newConfigTmp.toml' in the ./tmpFile directory.

    :param file_path: Path to the input .toml file.
    :param hostname: The value to replace '{hostname}' with.
    """
    try:
        # Ensure the input file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        # Read the content of the .toml file
        with open(file_path, 'r') as file:
            content = file.read()

        # Replace all occurrences of '{hostname}' with the provided hostname
        updated_content = content.replace('{hostname}', hostname)

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
