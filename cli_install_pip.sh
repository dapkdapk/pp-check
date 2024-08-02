#!/usr/bin/env bash

pip list | awk '{print $1}' | grep pp-check | xargs pip uninstall -y
poetry install
poetry run pytest
poetry build
pip install dist/pp_check-$(poetry version -s)-py3-none-any.whl