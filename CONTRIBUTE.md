Contributing Guidelines
=========

## Development Environment

To manage packaging and dependencies, please [install `uv` first](https://docs.astral.sh/uv/getting-started/installation/).

To run development scripts, please [install `just`](https://just.systems/man/en/). To display the list of all `just` commands (a.k.a. recipes), run `just`:

```shell
$ just
Available recipes:
    help                                # List available recipes.
    test                                # Run unit tests.
    test-cov                            # Run unit tests with coverage report.
    lint                                # Run linting and formatting checks.
    type                                # Run static typing analysis.
    analyze                             # Run dead-code and maintainability analysis.
    check                               # Run all checks.
    commits                             # Extract the latest commits
    reformat                            # Reformat the code and sort imports using ruff.
    docs                                # Serve documentation website for development purposes.
    docs-build                          # Build the documentation website.
    reqs                                # Extract current production requirements. Save to a file by appending `> requirements.txt`.
    news type id=('+' + datetime('%s')) # Add a news fragment: `just news added` (auto id) or `just news fixed 42` (issue ref).
    changelog-draft version             # Preview the collated changelog for a version without writing it.
    suggest-version                     # Suggest the next version from the pending news fragments (advisory).
    release version                     # Validate, collate the changelog, commit, tag, and push a release (see CONTRIBUTE.md).
```


### Development Checks

During development, the command `just check` will execute a number of checks and tests on the library codebase:

* correct dependency declarations using `deptry`
* code linting check using `ruff`
* code format check using `ruff format`
* documentation styling check using `pydocstyle`

The full unit test suite can be executed with `just test`.


## Changelog and news fragments

Don't edit `CHANGELOG.md` directly. Each change adds one file to `release-notes/`,
named `<id>.<type>.md`, containing a one-line description. `<type>` is the change
category — `breaking`, `added`, `changed`, `deprecated`, `removed`, `fixed`,
`security` (see `release-notes/README.md` for what each means and how it maps to a
version bump). `<id>` defaults to a unique timestamp (no reference); pass a PR/issue
number to render a `(#42)` reference instead.

```shell
$ just news added           # -> release-notes/+<timestamp>.added.md (no reference)
$ just news fixed 42        # -> release-notes/42.fixed.md (renders "(#42)")
```

Preview how the collated changelog will look for a given version, and get a
recommended version derived from the pending fragments:

```shell
$ just changelog-draft 0.3.0
$ just suggest-version       # e.g. "0.2.1 -> 0.2.2  (patch: fixed)"
```

`towncrier` folds the fragments into a dated `CHANGELOG.md` section at release time
(see below). The date is stamped automatically when the release is cut, so
fragments never carry a date — you don't need to know the release date in advance.

## Releasing

The release version lives in **exactly one place: the git tag**. `pyproject.toml`
declares the version as `dynamic` and `hatch-vcs` derives it from the tag at build
time, so there is no version number to bump by hand.

To cut a release, state the version once:

```shell
$ just release 0.3.0
```

This recipe:

1. Runs `just check` and `just test` first. If anything fails it aborts here, so a
   broken tree produces no changelog, commit, or tag.
2. Runs `towncrier build` to collate the news fragments into a new
   `## [0.3.0] - <today>` section in `CHANGELOG.md` and delete the fragments.
3. Commits the changelog, creates the `0.3.0` tag, and pushes the commit and tag.

Pushing the tag triggers the GitHub Actions workflow, which runs the checks and the
full test matrix and — **only if they pass** — builds the package, publishes it to
PyPI, and creates the GitHub release (notes are extracted from the new changelog
section). Ordinary pushes without a tag only run the checks and tests; they never
publish. Prereleases (e.g. `0.3.0rc1`) are detected automatically and marked as such
on GitHub.

> Because the tag is created locally before CI runs, a CI failure leaves a tag that
> published nothing. To redo the release, delete the tag and try again:
>
> ```shell
> $ git push --delete origin 0.3.0 && git tag -d 0.3.0
> ```

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
