# pp-check

This tool is used exclusively for Poetry projects. As soon as you have a poetry project in front of you in the console, you can use this tool to quickly find out which script commands the poetry project contains.

## requirements

poetry version >=1.83, python version >= 3.10

## install

```
poetry update
poetry install
```

## execute as poetry command

```
poetry run ppcheck .
```

## install as cli command

```
sh ./cli_install_bash.sh
```

## execute as cli command

```
ppcheck .
```

## poetry run help

```
poetry run ppcheck --help
Usage: ppcheck [OPTIONS] CHECK_POETRY_PATH

  This tool is used exclusively for Poetry projects. As soon as you have a
  poetry project in front of you in the console, you can use this tool to
  quickly find out which script commands the poetry project contains.

  usage: set path of poetry project, eg.

  $ poetry run ppcheck ~/poetry-project

Options:
  --help  Show this message and exit.
```

## screenshots

| MacOSX    | <img src="res/mac.png"> |
|---------------|:------------------------|
| Windows    | <img src="res/win.png"> |
