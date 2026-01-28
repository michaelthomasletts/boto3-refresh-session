## Requirements

- Python >= 3.10
- Local development requires `uv`. Installation instructions can be found [here](https://docs.astral.sh/uv/getting-started/installation/).
- Development dependencies can be installed by running `pip install boto3-refresh-session[dev,iot]`

## Documentation

boto3-refresh-session employs a consistent docstring standard and online documentation. Adding and editing methods and classes generally requires edits to docstrings and online documentation. The following information should help you add and edit docstrings and online documentation.

- boto3-refresh-session uses [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html) for docstrings.
- The [official documentation](https://michaelthomasletts.com/boto3-refresh-session/) is generated using `sphinx` and `pydata-sphinx-theme`.
- Documentation configurations can be found in `doc/conf.py`.  
- `autosummary_generate` is **deliberately** deactivated in `doc/conf.py`! RST files are customarily written *manually* in this project; this provides granular control over resultant documentation.
- Verify your documentation edits *before* opening a pull request. To do this, run `cd doc && make clean && make html`. Navigate to `doc/_build/html` and open `index.html` to check the documentation locally from your internet browser.
- A great deal of care goes into the documentation for boto3-refresh-session. Ensure your writing is coherent, concise, and helpful for an audience ranging from novices to experts.

## Local Development

- Ensure your changes include unit tests (with mocks, etc as necessary). Integration tests are also fine.
- `pre-commit` runs a [variety of checks](https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/.pre-commit-config.yaml) automatically.
- Include the version part parameter (i.e. [major | minor | patch]) to the beginning of your pull request title so that the version is bumped correctly.