# Setup

Getting from a fresh clone to a passing test run and a built docs site. There is nothing to compile
(the library is pure Python, see [Overview](../Overview/CLAUDE.md)); next go to
[Testing](../Testing/CLAUDE.md) or [Documentation](../Documentation/CLAUDE.md).

## Prerequisites

| What | Version | Needed for |
| --- | --- | --- |
| Python | 3.9 or newer (this machine: 3.9.3, as `py -3`, 2026-10-05) | everything |
| Sphinx, sphinx_design, furo | pinned in `Docs/requirements.txt` | the docs only |
| numpy | `>=1.26.4` | the library |
| FixRaidenBoss2 (AGRemap's API) | `>=5.0.0`, binary wheels for Windows x64 / glibc Linux on Python 3.9-3.13 | **everything**: the library imports it (its logger, `Model`, versions, downloads) |
| AGRemapUtils | `>=1.0.7` (or `AGREMAP_UTILS_SRC`, see [Testing](../Testing/CLAUDE.md)) | the unit tester |

**This machine has numpy 1.26.4 but neither FixRaidenBoss2 nor AGRemapUtils pip-installed (2026-10-05).** Put
AGRemap's API source on `PYTHONPATH` for everything here: the tests, the checks, the tools, the docs and the
command line:

```bash
export PYTHONPATH="E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Anime Game Remap (for all users)/api/src/py"
```

Its compiled `core.cp39-win_amd64.pyd` is built there, and `import FixRaidenBoss2` adds its own DLL folder.
It takes 3.2 s cold and 0.3 s warm.

## The package itself needs no install to test or build the docs

Both the unit tester and `Docs/src/conf.py` put `AGIDMGen/src/py` at the **front** of `sys.path` and
import the package from source. The tester also needs AGRemapUtils: either pip-installed, or AGRemap's
source named by `AGREMAP_UTILS_SRC`. So, from a fresh clone on this machine:

```bash
cd "Testing/Unit Tester" && PYTHONPATH="E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Anime Game Remap (for all users)/api/src/py" AGREMAP_UTILS_SRC="E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Tools/Utilities/src/AGRemapUtils" py -3 main.py
```

That is deliberate: a pip-installed release of `AGIDMGen` must never be the copy under test or the
copy documented. (AGRemap hit exactly this, with autodoc documenting an older installed
`FixRaidenBoss2`.)

## THE NAMESPACE-PACKAGE TRAP (2026-10-05)

The distribution folder `AGIDMGen/` at the repo root has no `__init__.py`. Python 3 therefore imports
it as an empty **namespace package** whenever the repo root is on `sys.path` — which it is, as the
working directory, every time you run `python -c` from the root:

```
> py -3 -c "import AGIDMGen; print(AGIDMGen.__file__)"
None
```

The import *succeeds*, and every attribute access then fails, or `__file__` is `None`. If
`import AGIDMGen` "works" but nothing is in it, this is why; put `AGIDMGen/src/py` first on `sys.path`.
`test_ImportCheck.py` guards the tester against it by checking that the imported package's folder is
the source folder.

## Installing the package (editable)

```bash
py -3 -m pip install -e AGIDMGen
```

This needs **setuptools 61 or newer**, because the metadata is in `pyproject.toml`'s `[project]` table.
On 2026-10-05 this machine had setuptools 49.2.1, and the agent sandbox could not reach PyPI to fetch a
newer one in pip's isolated build (`CERTIFICATE_VERIFY_FAILED`). With `--no-build-isolation`, the old
setuptools silently builds a wheel named `UNKNOWN-0.0.0` with no package in it: a clean run with the
wrong artifact. **Check the wheel's name and contents** before trusting an install here. The tests and
docs do not need the install.
