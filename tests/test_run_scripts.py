import os
import platform
import sys
import unittest
from unittest.mock import MagicMock, patch

import pyperclip

from app.libs.func import execute_cmd, run_exec, run_scripts
from app.libs.ppinfo import AKPPInfo


class TestFunctions(unittest.TestCase):

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
        result = AKPPInfo.GetInfo(pp_dict)
        self.assertIn("example", result)
        self.assertIn("0.1.0", result)
        self.assertIn("An example package", result)
        self.assertIn("dep1", result)

    def test_cout(self):
        if str(platform.platform()).startswith("mac"):
            self.assertEqual(
                AKPPInfo.ColorOut("Test", "red"), "\x1b[38;5;1mTest\x1b[0m"
            )
            self.assertEqual(
                AKPPInfo.ColorOut("Test", "blue"), "\x1b[38;5;4mTest\x1b[0m"
            )
            self.assertEqual(
                AKPPInfo.ColorOut("Test"), "\x1b[38;5;15mTest\x1b[0m"
            )  # Default is white

    def test_attr_exists(self):
        obj_dct = {"key1": {"key2": "value"}}
        self.assertTrue(AKPPInfo.AttrExists(obj_dct, str, "key1", "key2"))
        self.assertFalse(AKPPInfo.AttrExists(obj_dct, str, "key1", "non_existing_key"))

    def test_short(self):
        self.assertEqual(AKPPInfo.StrShort("Hello World", 5), "Hello...")
        self.assertEqual(AKPPInfo.StrShort("Hello", 10), "Hello")

    def test_deps(self):
        pp_dict = {
            "tool": {"poetry": {"dependencies": {"dep1": "^1.0", "dep2": "^2.0"}}}
        }
        result = AKPPInfo.Dependencies(pp_dict)
        self.assertEqual(len(result), 2)

    def test_tabs(self):
        deps_list = [["dep1", "1.0"], ["dep2", "2.0"]]
        dev_deps_list = [["dev1", "1.0"]]
        result = AKPPInfo.Table(deps_list, dev_deps_list)
        self.assertIn("deps", result)
        self.assertIn("dev-deps", result)
