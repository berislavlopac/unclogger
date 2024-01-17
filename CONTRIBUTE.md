Contributing Guidelines
=========

## Development Environment

[PDM](https://pdm-project.org) is used for dependency and package management. The steps for setting up the development environment:

1. Install PDM: either [globally](https://pdm-project.org/latest/#recommended-installation-method), or in a Python virtual environment (using `pip install pdm`).

3. Install the project (if outside a virtual environment, PDM will create one):

        $ pdm install


### Development Checks

During development, the command `pdm run checks` will execute a number of checks and tests on the library codebase:

* code linting check using `ruff`
* code format check using `black`
* import statement sorting check using `isort`
* documentation styling check using `pydocstyle`

The full unit test suite can be executed with `pdm run tests`.


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

The online documentation is built and hosted on ReadTheDocs, and configured in the `.readthedocs.yaml` file. The requirements file used for ReadTheDocs builds is located at `docs/requirements.txt`; to update it using Poetry run the following command:

```shell
$ poetry export -o docs/requirements.txt --with=docs --without-hashes --without-urls
```
