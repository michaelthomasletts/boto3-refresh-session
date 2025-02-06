import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "boto3-refresh-session"
copyright = "2025, Michael Letts"
author = "Michael Letts"
release = "0.0.11"
extensions = [
    "sphinx.ext.autodoc",
    "numpydoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "tests/"]
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
generate_autosummary = True
html_title = "boto3-refresh-session"
numpydoc_show_class_members = False
