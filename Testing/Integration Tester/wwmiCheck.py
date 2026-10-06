#
# ===== wwmiCheck =====
#
# The acceptance checks of the WWMI identity mod generator, against data outside this repo:
#
#   py -3 wwmiCheck.py golden <WWMI-Assets/PlayerCharacterData> <AGRemap/Data/Mod Downloads/WuWa>
#       generate every character that has both an asset folder and an AGRemap download folder, and
#       compare its buffers byte for byte with the download folder's <Name><Buffer>.buf -- AGRemap's
#       committed copy of the identity mod's buffers. The download folder's <Name>Metadata.json is used
#       as the asset folder's Metadata.json (it carries 'export_format', which older WWMI-Assets lack).
#       --alias SanhuaExorcist=SanhuaSkin1 pairs a download folder with an asset folder named differently
#
#   py -3 wwmiCheck.py prototype <WWMI-Assets/PlayerCharacterData> <AGRemap/Tools/Misc/Prototypes/wwmiIdentityMod.py>
#       [--exportFormatFrom <a Metadata.json with export_format>] [--only Name ...]
#       run AGRemap's prototype and this library on every character and compare EVERY file they write.
#       mod.ini may differ only in the two lines that name the program that generated it. An asset
#       folder whose Metadata.json has no 'export_format' gets the one from --exportFormatFrom; both
#       programs then read the same input, so they must still agree byte for byte. A character both
#       programs refuse, with the same message, counts as agreeing
#
# Exits 1 on any difference, and when nothing was compared.
#

import argparse
import filecmp
import json
import os
import shutil
import sys
import tempfile

from checkTools import compareTrees, runPrototype, sameRefusal
import AGIDMGen as IDMG


# the lines of mod.ini that name the program that wrote it, which is all the two programs may disagree on
GeneratorLines = ('data = "The identity mod of ', "; This mod.ini is the IDENTITY mod of ")

# AGRemap's download folders name the TexCoord buffer 'Texcoord'
DownloadNames = {IDMG.WWMIBuffers.TexCoord: "Texcoord"}


def copyAssets(assetsFolder: str, dst: str, metadata: dict):
    os.makedirs(dst, exist_ok = True)
    for fileName in os.listdir(assetsFolder):
        if (fileName != "Metadata.json"):
            shutil.copy2(os.path.join(assetsFolder, fileName), os.path.join(dst, fileName))
    with open(os.path.join(dst, "Metadata.json"), "w", encoding = "utf-8") as f:
        json.dump(metadata, f)


def golden(args) -> int:
    compared = 0
    differences = 0
    aliases = dict(alias.split("=", 1) for alias in (args.alias or []))
    for name in sorted(os.listdir(args.downloads)):
        assetsFolder = os.path.join(args.assets, aliases.get(name, name))
        if (not os.path.isfile(os.path.join(assetsFolder, "Metadata.json"))):
            continue

        for version in sorted(os.listdir(os.path.join(args.downloads, name))):
            downloadFolder = os.path.join(args.downloads, name, version)
            metadataPath = os.path.join(downloadFolder, f"{name}Metadata.json")
            if (not os.path.isfile(metadataPath)):
                continue

            with open(metadataPath, "r", encoding = "utf-8") as f:
                metadata = json.load(f)

            with tempfile.TemporaryDirectory() as temp:
                assets = os.path.join(temp, name)
                copyAssets(assetsFolder, assets, metadata)
                try:
                    mod = IDMG.WWMIIdentityModGenerator(includeTextures = False).generate(assets, os.path.join(temp, "mod"), name = name)
                except IDMG.Error as e:
                    # the download folder may be for a game version the asset folder is not
                    print(f"{name} {version}: not generated ({e})")
                    continue

                for buffer in mod.bufferSizes:
                    expected = os.path.join(downloadFolder, f"{name}{DownloadNames.get(buffer, buffer.name)}.buf")
                    if (not os.path.isfile(expected)):
                        print(f"{name} {version}: {buffer.value} has no golden file")
                        differences += 1
                        continue
                    compared += 1
                    same = filecmp.cmp(os.path.join(temp, "mod", "Meshes", buffer.value), expected, shallow = False)
                    differences += 0 if same else 1
                    print(f"{name} {version}: {buffer.value} {'identical' if same else 'DIFFERENT'}")

    print(f"\n{compared} buffers compared, {differences} differences")
    return 1 if (differences or not compared) else 0


def prototype(args) -> int:
    exportFormat = None
    if (args.exportFormatFrom):
        with open(args.exportFormatFrom, "r", encoding = "utf-8") as f:
            exportFormat = json.load(f)["export_format"]

    compared = 0
    failed = []
    names = args.only or sorted(os.listdir(args.assets))
    for name in names:
        assetsFolder = os.path.join(args.assets, name)
        if (not os.path.isfile(os.path.join(assetsFolder, "Metadata.json"))):
            continue

        with open(os.path.join(assetsFolder, "Metadata.json"), "r", encoding = "utf-8") as f:
            metadata = json.load(f)
        if ("export_format" not in metadata and exportFormat is not None):
            metadata["export_format"] = exportFormat

        with tempfile.TemporaryDirectory() as temp:
            assets = os.path.join(temp, name)
            copyAssets(assetsFolder, assets, metadata)
            expectedRoot = os.path.join(temp, "prototype")
            resultRoot = os.path.join(temp, "library")

            prototypeError, stderr = runPrototype(args.prototype, [assets, expectedRoot])

            # the prototype's report reads 'keys[0]' of the shape keys, so a character with none
            #   (CarlottaHairCrystal) crashes it AFTER its mod is written: compare that mod anyway
            reportCrash = (prototypeError is not None and "keys[0]" in stderr and os.path.isfile(os.path.join(expectedRoot, "mod.ini")))
            if (reportCrash):
                prototypeError = None

            libraryError = None
            try:
                IDMG.WWMIIdentityModGenerator().generate(assets, resultRoot, name = name)
            except IDMG.Error as e:
                libraryError = str(e)

            if (prototypeError is not None or libraryError is not None):
                same = sameRefusal(prototypeError, libraryError)
                print(f"{name}: both refuse ({libraryError})" if same else f"{name}: DIFFERENT outcomes -- prototype: {prototypeError}; library: {libraryError}")
                if (not same):
                    failed.append(name)
                continue

            differences, count = compareTrees(expectedRoot, resultRoot, GeneratorLines)
            compared += count
            note = " (the prototype crashed in its report after writing the mod: no shape keys)" if (reportCrash) else ""
            print(f"{name}: {count} files, " + ("identical" if not differences else "DIFFERENT: " + "; ".join(differences)) + note)
            if (differences):
                failed.append(name)

    print(f"\n{compared} files compared; characters that differ: {', '.join(failed) if failed else 'none'}")
    return 1 if (failed or not compared) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description = "acceptance checks of the WWMI identity mod generator")
    commands = parser.add_subparsers(dest = "command", required = True)

    goldenParser = commands.add_parser("golden", help = "compare against AGRemap's committed download folders")
    goldenParser.add_argument("assets", help = "WWMI-Assets' PlayerCharacterData folder")
    goldenParser.add_argument("downloads", help = "AGRemap's 'Data/Mod Downloads/WuWa' folder")
    goldenParser.add_argument("--alias", nargs = "+", default = None, help = "DownloadName=AssetName, for a character the two repos name differently (eg. SanhuaExorcist=SanhuaSkin1)")

    prototypeParser = commands.add_parser("prototype", help = "compare against AGRemap's wwmiIdentityMod.py")
    prototypeParser.add_argument("assets", help = "WWMI-Assets' PlayerCharacterData folder")
    prototypeParser.add_argument("prototype", help = "AGRemap's Tools/Misc/Prototypes/wwmiIdentityMod.py")
    prototypeParser.add_argument("--exportFormatFrom", default = None, help = "a Metadata.json whose export_format is given to asset folders that have none")
    prototypeParser.add_argument("--only", nargs = "+", default = None, help = "only these characters")

    args = parser.parse_args()
    return golden(args) if (args.command == "golden") else prototype(args)


if (__name__ == "__main__"):
    sys.exit(main())
