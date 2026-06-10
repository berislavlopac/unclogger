# AGENTS.md

Guidance for AI agents (and humans) working on **unclogger**. Complements
`README.md` and the docs under `docs/`. This file is about *how to work in this
repo* — conventions, commands, and the public contract that must not break.

## What this is

unclogger is a small library for customisable **structured logging** — a thin
wrapper over [`structlog`](https://www.structlog.org) that mirrors the standard
`logging` API but emits a JSON object per line, with any keyword arguments folded
into the log context alongside `event`, `logger`, `level`, and `timestamp`.

It is a **library**, not an application: it is imported by other projects. Treat
the public API as a contract (see below) — changing it ripples into every
dependant, so it changes only deliberately and with a release note.

## Layout

- `unclogger/__init__.py` — the public surface (re-exports).
- `unclogger/logger.py` — `structlog.configure(...)` runs here at import time;
  defines the `Unclogger` class, `get_logger`, `set_level`, and the
  `context_bind` / `context_clear` global-context helpers.
- `unclogger/processors.py` — the custom-processor registry: `CUSTOM_PROCESSORS`,
  `add_processors(...)`, and `run_custom_processors` (already wired into the
  structlog chain, before the JSON renderer).
- `unclogger/defaults.py` — `json_default`, a `singledispatch` JSON serialiser for
  `UUID` / `datetime` / `date` / `Decimal`.
- `tests/` — pytest suite. `docs/` — mkdocs source. `release-notes/` — per-version notes.

## Public API (the contract)

Exported from `unclogger`: `get_logger`, `context_bind`, `context_clear`,
`set_level`, `add_processors`, `Unclogger`. Keep these stable. Anything else is
internal and may change. Update `docs/reference.md` and add a `release-notes/`
entry when the public API changes.

## Environment & workflow

- **Python ≥ 3.10** (`requires-python = ">=3.10,<4.0"`). The only runtime
  dependency is `structlog`.
- **[`uv`](https://docs.astral.sh/uv/)** for environments and dependencies;
  **[`just`](https://just.systems/)** as the task runner. Run `just` for the list.
- **Always use the `just` recipe** rather than calling the tool directly — the
  recipes encode the right flags.

| Recipe | Purpose |
|---|---|
| `just test` | Unit tests (`pytest --spec`). |
| `just test-cov` | Tests with coverage (floor is **90%**). |
| `just lint` | `deptry` + `ruff format --check` + `ruff check` + `pydocstyle`. |
| `just type` | `mypy` over `unclogger/`. |
| `just analyze` | `vulture` (dead code) + `radon` (maintainability). |
| `just check` | `lint` + `type` + `analyze` — the pre-push gate. |
| `just reformat` | Auto-fix format + import order (`[confirm]` recipe). |
| `just docs` / `just docs-build` | Serve / build the mkdocs site. |
| `just commits` | Commits since the last tag (for release notes). |

Multi-version testing (py310–313) is via **tox** (`tox.ini`, `uv-venv-lock-runner`).
The pre-push quality gate is `just check` + `just test`, or the full `tox` matrix.
CI is **GitHub Actions** (`.github/workflows/ci.yml`): on push to `main` and on
PRs it runs the `checks` env and the py310–313 test matrix via
`uvx --with tox-uv tox` — the same tox envs you run locally.

## Conventions

- **Type checker is `mypy`** (not pyright/ty). `mypy_path = unclogger/`.
- **`ruff` is linter + formatter**, line length **96**. The lint `select` set in
  `pyproject.toml` is the contract; don't disable rules without a `# noqa: <code>`
  and a reason. Note `F841` is delegated to `vulture` (the `external` list).
- **Docstrings: Google convention** (enforced by `pydocstyle`; `D105/D107/D212/D401`
  are ignored). Markdown in docstrings, single backticks for inline code.
- Keep the dependency surface minimal — this is a foundational library.
- Mark intentionally-unused names with `# noqa: F841` (so vulture ignores them),
  not by underscore-prefixing.
- ASCII-only in code (identifiers, strings, comments). Typographic characters
  (em-dashes, smart quotes) belong in docs and prose, not in code.

## Working conventions

- Small, focused commits. Lowercase imperative subject; optional body explaining
  the *why*, not the *what*.
- **No `Co-Authored-By` footer.**
- Branch names use only `-` as a separator, never `/`.
- On a long-running WIP branch, commit locally; don't push every commit (it
  spams CI and notifications).
- Keep PR descriptions scoped to the change - no "future work" / "next steps"
  section.
- Finish PR work with a neutral-reviewer pass over your own diff.
- Review comments detach on force-push/rebase - warn before rewriting history on
  a PR that already has feedback; prefer a merge.
- Stay on the task at hand - note an incidental or unrelated issue in one line
  and move on, rather than rabbit-holing into it.

## Docs

Docs live in `docs/` (mkdocs + MaterialX + `mkapi`), hosted on readthedocs.
`docs/reference.md` autogenerates the API reference from docstrings via `mkapi`
`:::` directives, so keep docstrings accurate. The `sanitary` library is used as
the worked example for custom processors — keep that example in sync if the
processor API changes.

## Related

`sanitary` (the structlog redaction processor shown in the docs) is a sibling
project by the same author; the two are designed to work together via
`add_processors(StructlogSanitizer(...))`.