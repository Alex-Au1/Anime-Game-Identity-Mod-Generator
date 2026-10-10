# AGIDMGen

**Anime Game Identity Mod Generator** -- generates *identity mods*: a character's own, unmodified model
written out as a mod (every object, vertex group, texture and material band of the real model in one
folder), for 3DMigoto-based mod loaders.

A sub-project of [Anime Game Remap (AG Remap)](https://github.com/nhok0169/Anime-Game-Remap).

## Supported mod loaders

| Loader | Game |
| --- | --- |
| GIMI | Genshin Impact |
| WWMI | Wuthering Waves |

## Installation

```bash
pip install AGIDMGen
```

Requires Python 3.9 or newer.

## Usage

### The service: `IDModGenService`

The library's entry point, as Anime Game Remap's is `RemapService`: it generates several characters' identity mods
at once, each into `<outputFolder>/<name>`, from their **asset folders** or from their **download folders**. A
character that cannot be generated does not stop the others; `service.stats` holds every mod generated and every
exception, and nothing is printed unless you give it a logger.

```python
import AGIDMGen as IDMG
import FixRaidenBoss2 as FRB          # Anime Game Remap's API: its logger serves both libraries

# from download folders: no asset repo needed
service = IDMG.IDModGenService(IDMG.ModLoaders.GIMI, names = ["Yelan", "YelanTranquil"], outputFolder = "Mods", logger = FRB.Logger())
service.generate()
print(sorted(service.stats.generated), service.stats.skipped)

# from asset folders
service = IDMG.IDModGenService(IDMG.ModLoaders.WWMI, assetsFolders = ["WWMI-Assets/PlayerCharacterData/Sanhua"], outputFolder = "Mods")
service.generate()
```

**In a server**, give each request its own logger, and either read the transcript afterwards or forward each line as
it is written:

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

The logger is Anime Game Remap's own (`FixRaidenBoss2.BaseLogger` / `Logger`), so one logger serves both libraries.

### Download folders

Each download folder file is taken from [Anime Game Remap](https://github.com/nhok0169/Anime-Game-Remap)'s
`Data/Mod Downloads` if it has it, and from this repository's otherwise; the newest game version is used unless you
ask for one (`version = "4.0"`). `IDMG.ModDownloader.getCharacters(IDMG.ModLoaders.GIMI)` lists every character.
Downloading uses Anime Game Remap's `FixRaidenBoss2` package.

### The command line

```bash
python -m AGIDMGen gimi Yelan YelanTranquil --download --out Mods
python -m AGIDMGen wwmi --download --all --out Mods --log Mods
python -m AGIDMGen gimi "GI-Model-Importer-Assets/PlayerCharacterData/Yelan" --out Mods
python -m AGIDMGen wwmi "WWMI-Assets/PlayerCharacterData/Sanhua" --out Mods --noTextures
```

The sources are asset folders, or with `--download` characters' names. Every mod is written into `<out>/<name>`.

| Option | Does |
| --- | --- |
| `--out F` | the folder the mods are written into (default: the current folder) |
| `--download` | the sources are characters' names: generate from their download folders |
| `--all` | with `--download`: every character that has a download folder |
| `--version V` | with `--download`: the game version wanted (default: the newest) |
| `--localData REPO=F` | with `--download`: copy `AGRemap` / `AGIDMGen`'s files from a local copy of its `Data/Mod Downloads` (repeatable) |
| `--downloadFolder F` | with `--download`: keep the downloaded files in `F/<name>` |
| `--proxy P` | with `--download`: the proxy to download through |
| `--name N` | the character's name in the mod (one character only) |
| `--log F` | also write everything printed into `F/IDModGenLog.txt` |
| `--quiet` | print only errors |

GIMI only:

| Option | Does |
| --- | --- |
| `--assetPrefix P` | what the asset folder's files start with, when that is not the folder's name (one asset folder only) |
| `--noFix` | leave the `ORFix` / `NNFix` `run =` lines out |
| `--faceRegister R` | the register the face diffuse is bound to (default `ps-t0`; some 6.x skins use `ps-t1`) |
| `--textureFrom B=C:O[:plain\|normalMap]` | component `B`, which has no textures of its own, binds object `O` of component `C`'s textures (repeatable) |

WWMI only:

| Option | Does |
| --- | --- |
| `--author A` | the mod author WWMI shows (default: `Anime Game Remap`) |
| `--noTextures` | leave the textures out |
| `--rawBones` | write bone indices as `vg_offset` + local index instead of through the `vg_map` |

The command exits with 0 when every mod was generated, 1 when one could not be (or the arguments are not valid), and
2 when a WWMI mod's shape keys do not match its `Metadata.json`.

### One character, directly

The generators can also be used on their own; unlike the service, they raise when they fail:

```python
mod = IDMG.GIMIIdentityModGenerator().generate("GI-Model-Importer-Assets/PlayerCharacterData/Yelan", "Mods/Yelan")
mod = IDMG.WWMIIdentityModGenerator().generateFromRepo("Sanhua", "Mods/Sanhua", version = "2.5")
print("\n".join(mod.getSummary()))
```

The asset folders are laid out as [GI-Model-Importer-Assets](https://github.com/SilentNightSound/GI-Model-Importer-Assets)'
and [WWMI-Assets](https://github.com/SpectrumQT/WWMI-Assets)' `PlayerCharacterData/<Name>` folders are.
