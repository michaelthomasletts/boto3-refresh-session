import importlib
import inspect
import os
import sys
from datetime import date
from pathlib import Path

import tomlkit

# fetching pyproject.toml
path = Path("../pyproject.toml")

with path.open("r", encoding="utf-8") as f:
    pyproject = tomlkit.parse(f.read())

# adding project root and docs source to path
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

# sphinx config
language = "en"
project = str(pyproject["project"]["name"])  # type: ignore
author = str(pyproject["project"]["maintainers"][0]["name"])  # type: ignore
copyright = f"{date.today().year}, {author}"
release = str(pyproject["project"]["version"])  # type: ignore
source_encoding = "utf-8"
source_suffix = ".rst"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "numpydoc",
    "sphinx_copybutton",
    "sphinxext.opengraph",
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# html config
html_logo = "_static/favicon.ico"
html_favicon = html_logo
html_theme = "furo"
html_static_path = ["_static"]
html_file_suffix = ".html"
htmlhelp_basename = project
html_baseurl = str(pyproject["project"]["urls"]["Documentation"]).rstrip("/")  # type: ignore
repository_url = str(pyproject["project"]["urls"]["Repository"]).rstrip("/")  # type: ignore
repository_branch = "main"
repository_root = Path(__file__).resolve().parent.parent
html_favicon = "_static/favicon.ico"
html_theme_options = {
    "top_of_page_buttons": ["view"],
    "source_view_link": repository_url,
}

# opengraph config
ogp_site_url = html_baseurl
ogp_image = "_static/og.png"
ogp_description_length = 100
ogp_description = str(pyproject["project"]["description"]).rstrip("/")  # type: ignore

# autosummary config
autosummary_generate = True

# autodoc config
autodoc_default_options = {
    "members": True,
    "member-order": "alphabetical",
    "exclude-members": "__init__,__new__",
    "inherited-members": True,
}
autodoc_class_signature = "separated"
autodoc_inherit_docstrings = True

# numpydoc config
numpydoc_show_class_members = False
numpydoc_show_inherited_class_members = False
numpydoc_attributes_as_param_list = False
numpydoc_class_members_toctree = False

# napoleon config
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False

# intersphinx
intersphinx_mapping = {
    "boto3": (
        "https://boto3.amazonaws.com/v1/documentation/api/latest/",
        None,
    ),
    "boto3_client_cache": (
        "https://61418.io/boto3-client-cache/",
        (
            "https://61418.io/boto3-client-cache/objects.inv",
            "https://61418.io/boto3-client-cache/reference/objects.inv",
        ),
    ),
    "python": ("https://docs.python.org/3", None),
}
extlinks = {
    "botocore": (
        "https://botocore.amazonaws.com/v1/documentation/api/latest/%s",
        "",
    ),
}


def linkcode_resolve(domain, info) -> str | None:
    """Resolves 'source' link in documentation."""

    if domain != "py":
        return None
    module_name = info.get("module")
    if not module_name:
        return None

    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return None

    obj = module
    fullname = info.get("fullname")
    if fullname:
        for part in fullname.split("."):
            obj = getattr(obj, part, None)
            if obj is None:
                break

    try:
        if obj is not None:
            obj = inspect.unwrap(obj)  # type: ignore
            source_file = inspect.getsourcefile(obj)
            source_lines, start_line = inspect.getsourcelines(obj)
            end_line = start_line + len(source_lines) - 1
        else:
            source_file = None
            start_line = None
            end_line = None
    except (OSError, TypeError):
        source_file = None
        start_line = None
        end_line = None

    if source_file is None:
        source_file = inspect.getsourcefile(module)
        if source_file is None:
            return None

    try:
        relative_path = (
            Path(source_file).resolve().relative_to(repository_root)
        )
    except ValueError:
        relative_path = Path(*module_name.split(".")).with_suffix(".py")

    url = (
        f"{repository_url}/blob/{repository_branch}/{relative_path.as_posix()}"
    )
    if start_line is not None and end_line is not None:
        return f"{url}#L{start_line}-L{end_line}"

    return url
