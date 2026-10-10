# Architecture

How library code is laid out and written. Everything here is AGRemap's Python convention, carried
over; when something is not covered, read a file in AGRemap's
`Anime Game Remap (for all users)/api/src/py/FixRaidenBoss2/` and match it. See
[Documentation](../Documentation/CLAUDE.md) for docstrings and [Testing](../Testing/CLAUDE.md) for
tests, which every new class needs.

## Package layout

```
AGIDMGen/api/                 distribution folder: pyproject.toml, README.md, LICENSE (MIT)
  src/
    py/AGIDMGen/              the Python package
      __init__.py             flat re-export of every public name + explicit __all__
      py.typed
      constants/              enums and module-level constants
      exceptions/             Error and its subclasses
      model/                  data types (what an identity mod is built from and made of)
        files/                file formats: FmtFile; the 3DMigoto dump readers VbDumpFile, IbDumpFile, DumpElement, DumpDataType
        gimi/                 GIMIComponent, GIMITextureSource, GIMIIdentityMod (the result)
        wwmi/                 WWMIComponent, WWMIShapeKeys, WWMIBlendRemap, WWMIIdentityMod (the result)
      tools/                  helpers that are not model types (FormatTools, DumpValueTools)
        gimi/                 GIMIIdentityModGenerator, GIMIIniBuilder
        wwmi/                 WWMIIdentityModGenerator, WWMIIniBuilder
      data/                   generated data: ModDownloadData.py (the download folders, by buildDownloadManifest.py)
      model/ModDownload.py    one version of a character's download folder
      tools/ModDownloader.py, tools/VersionTools.py   finding / fetching download folders, choosing a version
      tools/gimi/GIMIDownloadFolderBuilder.py, tools/wwmi/WWMIDownloadFolderBuilder.py   asset folder -> download folder
      IDModGenService.py      the entry point (see "THE SERVICE, THE LOGGER AND Model")
      view/                   BaseLogger, Logger: where everything is reported
      model/Model.py, model/IDModGenStats.py   the base of every reporting class; what a service run did
      main.py, __main__.py    the command line: python -m AGIDMGen <gimi|wwmi> SOURCE ... --out FOLDER
    cpp/                      (does not exist) the future C++ core, only once Python is measured too slow
    cy/                       (does not exist) the future Cython layer, same rule
```

- **Folder per concept, one class per file, the file named after the class**
  (`exceptions/Error.py` holds `Error`). Subfolders inside a concept are fine (`model/files/`,
  `tools/enums/`). A small constant that belongs to an enum lives in the enum's file
  (`IniFileEncoding` in `constants/FileEncodings.py`).
- **Relative imports inside the package** (`from ..exceptions.Error import Error`).
- **`__init__.py` re-exports every public name flat** under a comment per folder
  (`# --- Constants --------`), and lists it in `__all__`. Users write `AGIDMGen.ModLoaders`, never
  `AGIDMGen.constants.ModLoaders`. `test_ImportCheck.py` checks every name in `__all__` exists; it
  cannot check that a public class was *added* to `__all__`, so do that yourself.

## Every source file carries a credits block and section markers

```python
##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
# ...

##### EndCredits


##### ExtImports
from enum import Enum
##### EndExtImports


##### LocalImports
from ..exceptions.Error import Error
##### EndLocalImports


##### Script
class ...
##### EndScript
```

Copy the credits block from a sibling file. The markers are AGRemap's: its `Tools/ScriptBuilder`
concatenates the package into one single-file script by them, matching them as **substrings** (so never
write `##### Script` inside a comment or string). Nothing here builds a script yet (2026-10-05), but the
markers are kept so one can be built without touching every file. Omit a section that would be empty
(`ExtImports` when there are no outside imports), except `Script`.

## Style

| Thing | Style | Example |
| --- | --- | --- |
| classes | PascalCase, often with empty parentheses | `class Heading():` |
| methods, variables, parameters | camelCase | `getVertexCount`, `assetsFolder` |
| private | leading underscore | `self._components`, `def _buildIni(self)` |
| module-level constants | PascalCase | `IniFileEncoding`, `ReadEncodings` |
| enum members | PascalCase (or the loader's own spelling) | `FileEncodings.UTF8`, `ModLoaders.GIMI` |
| keyword arguments | spaces around `=` | `Heading(title = t, sideLen = 2)` |
| conditions | parenthesised | `if (self.logger is not None):` |
| type hints | `typing` generics, not builtin ones (3.9 floor) | `Optional[str]`, `List[int]`, `Dict[str, Any]` |

- **Exceptions**: one file each in `exceptions/`, subclassing `Error`, which prefixes `"ERROR: "`.
- **Comments are sparse** in plain code; the *why* of a non-obvious choice goes in a `#` comment above
  it. Docstrings say what, for a user (see [Documentation](../Documentation/CLAUDE.md)).
- **Do not assume a mod's or an asset folder's structure** beyond what its own metadata declares
  (AGRemap's rule, 2026-09-30): a fallback default path is a guess about someone else's filesystem, and
  it is silent exactly when it is wrong. Raise an `Error` that says what was missing.
- **A generator builds everything before it writes anything** (`WWMIIdentityModGenerator.generate`), so
  bad asset data raises with no half-written mod left behind. AGRemap's prototypes wrote as they went.
- **Library code raises an `Error` subclass, never `SystemExit`.** The prototypes exit with a message;
  a port turns each into a `BadAssetData` (or a more specific `Error`) with the same message, which
  `Testing/Integration Tester/wwmiCheck.py` relies on to match the two programs' refusals.
- **Module-level constants get a `#:` comment** right above them. That is what autodoc shows. They are
  documented in `api.rst` from their SOURCE module (`AGIDMGen.constants.WWMIBuffers.WWMIShapeKeySlots`),
  because autodoc looks for the `#:` comment in the module named, and `AGIDMGen/__init__.py` only
  re-exports. Through `AGIDMGen.DXGIFormats` the entry showed `dict`'s own docstring instead
  (four docutils errors, 2026-10-05).
- **No hard-coded machine paths in the library.** AGRemap's prototypes default to `E:\...` folders and
  an `AG_REMAP_REPO` environment variable; a library takes its folders as arguments.

## THE SERVICE, THE LOGGER AND `Model`: THE PUBLIC SHAPE (the maintainer's direction, 2026-10-05)

The maintainer asked for two things:

- a global entry point like AGRemap's `RemapService`;
- a logger like AGRemap's.

The goals are good support for API users, and **a future Django backend that will use AGRemap and AGIDMGen
together**. What exists, and the rules it sets:

- **`IDModGenService` (`AGIDMGen/IDModGenService.py`) is the entry point.** It generates several characters
  into `<outputFolder>/<name>`, from asset folders (`assetsFolders`) or download folders (`names`).
  - **`generate()` returns nothing; results are in `stats`** (`IDModGenStats`: `generated`, `skipped`,
    `noErrors`), as in `RemapService`.
  - **A failing character is recorded in `stats.skipped`, never raised.**
  - **`handleExceptions` governs only whole-run failures** (options that contradict each other): raise, or
    report and return.
  - A library `Error` is reported by its message; any other exception, being a bug, with its traceback.
- **The command line (`main.py`) is a thin view over the service**, as AGRemap's `main.py` is over
  `RemapServiceCLI`. It parses arguments, builds a `Logger` and a service with `handleExceptions = True`,
  runs it, and writes `--log`. Put no generation logic in `main.py`.
- **The logger IS AGRemap's: `FixRaidenBoss2.BaseLogger` / `FixRaidenBoss2.Logger`.** This library has no
  logger of its own, so one logger object serves both libraries in the Django backend.
  - A server subclasses `BaseLogger` and implements `write` / `read`, or reads `loggedTxt` with
    `logTxt = True`. `Testing/Unit Tester/UnitTester/Tests/captureLogger.py` is such a subclass.
  - **A logger keeps state between runs** (prefix, headings, transcript): one per request, or `clear()`.
  - (A pure-Python port existed for one revision, 2026-10-05. It was dropped on the maintainer's rule
    below; importing `FixRaidenBoss2` measured 3.2 s cold and 0.3 s warm, not the 30-60 s first seen.)
- **`FixRaidenBoss2.Model` is the base of everything that reports**: the generators, `ModDownloader` and the
  service. It holds `logger`, and every message goes through `self.print("log", ...)`, which does nothing
  without a logger. **A new class that reports progress extends `Model` and takes `logger = None` last**;
  it never calls `print()` itself.
- The download-folder builders and the data classes do not report.

## USE AGREMAP'S API WHERE IT ALREADY DOES THE JOB (the maintainer's rule, 2026-10-05)

*"If there are parts of AGIDMGen that could simply use the powerful API of AGRemap, I recommend just
using AGRemap."* `FixRaidenBoss2` is a dependency and is imported with the package. **Before writing a
helper, look for it in AGRemap's API**: `core.pyi` in `<AGRemap>/Anime Game Remap (for all users)/api/src/py/FixRaidenBoss2/`
lists every bound class, and the package's `data/` modules hold its tables.

What this library takes from AGRemap (2026-10-05):

| Need | AGRemap's | Where |
| --- | --- | --- |
| logging | `BaseLogger`, `Logger` | the service, the generators, `ModDownloader`, `main.py` |
| the reporting base class | `Model` | the same |
| game versions and AGRemap's "newest not newer" rule | `Version`, `VersionSet.findClosest` | `VersionTools` (an adapter for `4_0` folder names) |
| downloading, with retries and redirects | `FileDownload` | `ModDownloader` |
| hashes and object indices of skins with no asset folder | `ModData.Hashes`, `ModData.Indices` | `Tools/Downloads/hashFromAGRemap.py` |
| the test runner | AGRemapUtils' `BaseTestProgram` | `Testing/Unit Tester` |

What is deliberately NOT AGRemap's:

- **The 3DMigoto dump readers (`VbDumpFile` / `IbDumpFile`).** The maintainer chose a Python rewrite of
  `VbFile` / `IbFile.readDumpStr`, and it is proved byte-identical to them.
- **`IDModGenStats`.** AGRemap's `FileStats` counts fixed / removed / undone files, which is not what a
  generation produces.
- **Texture donors.** AGRemap's `GIMIComponentParserConfig` has no Python accessor: the configs are built
  inside C++ factory functions. So `hashFromAGRemap.py` reads them out of the parser sources once, and stores
  them in `Hash.json`.

## Dependencies

AGRemap's API first (above), then the standard library. A third-party dependency goes in
`AGIDMGen/api/pyproject.toml` with a lower bound, and in `Docs/requirements.txt` and
`Testing/Unit Tester/requirements.txt` too: Read the Docs and the tester import the package. The
dependencies are **numpy** (`>=1.26.4`) and **FixRaidenBoss2** (`>=5.0.0`).

**Depending on `FixRaidenBoss2` (AGRemap's API) is an open decision (2026-10-05).** AGRemap's GIMI
generator uses only its compiled `VbFile` / `IbFile` (`readDumpStr`, `elements`, `data`,
`bytesPerLine`, `getVertexCount`, `getIndexCount`) to parse 3DMigoto's dump text. Depending on it
pulls in a compiled package and its DLLs for one parser; re-implementing the parser in Python keeps
this library pure. Ask the maintainer before adding the dependency. If the parser is re-implemented, its
tests compare against `FixRaidenBoss2`'s output on the same dumps, which is the reference.

## When C++ / Cython comes in

Only when a part is **measured** too slow, or is plainly better in C++, and the maintainer agrees. Then
follow AGRemap's layout and build (its `AI Agent Help/Architecture`, `Building` and `Setup` guides):
`src/cpp` (C++ core + pybind11 bindings), `src/cy` (Cython), scikit-build-core in `pyproject.toml`, and
the Python package imports the compiled module. Keep a Python reference implementation and a test that
the two agree byte for byte.
