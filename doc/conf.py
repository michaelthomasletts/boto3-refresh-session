import os
import sys
from datetime import date
from pathlib import Path

import tomlkit

# fetching pyproject.toml
path = Path("../pyproject.toml")

with path.open("r", encoding="utf-8") as f:
    pyproject = tomlkit.parse(f.read())

# sphinx config
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))
extensions = [
    "sphinx.ext.autodoc",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.linkcode",
    "sphinx.ext.extlinks",
]
language = "en"
project = str(pyproject["project"]["name"])
author = "Michael Letts"
copyright = f"{date.today().year}, {author}"
release = str(pyproject["project"]["version"])
source_encoding = "utf-8"
source_suffix = ".rst"
pygments_style = "sphinx"
add_function_parentheses = False
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "tests/"]
html_logo = "brs.png"
html_favicon = html_logo
html_title = project
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_file_suffix = ".html"
html_sidebars = {
    "index": [],
    "usage": [],
    "authorization": [],
    "contributing": [],
    "raison": [],
    "qanda": [],
    "installation": [],
    "modules/**": ["sidebar-nav-bs.html", "search-field.html"],
}
html_context = {
    "default_mode": "dark",
}
htmlhelp_basename = project
html_css_files = ["custom.css"]
html_theme_options = {
    "collapse_navigation": True,
    "navbar_end": [
        "search-button",
        "navbar-icon-links.html",
    ],
    "icon_links": [
        {
            "name": "GitHub",
            "url": f"https://github.com/michaelthomasletts/{project}",
            "icon": "fab fa-github-square",
            "type": "fontawesome",
        },
        {
            "name": "PyPI",
            "url": f"https://pypi.org/project/{project}/",
            "icon": "fab fa-python",
            "type": "fontawesome",
        },
    ],
}

# autodoc config
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "exclude-members": "__init__,__new__",
    "inherited-members": True,
}
autodoc_typehints = "signature"
autodoc_inherit_docstrings = True

# numpydoc config
numpydoc_show_class_members = False
numpydoc_show_inherited_class_members = False
numpydoc_attributes_as_param_list = False
numpydoc_class_members_toctree = False

# napoleon config
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False

# autosummary
autosummary_generate = False

# intersphinx
intersphinx_mapping = {
    "boto3": (
        "https://boto3.amazonaws.com/v1/documentation/api/latest/",
        None,
    ),
}
extlinks = {
    "botocore": (
        "https://botocore.amazonaws.com/v1/documentation/api/latest/%s",
        "",
    ),
}


def linkcode_resolve(domain, info):
    """Resolves 'source' link in documentation."""

    if domain != "py":
        return None
    if not info["module"]:
        return None

    filename = info["module"].replace(".", "/")
    result = (
        f"https://github.com/michaelthomasletts/{project}/blob/main/"
        f"{filename}.py"
    )
    return result
