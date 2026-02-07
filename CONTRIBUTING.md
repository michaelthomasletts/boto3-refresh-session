# boto3-refresh-session

<div align="left">

  <a href="https://pypi.org/project/boto3-refresh-session/">
    <img 
      src="https://img.shields.io/pypi/v/boto3-refresh-session?color=%23FF0000FF&logo=python&label=Latest%20Version"
      alt="pypi_version"
    />
  </a>

  <a href="https://pypi.org/project/boto3-refresh-session/">
    <img 
      src="https://img.shields.io/pypi/pyversions/boto3-refresh-session?style=pypi&color=%23FF0000FF&logo=python&label=Compatible%20Python%20Versions" 
      alt="py_version"
    />
  </a>

  <a href="https://michaelthomasletts.github.io/boto3-refresh-session/index.html">
    <img 
      src="https://img.shields.io/badge/Official%20Documentation-📘-FF0000?style=flat&labelColor=555&logo=readthedocs" 
      alt="documentation"
    />
  </a>

  <a href="https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/LICENSE">
    <img 
      src="https://img.shields.io/static/v1?label=License&message=MPL-2.0&color=FF0000&labelColor=555&logo=github&style=flat"
      alt="license"
    />
  </a>

</div>

</br>

## Requirements

- Python >= 3.10
- Local development requires `uv`. Installation instructions can be found [here](https://docs.astral.sh/uv/getting-started/installation/).
- Development dependencies are managed via `uv` and `uv.lock` (see quickstart below).

## Quickstart

```bash
# create/update the local venv with dev + iot extras
uv sync --extra dev --extra iot

# install git hooks (optional but recommended)
uv run pre-commit install

# run tests
uv run pytest -v

# lint and format checks
uv run ruff check .
uv run ruff format --check .
```

## Documentation

boto3-refresh-session employs a consistent docstring standard and online documentation. Adding and editing methods and classes generally requires edits to docstrings and online documentation. The following information should help you add and edit docstrings and online documentation.

- boto3-refresh-session uses [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html) for docstrings.
- boto3-refresh-session also employs `.pyi` files to improve the typing experience. Evaluate whether `.pyi` additions or edits are necessary for your changes.
- The [official documentation](https://michaelthomasletts.com/boto3-refresh-session/) is generated using `sphinx` and `pydata-sphinx-theme`.
- Documentation configurations can be found in `docs/conf.py`.  
- `autosummary_generate` is **deliberately** deactivated in `docs/conf.py`! RST files are customarily written *manually* in this project; this provides granular control over resultant documentation.
- Verify your documentation edits *before* opening a pull request. To do this, run `uv run bash -lc "cd docs && make clean && make html"`. Navigate to `docs/_build/html` and open `index.html` to check the documentation locally from your internet browser.
- A great deal of care goes into the documentation for boto3-refresh-session. Ensure your writing is coherent, concise, and helpful for an audience ranging from novices to experts.

## Local Development

- Ensure your changes include unit tests (with mocks, etc as necessary). Integration tests are also fine.
- `pre-commit` runs a [variety of checks](https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/.pre-commit-config.yaml) automatically.
- Include the version part parameter (i.e. [major | minor | patch]) in your pull request title so that the version is bumped correctly.

## Support and Issues

- For bugs, please open a GitHub Issue with steps to reproduce, expected behavior, and actual behavior.
- For questions or usage help, open a GitHub Discussion or Issue with a minimal example.
- For security issues, please avoid public issues and contact the maintainer directly.
