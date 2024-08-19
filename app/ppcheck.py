import os
import platform
import subprocess
import sys
import time
from enum import Enum

import click
import inquirer
import pyperclip
import tomli
from colored import Fore, Style
from inquirer.themes import BlueComposure, GreenPassion
from terminaltables import AsciiTable

"""
author:     dapk@gmx.net
license:    MIT

using:      - https://python-inquirer.readthedocs.io/
            - https://dslackw.gitlab.io/colored/tables/colors/
"""

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
                _packages = [list(dict(p).values())[0] for p in _info["packages"]]
                _deps_list = _deps(pp_dict, "dependencies", "green")
                _deps_dev_list = _deps(pp_dict, "dev-dependencies", "blue")
                _dependencies = _tabs(_deps_list, _deps_dev_list)
                info = {
                    cprint("PPCHECK", fore_256="yellow"): "POETRY PYPROJECT.TOML CHECK",
                    "name": cprint(_info["name"], fore_256="light_green"),
                    "version": cprint(_info["version"], fore_256="light_blue"),
                    "description": cprint(
                        _short(_info["description"], 72), fore_256="light_magenta"
                    ),
                    "authors": cprint("\n".join(_info["authors"]), fore_256="blue"),
                    "packages": "\n".join(_packages),
                }
                if len(_dependencies) > 0:
                    info.update({"dependencies": _dependencies})
                print(
                    _create_table(
                        info,
                        "",
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
                        "run script commands",
                        "run poetry commands",
                        "< exit",
                    ],
                    default="no",
                ),
            ]
            start_seq = inquirer.prompt(q)

            if start_seq["intro"] == "run script commands":

                # check scripts with inputs
                if _attr_exists(pp_dict, dict, "tool", "poetry", "scripts"):
                    _run_scripts(
                        pp_dict, copy_clipboard, toml_file, DEFAULT_LINE_LENGTH
                    )
                else:
                    print(
                        f"No script command(s) available in {os.path.basename(toml_file)}."
                    )
            elif start_seq["intro"] == "run poetry commands":
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
    start_time = time.time()
    _print_title(f"Execute '{cmd}'", line_len)
    _execute_cmd(exec_path, cmd)
    _print_title(".. execution took %s seconds" % (time.time() - start_time), line_len)


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
            start_time = time.time()
            _print_title(_exec_title, line_len)
            _execute_cmd(os.path.dirname(toml_file), cmd)
            print("")
            _print_title(
                ".. execution took %s seconds" % (time.time() - start_time), line_len
            )
            input("Press Enter to continue ...")


def cprint(val, fore_256: str = "white"):
    return "{}{}{}".format(getattr(Fore, fore_256), str(val), getattr(Style, "reset"))


def _print_title(title: str, width: int, str_repeat: str = "~"):
    _exec_len = len(title)
    _lines = str_repeat * (_exec_len if _exec_len > width else width)
    print(cprint(_lines, fore_256="grey_0"))
    print(cprint(title, fore_256="deep_sky_blue_4a"))
    print(cprint(_lines, fore_256="grey_0"))


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


def _create_table(entries: dict, title: str = "", heading_border: bool = True):
    """
    check: https://robpol86.github.io/terminaltables/
    """
    tab = []
    for k, v in entries.items():
        tab.append([k, v])
    table = AsciiTable(table_data=tab, title=title)
    table.inner_heading_row_border = heading_border
    return table.table


def _short(input_str: str, char_length: int, ends: str = "..."):
    if len(input_str) > char_length:
        return input_str[:char_length] + ends
    else:
        return input_str


def _deps(pp_dict: dict, section: str = "dependencies", col: str = "white") -> list:
    if _attr_exists(pp_dict, dict, "tool", "poetry", section):
        _dlist = pp_dict["tool"]["poetry"][section]
        _dl = []
        for k, v in _dlist.items():
            _dl.append([cprint(k, fore_256=col), v])
        return _dl
    else:
        return []


def _tabs(_deps_list: list, _deps_dev_list: list, as_table: bool = True):
    tab = []
    if len(_deps_list) > 0 and len(_deps_dev_list) > 0:
        tab = [
            [
                cprint("prod", fore_256="light_green"),
                "",
                cprint("dev", fore_256="light_blue"),
                "",
            ]
        ]
        if len(_deps_list) >= len(_deps_dev_list):
            i = 0
            for i in range(len(_deps_list)):
                if 0 <= i < len(_deps_dev_list):
                    tab.append(_deps_list[i] + _deps_dev_list[i])
                else:
                    tab.append(_deps_list[i] + ["", ""])
                i += 1
        else:
            i = 0
            for i in range(len(_deps_dev_list)):
                if 0 <= i < len(_deps_list):
                    tab.append(_deps_list[i] + _deps_dev_list[i])
                else:
                    tab.append(["", ""] + _deps_dev_list[i])
                i += 1
    elif len(_deps_list) > 0 and len(_deps_dev_list) < 1:
        tab = [["prod", ""]]
        i = 0
        for i in range(len(_deps_list)):
            tab.append(_deps_list[i])
            i += 1
    elif len(_deps_dev_list) > 0 and len(_deps_list) < 1:
        tab = [["dev", ""]]
        i = 0
        for i in range(len(_deps_dev_list)):
            tab.append(_deps_dev_list[i])
            i += 1
    if as_table and len(tab) > 0:
        table = AsciiTable(table_data=tab)
        return table.table
    else:
        return tab


if __name__ == "main":
    main()
