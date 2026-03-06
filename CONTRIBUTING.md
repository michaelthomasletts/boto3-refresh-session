## Development Prerequisites

- Python 3.10+ (CI currently runs on Python 3.10)
- `uv`
- `git`

## Local Setup

1. Clone the repository and move into it.
2. Install project and development dependencies:

```bash
uv sync --all-groups
```

3. Install pre-commit hooks:

```bash
uv run pre-commit install
uv run pre-commit install-hooks
```

## Repository Layout

- `boto3_refresh_session/`: package source code
- `tests/`: unit tests
- `docs/`: Sphinx documentation
- `.github/workflows/`: CI/CD pipelines

## Development Workflow

1. Create a branch from `main`.
2. Make your changes with tests.
3. Run local checks before opening a PR.
4. Open a PR using the repository template.

## Run Quality Checks Locally

Run the same checks used in CI:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest tests/ -v
```

To run the full pre-commit suite:

```bash
uv run pre-commit run --all-files
```

## Testing Guidance

- Add or update tests in `tests/` for behavioral changes.
- Keep tests focused on observable behavior and error handling.
- Prefer small, isolated tests over broad integration-style tests for core logic.

## Documentation Guidance

Documentation is built with Sphinx (`docs/`) using `numpydoc`.

- Update docs when behavior or public APIs change.
- Add or update docstrings for public classes, methods, and functions.
- Keep examples aligned between `README.md` and docs pages.

Build docs locally from the repository root:

```bash
uv run --directory docs make clean html
```

Generated HTML will be in `docs/_build/html/`.

## Pull Request Requirements

- PR titles must follow Conventional Commits:
  - Format: `type(scope)!: summary`
  - Allowed types: `feat`, `fix`, `perf`, `refactor`, `docs`, `style`, `test`, `build`, `ci`, `chore`, `revert`
- Ensure formatting, lint, and tests pass locally before opening or updating a PR.
- Include test coverage for code changes.
- Include docs updates for user-facing changes.

## Release Notes and Versioning

Releases are automated with Release Please.

- Do not manually edit the package version for normal contributions.
- Do not manually maintain `CHANGELOG.md` unless a maintainer asks for it.
- Conventional Commit types influence release bump behavior.

## Licensing

By contributing, you agree that your contributions are provided under the repository license (MPL-2.0).
