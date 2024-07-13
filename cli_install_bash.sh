#!/usr/bin/env bash

poetry install
poetry build
if [[ $(pip list | grep 'pp-check') == *fotosort* ]]; then
  pip uninstall pp-check -y
fi
pip install dist/pp_check-$(poetry version -s)-py3-none-any.whl