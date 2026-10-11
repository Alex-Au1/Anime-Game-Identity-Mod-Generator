# Anime Game Identity Mod Generator (AGIDMGen)
[![PyPI](https://img.shields.io/pypi/pyversions/AGIDMGen?style=for-the-badge)](https://www.python.org/downloads/)

[![PyPI - Version](https://img.shields.io/pypi/v/AGIDMGen?label=AGIDMGen%20pypi&style=for-the-badge)](https://pypi.org/project/AGIDMGen/)

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Alex-Au1/Anime-Game-Identity-Mod-Generator/tests.yml?branch=main&label=Unit%2FIntegration%20Tests&style=for-the-badge)](https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/actions/workflows/tests.yml)

<br>

The library that generates ***identity mods***: a character's own, unmodified model written out as a
mod, with every object, vertex group, texture and material band of the real model in one folder.

A sub-project of [Anime Game Remap (AG Remap)](https://github.com/nhok0169/Anime-Game-Remap).

<br>

## Contributors
|   |   |
|---|---|
| **[Albert Gold](https://github.com/Alex-Au1)** *(Active Lead Maintainer)* | [![@albertgold](https://dcbadge.limes.pink/api/shield/367087171154214914?theme=discord-inverted)](https://discord.com/users/367087171154214914) |
| [![The Council](Docs/src/_static/images/TheCouncilofClaudeAgentsBadgeMini.svg)](AI%20Agent%20Help/README.md) *(Maintainer Team)* | [![The Council Badge](Docs/src/_static/images/TheCouncilofClaudeAgentsBadgeWithCount.svg)](AI%20Agent%20Help/README.md) |

<br>

## Supported Mod Loaders

| Loader | Game |
| --- | --- |
| GIMI | GI |
| WWMI | WuWa |

<br>

## Pre-generated Mods
Don't want to run the library? Every character's identity mod is ready-made in the [Mods](Mods/README.md) folder:
144 GI (GIMI) and 54 WuWa (WWMI) characters. Clone with [Git LFS](https://git-lfs.com) installed.

<br>

## Run It Without Installing
Don't know how to install a Python package? The whole library is also a single script,
[AGIDMGen.py](AGIDMGen/script%20build/src/AGIDMGen/AGIDMGen.py). Install [Python](https://www.python.org/downloads/), download the
script, and run:

```bash
python AGIDMGen.py gimi Albedo --download
```

See the [script's README](AGIDMGen/script%20build/README.md) for the details.

<br>

## How To Run:
See the [library's README](AGIDMGen/api/README.md).

