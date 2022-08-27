# Pyetta

[![Documentation Status](https://readthedocs.org/projects/pyetta/badge/?version=latest)](https://pyetta.readthedocs.io/en/latest/)
[![Discord](https://img.shields.io/discord/1005420113194930309?color=C5F0A4)](https://discord.gg/4cmv4vrmYC)
[![codecov](https://codecov.io/gh/kenkaijie/pyetta/branch/master/graph/badge.svg?token=7PFFKAUR25)](https://codecov.io/gh/kenkaijie/pyetta)

`pyetta` is a multi-tool made to simplify device on target testing workflows by
providing some helpers which modularise the process of on target testing. It
provides both a CLI for simple use cases, and a library of components that can
simplify creation of test scripts.

# Project Structure

The project is structured as follows.

```text
root
|---.github: Github specific CI/CD actions
|
|---docs: Documentation for this project
|
|---examples: Examples relating to plugin development.
|
|---pyetta: Project sources
|
|---test: Test directory for project. 
```

# Project Environment

The project python dependencies can be obtained by using pip to install them.
Ensure the `[dev]` extras is installed in order to perform common developer
actions such as testing or building docs.

## Building

The command below will install all the dependencies and the project itself into
the standard python locations for your platform.

```shell
$ pip install .[dev]
```

If only the dependencies are needed, you can subsequently call an uninstall to
the pyetta package.

```shell
$ pip uninstall --yes pyetta
```

## Linting and Analysis

Linting and static analysis is done using `flake8`. The command below can be
used to run the linter.

```shell
$ flake8 
```

## Tests and Coverage

Tests for this project use `tox` with `pytest` and `flake8` to operate. You can 
check linting, run unit tests, and generate coverage by running the following 
command.

```shell
$ tox
```

The command is optimised for automated testing, so the output may not be 
suitable for interpretation by developers.

### Local Testing

As the `tox` call is used for final testing and preparing a branch for 
submission it is the recommended way to do preliminary testing on the 
development machine as well. If not all the python environments are 
available on your development machine, you can filter them out with the 
`-e ENV` option to tox.

For example, if you have python 3.8 and 3.9 on your development machine, you 
would call the command to only run tox with these platforms.

```shell
$ tox -e py38,py39
```

If you do not wish to use `tox`, the individual actions from `tox.ini` can 
be inspected and run individually. This gives the best control and allows 
custom reports to be generated (like html coverage).

## Documentation

Documentation for this project is located in the `docs` folder. It uses
`sphinx` to build out all documentation (except this readme).

```shell
$ sphinx-build docs dist/docs
```

Running the command above will generate the documentation for this project and
save it to a folder `dist/docs`.

## Packaging

Packing is done using python's build command. The command below will build the
package for deployment to a python package repository.

```shell
$ python -m build
```
