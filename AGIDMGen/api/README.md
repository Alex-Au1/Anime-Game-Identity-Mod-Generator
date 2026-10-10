# Anime Game Identity Mod Generator (AGIDMGen)
[![Static Badge](https://img.shields.io/badge/3.9%2B-3776AB?style=for-the-badge&label=Python)](https://www.python.org/downloads/)
[![Static Badge](https://img.shields.io/badge/GIMI%20%7C%20WWMI-6E4FA3?style=for-the-badge&label=Mod%20Loaders)](#supported-games)
[![Static Badge](https://img.shields.io/badge/MIT-green?style=for-the-badge&label=License)](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/blob/main/AGIDMGen/api/LICENSE)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Alex-Au1/Anime-Game-Identity-Mod-Generator/tests.yml?branch=main&label=Unit%2FIntegration%20Tests&style=for-the-badge)](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/actions/workflows/tests.yml)

<br>

Makes ***identity mods***: a mod of a character that looks **exactly like the character already does in the game**.

<br>

An identity mod changes nothing you can see. It is the character's own model, textures and colours, written out as a mod
folder. That makes it the perfect starting point for making your own mod, or for checking that a mod loader works.

A sub-project of [Anime Game Remap (AG Remap)](https://github.com/nhok0169/Anime-Game-Remap).

<br>

## Contributors

|   |   |
|---|---|
| **[Albert Gold](https://github.com/Alex-Au1)** *(Active Lead Maintainer)* | [![@albertgold](https://dcbadge.limes.pink/api/shield/367087171154214914?theme=discord-inverted)](https://discord.com/users/367087171154214914) |
| [![The Council](https://raw.githubusercontent.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/main/Docs/src/_static/images/TheCouncilofClaudeAgentsBadgeMini.svg)](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/blob/main/AI%20Agent%20Help/README.md) *(Maintainer Team)* | [![The Council Badge](https://raw.githubusercontent.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/main/Docs/src/_static/images/TheCouncilofClaudeAgentsBadgeWithCount.svg)](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/blob/main/AI%20Agent%20Help/README.md) |

<br>

## Requirements
- [Python (version 3.9 and up)](https://www.python.org/downloads/)
  - *When installing Python, tick the box **"Add python.exe to PATH"** at the bottom of the first screen.*
- An internet connection (the character's files are downloaded for you)

<br>

## Supported Games

| Game | Mod Loader | The word to type |
| --- | --- | --- |
| GI | GIMI | `gimi` |
| WuWa | WWMI | `wwmi` |

<br>

> [!TIP]
> **Just want the mod?** Every character's identity mod is already made for you in the
> [Mods](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/blob/main/Mods/README.md) folder.
> That page also lists every character's name you can type below.

<br>

## How to Run
- Choose your pick of which way to run it:

  - **Choice A:** &nbsp; [Quickstart!](#choice-a-lets-start--) 🟢 &nbsp;&nbsp; (for beginners)
  - **Choice B:** &nbsp; [CMD WITHOUT a Script](#choice-b-run-on-cmd-without-a-script-) 🟡 &nbsp;&nbsp; (recommended if you run by CMD)
  - **Choice C:** &nbsp; [CMD with a Script](#choice-c-run-on-cmd-with-a-script-) 🟡 &nbsp;&nbsp; (the convention that other GIMI scripts follow)
  - **Choice D:** &nbsp; [API](#choice-d-api-usage-) 🟠 &nbsp;&nbsp; (for expert coders)

<br>

## Choice A: Let's Start ! 🟢
### STEP 1:
- Right-click [AGIDMGen.py](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/raw/main/AGIDMGen/script%20build/src/AGIDMGen/AGIDMGen.py), choose **"Save link as..."**, and save the script into GIMI's or WWMI's `Mods` folder.

### STEP 2:
- Double click on the script, and answer its two questions:
  - **Which game?** Type `gimi` for GI or `wwmi` for WuWa, then enter
  - **Which characters?** Type the character's name (eg. `Yelan`), then enter. For several characters, put a space between their names. For every character, type `all`.

- A new folder with the character's name (eg. `Yelan`) appears beside the script, holding the mod. When the script says `== Press ENTER to exit ==`, press enter.

> [!TIP]
> Copy the character's name as it is written in the [Mods list](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/blob/main/Mods/README.md).
> The new folder is named exactly as you typed it.

> [!NOTE]
> The first run installs what the script needs (numpy, and [AG Remap's API](https://pypi.org/project/FixRaidenBoss2/)), so it
> takes a little longer. Later runs skip that.

### STEP 3:
- Open the game and enjoy it

<br>

## Choice B: Run on CMD Without a Script 🟡
### STEP 1:
- Install the generator onto your computer by [opening cmd](https://www.google.com/search?q=how+to+open+cmd+in+a+folder&oq=how+to+open+cmd) and typing:
```bash
python -m pip install -U AGIDMGen
```
then enter

*( you can now run the program anywhere without copying a script! )*

### STEP 2:
- [open cmd](https://www.google.com/search?q=how+to+open+cmd+in+a+folder&oq=how+to+open+cmd) in GIMI's or WWMI's `Mods` folder and type the game's word, the character's name, then `--download`:
```bash
python -m AGIDMGen gimi Yelan --download
```
then enter

*( or type only `python -m AGIDMGen`, and it asks you, as in [Choice A](#choice-a-lets-start--) )*

### STEP 3:
- Open the game and enjoy it

<br>

## Choice C: Run on CMD With a Script 🟡
### STEP 1:
- Get the script, as in [Choice A's STEP 1](#choice-a-lets-start--)

### STEP 2:
- [open cmd](https://www.google.com/search?q=how+to+open+cmd+in+a+folder&oq=how+to+open+cmd) in that `Mods` folder and type `python AGIDMGen.py`, the game's word, the character's name, then `--download`.

  *eg. for Yelan in GI:*
```bash
python AGIDMGen.py gimi Yelan --download
```
then enter

  *eg. for Sanhua in WuWa:*
```bash
python AGIDMGen.py wwmi Sanhua --download
```

> [!TIP]
> - Want several characters? Put a space between their names: `python AGIDMGen.py gimi Yelan YelanTranquil --download`
> - Want every character? Use `--all` instead of a name: `python AGIDMGen.py gimi --download --all`
> - Already have [GI-Model-Importer-Assets](https://github.com/SilentNightSound/GI-Model-Importer-Assets) or
>   [WWMI-Assets](https://github.com/SpectrumQT/WWMI-Assets)? Give the **full** path to the character's folder instead of
>   its name, without `--download`: `python AGIDMGen.py gimi "C:\path\to\GI-Model-Importer-Assets\PlayerCharacterData\Yelan"`

### STEP 3:
- Open the game and enjoy it

<br>
<br>

## Choice D: API Usage 🟠

Tool developers can make identity mods within their own code!

### API Setup

*Make sure you first install the module by typing into [cmd](https://www.google.com/search?q=how+to+open+cmd+in+a+folder&oq=how+to+open+cmd):*
```bash
python -m pip install -U AGIDMGen
```
<br>

### API Example

```python
import AGIDMGen as IDMG
import FixRaidenBoss2 as FRB          # AG Remap's API: its logger works for both libraries

service = IDMG.IDModGenService(IDMG.ModLoaders.GIMI, names = ["Yelan", "YelanTranquil"], outputFolder = "Mods", logger = FRB.Logger())
service.generate()

print("Made:", sorted(service.stats.generated))
```

`IDModGenService` makes each mod into `<outputFolder>/<name>`, from download folders (`names = [...]`) or from asset
folders (`assetsFolders = [...]`). A character that fails does not stop the others: it is recorded in `service.stats`,
and nothing is printed unless you give it a logger.

<details>
<summary>More API examples</summary>
<br>

**In a server**, give each request its own logger, and either read what it wrote afterwards or forward each line as it
is written:

```python
class ForwardingLogger(FRB.BaseLogger):
    def write(self, message: str):
        send_to_frontend(message)          # eg. a websocket, a queue, a database row

    def read(self, desc: str) -> str:
        return ""                          # nothing interactive on a server

logger = FRB.Logger(logTxt = True, verbose = False)     # or: ForwardingLogger()
service = IDMG.IDModGenService(IDMG.ModLoaders.GIMI, names = ["Yelan"], outputFolder = folder, logger = logger)
service.generate()
transcript = logger.loggedTxt
```

**From asset folders:**

```python
service = IDMG.IDModGenService(IDMG.ModLoaders.WWMI, assetsFolders = ["WWMI-Assets/PlayerCharacterData/Sanhua"], outputFolder = "Mods")
service.generate()
```

**One character, directly.** Unlike the service, the generators raise an error when they fail:

```python
mod = IDMG.GIMIIdentityModGenerator().generate("GI-Model-Importer-Assets/PlayerCharacterData/Yelan", "Mods/Yelan")
mod = IDMG.WWMIIdentityModGenerator().generateFromRepo("Sanhua", "Mods/Sanhua", version = "2.5")
print("\n".join(mod.getSummary()))
```

**Every character with a download folder:** `IDMG.ModDownloader.getCharacters(IDMG.ModLoaders.GIMI)`

</details>

<br>
<br>

## Command Options
Add these after the character's name. The **Game** column says which game has the option.

| Options | Game | Description |
| --- | --- | --- |
| -h, --help | All | show the help message and exit |
| --download | All | the names typed are characters' names: download their files and make their mods from them |
| --all | All | with `--download`: make the mod of every character |
| --out folder | All | the folder the mods are made in, as `<folder>/<name>`. If this option is not specified, then the mods are made in the current folder. |
| --version str | All | with `--download`: the game version wanted, eg. `4.0`. If this option is not specified, then the newest version is used. |
| --name str | All | the character's name inside the mod (one character only) |
| --log folder | All | also write everything printed into `<folder>/IDModGenLog.txt` |
| --quiet | All | print only errors |
| --proxy str | All | with `--download`: the link to the proxy server, for those whose internet access must go through a proxy |
| --downloadFolder folder | All | with `--download`: keep the downloaded files in `<folder>/<name>`. If this option is not specified, then they are deleted afterwards. |
| --localData REPO=folder | All | with `--download`: copy the files of `AGRemap` or `AGIDMGen` from a copy of its `Data/Mod Downloads` folder on your computer, instead of downloading them (can be given more than once) |
| --noFix | GI | leave the `ORFix` / `NNFix` lines out of the mod |
| --faceRegister str | GI | the slot the face texture is bound to. If this option is not specified, then `ps-t0` is used (some 6.x skins need `ps-t1`). |
| --assetPrefix str | GI | what the asset folder's files start with, when that is not the folder's name (one asset folder only) |
| --textureFrom B=C:O[:plain\|normalMap] | GI | part `B`, which has no textures of its own, uses object `O` of part `C`'s textures, eg. `Bang=Body:A` (can be given more than once) |
| --author str | WuWa | the mod author WWMI shows. If this option is not specified, then `Anime Game Remap` is used. |
| --noTextures | WuWa | leave the textures out |
| --rawBones | WuWa | write bone indices as `vg_offset` + local index, instead of through the `vg_map` |

<br>

> [!NOTE]
> The command ends with exit code **0** when every mod was made, **1** when one could not be (or the options are not
> valid), and **2** when a WWMI mod's shape keys do not match its `Metadata.json`.

<br>
