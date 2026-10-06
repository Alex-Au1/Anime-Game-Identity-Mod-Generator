#
# ===== populateDownloads =====
#
# Fills this repo's Data/Mod Downloads from an asset repo, keeping nothing AG Remap already has:
#
#   py -3 Tools/Downloads/populateDownloads.py gi   <GI-Model-Importer-Assets/PlayerCharacterData> <AGRemap/Data/Mod Downloads> --version 6_8
#   py -3 Tools/Downloads/populateDownloads.py wuwa <WWMI-Assets/PlayerCharacterData>              <AGRemap/Data/Mod Downloads> --version 2_7
#
# For each character of the asset repo (named as Data/Mod Downloads/Aliases.json says, or as AG Remap
# names it in any case, or as the asset repo does), its download folder is built and compared with AG
# Remap's newest folder for that character:
#
#   * AG Remap's folder has every file, byte for byte  -> only what AG Remap lacks is written here, into
#     the SAME version folder: a GI character's <prefix>Hash.json, and nothing at all for WuWa
#   * anything differs, or AG Remap has no folder    -> the whole folder is written here, under --version
#     (the game version the asset repo is at)
#
# Then run buildDownloadManifest.py, so the library knows about the folders.
#
#   --only Name ...   only these asset folders
#   --dryRun          write nothing; report what would be written
#

import argparse
import filecmp
import os
import shutil
import sys
import tempfile

from downloadTools import Games, OwnDownloads, readAliases, getVersionFolders, findPrefix
import AGIDMGen as IDMG


def build(loader, assetsFolder: str, out: str, prefix: str):
    if (loader == IDMG.ModLoaders.GIMI):
        return IDMG.GIMIDownloadFolderBuilder().build(assetsFolder, out, prefix)
    return IDMG.WWMIDownloadFolderBuilder().build(assetsFolder, out, prefix)


def main() -> int:
    parser = argparse.ArgumentParser(description = "fill Data/Mod Downloads from an asset repo, keeping nothing AG Remap already has")
    parser.add_argument("game", choices = sorted(Games), help = "the game of the asset repo")
    parser.add_argument("assets", help = "the asset repo's PlayerCharacterData folder")
    parser.add_argument("agRemap", help = "AG Remap's 'Data/Mod Downloads' folder")
    parser.add_argument("--version", required = True, help = "the version folder new download folders go into (the game version the asset repo is at), eg. 6_8")
    parser.add_argument("--only", nargs = "+", default = None, help = "only these asset folders")
    parser.add_argument("--dryRun", action = "store_true", help = "write nothing")
    args = parser.parse_args()

    loader = Games[args.game]
    game = IDMG.ModDownloadGameFolders[loader]
    IDMG.VersionTools.parse(args.version)
    aliases = readAliases().get(game, {})
    manifest = "hash.json" if (loader == IDMG.ModLoaders.GIMI) else "Metadata.json"

    agGame = os.path.join(args.agRemap, game)
    agNames = {name.lower(): name for name in os.listdir(agGame)} if (os.path.isdir(agGame)) else {}
    results = {"hash only": [], "nothing": [], "new": [], "newer than AG Remap": [], "failed": []}

    for assetName in (args.only or sorted(os.listdir(args.assets))):
        assetsFolder = os.path.join(args.assets, assetName)
        if (not os.path.isfile(os.path.join(assetsFolder, manifest))):
            continue

        name = aliases.get(assetName, agNames.get(assetName.lower(), assetName))
        agVersions = getVersionFolders(os.path.join(agGame, name))
        agVersion = agVersions[-1] if (agVersions) else None
        agFolder = os.path.join(agGame, name, agVersion) if (agVersion) else None
        agFiles = sorted(os.listdir(agFolder)) if (agFolder) else []
        prefix = (findPrefix(loader, agFiles) if (agFolder) else None) or name

        with tempfile.TemporaryDirectory() as temp:
            try:
                written = build(loader, assetsFolder, temp, prefix)
            except IDMG.Error as e:
                results["failed"].append(f"{assetName}: {e}")
                print(f"{assetName}: FAILED -- {e}", flush = True)
                continue

            extra = [f"{prefix}{IDMG.GIMIHashFileSuffix}"] if (loader == IDMG.ModLoaders.GIMI) else []
            differences = []
            if (agFolder):
                differences += [f for f in agFiles if f not in written or not filecmp.cmp(os.path.join(temp, f), os.path.join(agFolder, f), shallow = False)]
                differences += [f for f in written if f not in agFiles and f not in extra]

            if (agFolder and not differences):
                kind = "hash only" if (extra) else "nothing"
                target = os.path.join(OwnDownloads, game, name, agVersion)
                files = extra
            else:
                kind = "newer than AG Remap" if (agFolder) else "new"
                target = os.path.join(OwnDownloads, game, name, args.version)
                files = written

            note = f" (AG Remap's {agVersion} differs in {len(differences)} files: {', '.join(differences[:4])}{' ...' if len(differences) > 4 else ''})" if (differences) else ""
            results[kind].append(name)
            print(f"{assetName} -> {game}/{name}: {kind}, {len(files)} files into {os.path.relpath(target, OwnDownloads) if files else '-'}{note}", flush = True)

            if (files and not args.dryRun):
                os.makedirs(target, exist_ok = True)
                for fileName in files:
                    shutil.copyfile(os.path.join(temp, fileName), os.path.join(target, fileName))

    print()
    for kind, names in results.items():
        print(f"{kind}: {len(names)}" + (f" -- {', '.join(names)}" if (names and kind != 'failed') else ""))
    for failure in results["failed"]:
        print(f"  {failure}")
    return 0


if (__name__ == "__main__"):
    sys.exit(main())
