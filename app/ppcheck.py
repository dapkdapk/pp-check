import os
import sys

import click
import inquirer
import pyperclip
import tomli
from terminaltables import AsciiTable


@click.command()
@click.argument("check_poetry_path", type=click.Path(exists=True))
def main(check_poetry_path):
    """
    This tool is used exclusively for Poetry projects.
    As soon as you have a poetry project in front of you in the console,
    you can use this tool to quickly find out which script commands the poetry project contains.

    usage:
    set path of poetry project, eg.\n
    $ poetry run ppcheck ~/poetry-project
    """
    try:
        toml_file = os.path.join(
            os.path.expanduser(check_poetry_path), "pyproject.toml"
        )
        if os.path.isfile(toml_file):
            with open(toml_file, "rb") as f:
                pp_dict = tomli.load(f)
            print(_create_table(pp_dict["tool"]["poetry"]["scripts"], "scripts"))
            questions = [
                inquirer.List(
                    "script",
                    message="Which script you want to execute as 'poetry run ..'?",
                    choices=list(pp_dict["tool"]["poetry"]["scripts"].keys()),
                ),
            ]
            answers = inquirer.prompt(questions)
            script = "poetry run {}".format(answers["script"])
            print(f"Copied '{script}' to clipboard:", script)
            pyperclip.copy(script)

    except Exception as e:
        print(f"ERROR: Something goes wrong. {e}")


def _create_table(entries: dict, title: str = ""):
    tab = []
    for k, v in entries.items():
        tab.append([k, v])
    table = AsciiTable(table_data=tab, title=title)
    return table.table


if __name__ == "main":
    main()
