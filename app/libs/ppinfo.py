"""
Utilities for extracting, formatting, and displaying project metadata
from pyproject.toml and poetry.lock files.

Provides colorized output, ASCII table rendering, and dependency listing
for Poetry-managed Python projects.
"""

import os
import re

import jmespath
import tomli
from colored import Fore, Style
from terminaltables import AsciiTable


class AKPPInfo:
    """
    Collection of static helper methods for project information display.

    Methods handle parsing pyproject.toml / poetry.lock, formatting output
    with ANSI color codes, building ASCII tables, and traversing nested dicts.
    """

    @staticmethod
    def GetInfo(
        pp_dict: dict | str | None = None,
        pl_dict: dict | str | None = None,
        short_info: bool = False,
    ):
        """
        Retrieve and format project information into an ASCII table.

        Accepts either file paths or already-loaded dictionaries for both
        pyproject.toml (pp_dict) and poetry.lock (pl_dict). When paths are
        given, the files are loaded via tomli.

        Args:
            pp_dict: pyproject.toml as dict, file path, or None (defaults to
                     './pyproject.toml').
            pl_dict: poetry.lock as dict, file path, or None (defaults to
                     './poetry.lock').
            short_info: If True, omit dependencies table (not implemented
                        in data collection; primarily controls display).

        Returns:
            A formatted ASCII table string, or an empty string if no data.
        """
        _pp_dict = {}

        # Resolve pyproject.toml source: default path, dict, or explicit path
        if pp_dict is None:
            pp_dict = "./pyproject.toml"
        else:
            _pp_dict = pp_dict if isinstance(pp_dict, dict) else {}
        if isinstance(pp_dict, str) and os.path.isfile(pp_dict):
            with open(pp_dict, "rb") as f:
                _pp_dict = tomli.load(f)

        _pl_dict = {}
        # Resolve poetry.lock source similarly
        if pl_dict is None:
            pl_dict = "./poetry.lock"
        else:
            _pl_dict = pl_dict if isinstance(pl_dict, dict) else {}
        if isinstance(pl_dict, str) and os.path.isfile(pl_dict):
            with open(pl_dict, "rb") as f:
                _pl_dict = tomli.load(f)

        # Extract the [tool.poetry] section; fall back to [project] if no name found
        _info: dict = jmespath.search("tool.poetry", _pp_dict)
        if "name" not in _info:
            _info.update(jmespath.search("project", _pp_dict))

        # Augment info with lock metadata (lock version + Python versions)
        _info["metadata"] = "lock-version: {}, python-versions: {}".format(
            AKPPInfo.ColorOut(
                jmespath.search('metadata."lock-version"', _pl_dict), fore_256="yellow"
            ),
            AKPPInfo.ColorOut(
                jmespath.search('metadata."python-versions"', _pl_dict),
                fore_256="yellow",
            ),
        )
        info = {}

        if not short_info:
            # Extract package names from the packages list
            _packages = [list(dict(p).values())[0] for p in _info["packages"]]

            # Collect main dependencies and dev/test dependencies
            _deps_list = AKPPInfo.Dependencies(_pp_dict, "dependencies", "green")
            _deps_dev_list = AKPPInfo.Dependencies(
                _pp_dict,
                [
                    "dev-dependencies",
                    "dev.dependencies",
                    "group.dev.dependencies",
                    "group.test.dependencies",
                ],
                "blue",
            )
            _dependencies = AKPPInfo.Table(_deps_list, _deps_dev_list)

            info.update(
                {
                    "name": AKPPInfo.ColorOut(_info["name"], fore_256="light_green"),
                    "version": AKPPInfo.ColorOut(
                        _info["version"], fore_256="light_blue"
                    ),
                    "description": AKPPInfo.ColorOut(
                        AKPPInfo.StrShort(_info["description"], 72),
                        fore_256="light_magenta",
                    ),
                    "authors": AKPPInfo.ColorOut(
                        "\n".join(AKPPInfo._PPValueParse(_info["authors"])),
                        fore_256="blue",
                    ),
                    "packages": "\n".join(_packages),
                    "metadata": _info["metadata"],
                }
            )
            if len(_dependencies) > 0:
                info.update({"dependencies": _dependencies})

        if len(info) > 0:
            return AKPPInfo.CreateTable(info, "")
        else:
            return ""

    @staticmethod
    def ColorOut(val, fore_256: str = "white"):
        """
        Wrap a value in ANSI color codes for terminal output.

        Args:
            val: The value to colorize.
            fore_256: Color name as recognized by the 'colored' library
                      (default 'white').

        Returns:
            The input wrapped with foreground and reset escape sequences.
        """
        return "{}{}{}".format(
            getattr(Fore, fore_256), str(val), getattr(Style, "reset")
        )

    @staticmethod
    def StrShort(input_str: str, char_length: int, ends: str = "..."):
        """
        Truncate a string to a given length, appending an ending marker.

        Args:
            input_str: The string to truncate.
            char_length: Maximum allowed length.
            ends: Suffix appended when truncated (default '...').

        Returns:
            The original string if short enough, otherwise truncated + ends.
        """
        if len(input_str) > char_length:
            return input_str[:char_length] + ends
        else:
            return input_str

    @staticmethod
    def Dependencies(
        pp_dict: dict, sections: str | list = "dependencies", col: str = "white"
    ) -> list:
        """
        Extract dependency list from pyproject.toml for given section(s).

        Supports traditional [tool.poetry.dependencies] as well as PEP 621
        [project.dependencies] layouts. Returns a list of [name, version_spec]
        pairs.

        Args:
            pp_dict: Parsed pyproject.toml dictionary.
            sections: One or more dot-separated section paths to search
                      (e.g. 'dependencies', 'group.dev.dependencies').
            col: Color name for the dependency names in output.

        Returns:
            List of [colorized_name, version_spec] entries.
        """
        if isinstance(sections, str):
            sections = [sections]
        _dl = []

        # Try traditional [tool.poetry.<section>] format first
        for section in sections:
            use = ["tool", "poetry"]
            use.extend(str(section).split("."))
            if AKPPInfo.AttrExists(pp_dict, dict, *use):
                _dlist = jmespath.search(".".join(use[:-1]), pp_dict)[use[-1:][0]]
                for k, v in _dlist.items():
                    _dl.append([AKPPInfo.ColorOut(k, fore_256=col), v])

        # Fall back to PEP 621 [project.dependencies] format
        if len(_dl) < 1:
            _dlist = jmespath.search("project.dependencies", pp_dict)
            if isinstance(_dlist, list):
                for d in _dlist:
                    # Extract package name (alphanumeric prefix) from spec string
                    _m = re.match("^[a-zA-Z]*", d)
                    if _m:
                        _s = _m.group()
                        _dl.append(
                            [
                                AKPPInfo.ColorOut(_s, fore_256=col),
                                str(d[len(_s) :]).strip(),
                            ]
                        )
        return _dl

    @staticmethod
    def Table(_deps_list: list, _deps_dev_list: list, as_table: bool = True):
        """
        Build a side-by-side ASCII table of regular and dev dependencies.

        Aligns the two dependency lists so that corresponding rows are
        displayed next to each other. Handles uneven list lengths by padding
        with empty cells.

        Args:
            _deps_list: List of [name, version] for production dependencies.
            _deps_dev_list: List of [name, version] for dev dependencies.
            as_table: If True, return the formatted table string; otherwise
                      return the raw list-of-lists.

        Returns:
            Formatted ASCII table string or raw tabular data.
        """
        tab = []

        if len(_deps_list) > 0 and len(_deps_dev_list) > 0:
            # Both lists present: build a 4-column header row
            tab = [
                [
                    AKPPInfo.ColorOut("deps", fore_256="light_green"),
                    "",
                    AKPPInfo.ColorOut("dev-deps", fore_256="light_blue"),
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
            # Only production dependencies
            tab = [["deps", ""]]
            i = 0
            for i in range(len(_deps_list)):
                tab.append(_deps_list[i])
                i += 1
        elif len(_deps_dev_list) > 0 and len(_deps_list) < 1:
            # Only dev dependencies
            tab = [["dev-deps", ""]]
            i = 0
            for i in range(len(_deps_dev_list)):
                tab.append(_deps_dev_list[i])
                i += 1

        if as_table and len(tab) > 0:
            table = AsciiTable(table_data=tab)
            return table.table
        else:
            return tab

    @staticmethod
    def CreateTable(entries: dict, title: str = "", heading_border: bool = True):
        """
        Render a dictionary as a two-column ASCII table (key / value).

        Wraps terminaltables.AsciiTable for consistent project display.

        Args:
            entries: Dictionary where keys become the left column and values
                     become the right column.
            title: Optional table title.
            heading_border: Whether to show the heading separator line.

        Returns:
            Formatted ASCII table string.
        """
        tab = []
        for k, v in entries.items():
            tab.append([str(k).upper(), v])
        table = AsciiTable(table_data=tab, title=title)
        table.inner_heading_row_border = heading_border
        return table.table

    @staticmethod
    def AttrExists(obj_dct, should_type, *keys):
        """
        Safely check for the existence of a nested key path in a dictionary,
        optionally verifying the final value's type.

        Traverses the dictionary following the key order. Returns False if
        any intermediate key is missing or is not a dict.

        Args:
            obj_dct: The dictionary to traverse.
            should_type: Expected type of the final value, or None/falsy to
                         skip type checking.
            *keys: Sequence of keys forming the path (e.g. 'tool', 'poetry',
                   'dependencies').

        Returns:
            True if the path exists and the final value matches should_type
            (if specified), otherwise False.
        """
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

    @staticmethod
    def _PPValueParse(items: list, *keys):
        """
        Parse and format values from pyproject.toml list entries.

        Handles three cases:
          - Dict with only 'name' and 'email' -> formatted as "Name <email>"
          - Other dicts -> extract values by provided keys
          - Strings -> passed through as-is

        Args:
            items: List of dicts and/or strings (e.g. authors, maintainers).
            *keys: Optional keys to extract from non-standard dict entries.

        Returns:
            List of formatted string representations.
        """
        ret = []
        for i in items:
            if isinstance(i, dict):
                if "name" in i and "email" in i and len(i) == 2:
                    ret.append("{} <{}>".format(i["name"], i["email"]))
                else:
                    _s = []
                    for k in keys:
                        if k in i:
                            _s.append(i[k])
                    ret.extend(_s)
            elif isinstance(i, str):
                ret.append(i)
        return ret
