import os

import click
import inquirer
import pyperclip
import tomli
from terminaltables import AsciiTable

"""
author:     dapk@gmx.net
license:    MIT
"""

# using https://python-inquirer.readthedocs.io/


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
    _title = "|         Poetry pyproject.toml check for script(s)         |"
    _title_len = len(_title)
    print("/" + str("=" * (_title_len - 2)) + "\\")
    print(_title.upper())
    print("\\" + str("=" * (_title_len - 2)) + "/")
    try:
        toml_file = os.path.join(
            os.path.expanduser(check_poetry_path), "pyproject.toml"
        )
        if os.path.isfile(toml_file):
            with open(toml_file, "rb") as f:
                pp_dict = tomli.load(f)
            if (
                "tool" in pp_dict
                and "poetry" in pp_dict["tool"]
                and "scripts" in pp_dict["tool"]["poetry"]
            ):
                print(_create_table(pp_dict["tool"]["poetry"]["scripts"], "scripts"))
                questions = [
                    inquirer.List(
                        "script",
                        message="Choose script to execute",
                        choices=[
                            "poetry run {}".format(cmd)
                            for cmd in list(pp_dict["tool"]["poetry"]["scripts"].keys())
                        ],
                    ),
                    inquirer.Text(
                        "args", message="Run w/ argument(s)", default="--help"
                    ),
                ]
                answers = inquirer.prompt(questions)
                cmd = "{} {}".format(answers["script"], answers["args"])
                if copy_clipboard:
                    pyperclip.copy(cmd)
                _exec_title = (
                    "exec: " + cmd + (" <- copy to clipboard" if copy_clipboard else "")
                )
                _exec_len = len(_exec_title)
                print("-" * (_exec_len if _exec_len > _title_len else _title_len))
                print(_exec_title)
                print("-" * (_exec_len if _exec_len > _title_len else _title_len))
                print(
                    os.popen(
                        "pushd {} > /dev/null && ".format(os.path.dirname(toml_file))
                        + cmd
                        + " && popd > /dev/null"
                    ).read()
                )
            else:
                print(
                    f"No script command(s) available in {os.path.basename(toml_file)}."
                )
        else:
            print(f"ERROR: {toml_file} does not exist.")

    except Exception as e:
        print(f"WARNING: Something goes wrong or aborted. {e}")


def _create_table(entries: dict, title: str = ""):
    tab = []
    for k, v in entries.items():
        tab.append([k, v])
    table = AsciiTable(table_data=tab, title=title)
    return table.table


if __name__ == "main":
    main()
