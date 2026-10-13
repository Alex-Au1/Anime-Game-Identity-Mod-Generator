# AGIDMGen's Script

One file, [AGIDMGen.py](src/AGIDMGen/AGIDMGen.py), for running AGIDMGen without knowing how to install a Python
package: it downloads the library from [PyPI](https://pypi.org/project/AGIDMGen/) for you, then runs it.

<br>

> [!NOTE]
> The `.py` files under [src/AGIDMGen](src/AGIDMGen) are **generated** by the [ScriptBuilder](../../Tools/ScriptBuilder)
> from [the script's source](../../Tools/Script). Do not edit them; change the source and rebuild.

<br>

## How To Run

1. Install [Python](https://www.python.org/downloads/) 3.9 to 3.13 (on Windows, tick *"Add python.exe to PATH"* in the
   installer).
2. Download [AGIDMGen.py](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/raw/main/AGIDMGen/script%20build/src/AGIDMGen/AGIDMGen.py)
   and put it in your GIMI or WWMI `Mods` folder.
3. **Double-click it.** It asks which characters (their names with a space between each, of either game, or `all`),
   makes their mods, then waits for ENTER so you can read what it did.

Or open [CMD](https://www.google.com/search?q=how+to+open+cmd+in+a+folder) in that folder and enter, for example:

```bash
python AGIDMGen.py Albedo
```

```bash
python AGIDMGen.py Albedo Aalto
```

Each character's game is found from its name, so GI's Albedo and WuWa's Aalto can be made in one run.

Either way, the identity mod is written into a folder named after the character, **beside the script**.

<br>

> [!NOTE]
> The script itself is small: it downloads the generator, [AGIDMGen](https://pypi.org/project/AGIDMGen/) (with numpy and
> [AG Remap's API](https://pypi.org/project/FixRaidenBoss2/)), with `pip`. The first run takes a little longer for that.
> Every run then checks for a newer version; without an internet connection, it runs the version already downloaded.
> Add `--disableUpdate` to skip the check.

<br>

> [!IMPORTANT]
> The script runs from **its own folder**, so that it also works when you double-click it. Any folder you give it
> (`--out`, `--log`, an asset folder) is read relative to the script, not to where you opened CMD. Give a full path
> to be sure.

<br>

## Options

Every option of the library's command line works here, since the script hands its command line to the library:

```bash
python AGIDMGen.py --help
```

| Example | What it does |
| --- | --- |
| `python AGIDMGen.py Albedo Aino Zani` | several characters at once, of either game |
| `python AGIDMGen.py --all --game GI` | every GI character (`--all` alone: every character) |
| `python AGIDMGen.py ChisaParfait --version 3.5` | the character as of an older game version, when there is a download folder for it |
| `python AGIDMGen.py "C:\GI-Model-Importer-Assets\PlayerCharacterData\Albedo"` | from an asset folder you already have |

<br>

### The script's own options

These two are the script's, not the library's, and go anywhere on the command line:

| Option | What it does |
| --- | --- |
| `-dup`, `--disableUpdate` | skips checking for a newer AGIDMGen; it is only downloaded when it is not installed yet |
| `-pre`, `--preRelease` | also considers prereleases of AGIDMGen when downloading it |
