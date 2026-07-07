"""
PPCheck - Poetry Project Checker

A CLI tool for inspecting and running scripts/commands in Poetry-based Python projects.
Parses pyproject.toml to discover available poetry scripts and provides an interactive
menu to execute them or run standard poetry commands.

author:     dapk@gmx.net
license:    MIT

using:      - https://python-inquirer.readthedocs.io/
            - https://dslackw.gitlab.io/colored/tables/colors/
"""

import os  # File path resolution and directory operations

import click  # CLI framework for command definitions and arguments
import inquirer  # Interactive terminal prompts (lists, checkboxes)
import tomli  # TOML parser for reading pyproject.toml and poetry.lock
from pyfiglet import Figlet  # ASCII art banner generator

# Internal library imports
from .libs.cls import \
    EPoetryCmds  # Enum of standard poetry commands (e.g. PYTEST, BUILD)
from .libs.func import (run_exec,  # Execution helpers for scripts and commands
                        run_scripts)
from .libs.ppinfo import \
    AKPPInfo  # Info/formatter utilities: color output, attribute checks, project display

# Maximum line length used for formatting script output tables
DEFAULT_LINE_LENGTH = 72


@click.command()
@click.argument("check_poetry_path", type=click.Path(exists=True), required=False)
def main(check_poetry_path):
    """
    This tool is used exclusively for Poetry projects.
    As soon as you have a poetry project in front of you in the console,
    you can use this tool to quickly find out which script commands the poetry project contains.

    usage:
    set path of poetry project, eg.\n
    $ poetry run ppcheck ~/poetry-project
    """
    # Print ASCII banner and intro text
    print(
        Figlet(font="small").renderText("PPCHECK"),
        "Poetry pyproject.toml check!",
        end="",
    )
    try:
        # ----- Load project configuration files -----
        # If no path was provided, default to the current working directory
        if not check_poetry_path:
            check_poetry_path = os.getcwd()
        # Build path to pyproject.toml and extract its parent directory
        toml_file = os.path.join(
            os.path.expanduser(check_poetry_path), "pyproject.toml"
        )
        toml_dir = os.path.dirname(toml_file)

        # Parse pyproject.toml into a dictionary, if it exists
        pp_dict = {}
        if os.path.isfile(toml_file):
            with open(toml_file, "rb") as f:
                pp_dict = tomli.load(f)

        # Parse poetry.lock into a dictionary, if it exists (for dependency info)
        pl_dict = {}
        if os.path.isfile("poetry.lock"):
            with open("poetry.lock", "rb") as f:
                pl_dict = tomli.load(f)

        # ----- Display project summary header -----
        print(AKPPInfo.GetInfo(pp_dict, pl_dict, True))

        # ----- Main interactive loop -----
        _continue = True
        while _continue:
            print("")
            # Present the user with an introductory choice menu
            q = [
                inquirer.List(
                    "intro",
                    message="Make your choice:",
                    choices=[
                        "use poetry run scripts",
                        "use poetry commands",
                        "get poetry info",
                        "< exit",
                    ],
                    default="no",
                ),
            ]
            start_seq = inquirer.prompt(q)

            # Option 1: Run user-defined poetry scripts (from [tool.poetry.scripts])
            if start_seq["intro"] == "use poetry run scripts":

                # Guard: only proceed if the scripts section exists in pyproject.toml
                if AKPPInfo.AttrExists(pp_dict, dict, "tool", "poetry", "scripts"):
                    run_scripts(pp_dict, toml_dir, DEFAULT_LINE_LENGTH)
                else:
                    print(
                        AKPPInfo.ColorOut(
                            f"No script command(s) available in {os.path.basename(toml_file)}.",
                            fore_256="light_red",
                        )
                    )

            # Option 2: Run standard poetry commands (e.g. build, pytest, lint)
            elif start_seq["intro"] == "use poetry commands":
                # Build list of available standard commands from the enum; remove 'pytest' if no tests directory exists
                _choices = list(EPoetryCmds._value2member_map_)
                if os.path.isdir(os.path.join(toml_dir, "tests")) == False:
                    _choices.remove(EPoetryCmds.PYTEST.value)
                # Let user select one or more commands to execute
                q = [
                    inquirer.Checkbox(
                        "exec_cmds",
                        message="Run commands at first by selecting with key 'space', press 'enter' for next",
                        choices=_choices,
                    ),
                ]
                tasks = inquirer.prompt(q)

                # Execute each selected command in sequence
                if len(tasks["exec_cmds"]) > 0:
                    for cmd in _choices:
                        if cmd in tasks["exec_cmds"]:
                            run_exec(
                                cmd,
                                toml_dir,
                                DEFAULT_LINE_LENGTH,
                            )

            # Option 3: Display project metadata (name, version, dependencies, etc.)
            elif start_seq["intro"] == "get poetry info":
                if len(pp_dict) > 0:
                    print(AKPPInfo.GetInfo(pp_dict, pl_dict))
                else:
                    print(
                        AKPPInfo.ColorOut(
                            f"No pyproject.toml available in {toml_dir}.",
                            fore_256="light_red",
                        )
                    )

            # Option 4: Exit the loop and terminate
            elif start_seq["intro"] == "< exit":
                _continue = False

            # Fallback: pyproject.toml not found
            else:
                print(
                    AKPPInfo.ColorOut(
                        f"{toml_file} does not exist.", fore_256="light_red"
                    )
                )
                quit()

    # Catch-all for keyboard interrupts (Ctrl+C), unexpected errors, or user abort
    except Exception as e:
        _message = "" if e is None else str(e)
        print(
            AKPPInfo.ColorOut(
                "Something goes wrong or you aborted ppcheck!", fore_256="light_red"
            )
        )
        print(AKPPInfo.ColorOut(_message, fore_256="light_yellow"))


if __name__ == "main":
    main()
