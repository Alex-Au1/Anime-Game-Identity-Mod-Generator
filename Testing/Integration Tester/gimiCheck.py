#
# ===== gimiCheck =====
#
# The acceptance checks of the GIMI identity mod generator, against data outside this repo:
#
#   py -3 gimiCheck.py golden <GI-Model-Importer-Assets/PlayerCharacterData> <AGRemap/Data/Mod Downloads/GI>
#       generate every character that has both an asset folder and an AGRemap download folder, and
#       compare every .buf and .ib of each of its download folders (<Name>/<X_Y>) byte for byte. A
#       download folder holds the identity mod's buffers for one game version, while the asset folder is
#       the asset repo's current one: a folder for an OLDER version may differ because the game changed,
#       so every folder is reported, and only a character none of whose folders matches is a failure
#
#   py -3 gimiCheck.py prototype <GI-Model-Importer-Assets/PlayerCharacterData> <AGRemap/Tools/Misc/Prototypes/identityMod.py> [--only Name ...] [--extra "OPTIONS"]
#       run AGRemap's prototype (which needs AGRemap's compiled FixRaidenBoss2) and this library on every
#       character and compare EVERY file they write. Both get the same --extra options (the prototype's
#       own: --name, --assetPrefix, --noFix, --faceRegister, --textureFrom), default none. The .ini may differ only in
#       its last comment, which names the program that generated it. A character both programs refuse,
#       with the same message, counts as agreeing
#
# Exits 1 on any failure, and when nothing was compared.
#

import argparse
import shlex
import filecmp
import os
import sys
import tempfile

from checkTools import compareTrees, runPrototype, sameRefusal
import AGIDMGen as IDMG


# the line of the .ini that names the program that wrote it
GeneratorLines = ("; the identity mod of ",)


def golden(args) -> int:
    compared = 0
    failed = []
    for name in sorted(os.listdir(args.downloads)):
        assetsFolder = os.path.join(args.assets, name)
        downloadRoot = os.path.join(args.downloads, name)
        if (not os.path.isfile(os.path.join(assetsFolder, "hash.json")) or not os.path.isdir(downloadRoot)):
            continue

        with tempfile.TemporaryDirectory() as temp:
            try:
                IDMG.GIMIIdentityModGenerator().generate(assetsFolder, temp, name = name)
            except IDMG.Error as e:
                print(f"{name}: not generated ({e})")
                failed.append(name)
                continue

            matched = False
            for version in sorted(os.listdir(downloadRoot)):
                downloadFolder = os.path.join(downloadRoot, version)
                if (not os.path.isdir(downloadFolder)):
                    continue

                files = sorted(f for f in os.listdir(downloadFolder) if f.lower().endswith((".buf", ".ib")))
                differences = []
                for fileName in files:
                    result = os.path.join(temp, fileName)
                    if (not os.path.isfile(result)):
                        differences.append(f"{fileName} not generated")
                    elif (not filecmp.cmp(result, os.path.join(downloadFolder, fileName), shallow = False)):
                        differences.append(f"{fileName} differs")

                compared += len(files)
                matched = matched or (files and not differences)
                print(f"{name} {version}: {len(files)} buffers, " + ("identical" if not differences else "DIFFERENT: " + "; ".join(differences)))

            if (not matched):
                failed.append(name)

    print(f"\n{compared} buffers compared; characters with no matching download folder: {', '.join(failed) if failed else 'none'}")
    return 1 if (failed or not compared) else 0


def parseExtra(extra: str):
    # the prototype's options, turned into the library's arguments
    parser = argparse.ArgumentParser(prog = "--extra")
    parser.add_argument("--name", default = None)
    parser.add_argument("--assetPrefix", default = None)
    parser.add_argument("--noFix", action = "store_true")
    parser.add_argument("--faceRegister", default = "ps-t0")
    parser.add_argument("--textureFrom", action = "append", default = None)
    options = parser.parse_args(shlex.split(extra))

    generator = IDMG.GIMIIdentityModGenerator(includeFix = not options.noFix, faceRegister = options.faceRegister,
                                              textureSources = dict(IDMG.GIMITextureSource.parse(value) for value in (options.textureFrom or [])))
    return generator, {"name": options.name, "assetPrefix": options.assetPrefix}


def prototype(args) -> int:
    generator, generateArgs = parseExtra(args.extra)
    compared = 0
    failed = []
    names = args.only or sorted(os.listdir(args.assets))
    for name in names:
        assetsFolder = os.path.join(args.assets, name)
        if (not os.path.isfile(os.path.join(assetsFolder, "hash.json"))):
            continue

        with tempfile.TemporaryDirectory() as temp:
            expectedRoot = os.path.join(temp, "prototype")
            resultRoot = os.path.join(temp, "library")
            prototypeError, _ = runPrototype(args.prototype, [assetsFolder, expectedRoot] + shlex.split(args.extra))

            libraryError = None
            try:
                generator.generate(assetsFolder, resultRoot, **generateArgs)
            except IDMG.Error as e:
                libraryError = str(e)

            if (prototypeError is not None or libraryError is not None):
                same = sameRefusal(prototypeError, libraryError)
                print(f"{name}: both refuse ({libraryError})" if same else f"{name}: DIFFERENT outcomes -- prototype: {prototypeError}; library: {libraryError}", flush = True)
                if (not same):
                    failed.append(name)
                continue

            differences, count = compareTrees(expectedRoot, resultRoot, GeneratorLines)
            compared += count
            print(f"{name}: {count} files, " + ("identical" if not differences else "DIFFERENT: " + "; ".join(differences)), flush = True)
            if (differences):
                failed.append(name)

    print(f"\n{compared} files compared; characters that differ: {', '.join(failed) if failed else 'none'}")
    return 1 if (failed or not compared) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description = "acceptance checks of the GIMI identity mod generator")
    commands = parser.add_subparsers(dest = "command", required = True)

    goldenParser = commands.add_parser("golden", help = "compare against AGRemap's committed download folders")
    goldenParser.add_argument("assets", help = "GI-Model-Importer-Assets' PlayerCharacterData folder")
    goldenParser.add_argument("downloads", help = "AGRemap's 'Data/Mod Downloads/GI' folder")

    prototypeParser = commands.add_parser("prototype", help = "compare against AGRemap's identityMod.py")
    prototypeParser.add_argument("assets", help = "GI-Model-Importer-Assets' PlayerCharacterData folder")
    prototypeParser.add_argument("prototype", help = "AGRemap's Tools/Misc/Prototypes/identityMod.py")
    prototypeParser.add_argument("--only", nargs = "+", default = None, help = "only these characters")
    prototypeParser.add_argument("--extra", default = "", help = "options given to both programs, eg. \"--noFix --faceRegister ps-t1\"")

    args = parser.parse_args()
    return golden(args) if (args.command == "golden") else prototype(args)


if (__name__ == "__main__"):
    sys.exit(main())
