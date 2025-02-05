import os
import re

import jmespath
import tomli
from colored import Fore, Style
from terminaltables import AsciiTable


class AKPPInfo:
    @staticmethod
    def GetInfo(
        pp_dict: dict | str | None = None,
        pl_dict: dict | str | None = None,
        short_info: bool = False,
    ):
        _pp_dict = {}
        if pp_dict is None:
            pp_dict = "./pyproject.toml"
        else:
            _pp_dict = pp_dict if isinstance(pp_dict, dict) else {}
        if isinstance(pp_dict, str) and os.path.isfile(pp_dict):
            with open(pp_dict, "rb") as f:
                _pp_dict = tomli.load(f)
        _pl_dict = {}
        if pl_dict is None:
            pl_dict = "./poetry.lock"
        else:
            _pl_dict = pl_dict if isinstance(pl_dict, dict) else {}
        if isinstance(pl_dict, str) and os.path.isfile(pl_dict):
            with open(pl_dict, "rb") as f:
                _pl_dict = tomli.load(f)

        _info: dict = jmespath.search("tool.poetry", _pp_dict)
        if "name" not in _info:
            _info.update(jmespath.search("project", _pp_dict))
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
            _packages = [list(dict(p).values())[0] for p in _info["packages"]]
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
        return "{}{}{}".format(
            getattr(Fore, fore_256), str(val), getattr(Style, "reset")
        )

    @staticmethod
    def StrShort(input_str: str, char_length: int, ends: str = "..."):
        if len(input_str) > char_length:
            return input_str[:char_length] + ends
        else:
            return input_str

    @staticmethod
    def Dependencies(
        pp_dict: dict, sections: str | list = "dependencies", col: str = "white"
    ) -> list:
        if isinstance(sections, str):
            sections = [sections]
        _dl = []
        for section in sections:
            use = ["tool", "poetry"]
            use.extend(str(section).split("."))
            if AKPPInfo.AttrExists(pp_dict, dict, *use):
                _dlist = jmespath.search(".".join(use[:-1]), pp_dict)[use[-1:][0]]
                for k, v in _dlist.items():
                    _dl.append([AKPPInfo.ColorOut(k, fore_256=col), v])
        if len(_dl) < 1:
            _dlist = jmespath.search("project.dependencies", pp_dict)
            if isinstance(_dlist, list):
                for d in _dlist:
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
        tab = []
        if len(_deps_list) > 0 and len(_deps_dev_list) > 0:
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
            tab = [["deps", ""]]
            i = 0
            for i in range(len(_deps_list)):
                tab.append(_deps_list[i])
                i += 1
        elif len(_deps_dev_list) > 0 and len(_deps_list) < 1:
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
        check: https://robpol86.github.io/terminaltables/
        """
        tab = []
        for k, v in entries.items():
            tab.append([str(k).upper(), v])
        table = AsciiTable(table_data=tab, title=title)
        table.inner_heading_row_border = heading_border
        return table.table

    @staticmethod
    def AttrExists(obj_dct, should_type, *keys):
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
