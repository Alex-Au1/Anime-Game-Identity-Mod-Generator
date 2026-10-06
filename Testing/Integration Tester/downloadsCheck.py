#
# ===== downloadsCheck =====
#
# Proves the download folders: every character the library lists (AGIDMGen/data/ModDownloadData.py) is
# generated from its NEWEST download folder, read from local copies of both repositories, and compared with
# the same character generated from its asset folder:
#
#   py -3 downloadsCheck.py gi   <AGRemap/Data/Mod Downloads> --assets <GI-Model-Importer-Assets/PlayerCharacterData>
#   py -3 downloadsCheck.py wuwa <AGRemap/Data/Mod Downloads> --assets <WWMI-Assets/PlayerCharacterData>
#
# GI: every file must be identical, and the .ini apart from its last comment (what it was generated from).
# WuWa: every Meshes/ buffer must be identical, and the same texture hashes present -- a mod from a download
#   folder names its textures <prefix>Texture<hash>.dds, which cannot be turned back into the asset names.
#
# A character with no asset folder (AG Remap built it from a frame dump) is only generated, not compared;
# so is one whose newest folder is AG Remap's when the assets have moved on (it cannot be, after
# populateDownloads.py: the newer folder is the newest). Without --assets, nothing is compared.
#
# Exits 1 when a character fails to generate or differs, and when nothing was generated.
#

import argparse
import filecmp
import os
import sys
import tempfile

from checkTools import RepoRoot
import AGIDMGen as IDMG

OwnDownloads = os.path.join(RepoRoot, "Data", "Mod Downloads")
Games = {"gi": IDMG.ModLoaders.GIMI, "wuwa": IDMG.ModLoaders.WWMI}


def findAssetFolder(loader, assetsRoot: str, name: str):
    """The asset folder of a download folder's character: by its own name in any case, else by an alias that
    is an asset folder (an alias may also be just another name, like Raiden for RaidenShogun)"""
    if (assetsRoot is None):
        return None
    game = IDMG.ModDownloadGameFolders[loader]
    byName = {asset.lower(): asset for asset in os.listdir(assetsRoot) if os.path.isdir(os.path.join(assetsRoot, asset))}
    asset = byName.get(name.lower())
    if (asset is None):
        asset = next((byName[alias.lower()] for alias, folder in IDMG.ModDownloadAliases.get(game, {}).items() if folder == name and alias.lower() in byName), None)
    return None if (asset is None) else os.path.join(assetsRoot, asset)


def compareGIMI(fromAssets: str, fromDownload: str):
    differences = []
    for fileName in sorted(set(os.listdir(fromAssets)) | set(os.listdir(fromDownload))):
        a, b = os.path.join(fromAssets, fileName), os.path.join(fromDownload, fileName)
        if (not os.path.isfile(a) or not os.path.isfile(b)):
            differences.append(f"{fileName} in only one")
        elif (fileName.endswith(".ini")):
            with open(a, encoding = "utf-8") as fa, open(b, encoding = "utf-8") as fb:
                if (fa.read().splitlines()[:-2] != fb.read().splitlines()[:-2]):
                    differences.append(f"{fileName} differs")
        elif (not filecmp.cmp(a, b, shallow = False)):
            differences.append(f"{fileName} differs")
    return differences


def compareWWMI(fromAssets: str, fromDownload: str, modA, modB):
    differences = compareGIMI(os.path.join(fromAssets, "Meshes"), os.path.join(fromDownload, "Meshes"))
    if (sorted(h for _, h in modA.textures) != sorted(h for _, h in modB.textures)):
        differences.append("the texture hashes differ")
    return differences


def main() -> int:
    parser = argparse.ArgumentParser(description = "generate every character from its newest download folder, and compare it with its asset folder's mod")
    parser.add_argument("game", choices = sorted(Games))
    parser.add_argument("agRemap", help = "AG Remap's 'Data/Mod Downloads' folder")
    parser.add_argument("--assets", default = None, help = "the asset repo's PlayerCharacterData folder, to compare against")
    parser.add_argument("--only", nargs = "+", default = None, help = "only these characters")
    args = parser.parse_args()

    loader = Games[args.game]
    downloader = IDMG.ModDownloader(localFolders = {IDMG.ModDownloadRepos.AGRemap: args.agRemap, IDMG.ModDownloadRepos.AGIDMGen: OwnDownloads})
    Generator = IDMG.GIMIIdentityModGenerator if (loader == IDMG.ModLoaders.GIMI) else IDMG.WWMIIdentityModGenerator
    counts = {"identical": 0, "generated only": 0}
    failed = []

    for name in (args.only or IDMG.ModDownloader.getCharacters(loader)):
        try:
            download = IDMG.ModDownloader.find(loader, name)
        except IDMG.Error as e:
            failed.append(name)
            print(f"{name}: FAILED -- {e}", flush = True)
            continue

        with tempfile.TemporaryDirectory() as temp:
            fromDownload = os.path.join(temp, "download")
            try:
                modB = Generator().generateFromRepo(name, fromDownload, downloader = downloader)
            except IDMG.Error as e:
                failed.append(name)
                print(f"{name} {download.version}: FAILED -- {e}", flush = True)
                continue

            assetsFolder = findAssetFolder(loader, args.assets, download.name)
            label = f"{name} {download.version} ({', '.join(sorted(set(r.name for r in download.files.values())))})"
            if (assetsFolder is None):
                counts["generated only"] += 1
                print(f"{label}: generated; no asset folder to compare with", flush = True)
                continue

            fromAssets = os.path.join(temp, "assets")
            try:
                if (loader == IDMG.ModLoaders.GIMI):
                    Generator().generate(assetsFolder, fromAssets, name = download.prefix, assetPrefix = None)
                    differences = compareGIMI(fromAssets, fromDownload)
                else:
                    modA = Generator().generate(assetsFolder, fromAssets, name = download.prefix)
                    differences = compareWWMI(fromAssets, fromDownload, modA, modB)
            except IDMG.Error as e:
                counts["generated only"] += 1
                print(f"{label}: generated; its asset folder cannot be built from ({e})", flush = True)
                continue

            if (differences):
                failed.append(name)
            else:
                counts["identical"] += 1
            print(f"{label}: " + ("identical to the asset folder's mod" if not differences else "DIFFERENT: " + "; ".join(differences[:6])), flush = True)

    print(f"\n{counts['identical']} identical to their asset folder's mod, {counts['generated only']} generated only; failed or different: {', '.join(failed) if failed else 'none'}")
    return 1 if (failed or not sum(counts.values())) else 0


if (__name__ == "__main__"):
    sys.exit(main())
