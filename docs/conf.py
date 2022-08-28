# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sys
from pathlib import Path

import tomli

docs_source_path = Path(".").resolve()
python_source_path = Path("..").resolve()
sys.path.append(str(python_source_path))

# -- Project information -----------------------------------------------------

project = 'pyetta'
copyright = 'Copyright 2022 Kenneth Ng'
author = 'Kenneth Ng'

with open("../pyproject.toml", "rb") as pyproject_file:
    values = tomli.load(pyproject_file)
    # don't catch exception here, if this fails it means something was moved.
    version = values["project"]["version"]

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    'sphinxcontrib.mermaid',
    'myst_parser'
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

html_theme_options = {
    'logo_only': True,
    'display_version': True,
    'navigation_depth': 3
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['./css']

html_css_files = [
    'overrides.css',
]

html_logo = 'images/logo.png'
html_favicon = 'images/favicon.png'

# -- myst_parser configuration ---------------------------------------------------

myst_heading_anchors = 3

# -- autodoc configuration ---------------

autodoc_member_order = 'bysource'

# -- intersphinx configuration -----------

intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}
