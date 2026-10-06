#
# ===== downloadTools =====
#
# What populateDownloads.py and buildDownloadManifest.py share: where the download folders are, the
# aliases between the asset repos' names and the download folders', and how a folder's file prefix is
# found.
#

import json
import os
import sys
from typing import Dict, List, Optional

RepoRoot = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(RepoRoot, "AGIDMGen", "src", "py"))
import AGIDMGen as IDMG

# this repo's own download folders
OwnDownloads = os.path.join(RepoRoot, "Data", "Mod Downloads")
AliasesFile = os.path.join(OwnDownloads, "Aliases.json")

# the command line's name for each game, and its folder in Data/Mod Downloads
Games = {"gi": IDMG.ModLoaders.GIMI, "wuwa": IDMG.ModLoaders.WWMI}


def readAliases() -> Dict[str, Dict[str, str]]:
    """{game folder: {name in the asset repo: name of the download folder}}"""
    with open(AliasesFile, "r", encoding = "utf-8") as f:
        return json.load(f)


def getVersionFolders(charFolder: str) -> List[str]:
    """The version folders of a character's folder, oldest first"""
    if (not os.path.isdir(charFolder)):
        return []
    folders = []
    for name in os.listdir(charFolder):
        try:
            IDMG.VersionTools.parse(name)
        except IDMG.Error:
            continue
        if (os.path.isdir(os.path.join(charFolder, name))):
            folders.append(name)
    return sorted(folders, key = IDMG.VersionTools.parse)


def findPrefix(loader, files: List[str], hashOnly: bool = False) -> Optional[str]:
    """What a download folder's files start with: the name before its manifest (<prefix>Hash.json for GI,
    <prefix>Metadata.json for WuWa). With 'hashOnly' False, a GI folder with no Hash.json (one of AG Remap's)
    is read off its other files: <prefix>FaceDiffuse.dds, else the shortest <prefix>Position.buf"""
    manifest = IDMG.GIMIHashFileSuffix if (loader == IDMG.ModLoaders.GIMI) else "Metadata.json"
    found = sorted(f[:-len(manifest)] for f in files if f.endswith(manifest) and not f.endswith("TextureUsage.json"))
    if (found):
        return found[0]
    if (hashOnly or loader != IDMG.ModLoaders.GIMI):
        return None

    faces = sorted(f[:-len("FaceDiffuse.dds")] for f in files if f.endswith("FaceDiffuse.dds"))
    if (faces):
        return faces[0]
    positions = sorted((f[:-len("Position.buf")] for f in files if f.endswith("Position.buf")), key = len)
    return positions[0] if (positions) else None
