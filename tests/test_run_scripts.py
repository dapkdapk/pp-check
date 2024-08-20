import os
import unittest
from unittest.mock import MagicMock, patch

from app.libs.functions import run_scripts


class TestRunScripts(unittest.TestCase):

    @patch("inquirer.prompt")
    @patch("pyperclip.copy")
    @patch("os.path.dirname")
    @patch(
        "app.libs.functions.execute_cmd"
    )  # Replace 'app.ppcheck' with the actual module name
    @patch("app.libs.functions.print_title")
    @patch("app.libs.functions.create_table")
    @patch("app.libs.functions.input")
    def test_run_script_positive(
        self,
        mock_input,
        mock_create_table,
        mock_print_title,
        mock_execute_cmd,
        mock_dirname,
        mock_copy,
        mock_prompt,
    ):
        # Setup
        pp_dict = {
            "tool": {"poetry": {"scripts": {"test_script": {}, "another_script": {}}}}
        }
        mock_dirname.return_value = "/path/to/toml"
        mock_create_table.return_value = "Mocked Table"

        # Mock user input
        mock_prompt.side_effect = [
            {"script": "poetry run test_script"},  # First prompt
            {"args": "--arg1 value1"},  # Second prompt
            {"script": "< back"},  # Exit prompt
        ]

        with patch("builtins.print") as mocked_print:
            run_scripts(pp_dict, copy_clipboard=True, toml_file="mocked.toml")
            # Check if the command was executed correctly
            mock_execute_cmd.assert_called_once_with(
                "/path/to/toml", "poetry run test_script --arg1 value1"
            )
            mocked_print.assert_called()  # Ensure print was called

    @patch("inquirer.prompt")
    @patch("pyperclip.copy")
    @patch("os.path.dirname")
    @patch("app.libs.functions.execute_cmd")
    @patch("app.libs.functions.print_title")
    @patch("app.libs.functions.create_table")
    def test_run_script_negative(
        self,
        mock_create_table,
        mock_print_title,
        mock_execute_cmd,
        mock_dirname,
        mock_copy,
        mock_prompt,
    ):
        # Setup
        pp_dict = {
            "tool": {"poetry": {"scripts": {"test_script": {}, "another_script": {}}}}
        }
        mock_dirname.return_value = "/path/to/toml"
        mock_create_table.return_value = "Mocked Table"

        # Mock user input to simulate an invalid script selection
        mock_prompt.side_effect = [
            {"script": "invalid_script"},  # Invalid script
            {"args": "--arg1 value1"},  # Second prompt
            {"script": "< back"},  # Exit prompt
        ]

        with patch("builtins.print") as mocked_print:
            with self.assertRaises(
                Exception
            ):  # Expecting an exception due to invalid script
                run_scripts(pp_dict, copy_clipboard=False, toml_file="mocked.toml")
            mocked_print.assert_called()  # Ensure print was called

    @patch("inquirer.prompt")
    @patch("pyperclip.copy")
    @patch("os.path.dirname")
    @patch("app.libs.functions.execute_cmd")
    @patch("app.libs.functions.print_title")
    @patch("app.libs.functions.create_table")
    @patch("app.libs.functions.input")
    def test_run_script_edge_case(
        self,
        mock_input,
        mock_create_table,
        mock_print_title,
        mock_execute_cmd,
        mock_dirname,
        mock_copy,
        mock_prompt,
    ):
        # Setup
        pp_dict = {
            "tool": {
                "poetry": {
                    "scripts": {
                        "test_script": {},
                    }
                }
            }
        }
        mock_dirname.return_value = "/path/to/toml"
        mock_create_table.return_value = "Mocked Table"

        # Mock user input for edge case
        mock_prompt.side_effect = [
            {"script": "poetry run test_script"},  # Valid script
            {"args": ""},  # No arguments
            {"script": "< back"},  # Exit prompt
        ]

        with patch("builtins.print") as mocked_print:
            run_scripts(pp_dict, copy_clipboard=False, toml_file="mocked.toml")
            # Check if the command was executed correctly
            mock_execute_cmd.assert_called_once_with(
                "/path/to/toml", "poetry run test_script "
            )
            mocked_print.assert_called()  # Ensure print was called
