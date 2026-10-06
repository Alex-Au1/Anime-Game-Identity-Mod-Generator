import os, sys, re


# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'AGIDMGen'
copyright = '2026, Albert Gold'
author = 'Albert Gold'

# read the version from the pyproject.toml of the library
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'AGIDMGen', 'pyproject.toml')) as f:
    release = re.search(r"^version\s*=\s*[\"']([^\"']*)[\"']", f.read(), re.MULTILINE).group(1)

version = release

# path to the library
#
# note: insert(0, ...) rather than append(...) -- this has to take precedence over site-packages, or a
#   pip-installed release of AGIDMGen is the copy that gets documented
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'AGIDMGen', 'src', 'py')))

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    "sphinx_design"
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']
html_static_path = ['_static']

# -- Options for HTML output

html_theme = 'furo'

# -- Options for EPUB output
epub_show_urls = 'footnote'


# don't add the module names
add_module_names = False
toc_object_entries = False

autodoc_typehints = "description"

# Force autosectionlabel to prepend the filename to all section headings
autosectionlabel_prefix_document = True

# add the edit on github link
html_context = {
    "display_github": True,
    "github_user": "Alex-Au1",
    "github_repo": "Anime-Game-Identity-Mod-Generator",
    "github_version": "main",
    "conf_py_path": "/Docs/src/",
}

# the ':raw-html:' role the docstrings use for line breaks
rst_prolog = """
.. role:: raw-html(raw)
    :format: html
"""
