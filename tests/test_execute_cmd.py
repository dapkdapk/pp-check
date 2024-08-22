import subprocess
import sys
import unittest
from unittest.mock import patch

from app.libs.func import execute_cmd


class TestExecuteCmd(unittest.TestCase):

    @patch("subprocess.run")
    @patch("platform.system", return_value="Linux")
    def test_execute_cmd_success_linux(self, mock_platform, mock_subprocess):
        exec_path = "/some/path"
        cmd = "echo Hello"
        execute_cmd(exec_path, cmd)

        expected_cmd = "pushd /some/path > /dev/null && echo Hello && popd > /dev/null"
        mock_subprocess.assert_called_once_with(
            expected_cmd, shell=True, stderr=sys.stderr, stdout=sys.stdout
        )

    @patch("subprocess.run")
    @patch("platform.system", return_value="Windows")
    def test_execute_cmd_success_windows(self, mock_platform, mock_subprocess):
        exec_path = "C:\\some\\path"
        cmd = "echo Hello"
        execute_cmd(exec_path, cmd)

        expected_cmd = "pushd C:\\some\\path && echo Hello && popd"
        mock_subprocess.assert_called_once_with(
            expected_cmd, shell=True, stderr=sys.stderr, stdout=sys.stdout
        )

    @patch("subprocess.run")
    @patch("platform.system", return_value="Linux")
    def test_execute_cmd_failure(self, mock_platform, mock_subprocess):
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "cmd")
        exec_path = "/some/path"
        cmd = "exit 1"

        with self.assertRaises(subprocess.CalledProcessError):
            execute_cmd(exec_path, cmd)

    @patch("subprocess.run")
    @patch("platform.system", return_value="Windows")
    def test_execute_cmd_failure_windows(self, mock_platform, mock_subprocess):
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "cmd")
        exec_path = "C:\\some\\path"
        cmd = "exit 1"

        with self.assertRaises(subprocess.CalledProcessError):
            execute_cmd(exec_path, cmd)

    @patch("subprocess.run")
    @patch("platform.system", return_value="Linux")
    def test_execute_cmd_empty_command(self, mock_platform, mock_subprocess):
        exec_path = "/some/path"
        cmd = ""
        execute_cmd(exec_path, cmd)

        expected_cmd = "pushd /some/path > /dev/null &&  && popd > /dev/null"
        mock_subprocess.assert_called_once_with(
            expected_cmd, shell=True, stderr=sys.stderr, stdout=sys.stdout
        )

    @patch("subprocess.run")
    @patch("platform.system", return_value="Windows")
    def test_execute_cmd_empty_command_windows(self, mock_platform, mock_subprocess):
        exec_path = "C:\\some\\path"
        cmd = ""
        execute_cmd(exec_path, cmd)

        expected_cmd = "pushd C:\\some\\path &&  && popd"
        mock_subprocess.assert_called_once_with(
            expected_cmd, shell=True, stderr=sys.stderr, stdout=sys.stdout
        )
