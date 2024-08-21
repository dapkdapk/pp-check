poetry install
poetry run pytest
poetry build

@poetry version -s > tmpFile
@set /p myver= < tmpFile
@del tmpFile

pip install --upgrade --force-reinstall dist/pp_check-%myver%-py3-none-any.whl
