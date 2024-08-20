import os

import click
import inquirer
import tomli
from inquirer.themes import BlueComposure

from .libs.classes import EPoetryCmds
from .libs.functions import attr_exists, get_info, run_exec, run_scripts

"""
author:     dapk@gmx.net
license:    MIT

using:      - https://python-inquirer.readthedocs.io/
            - https://dslackw.gitlab.io/colored/tables/colors/
"""

DEFAULT_LINE_LENGTH = 72


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
            if attr_exists(pp_dict, dict, "tool", "poetry"):
                print(get_info(pp_dict))
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
                if attr_exists(pp_dict, dict, "tool", "poetry", "scripts"):
                    run_scripts(pp_dict, copy_clipboard, toml_file, DEFAULT_LINE_LENGTH)
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
                            run_exec(
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


if __name__ == "main":
    main()
