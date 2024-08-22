#!/usr/bin/env bash

poetry install --no-cache --only main
poetry run pytest
poetry build
pip install --upgrade dist/pp_check-$(poetry version -s)-py3-none-any.whl
