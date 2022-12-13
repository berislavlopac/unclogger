Contributing Guidelines
=========

## Development Environment

[Poetry](https://python-poetry.org) is used for dependency and package management. The steps for setting up the development environment:

1. Install Poetry: either [globally](https://python-poetry.org/docs/#installation), or in a Python virtual environment (using `pip install poetry`).

3. Install the project (if outside a virtual environment, Poetry will create one):

        $ poetry install


### Development Checks

During development, a number of checks and tests can be executed on the library codebase:

```shell
$ pylint unclogger/                                  # code linting
$ mypy --install-types --non-interactive unclogger/  # Python typing analysis
$ black --check .                                    # Python code formatting
$ isort --check .                                    # Import statement optimisation
$ pydocstyle unclogger/                              # styling and completeness of docstrings  
```

Unit tests can be executed using:

```shell
$ pytest --cov --spec
```

The indicated options add extra details to the report:

* `--cov` adds a test coverage report
* `--spec` formats the test report as a list of spec statementss


## API Documentation

The project documentation can be served locally by running:

```shell
$ mkdocs serve
```

To build the static documentation site, run:

```shell
$ mkdocs build
```

This will create the HTML documentation in the `site` directory.
