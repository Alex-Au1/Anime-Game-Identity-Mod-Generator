# Documentation

Writing docstrings and building the Sphinx site under `Docs/`. See
[Architecture](../Architecture/CLAUDE.md) for where docstrings go in a source file, and
[Setup](../Setup/CLAUDE.md) for the Sphinx install.

## Building the docs

From `Docs`:

```bash
py -3 -m sphinx -b html -W --keep-going src build/html
```

`Docs/build/` is gitignored. `conf.py` reads the version from `AGIDMGen/pyproject.toml` (the only place
the version lives) and imports the package from `AGIDMGen/src/py`, not from an install.

**The warning baseline is 2 (2026-10-05)**: the two intersphinx inventories (python, sphinx) cannot be
fetched from this machine's agent sandbox (`CERTIFICATE_VERIFY_FAILED`). Anything beyond those two is
yours. Read the warnings, don't just count them: a duplicate-object warning means an entry is
documented twice.

Read the Docs builds from `.readthedocs.yaml` at the repo root: Python 3.10, `Docs/requirements.txt`,
no install of the package.

## THE REFERENCE PAGE IS HAND-WRITTEN (2026-10-05)

`Docs/src/api.rst` lists every public export by hand, as in AGRemap: sections **Service, Model, View,
Constants, Data, Exceptions, Tools** (add a section when its first class arrives). The `Model` base class is
listed under Service, and `conf.py` suppresses `autosectionlabel.api`, because the section and the class are
both called 'Model', with entries in alphabetical order
inside each section, each shaped like:

```rst
ModLoaders
~~~~~~~~~~

.. autoclass:: AGIDMGen.ModLoaders
    :members:

:raw-html:`<br />`
```

**Every name in `AGIDMGen.__all__` needs an entry**, and a new class is not finished until it has one.
`py -3 Tools/auditApiDocs.py` checks it both ways (exits 1 on a missing or stale entry).
A module-level constant is an `.. autodata::` entry naming its SOURCE module
(`AGIDMGen.constants.WWMIBuffers.WWMIShapeKeySlots`), with a `#:` comment above the constant in the
code; see [Architecture](../Architecture/CLAUDE.md)'s style notes for why.
For an `Enum`, use `:members:` without `:undoc-members:`: the class docstring's `Attributes` section
already documents each member, and adding both documents them twice (four duplicate-object warnings on
2026-10-05).

## Docstring format

Numpydoc sections rendered by `sphinx.ext.napoleon`, with Sphinx roles for every type, as in AGRemap:

```python
class ModLoaders(Enum):
    """
    The 3DMigoto mod loaders that an identity mod can be generated for

    Attributes
    ----------
    GIMI: :class:`str`
        The Genshin Impact Model Importer
    """
```

```python
    def generate(self, assetsFolder: str, modFolder: Optional[str] = None) -> str:
        """
        Generates the identity mod of a character

        Parameters
        ----------
        assetsFolder: :class:`str`
            The folder of the character's assets

        modFolder: Optional[:class:`str`]
            The folder to write the mod into. If this value is ``None``, the mod is written beside ``assetsFolder`` :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Raises
        ------
        :class:`Error`
            If ``assetsFolder`` has no ``hash.json``

        Returns
        -------
        :class:`str`
            The folder the mod was written into
        """
```

- Optional types are written ``Optional[:class:`X`]``; defaults as `**Default**: ``value``` after two
  `:raw-html:` line breaks. `rst_prolog` in `conf.py` defines the `raw-html` role.
- Use an `r"""` docstring when it contains `\*args`.
- **Docstrings are published for a new user**: present tense, no dates, no history ("ported from..."),
  no links into `AI Agent Help/`. History and lessons go in these guides or in plain `#` comments.
