# AGIDMGen's Script Builder

Compiles [the script's source code](../Script) into a
[single script](../../AGIDMGen/script%20build/src/AGIDMGen/AGIDMGen.py), for users who do not know how to install a Python
package. How users run the script is in [script build's README](../../AGIDMGen/script%20build/README.md).

<br>

> [!NOTE]
> Like [AG Remap's ScriptBuilder](https://github.com/nhok0169/Anime-Game-Remap/tree/master/Tools/ScriptBuilder), this
> copies each module's `##### Script` section into the script in
> ***[topological ordering](https://en.wikipedia.org/wiki/Topological_sorting)***, with every `##### ExtImports`
> gathered at the top. It runs on AGRemapUtils' own `ScriptBuilder`.

<br>

> [!IMPORTANT]
> The script does not contain the library: it reaches it, by a path (`dev`) or from PyPI (`prod`). See
> [the script's README](../Script).

<br>

Beyond AGRemapUtils' builder, this one:

* puts **every module the source package's `__init__.py` exports** into the script, not only the ones `main` reaches;
* **never writes back to the source** (AGRemapUtils' builder rewrites a module whose credits are not AG Remap's);
* **refuses to build** when two modules define the same top-level name (they would overwrite each other in one file),
  or when a module did not make it into the script;
* reads the script's version from [`AGIDMGen/api/pyproject.toml`](../../AGIDMGen/api/pyproject.toml), and its credits
  from the library's `main.py`.

<br>

## How To Run
Needs [AGRemapUtils](https://pypi.org/project/AGRemapUtils/) (`pip install -r requirements.txt`), or AG Remap's source of
it named by `AGREMAP_UTILS_SRC` (`<AG Remap>/Tools/Utilities/src/AGRemapUtils`). The source is read as files, never run.

```bash
python main.py --env prod
```

<br>

## Options

### `--env/-e`

What environment to build the script for, which decides how the compiled script reaches the API:

| Env | How the script reaches the API | Options the script gains |
| --- | --- | --- |
| `dev` *(default)* | a path on this machine, relative to the compiled script (`AGIDMGen/api/src/py`) | none |
| `prod` | [AGIDMGen](https://pypi.org/project/AGIDMGen/), downloaded from PyPI when the script runs | `--disableUpdate/-dup`, `--preRelease/-pre` |

> [!IMPORTANT]
> **The committed script is a `prod` build.** A `dev` build is for trying a change to the library through the script on
> this machine; rebuild with `--env prod` before committing. CI's check fails on a committed `dev` build.

### `--check`

Builds nothing. Exits with 1 if the committed script build is not what the source builds now for the `--env` given,
ignoring the build's datetimes and hashes. CI runs this after the unit tests:

```bash
python main.py --env prod --check
```
