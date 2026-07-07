"""
Constants for common Poetry CLI commands used throughout the application.

Provides an enum that centralizes frequently invoked Poetry commands,
avoiding hardcoded strings scattered across the codebase.
"""

from enum import Enum


class EPoetryCmds(Enum):
    """
    Enum of commonly used Poetry commands.

    Each member maps a descriptive name to its corresponding shell command.
    """

    UPDATE = "poetry update"  # Update dependencies
    LOCK = "poetry lock"  # Regenerate poetry.lock
    INSTALL = "poetry install"  # Install project dependencies
    SHOW_TREE = "poetry show --tree"  # Display dependency tree
    PYTEST = "poetry run pytest"  # Run tests via pytest
    CACHE = "poetry cache clear --all ."  # Clear Poetry cache
    CONFIG = "poetry config --list"  # Show Poetry configuration
    INIT = "poetry init"  # Initialize a new pyproject.toml
    BLACK = "poetry run black ."  # Format code with Black
    ISORT = "poetry run isort ."  # Sort imports with isort
