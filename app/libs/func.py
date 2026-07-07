import os
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
    """
    Execute a shell command and measure its execution time.

    Displays a formatted title with the command being run, executes it,
    then prints the elapsed time.

    Args:
        cmd: The command string to execute.
        exec_path: The directory path from which to run the command.
        line_len: Width for the title formatting (default 72).
    """
    start_time = time.time()
    print_title(f"Execute '{cmd}'", line_len)
    execute_cmd(exec_path, cmd)
    print_title(".. it tooks %s seconds" % (time.time() - start_time), line_len)


def run_scripts(pp_dict, toml_dir, line_len: int = 72):
    """
    Interactive menu for selecting and running Poetry scripts defined in pyproject.toml.

    Presents a two-level interactive prompt:
      1. Choose a script from the available Poetry scripts.
      2. Choose one or more actions (show --help, copy to clipboard, back, exit).

    Args:
        pp_dict: Parsed pyproject.toml dictionary (output of toml parsing).
        toml_dir: Directory containing pyproject.toml.
        line_len: Width for title formatting (default 72).
    """
    _sub_continue = True

    # Build list of Poetry script commands from the pyproject.toml data
    _choices = [
        "poetry run {}".format(cmd)
        for cmd in list(jmespath.search("tool.poetry.scripts", pp_dict).keys())
    ]
    _choices.append("< back")

    while _sub_continue:
        # First-level prompt: select a script to work with
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
            # Second-level prompt: choose actions for the selected script
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
                        # Attempt to copy the command to clipboard; warn if unavailable
                        if _pyperclip_is_available() is False:
                            print(
                                AKPPInfo.ColorOut(
                                    "Clipboard (pyperclip) functionality is not available on this system.",
                                    fore_256="light_red",
                                ),
                                AKPPInfo.ColorOut(
                                    "\nPlease type to execute selected command by yourself:",
                                    fore_256="white",
                                ),
                            )
                            print(
                                AKPPInfo.ColorOut(
                                    f"{answers['script']}", fore_256="light_yellow"
                                )
                            )
                        else:
                            pyperclip.copy("{}".format(answers["script"]))
                            print(
                                AKPPInfo.ColorOut(
                                    "Command '{}' has been copied to clipboard.".format(
                                        answers["script"]
                                    ),
                                    fore_256="light_green",
                                )
                            )
                    elif cmd == "> show --help":
                        # Run the script with --help flag
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
    """
    Print a formatted title surrounded by repeated separator characters.

    Args:
        title: The title text to display.
        width: Minimum width of the separator line.
        str_repeat: Character used for the separator line (default "~").
    """
    _exec_len = len(title)
    # Use the longer of title length or minimum width for the separator
    _lines = str_repeat * (_exec_len if _exec_len > width else width)
    print(AKPPInfo.ColorOut(_lines, fore_256="grey_0"))
    print(AKPPInfo.ColorOut(title, fore_256="deep_sky_blue_4a"))
    print(AKPPInfo.ColorOut(_lines, fore_256="grey_0"))


def execute_cmd(exec_path: str, cmd: str):
    """
    Run a shell command in a specified directory.

    Changes to the target directory, executes the command, then returns to
    the original directory. On non-Windows systems, the navigation output
    is silenced by redirecting to /dev/null.

    Args:
        exec_path: The directory to run the command from.
        cmd: The shell command to execute.
    """
    # On Windows, keep cd output visible; on Unix, silence it
    _dest = "" if platform.system() == "Windows" else " > /dev/null"
    _cmd = (
        "cd {} && ".format(os.path.expanduser(os.path.join(exec_path, _dest)))
        + cmd
        + " && cd {}".format(_dest)
    )
    subprocess.run(_cmd, shell=True, stderr=sys.stderr, stdout=sys.stdout)


def _pyperclip_is_available() -> bool:
    """
    Check whether pyperclip clipboard access is available on the current system.

    Returns:
        True if a functional clipboard backend is detected, False otherwise.
    """
    _ = pyperclip.determine_clipboard()
    if len(_) > 0:
        # pyperclip falls back to a "no clipboard" placeholder class when
        # no real clipboard backend can be loaded; detect that case.
        return "pyperclip.init_no_clipboard" not in str(
            pyperclip.determine_clipboard()[0]
        )
    else:
        return False
