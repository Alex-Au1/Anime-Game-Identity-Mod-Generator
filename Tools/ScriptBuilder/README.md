# AGIDMGen's Script Builder

Compiles [the library's source code](../../AGIDMGen/api/src/py/AGIDMGen) into a
[single script](../../AGIDMGen/script%20build/src/AGIDMGen/AGIDMGen.py), for users who do not know how to install a Python
package. How users run the script is in [script build's README](../../AGIDMGen/script%20build/README.md).

<br>

> [!NOTE]
> Like [AG Remap's ScriptBuilder](https://github.com/nhok0169/Anime-Game-Remap/tree/master/Tools/ScriptBuilder), this
> copies each module's `##### Script` section into the script in
> ***[topological ordering](https://en.wikipedia.org/wiki/Topological_sorting)***, with every `##### ExtImports`
> gathered at the top. It runs on AGRemapUtils' own `ScriptBuilder`.

<br>

## How it differs from AG Remap's

AG Remap's script no longer *contains* its API: the API is C++/Cython/Python now, and a `.py` file cannot carry a
compiled module. AGIDMGen is pure Python, so its script **does contain the whole library**, the way AG Remap's script
did before. What it cannot contain is what the library is built on:

| Dependency | In the script? |
| --- | --- |
| AGIDMGen | yes, compiled in |
| numpy, [FixRaidenBoss2](https://pypi.org/project/FixRaidenBoss2/) (AG Remap's API, compiled) | no: installed with `pip` the first time the script runs, if missing or older than `pyproject.toml` asks |

Beyond AGRemapUtils' builder, this one:

* puts **every module the package's `__init__.py` exports** into the script, not only the ones `main` reaches;
* **never writes back to the library's source** (AGRemapUtils' builder rewrites a module whose credits are not AG Remap's);
* **refuses to build** when two modules define the same top-level name (they would overwrite each other in one file),
  or when a module did not make it into the script;
* reads the script's version and dependencies from [`AGIDMGen/api/pyproject.toml`](../../AGIDMGen/api/pyproject.toml), and its
  credits from the library's `main.py`.

<br>

## How To Run
Needs [AGRemapUtils](https://pypi.org/project/AGRemapUtils/) (`pip install -r requirements.txt`), or AG Remap's source of
it named by `AGREMAP_UTILS_SRC` (`<AG Remap>/Tools/Utilities/src/AGRemapUtils`). The library's own dependencies are not
needed: the package is read as files, never imported.

```bash
python main.py
```

<br>

## Options

### `--check`

Builds nothing. Exits with 1 if the committed script build is not what the source builds now, ignoring the build's
datetimes and hashes. CI runs this after the unit tests.

```bash
python main.py --check
```
