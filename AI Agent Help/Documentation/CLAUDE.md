# Documentation

Writing docstrings and building the Sphinx site under `Docs/`. See
[Architecture](../Architecture/CLAUDE.md) for where docstrings go in a source file, and
[Setup](../Setup/CLAUDE.md) for the Sphinx install.

## Building the docs

From `Docs`:

```bash
py -3 -m sphinx -b html -W --keep-going src build/html
```

`Docs/build/` is gitignored. `conf.py` reads the version from `AGIDMGen/api/pyproject.toml` (the only place
the version lives) and imports the package from `AGIDMGen/api/src/py`, not from an install.

**`FixRaidenBoss2` must be importable, or every autodoc entry fails (2026-10-10).** The maintainer's plain
`make html` gave 39 `No module named 'FixRaidenBoss2'` warnings: it is not pip-installed on this machine, and
only an agent's `PYTHONPATH` had hidden that. `conf.py` now falls back to AG Remap's source, from
`AGREMAP_API_SRC` or a `Fix-Raiden-Boss` checkout beside this repo, and stops with a clear error if neither
exists. Build once with no `PYTHONPATH` before calling the docs clean.

**The warning baseline is 2 (2026-10-05)**: the two intersphinx inventories (python, sphinx) cannot be
fetched from this machine's agent sandbox (`CERTIFICATE_VERIFY_FAILED`). Anything beyond those two is
yours. Read the warnings, don't just count them: a duplicate-object warning means an entry is
documented twice.

Read the Docs builds from `.readthedocs.yaml` at the repo root: Python 3.10, `Docs/requirements.txt`,
no install of the package.

To look at the result, serve it rather than opening the file: `py -3 -m http.server 8765 --bind 127.0.0.1` from
`Docs/build/html`. The browser pane renders a `file://` page as a snapshot without its stylesheets.

## THE SITE LOOKS LIKE AGREMAP'S (the maintainer's request, 2026-10-10)

Furo, styled as AGRemap's docs are, from copies of AGRemap's files. Keep them in step with AGRemap's
`Docs/src` rather than restyling here:

| File | From AGRemap's | Changed |
| --- | --- | --- |
| `_static/css/styles.css` | `_static/css/styles.css` | nothing |
| `extensions/attributetable.py` | `extensions/attributetable.py` (discord.py's) | nothing |
| `_static/images/python.png` | `_static/images/python.png` | nothing |
| `_templates/page.html` | `_templates/page.html` (the black top bar) | the links: this repo's GitHub, PyPI (AGIDMGen, FixRaidenBoss2), AG Remap's GitHub and docs; no GameBanana |

The pages follow AGRemap's too: `index.rst` (badges, then captioned sections), `tutorial.rst` (Choice A-D with
STEP 1-3; `conf.py` suppresses `autosectionlabel.tutorial` for the repeated STEP labels), `commandOpts.rst`,
`apiSetup.rst`, `apiExamples.rst`, `api.rst`. **The tutorial and command options repeat the library README
(`AGIDMGen/api/README.md`) and the script build's README: change them together.** `conf.py` also turns on
AGRemap's `inherited-members`, so a class lists what it inherits from AGRemap's `Model` (`print`, `report`).
There is no banner image yet (AGRemap's index has `AGRemapBanner.png`).

## THE REFERENCE PAGE IS HAND-WRITTEN (2026-10-05)

`Docs/src/api.rst` lists every public export by hand, as in AGRemap: a "Where to start" list, then sections
(headings underlined with `*`) **Service, Model, View,
Constants, Data, Exceptions, Tools** (add a section when its first class arrives). The `Model` base class is
listed under Service, and `conf.py` suppresses `autosectionlabel.api`, because the section and the class are
both called 'Model', with entries in alphabetical order
inside each section, each shaped like:

```rst
ModLoaders
==========

.. attributetable:: AGIDMGen.ModLoaders

.. autoclass:: AGIDMGen.ModLoaders
    :members:

:raw-html:`<br />`
```

**Every name in `AGIDMGen.__all__` needs an entry**, and a new class is not finished until it has one.
`py -3 Tools/auditApiDocs.py` checks it both ways (exits 1 on a missing or stale entry).
The entry's heading is underlined with `=`; `auditApiDocs.py` finds the entries by that underline (2026-10-10,
it was `~` before the AGRemap restyle). A class gets an `.. attributetable::`, a constant does not.
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
        The `GIMI <https://github.com/SilentNightSound/GI-Model-Importer>`_ mod loader for GI
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
- **Name the games and loaders by their short forms (the maintainer's request, 2026-10-10)**: GI and WuWa,
  GIMI and WWMI, never "Genshin Impact" / "Wuthering Waves" or the loaders' long names. The same holds for the
  READMEs, the docs pages and the command line's help.
- **Docstrings are published for a new user**: present tense, no dates, no history ("ported from..."),
  no links into `AI Agent Help/`. History and lessons go in these guides or in plain `#` comments.
