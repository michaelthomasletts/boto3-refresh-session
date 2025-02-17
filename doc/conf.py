import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))

extensions = [
    "sphinx.ext.autodoc",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.linkcode",
]
language = "en"
project = "boto3-refresh-session"
copyright = f"{date.today().year}, Michael Letts"
author = "Michael Letts"
release = "0.0.12"
source_encoding = "utf-8"
source_suffix = ".rst"
pygments_style = "sphinx"
add_function_parentheses = False
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "tests/"]
html_logo = "brs.png"
html_favicon = "brs.png"
html_title = "boto3-refresh-session"
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_file_suffix = ".html"
html_sidebars = {
    "**": [],
}
html_context = {
    "default_mode": "dark",
}
htmlhelp_basename = "boto3-refresh-session"
html_theme_options = {
    "collapse_navigation": True,
    "navbar_end": [
        "search-button",
        "navbar-icon-links.html",
    ],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/michaelthomasletts/boto3-refresh-session",
            "icon": "fab fa-github-square",
            "type": "fontawesome",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/boto3-refresh-session/",
            "icon": "fab fa-python",
            "type": "fontawesome",
        },
    ],
}
autodoc_default_options = {
    "members": True,
    "member-order": "alphabetical",
    "exclude-members": "__init__",
}
autodoc_typehints = "none"
autodoc_preserve_defaults = False
autodoc_class_signature = "separated"
numpydoc_show_class_members = False
numpydoc_show_inherited_class_members = False
numpydoc_attributes_as_param_list = False
numpydoc_class_members_toctree = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
generate_autosummary = True


def linkcode_resolve(domain, info):
    """Resolves 'source' link in documentation."""

    if domain != "py":
        return None
    if not info["module"]:
        return None
    filename = info["module"].replace(".", "/")
    return f"https://github.com/michaelthomasletts/boto3-refresh-session/blob/main/{filename}.py"
