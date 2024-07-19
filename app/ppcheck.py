import os
import sys
import tomli

import click
import inquirer
import pyperclip
from terminaltables import AsciiTable


@click.command()
@click.argument("checkpath", type=click.Path(exists=True))
def main(checkpath):
    try:
        toml_file = os.path.join(os.path.expanduser(checkpath), "pyproject.toml")
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
