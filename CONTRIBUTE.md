Contributing Guidelines
=========

## Development Environment

To manage packaging and dependencies, please [install `uv` first](https://docs.astral.sh/uv/getting-started/installation/).

Tu run development scripts, please [install `just`](https://just.systems/man/en/). To display the list of all `just` commands (a.k.a. recipes), run `just`:

```shell
$ just
Available recipes:
    help       # List available recipes.
    test       # Run unit tests.
    test-cov   # Run unit tests with coverage report.
    lint       # Run linting and formating checks.
    type       # Run static typing analysis.
    analyze    # Run security checks.
    check      # Run all checks.
    commits    # Extract the latest commits
    reformat   # Reformat the code using isort and ruff.
    docs       # Serve documentation website for development purposes.
    docs-build # Build the documentation website.
    reqs       # Extract current production requirements. Save to a file by appending `> requirements.txt`.
```


### Development Checks

During development, the command `just check` will execute a number of checks and tests on the library codebase:

* correct dependency declarations using `deptry`
* code linting check using `ruff`
* code format check using `ruff format`
* documentation styling check using `pydocstyle`

The full unit test suite can be executed with `just test`.


## API Documentation

The project documentation can then be served locally by running:

```shell
$ just docs
```

To build the static documentation site, run:

```shell
$ just docs-build
```

This will create the HTML documentation in the `site` directory.
