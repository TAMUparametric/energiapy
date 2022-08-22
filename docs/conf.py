# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Energiapy'
copyright = '2022, Rahul Kakodkar, Efstratios N. Pistikopoulos'
author = 'Rahul Kakodkar, Efstratios N. Pistikopoulos'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# import the new package
import os
import sys
import sphinx_rtd_theme

for x in os.walk("../src"):
    sys.path.insert(0, x[0])

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../src/energiapy/*"))
sys.path.insert(0, os.path.abspath("../"))
sys.setrecursionlimit(10000)


# edit extendsions to include the new theme
extensions = ['sphinx.ext.autodoc', 'sphinx_rtd_theme', ]

# change the html export theme


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
