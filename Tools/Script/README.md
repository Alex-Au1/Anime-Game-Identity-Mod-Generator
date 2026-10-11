# AGIDMGen's Script

The source for [AGIDMGen's single-file script](../../AGIDMGen/script%20build/src/AGIDMGen/AGIDMGen.py), ported from
[AG Remap's](https://github.com/nhok0169/Anime-Game-Remap/tree/master/Tools/Script).

<br>

> [!NOTE]
> The script does not *contain* the library. It makes the library (the API) importable, then hands the command line
> to the API's own `main`, the one `python -m AGIDMGen` runs. With no arguments (eg. double-clicked), the API asks
> which game and which characters to make.

<br>

## How the script reaches the API

Decided when the script is compiled, by the [ScriptBuilder](../ScriptBuilder)'s `--env` option:

| Env | How | Extra options |
| --- | --- | --- |
| `dev` | a path on this machine, relative to the script: `AGIDMGen/api/src/py`. numpy and FixRaidenBoss2 must already be importable | none |
| `prod` *(committed)* | [AGIDMGen](https://pypi.org/project/AGIDMGen/), downloaded from PyPI with `pip` at runtime (it brings numpy and FixRaidenBoss2 as its dependencies) | `--disableUpdate/-dup`, `--preRelease/-pre` |

<br>

### How it differs from AG Remap's

* **The API's command has no hook for the script's own options**, so they are read first and taken off the command
  line, and the rest goes to the API. On `--help`, the API's help page is printed, then the script's own options.
* **pip runs as `python -m pip`** in a subprocess, not through `pip._internal`. If it fails while AGIDMGen is already
  installed (eg. no internet), the installed version runs; otherwise the script prints the install command and exits 1.
* **The compiled script is named after the API** (`AGIDMGen.py`, in a package folder named `AGIDMGen`), so a plain
  import would find the script itself. `BaseApiRef.importApi` imports the API from anywhere but the script's own
  folders.

<br>

## How To Run

To run the script straight from this source, against the API in this repo, on
[CMD](https://www.google.com/search?q=how+to+open+cmd+in+a+folder&oq=how+to+open+cmd), enter

```bash
python main.py gimi Albedo --download
```

Every option of the API's own command line works here, since they are the API's:

```bash
python main.py gimi --help
```
