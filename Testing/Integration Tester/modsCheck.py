#
# ===== modsCheck =====
#
# Regenerates characters' identity mods from their download folders and compares them with the committed
# Mods/ -- the golden output. It is the integration test CI runs:
#
#   py -3 modsCheck.py                        the sample below, every file downloaded from GitHub
#   py -3 modsCheck.py --all                  every character in Mods/
#   py -3 modsCheck.py --names gi:Yelan wuwa:Sanhua [--localData AGRemap=<folder> --localData AGIDMGen=<folder>]
#
# Mods/' binaries are in Git LFS. When the checkout has only their POINTER files (a clone without LFS, as CI
# makes it), each binary is checked against the sha256 and size its pointer records, so the check never
# downloads Mods/ from LFS; otherwise the bytes are compared. Every .ini is compared byte for byte.
#
# Exits 1 on any difference, and when nothing was compared.
#

import argparse
import hashlib
import os
import sys
import tempfile

from checkTools import RepoRoot
import AGIDMGen as IDMG

ModsFolder = os.path.join(RepoRoot, "Mods")
Games = {"gi": IDMG.ModLoaders.GIMI, "wuwa": IDMG.ModLoaders.WWMI}

# what each one exercises:
#   Yelan          AG Remap's files, this repo's Hash.json
#   YelanTranquil  several components, texture donors from AG Remap's parser config
#   Razor          every file this repo's, through Git LFS
#   Sanhua         AG Remap's files only
#   Lynae          eight weights a vertex, three blend remaps
Sample = ["gi:Yelan", "gi:YelanTranquil", "gi:Razor", "wuwa:Sanhua", "wuwa:Lynae"]


def readPointer(path: str):
    """(sha256, size) out of a Git LFS pointer, or None if the file is not one"""
    if (not IDMG.ModDownloader.isLfsPointer(path)):
        return None
    fields = dict(line.split(" ", 1) for line in open(path, encoding = "utf-8").read().splitlines() if " " in line)
    return fields["oid"].split(":", 1)[1], int(fields["size"])


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compareMod(generated: str, committed: str):
    """The differences between a generated mod and the committed one, and how many files were compared"""
    def files(root):
        return {os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs}

    differences = [f"{path} in only one" for path in sorted(files(generated) ^ files(committed))]
    common = sorted(files(generated) & files(committed))
    for path in common:
        result, expected = os.path.join(generated, path), os.path.join(committed, path)
        pointer = readPointer(expected)
        if (pointer is not None):
            same = (sha256(result), os.path.getsize(result)) == pointer
        else:
            with open(result, "rb") as a, open(expected, "rb") as b:
                same = a.read() == b.read()
        if (not same):
            differences.append(f"{path} differs")
    return differences, len(common)


def main() -> int:
    parser = argparse.ArgumentParser(description = "regenerate identity mods from their download folders and compare them with Mods/")
    parser.add_argument("--names", nargs = "+", default = None, help = "game:Name for each character (default: a sample, see the header)")
    parser.add_argument("--all", action = "store_true", help = "every character in Mods/")
    parser.add_argument("--localData", action = "append", default = None, metavar = "REPO=FOLDER", help = "copy a repository's files from a local 'Data/Mod Downloads' instead of downloading them")
    args = parser.parse_args()

    localFolders = {}
    for value in (args.localData or []):
        repo, _, folder = value.partition("=")
        localFolders[IDMG.ModDownloadRepos[repo]] = folder

    if (args.all):
        names = [f"{key}:{name}" for key, loader in Games.items() for name in sorted(os.listdir(os.path.join(ModsFolder, IDMG.ModDownloadGameFolders[loader])))]
    else:
        names = args.names or Sample

    downloader = IDMG.ModDownloader(localFolders = localFolders)
    compared = 0
    failed = []
    for entry in names:
        key, _, name = entry.partition(":")
        loader = Games[key]
        Generator = IDMG.GIMIIdentityModGenerator if (loader == IDMG.ModLoaders.GIMI) else IDMG.WWMIIdentityModGenerator
        committed = os.path.join(ModsFolder, IDMG.ModDownloadGameFolders[loader], name)

        with tempfile.TemporaryDirectory() as temp:
            try:
                Generator().generateFromRepo(name, temp, downloader = downloader)
            except IDMG.Error as e:
                failed.append(entry)
                print(f"{entry}: FAILED -- {e}", flush = True)
                continue

            differences, count = compareMod(temp, committed)
            compared += count
            print(f"{entry}: {count} files, " + ("identical to Mods/" if not differences else "DIFFERENT: " + "; ".join(differences[:6])), flush = True)
            if (differences):
                failed.append(entry)

    print(f"\n{compared} files compared; failed or different: {', '.join(failed) if failed else 'none'}")
    return 1 if (failed or not compared) else 0


if (__name__ == "__main__"):
    sys.exit(main())
