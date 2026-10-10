# AGIDMGen's Script

The whole library in **one file**, [AGIDMGen.py](src/AGIDMGen/AGIDMGen.py), for running AGIDMGen without
installing it as a Python package.

<br>

> [!NOTE]
> The `.py` files under [src/AGIDMGen](src/AGIDMGen) are **generated** by the [ScriptBuilder](../../Tools/ScriptBuilder)
> from the library's source. Do not edit them; change the library and rebuild.

<br>

## How To Run

1. Install [Python](https://www.python.org/downloads/) 3.9 to 3.13 (on Windows, tick *"Add python.exe to PATH"* in the
   installer).
2. Download [AGIDMGen.py](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/raw/main/AGIDMGen/script%20build/src/AGIDMGen/AGIDMGen.py)
   and put it in an empty folder.
3. Open [CMD](https://www.google.com/search?q=how+to+open+cmd+in+a+folder) in that folder and enter, for example:

```bash
python AGIDMGen.py gimi Albedo --download
```

```bash
python AGIDMGen.py wwmi Aalto --download
```

The identity mod is written into a folder named after the character, **beside the script**. Copy that folder into
your GIMI or WWMI `Mods` folder.

<br>

> [!NOTE]
> The first run installs what the script needs (numpy, and [AG Remap's API](https://pypi.org/project/FixRaidenBoss2/)) with
> `pip`, so it needs an internet connection and takes a little longer. Later runs skip that.

<br>

> [!IMPORTANT]
> The script runs from **its own folder**, so that it also works when you double-click it. Any folder you give it
> (`--out`, `--log`, an asset folder) is read relative to the script, not to where you opened CMD. Give a full path
> to be sure.

<br>

## Options

Every option of the library's command line works here, since the script is the library:

```bash
python AGIDMGen.py gimi --help
```

| Example | What it does |
| --- | --- |
| `python AGIDMGen.py gimi Albedo Aino --download` | several characters at once |
| `python AGIDMGen.py gimi --download --all` | every GI character |
| `python AGIDMGen.py wwmi ChisaParfait --download --version 3.5` | the character as of an older game version, when there is a download folder for it |
| `python AGIDMGen.py gimi "C:\GI-Model-Importer-Assets\PlayerCharacterData\Albedo"` | from an asset folder you already have |
