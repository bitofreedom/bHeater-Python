import paramiko
import os

def transfer_file_to_remote_host(local_file_path, remote_file_path, hostname, username, private_key_path):
    """
    Transfers a file from the local machine to a remote host using SFTP with private key-based authentication.

    :param local_file_path: Path to the local file to be transferred.
    :param remote_file_path: Path to the remote file (including filename) where the file will be saved.
    :param hostname: Hostname or IP address of the remote host.
    :param username: Username for SSH authentication.
    :param private_key_path: Path to the private key file for SSH authentication.
    """
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the private key
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

        # Connect to the remote host using the private key
        ssh.connect(hostname, username=username, pkey=private_key)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        # Transfer the file
        sftp.put(local_file_path, remote_file_path)
        print(f"File {local_file_path} transferred to {remote_file_path} on {hostname}")

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    # local_file_path = "/path/to/local/file.txt"  # Replace with your local file path
    # remote_file_path = "/path/to/remote/file.txt"  # Replace with your remote file path
    # hostname = "remote.host.com"  # Replace with your remote host's IP or hostname
    # username = "your_username"  # Replace with your SSH username
    # private_key_path = "/path/to/private/key"  # Replace with your private key path

    local_file_path = "./bosminerConfig/bosminer-default.toml"  # Replace with your local file path
    remote_file_path = "/etc/bosminer.toml"  # Replace with your remote file path
    hostname = "192.168.24.206"  # Replace with your remote host's IP or hostname
    username = "root"  # Replace with your SSH username
    private_key_path = os.path.expanduser("~/.ssh/id_rsa")  # Replace with your private key path

    transfer_file_to_remote_host(local_file_path, remote_file_path, hostname, username, private_key_path)