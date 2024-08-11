import os
import platform
import subprocess
import sys
from enum import Enum

import click
import inquirer
import pyperclip
import tomli
from inquirer.themes import BlueComposure, GreenPassion
from terminaltables import AsciiTable

"""
author:     dapk@gmx.net
license:    MIT
"""

# using https://python-inquirer.readthedocs.io/

DEFAULT_LINE_LENGTH = 72


class EPoetryCmds(Enum):
    UPDATE = "poetry update"
    LOCK = "poetry lock"
    INSTALL = "poetry install"
    SHOW_TREE = "poetry show --tree"
    PYTEST = "poetry run pytest"


@click.command()
@click.argument("check_poetry_path", type=click.Path(exists=True))
@click.option(
    "-c",
    "--copy-clipboard",
    is_flag=True,
    help="flag for copy choosen command to clipboard",
)
def main(check_poetry_path, copy_clipboard):
    """
    This tool is used exclusively for Poetry projects.
    As soon as you have a poetry project in front of you in the console,
    you can use this tool to quickly find out which script commands the poetry project contains.

    usage:
    set path of poetry project, eg.\n
    $ poetry run ppcheck ~/poetry-project
    """

    print(_create_table({"PPCHECK": "GET POETRY DETAILS"}))
    try:
        # get/load pyproject.yaml
        toml_file = os.path.join(
            os.path.expanduser(check_poetry_path), "pyproject.toml"
        )
        if os.path.isfile(toml_file):
            with open(toml_file, "rb") as f:
                pp_dict = tomli.load(f)
            # check info
            if _attr_exists(pp_dict, dict, "tool", "poetry"):
                _info = pp_dict["tool"]["poetry"]
                print(
                    _create_table(
                        {
                            "name": _info["name"],
                            "version": _info["version"],
                            "description": _short(_info["description"], 72),
                            "authors": "\n".join(_info["authors"]),
                        },
                        "info",
                    )
                )
        _continue = True
        while _continue:

            print("")

            # choose scripts or stndards commands
            q = [
                inquirer.List(
                    "intro",
                    message="Make your choice:",
                    choices=[
                        "show script commands",
                        "execute poetry commands",
                        "< exit",
                    ],
                    default="no",
                ),
            ]
            start_seq = inquirer.prompt(q)

            if start_seq["intro"] == "show script commands":

                # check scripts with inputs
                if _attr_exists(pp_dict, dict, "tool", "poetry", "scripts"):
                    _run_scripts(
                        pp_dict, copy_clipboard, toml_file, DEFAULT_LINE_LENGTH
                    )
                else:
                    print(
                        f"No script command(s) available in {os.path.basename(toml_file)}."
                    )
            elif start_seq["intro"] == "execute poetry commands":
                # choice what do you want?
                _choices = list(EPoetryCmds._value2member_map_)
                if (
                    os.path.isdir(os.path.join(os.path.dirname(toml_file), "tests"))
                    == False
                ):
                    _choices.remove(EPoetryCmds.PYTEST.value)
                q = [
                    inquirer.Checkbox(
                        "exec_cmds",
                        message="Run commands at first by selecting with key 'space', press 'enter' for next",
                        choices=_choices,
                    ),
                ]
                tasks = inquirer.prompt(q, theme=BlueComposure())

                if len(tasks["exec_cmds"]) > 0:
                    for cmd in _choices:
                        if cmd in tasks["exec_cmds"]:
                            _run_exec(
                                cmd,
                                os.path.dirname(toml_file),
                                DEFAULT_LINE_LENGTH,
                            )
            elif start_seq["intro"] == "< exit":
                _continue = False
            else:
                print(f"ERROR: {toml_file} does not exist.")
                quit()

    except Exception as e:
        print(f"WARNING: Something goes wrong or aborted. {e}")


def _run_exec(cmd, exec_path, line_len: int = 72):
    _print_title(f"Execute '{cmd}'", line_len)
    _execute_cmd(exec_path, cmd)


def _run_scripts(pp_dict, copy_clipboard, toml_file, line_len: int = 72):
    _sub_continue = True
    _choices = [
        "poetry run {}".format(cmd)
        for cmd in list(pp_dict["tool"]["poetry"]["scripts"].keys())
    ]
    _choices.append("< back")
    while _sub_continue:
        print(_create_table(pp_dict["tool"]["poetry"]["scripts"], "scripts"))
        questions = [
            inquirer.List(
                "script",
                message="Choose script to execute",
                choices=_choices,
            ),
        ]
        answers = inquirer.prompt(questions, theme=GreenPassion())

        if answers["script"] == "< back":
            _sub_continue = False
        else:
            sub_questions = [
                inquirer.Text("args", message="Run w/ argument(s)", default="--help"),
            ]
            answers_sub = inquirer.prompt(sub_questions, theme=GreenPassion())
            cmd = "{} {}".format(answers["script"], answers_sub["args"])
            if copy_clipboard:
                pyperclip.copy(cmd)
            _exec_title = (
                "exec: " + cmd + (" <- copy to clipboard" if copy_clipboard else "")
            )
            _print_title(_exec_title, line_len)
            _execute_cmd(os.path.dirname(toml_file), cmd)
            print("")
            input("Press Enter to continue ...")


def _print_title(title, width):
    _exec_len = len(title)
    _lines = "-" * (_exec_len if _exec_len > width else width)
    print(_lines)
    print(title)
    print(_lines)


def _execute_cmd(exec_path: str, cmd: str):
    _dest = "" if platform.system() == "Windows" else " > /dev/null"
    _cmd = "pushd {}{} && ".format(exec_path, _dest) + cmd + " && popd{}".format(_dest)
    subprocess.run(_cmd, shell=True, stderr=sys.stderr, stdout=sys.stdout)


def _attr_exists(obj_dct, should_type, *keys):
    keys = list(keys)
    while keys:
        match = keys.pop(0)
        if isinstance(obj_dct, dict):
            if match in obj_dct:
                if not keys:
                    return (
                        (True if isinstance(obj_dct[match], should_type) else False)
                        if should_type
                        else True
                    )
                else:
                    obj_dct = obj_dct[match]
            else:
                return False
        else:
            return False


def _create_table(entries: dict, title: str = ""):
    tab = []
    for k, v in entries.items():
        tab.append([k, v])
    table = AsciiTable(table_data=tab, title=title)
    return table.table


def _short(input_str: str, char_length: int, ends: str = "..."):
    if len(input_str) > char_length:
        return input_str[:char_length] + ends
    else:
        return input_str


if __name__ == "main":
    main()
