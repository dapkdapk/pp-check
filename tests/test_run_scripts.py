import os
import platform
import sys
import unittest
from unittest.mock import MagicMock, patch

import pyperclip

from app.libs.func import (attr_exists, cout, create_table, deps, execute_cmd,
                           get_info, run_exec, run_scripts, short, tabs)


class TestFunctions(unittest.TestCase):

    @patch("app.libs.func.subprocess.run")
    @patch("app.libs.func.print_title")
    def test_run_exec(self, mock_print_title, mock_subprocess_run):
        cmd = "echo Hello World"
        exec_path = os.getcwd()

        run_exec(cmd, exec_path)
        mock_print_title.assert_called()
        _dest = "" if platform.system() == "Windows" else " > /dev/null"
        mock_subprocess_run.assert_called_with(
            f"pushd {exec_path}{_dest} && {cmd} && popd{_dest}",
            shell=True,
            stderr=sys.stderr,
            stdout=sys.stdout,
        )

    @patch("inquirer.prompt")
    @patch("pyperclip.copy")
    @patch("app.libs.func.run_exec")
    def test_run_script_exit(self, mock_run_exec, mock_copy, mock_prompt):
        # Setup mock responses
        mock_prompt.side_effect = [
            {"script": "example_script"},  # First prompt response
            {"use": ["< exit"]},  # Second prompt response
        ]

        pp_dict = {
            "tool": {"poetry": {"scripts": {"example_script": "example command"}}}
        }
        toml_dir = "dummy_dir"

        with self.assertRaises(SystemExit):
            run_scripts(pp_dict, toml_dir)

    @patch("inquirer.prompt")
    def test_run_script_back(self, mock_prompt):
        # Setup mock responses
        mock_prompt.side_effect = [
            {"script": "example_script"},  # First prompt response
            {"use": ["< back"]},  # Second prompt response
        ]

        pp_dict = {
            "tool": {"poetry": {"scripts": {"example_script": "example command"}}}
        }
        toml_dir = "dummy_dir"

        # Execute the function and assert that it does not raise an error
        try:
            run_scripts(pp_dict, toml_dir)
        except Exception as e:
            self.fail(f"run_scripts raised an exception: {e}")

    def test_get_info(self):
        pp_dict = {
            "tool": {
                "poetry": {
                    "name": "example",
                    "version": "0.1.0",
                    "description": "An example package",
                    "authors": ["Author <author@example.com>"],
                    "packages": [{"example": "example"}],
                    "dependencies": {"dep1": "^1.0", "dep2": "^2.0"},
                    "dev-dependencies": {"dev1": "^1.0"},
                }
            }
        }
        result = get_info(pp_dict)
        self.assertIn("example", result)
        self.assertIn("0.1.0", result)
        self.assertIn("An example package", result)
        self.assertIn("dep1", result)

    def test_cout(self):
        if str(platform.platform()).startswith("mac"):
            self.assertEqual(cout("Test", "red"), "\x1b[38;5;1mTest\x1b[0m")
            self.assertEqual(cout("Test", "blue"), "\x1b[38;5;4mTest\x1b[0m")
            self.assertEqual(
                cout("Test"), "\x1b[38;5;15mTest\x1b[0m"
            )  # Default is white

    @patch("app.libs.func.subprocess.run")
    def test_execute_cmd(self, mock_subprocess_run):
        if str(platform.platform()).startswith("mac"):
            exec_path = os.getcwd()
            cmd = "echo Hello"
            execute_cmd(exec_path, cmd)
            mock_subprocess_run.assert_called_with(
                f"pushd {exec_path} > /dev/null && {cmd} && popd > /dev/null",
                shell=True,
                stderr=sys.stderr,
                stdout=sys.stdout,
            )

    def test_attr_exists(self):
        obj_dct = {"key1": {"key2": "value"}}
        self.assertTrue(attr_exists(obj_dct, str, "key1", "key2"))
        self.assertFalse(attr_exists(obj_dct, str, "key1", "non_existing_key"))

    def test_create_table(self):
        entries = {"name": "value", "test": "123"}
        table = create_table(entries)
        self.assertIn("name", table)
        self.assertIn("value", table)

    def test_short(self):
        self.assertEqual(short("Hello World", 5), "Hello...")
        self.assertEqual(short("Hello", 10), "Hello")

    def test_deps(self):
        pp_dict = {
            "tool": {"poetry": {"dependencies": {"dep1": "^1.0", "dep2": "^2.0"}}}
        }
        result = deps(pp_dict)
        self.assertEqual(len(result), 2)

    def test_tabs(self):
        deps_list = [["dep1", "1.0"], ["dep2", "2.0"]]
        dev_deps_list = [["dev1", "1.0"]]
        result = tabs(deps_list, dev_deps_list)
        self.assertIn("prod", result)
        self.assertIn("dev", result)
