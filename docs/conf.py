import sys
import os

# Include the parent path so that the package may be imported by autodoc
sys.path.insert(0, os.path.abspath(os.path.pardir))

# Enable the appropriate Sphinx extensions
extensions = ["sphinx.ext.autodoc"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "Easy SNMP"
copyright = "2015-2022, Fotis Gimian, Kent Coble"
author = "Fotis Gimian, Kent Coble"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# The theme to use for HTML and HTML Help pages.
html_theme = "alabaster"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the Alabaster
# documentation at https://github.com/bitprophet/alabaster.
html_theme_options = {
    "github_user": "kamakazikamikaze",
    "github_repo": "easysnmp",
    "github_banner": True,
    "logo": "easysnmp.svg",
    "logo_name": True,
    "font_family": "'Hiragino Mincho Pro', Georgia, serif",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, maps document names to template names.
html_sidebars = {
    "**": [
        "about.html",
        "localtoc.html",
        "relations.html",
        "searchbox.html",
    ]
}
