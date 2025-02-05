import platform
import subprocess
import sys
import time

import inquirer
import inquirer.themes
import jmespath
import pyperclip

from app.libs.ppinfo import AKPPInfo


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
        answers = inquirer.prompt(questions, theme=inquirer.themes.GreenPassion())

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
                    message="Selecting by key 'space' and press 'enter' to execute the command '{}'".format(
                        answers["script"]
                    ),
                    choices=sub_choices,
                    default=["> copy command to clipboard", "< exit"],
                )
            ]
            answers_sub = inquirer.prompt(sub_questions)
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


def print_title(title: str, width: int, str_repeat: str = "~"):
    _exec_len = len(title)
    _lines = str_repeat * (_exec_len if _exec_len > width else width)
    print(AKPPInfo.ColorOut(_lines, fore_256="grey_0"))
    print(AKPPInfo.ColorOut(title, fore_256="deep_sky_blue_4a"))
    print(AKPPInfo.ColorOut(_lines, fore_256="grey_0"))


def execute_cmd(exec_path: str, cmd: str):
    _dest = "" if platform.system() == "Windows" else " > /dev/null"
    _cmd = "pushd {}{} && ".format(exec_path, _dest) + cmd + " && popd{}".format(_dest)
    subprocess.run(_cmd, shell=True, stderr=sys.stderr, stdout=sys.stdout)
