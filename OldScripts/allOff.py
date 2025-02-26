import paramiko
import getpass

def read_hosts(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def execute_remote_commands():
    hosts_file = 'hosts.txt'  # Path to file containing IP addresses
    hosts = read_hosts(hosts_file)
    
    if not hosts:
        print("No hosts found in hosts.txt")
        return

    # Get user credentials
    username = input("Enter SSH username: ")
    auth_type = input("Authentication method (password/key): ").lower()

    password = None
    key_path = None
    
    if auth_type == 'password':
        password = getpass.getpass("Enter SSH password: ")
    elif auth_type == 'key':
        key_path = input("Enter path to private key (optional): ") or None
    else:
        print("Invalid authentication method")
        return

    # Get command to execute
    # command = input("Enter command to execute: ")
    command = "/etc/init.d/bosminer stop"

    # Process each host
    for host in hosts:
        print(f"\n{'='*30}\nConnecting to {host}\n{'='*30}")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Establish connection
            if auth_type == 'password':
                client.connect(hostname=host, username=username, password=password, timeout=10)
            else:
                client.connect(hostname=host, username=username, key_filename=key_path, timeout=10)

            # Execute command using system's default shell
            stdin, stdout, stderr = client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()

            # Get output
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            print(f"Command exited with status: {exit_code}")
            if output:
                print(f"Output:\n{output}")
            if error:
                print(f"Errors:\n{error}")

        except paramiko.AuthenticationException:
            print(f"Authentication failed for {host}")
        except paramiko.SSHException as e:
            print(f"SSH connection failed to {host}: {str(e)}")
        except Exception as e:
            print(f"Error connecting to {host}: {str(e)}")
        finally:
            client.close()

if __name__ == "__main__":
    execute_remote_commands()