import unittest
from unittest.mock import patch, MagicMock
import os
from utils import transfer_file_to_remote_host, replace_host_name_in_toml

class TestUtils(unittest.TestCase):

    @patch('utils.paramiko.SSHClient')
    @patch('utils.replace_host_name_in_toml')
    def test_transfer_file_to_remote_host(self, mock_replace_host_name_in_toml, mock_ssh_client):
        # Mock the SSH client and SFTP session
        mock_ssh = MagicMock()
        mock_sftp = MagicMock()
        mock_ssh_client.return_value = mock_ssh
        mock_ssh.open_sftp.return_value = mock_sftp

        # Define test parameters
        # local_file_path = 'test_local.toml'
        local_file_path = './bosminerConfig/test_local.toml'
        remote_file_path = '/remote/path/test_remote.toml'
        hostname = 'test_host'

        # Call the function
        transfer_file_to_remote_host(local_file_path, remote_file_path, hostname)

        # Assertions
        mock_ssh.connect.assert_called_once_with(hostname, username='root', pkey=unittest.mock.ANY)
        mock_replace_host_name_in_toml.assert_called_once_with(local_file_path, hostname)
        mock_sftp.put.assert_called_once_with('./tmpFile/newConfigTmp.toml', remote_file_path)
        mock_sftp.close.assert_called_once()
        mock_ssh.close.assert_called_once()

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='hostname={hostname}')
    def test_replace_host_name_in_toml(self, mock_open, mock_makedirs, mock_exists):
        # Mock os.path.exists to return True
        mock_exists.return_value = True

        # Define test parameters
        # file_path = 'test_local.toml'
        file_path = './bosminerConfig/test_local.toml'
        hostname = '12345'

        # Call the function
        replace_host_name_in_toml(file_path, hostname)

        # Assertions
        mock_open.assert_called_with(file_path, 'w')
        mock_open().read.assert_called_once()
        mock_open().write.assert_called_once_with('hostname=12345')
        mock_makedirs.assert_called_once_with('./tmpFile', exist_ok=True)

if __name__ == '__main__':
    unittest.main()