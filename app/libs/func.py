import platform
import subprocess
import sys
import time

import inquirer
import jmespath
import pyperclip
from colored import Fore, Style
from inquirer.themes import BlueComposure, GreenPassion
from terminaltables import AsciiTable


def run_exec(cmd, exec_path, line_len: int = 72):
    start_time = time.time()
    print_title(f"Execute '{cmd}'", line_len)
    execute_cmd(exec_path, cmd)
    print_title(".. it tooks %s seconds" % (time.time() - start_time), line_len)


def run_scripts(pp_dict, toml_dir, line_len: int = 72):
    _sub_continue = True
    _choices = [
        "poetry run {}".format(cmd)
        for cmd in list(jmespath.search("tool.poetry.scripts", pp_dict).keys())
    ]
    _choices.append("< back")
    while _sub_continue:
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
            sub_choices = [
                "> show --help",
                "> copy command to clipboard",
                "< back",
                "< exit",
            ]
            sub_questions = [
                inquirer.Checkbox(
                    "use",
                    message="How to execute the command '{}' - key 'space' for selection".format(
                        answers["script"]
                    ),
                    choices=sub_choices,
                    default=["> copy command to clipboard", "< exit"],
                )
            ]
            answers_sub = inquirer.prompt(sub_questions, theme=BlueComposure())
            if len(answers_sub["use"]) > 0:
                _exit_end = False
                _back_end = False
                for cmd in answers_sub["use"]:
                    if cmd == "> copy command to clipboard":
                        pyperclip.copy("{}".format(answers["script"]))
                    elif cmd == "> show --help":
                        cmd = "{} {}".format(answers["script"], "--help")
                        run_exec(cmd, toml_dir, line_len)
                    elif cmd == "< exit":
                        _exit_end = True
                    elif cmd == "< back":
                        _back_end = True
                if _exit_end:
                    sys.exit()
                if _back_end:
                    _sub_continue = False


def get_info(pp_dict: dict, short_info: bool = False):
    _info = jmespath.search("tool.poetry", pp_dict)
    info = {cout("PPCHECK", fore_256="yellow"): "POETRY PYPROJECT.TOML CHECK"}
    if not short_info:
        _packages = [list(dict(p).values())[0] for p in _info["packages"]]
        _deps_list = deps(pp_dict, "dependencies", "green")
        _deps_dev_list = deps(
            pp_dict,
            [
                "dev-dependencies",
                "dev.dependencies",
                "group.dev.dependencies",
                "group.test.dependencies",
            ],
            "blue",
        )
        _dependencies = tabs(_deps_list, _deps_dev_list)
        info.update(
            {
                "name": cout(_info["name"], fore_256="light_green"),
                "version": cout(_info["version"], fore_256="light_blue"),
                "description": cout(
                    short(_info["description"], 72), fore_256="light_magenta"
                ),
                "authors": cout("\n".join(_info["authors"]), fore_256="blue"),
                "packages": "\n".join(_packages),
            }
        )
        if len(_dependencies) > 0:
            info.update({"dependencies": _dependencies})
    return create_table(info, "")


def cout(val, fore_256: str = "white"):
    return "{}{}{}".format(getattr(Fore, fore_256), str(val), getattr(Style, "reset"))


def print_title(title: str, width: int, str_repeat: str = "~"):
    _exec_len = len(title)
    _lines = str_repeat * (_exec_len if _exec_len > width else width)
    print(cout(_lines, fore_256="grey_0"))
    print(cout(title, fore_256="deep_sky_blue_4a"))
    print(cout(_lines, fore_256="grey_0"))


def execute_cmd(exec_path: str, cmd: str):
    _dest = "" if platform.system() == "Windows" else " > /dev/null"
    _cmd = "pushd {}{} && ".format(exec_path, _dest) + cmd + " && popd{}".format(_dest)
    subprocess.run(_cmd, shell=True, stderr=sys.stderr, stdout=sys.stdout)


def attr_exists(obj_dct, should_type, *keys):
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


def create_table(entries: dict, title: str = "", heading_border: bool = True):
    """
    check: https://robpol86.github.io/terminaltables/
    """
    tab = []
    for k, v in entries.items():
        tab.append([k, v])
    table = AsciiTable(table_data=tab, title=title)
    table.inner_heading_row_border = heading_border
    return table.table


def short(input_str: str, char_length: int, ends: str = "..."):
    if len(input_str) > char_length:
        return input_str[:char_length] + ends
    else:
        return input_str


def deps(
    pp_dict: dict, sections: str | list = "dependencies", col: str = "white"
) -> list:
    if isinstance(sections, str):
        sections = [sections]
    _dl = []
    for section in sections:
        use = ["tool", "poetry"]
        use.extend(str(section).split("."))
        if attr_exists(pp_dict, dict, *use):
            _dlist = jmespath.search(".".join(use[:-1]), pp_dict)[use[-1:][0]]
            for k, v in _dlist.items():
                _dl.append([cout(k, fore_256=col), v])
    return _dl


def tabs(_deps_list: list, _deps_dev_list: list, as_table: bool = True):
    tab = []
    if len(_deps_list) > 0 and len(_deps_dev_list) > 0:
        tab = [
            [
                cout("prod", fore_256="light_green"),
                "",
                cout("dev", fore_256="light_blue"),
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
