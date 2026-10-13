# Anime Game Identity Mod Generator (AGIDMGen)
[![PyPI](https://img.shields.io/pypi/pyversions/AGIDMGen?style=for-the-badge)](https://www.python.org/downloads/)

[![PyPI - Version](https://img.shields.io/pypi/v/AGIDMGen?label=AGIDMGen%20pypi&style=for-the-badge)](https://pypi.org/project/AGIDMGen/)

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
| [![The Sub-Council](https://raw.githubusercontent.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/main/Docs/src/_static/images/TheCouncilofClaudeAgentsBadgeMini.svg)](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/blob/main/AI%20Agent%20Help/README.md) *(Maintainer Team)* | [![The Sub-Council Badge](https://raw.githubusercontent.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/main/Docs/src/_static/images/TheCouncilofClaudeAgentsBadgeWithCount.svg)](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/blob/main/AI%20Agent%20Help/README.md) |

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
- Double click on the script, and answer its question:
  - **Which characters?** Type the character's name (eg. `Yelan`), then enter. For several characters, put a space between their names: they can be of both games (eg. `Zani Ayaka`). For every character, type `all`.

- A new folder for each character (eg. `Yelan`) appears beside the script, holding the mod. When the script says `== Press ENTER to exit ==`, press enter. Copy a GI mod into GIMI's `Mods` folder, and a WuWa mod into WWMI's.

> [!TIP]
> A character's name is not case sensitive, and any of its other names work too (eg. `ei` for `Raiden`): see the
> [Mods list](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/blob/main/Mods/README.md).
> The new folder is always named by the mod's name (`ei` makes `Raiden`).

> [!NOTE]
> The first run downloads the generator, [AGIDMGen](https://pypi.org/project/AGIDMGen/) (with numpy and
> [AG Remap's API](https://pypi.org/project/FixRaidenBoss2/)), so it takes a little longer. Later runs only check for a
> newer version.

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
- [open cmd](https://www.google.com/search?q=how+to+open+cmd+in+a+folder&oq=how+to+open+cmd) in GIMI's or WWMI's `Mods` folder and type the character's name:
```bash
python -m AGIDMGen Yelan
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
- [open cmd](https://www.google.com/search?q=how+to+open+cmd+in+a+folder&oq=how+to+open+cmd) in that `Mods` folder and type `python AGIDMGen.py`, then the character's name. The game is found from the character's name.

  *eg. for Yelan in GI:*
```bash
python AGIDMGen.py Yelan
```
then enter

  *eg. for Sanhua in WuWa:*
```bash
python AGIDMGen.py Sanhua
```

> [!TIP]
> - Want several characters, of either game? Put a space between their names: `python AGIDMGen.py Zani Ayaka YelanTranquil`
> - Want every character? Use `--all` instead of a name: `python AGIDMGen.py --all`. For one game's only, add `--game GI` or `--game WuWa`
> - Already have [GI-Model-Importer-Assets](https://github.com/SilentNightSound/GI-Model-Importer-Assets) or
>   [WWMI-Assets](https://github.com/SpectrumQT/WWMI-Assets)? Give the **full** path to the character's folder instead of
>   its name: `python AGIDMGen.py "C:\path\to\GI-Model-Importer-Assets\PlayerCharacterData\Yelan"`

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

service = IDMG.IDModGenService(names = ["Yelan", "YelanTranquil", "Zani"], outputFolder = "Mods", logger = FRB.Logger())
service.generate()

print("Made:", sorted(service.stats.generated))
```

`IDModGenService` makes each mod into `<outputFolder>/<name>`, from download folders (`names = [...]`) or from asset
folders (`assetsFolders = [...]`), of both games: each character's game is found from its name (`Zani` is WuWa's). A character that fails does not stop the others: it is recorded in `service.stats`,
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
service = IDMG.IDModGenService(names = ["Yelan"], outputFolder = folder, logger = logger)
service.generate()
transcript = logger.loggedTxt
```

**From asset folders:**

```python
service = IDMG.IDModGenService(assetsFolders = ["WWMI-Assets/PlayerCharacterData/Sanhua"], outputFolder = "Mods")
service.generate()
```

**One character, directly.** Unlike the service, the generators raise an error when they fail:

```python
mod = IDMG.GIMIIdentityModGenerator().generate("GI-Model-Importer-Assets/PlayerCharacterData/Yelan", "Mods/Yelan")
mod = IDMG.WWMIIdentityModGenerator().generateFromRepo("Sanhua", "Mods/Sanhua", version = "2.5")
print("\n".join(mod.getSummary()))
```

**Every character with a download folder:** `[modName.name for modName in IDMG.ModNames.getAll()]` (or `IDMG.ModNames.getAll([IDMG.ModLoaders.GIMI])` for one game's)

</details>

<br>
<br>

## Command Options
Type the characters' names, of either game (eg. `python -m AGIDMGen Zani Ayaka ei`), then any of these. Each character's
game is found from its name, and its files are downloaded. The **Game** column says which game's mods an option is for.

| Options | Game | Description |
| --- | --- | --- |
| -h, --help | All | show the help message and exit |
| --game GI,WuWa | All | look the names up only in these games, separated by commas (`GI`, `Genshin`, `WuWa`, `WutheringWaves`, `GIMI`, `WWMI`). If this option is not specified, then every game is. |
| --all | All | make the mod of every character (of the `--game` games, if given) |
| --out folder | All | the folder the mods are made in, as `<folder>/<name>`. If this option is not specified, then the mods are made in the current folder. |
| --version str | All | for downloaded characters: the game version wanted, eg. `4.0`. If this option is not specified, then the newest version is used. |
| --nameReplace CHARACTER:NEWNAME,... | All | new names for some of the characters, written into their mods instead of their usual names, eg. `--nameReplace "ei:Raiden1, Zani:Shorty"`. `CHARACTER` is any name or alias of a character being made, a character's base name for all its parts (`Carlotta:Shorty` makes `CarlottaBody` `ShortyBody`), or an asset folder's name. If a character is given twice, the later new name wins. A pair for no character being made, or that cannot be used, is skipped, and the run says so. |
| --log folder | All | also write everything printed into `<folder>/IDModGenLog.txt` |
| --quiet | All | print only errors |
| --proxy str | All | for downloaded characters: the link to the proxy server, for those whose internet access must go through a proxy |
| --downloadFolder folder | All | for downloaded characters: keep the downloaded files in `<folder>/<name>`. If this option is not specified, then they are deleted afterwards. |
| --localData REPO=folder | All | for downloaded characters: copy the files of `AGRemap` or `AGIDMGen` from a copy of its `Data/Mod Downloads` folder on your computer, instead of downloading them (can be given more than once) |
| --noFix | GI | leave the `ORFix` / `NNFix` lines out of the mod |
| --faceRegister str | GI | the slot the face texture is bound to. If this option is not specified, then `ps-t1` is used, where GI 6.0 and newer read it (`ps-t0` is for older versions, and on 6.x it gives white cheeks). |
| --assetPrefix str | GI | what the asset folder's files start with, when that is not the folder's name (one asset folder only) |
| --textureFrom B=C:O[:plain\|normalMap] | GI | part `B`, which has no textures of its own, uses object `O` of part `C`'s textures, eg. `Bang=Body:A` (can be given more than once) |
| --author str | WuWa | the mod author WWMI shows. If this option is not specified, then `AGIDMGen` is used. |
| --noTextures | WuWa | leave the textures out |
| --rawBones | WuWa | write bone indices as `vg_offset` + local index, instead of through the `vg_map` |

<br>

> [!NOTE]
> The command ends with exit code **0** when every mod was made, **1** when one could not be (or the options are not
> valid), and **2** when a WWMI mod's shape keys do not match its `Metadata.json`.

<br>
