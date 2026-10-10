import os, sys, re


# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'AGIDMGen'
copyright = '2026, Albert Gold'
author = 'Albert Gold'

# read the version from the pyproject.toml of the library
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'AGIDMGen', 'api', 'pyproject.toml')) as f:
    release = re.search(r"^version\s*=\s*[\"']([^\"']*)[\"']", f.read(), re.MULTILINE).group(1)

version = release

# path to the library
#
# note: insert(0, ...) rather than append(...) -- this has to take precedence over site-packages, or a
#   pip-installed release of AGIDMGen is the copy that gets documented
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'AGIDMGen', 'api', 'src', 'py')))

# path to AG Remap's API (FixRaidenBoss2), which the library imports
#
# note: Read the Docs pip installs it from Docs/requirements.txt. A local build without it installed takes it from
#   the source of AG Remap: the folder in the AGREMAP_API_SRC environment variable, or else a checkout of AG Remap
#   beside this repo's ('Fix-Raiden-Boss'). Without either, every autodoc entry fails on 'No module named FixRaidenBoss2'
try:
    import FixRaidenBoss2
except ImportError:
    agRemapApiSrc = os.environ.get("AGREMAP_API_SRC") or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'Fix-Raiden-Boss', 'Anime Game Remap (for all users)', 'api', 'src', 'py')
    agRemapApiSrc = os.path.abspath(agRemapApiSrc)
    if (not os.path.isdir(os.path.join(agRemapApiSrc, 'FixRaidenBoss2'))):
        raise ImportError(f"FixRaidenBoss2 is not installed, and AG Remap's API source is not at {agRemapApiSrc}: "
                          "run 'pip install -r Docs/requirements.txt', or set AGREMAP_API_SRC to AG Remap's 'api/src/py' folder")
    sys.path.append(agRemapApiSrc)
    print(f"[conf] FixRaidenBoss2 from {agRemapApiSrc}")

# path for some external libaries for the sphinx docs (attributetable, copied from AG Remap's docs)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extensions')))

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    "sphinx_design",
    'attributetable'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'furo'

# -- Options for EPUB output
epub_show_urls = 'footnote'


# don't add the module names
add_module_names = False
toc_object_entries = False

autodoc_typehints = "description"

# Every class page also lists what it inherits, as in AG Remap's docs, so a reader does not have to go up to the
# parent class to find a method. Members that come from Python's own built-in types are left out.
autodoc_default_options = {
    "inherited-members": "object,str,int,float,bool,bytes,dict,list,set,frozenset,tuple,"
                         "Enum,IntEnum,Flag,IntFlag,Exception,BaseException,ABC,Generic",
}

# Force autosectionlabel to prepend the filename to all section headings
autosectionlabel_prefix_document = True

# The tutorial's choices each walk through their own STEP 1 / 2 / 3, so those headings share labels.
# Nothing references a STEP heading (a reference goes to the choice's own heading instead)
suppress_warnings = ["autosectionlabel.tutorial"]

# add the edit on github link
html_context = {
    "display_github": True,
    "github_user": "Alex-Au1",
    "github_repo": "Anime-Game-Identity-Mod-Generator",
    "github_version": "main",
    "conf_py_path": "/Docs/src/",
    "page_source_suffix": ".rst"
}

# These folders are copied to the documentation's HTML output
html_static_path = ['_static']

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'css/styles.css',
]

# the ':raw-html:' role the docstrings use for line breaks
rst_prolog = """
.. role:: raw-html(raw)
    :format: html
"""
