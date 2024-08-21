#!/usr/bin/env bash

poetry install
poetry run pytest
poetry build
pip install --upgrade --force-reinstall dist/pp_check-$(poetry version -s)-py3-none-any.whl
