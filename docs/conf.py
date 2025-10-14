# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime

for x in os.walk("../src"):
    sys.path.insert(0, x[0])

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../src/energia/*"))
sys.path.insert(0, os.path.abspath("../src"))
sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("../../"))

sys.setrecursionlimit(10000)


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Energia'
copyright = str(datetime.now().year)
author = 'Rahul Kakodkar, Efstratios N. Pistikopoulos'
release = '2.0.1'

master_doc = 'index'
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # "myst_parser",
    "myst_nb",
    # "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
    # "sphinx_design",
    # "sphinx_examples",
    # "sphinx_tabs.tabs",
    # "sphinx_thebe",
    "sphinx_togglebutton",
    "sphinxcontrib.bibtex",
    # "sphinxext.opengraph",
    # "sphinx.ext.todo",
]
myst_enable_extensions = [
    "amsmath",
    "deflist",
    "html_admonition",
    "html_image",
    # "linkify",
    "dollarmath",
    "colon_fence",
    "smartquotes",
    "replacements",
    "substitution",
]
add_module_names = False

autosummary_context = {
    "skip_module_names": True,
}


templates_path = ['_templates']
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    'jupyter_execute',
    '**.ipynb_checkpoints',
]
autosummary_generate = True
autosummary_imported_members = True
autodoc_inherit_docstrings = True
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'inherited-members': True,
}
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
html_logo = "_static/logo2.jpg"
html_title = "Energia"
source_suffix = {".rst": 'restructuredtext', ".md": 'markdown', ".ipynb": 'myst-nb'}
html_copy_source = True
html_last_updated_fmt = ""
# html_sidebars = {
#     "reference/blog/*": [
#         "navbar-logo.html",
#         "search-field.html",
#         "sbt-sidebar-nav.html",
#     ]
# }
# toc_object_entries_show_parents = "hide"
suppress_warnings = [
    "ref.python",  # suppress all ambiguous cross-reference warnings in Python domain
]
html_theme_options = {
    "path_to_docs": "docs",
    "repository_url": "https://github.com/TAMUparametric/energiapy",
    "repository_branch": "main",
    "use_edit_page_button": True,
    "use_source_button": True,
    "use_issues_button": True,
    "use_repository_button": True,
    "use_download_button": True,
    # "use_sidenotes": True,
    # "show_toc_level": 4,
    "announcement": (
        "⚠️Energia 2.0.0 is a beta release. It is not compatible with Energia 1.x⚠️"
    ),
    "logo": {
        "image_dark": "_static/logo.jpg",
        # "text": html_title,  # Uncomment to try text with logo
    },
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/TAMUparametric/energiapy",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/energiapy/",
            "icon": "https://img.shields.io/pypi/dw/energiapy",
            "type": "url",
        },
    ],
}
nb_execution_mode = "off"

bibtex_bibfiles = ["refs.bib", "frameworks.bib"]
bibtex_default_style = "unsrt"
autodoc_member_order = 'bysource'
