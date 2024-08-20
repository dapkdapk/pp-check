from enum import Enum


class EPoetryCmds(Enum):
    UPDATE = "poetry update"
    LOCK = "poetry lock"
    INSTALL = "poetry install"
    SHOW_TREE = "poetry show --tree"
    PYTEST = "poetry run pytest"
