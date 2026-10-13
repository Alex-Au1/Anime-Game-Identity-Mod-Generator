#
# ===== faceDumpRegisters =====
#
# Lists, for each GIMI frame dump, every draw that binds a known face texture, with the pixel shader and the
# textures on ps-t0 .. ps-t3, each named by what GI-Model-Importer-Assets' hash.json says it is:
#
#   py -3 Tools/faceDumpRegisters.py <GI-Model-Importer-Assets/PlayerCharacterData> <a FrameAnalysis-* folder, or a folder of them>
#
# It answers "which register does the game read the face diffuse from?" off the game's own dumps. On GI 6.x
# (dumps of 2026-09) the face's colour pass, pixel shader 82c84814, read it from ps-t1 for all 11 characters
# dumped, while the face's other passes kept it on ps-t0. That is why the GIMI generator's --faceRegister
# defaults to ps-t1: a diffuse bound to ps-t0 lands in the slot the colour pass reads as the face's light map,
# and its alpha (the blush mask) shows as white cheeks.
#
# A dump taken with a mod of the character loaded shows the MOD's bindings; take one with none loaded.
#

import argparse
import collections
import glob
import json
import os
import re
import sys

TextureFile = re.compile(r"^(\d+)-ps-t(\d+)=([0-9a-f]{8})-vs=([0-9a-f]+)-ps=([0-9a-f]+)")
IbFile = re.compile(r"^(\d+)-ib=([0-9a-f]{8})")


def readTextureNames(assets: str):
    # texture hash -> "<Character>.<Component>.<Kind>", from every hash.json
    names = {}
    for character in sorted(os.listdir(assets)):
        path = os.path.join(assets, character, "hash.json")
        if (not os.path.isfile(path)):
            continue
        with open(path, encoding = "utf-8") as f:
            entries = json.load(f)
        for entry in entries:
            for objectTextures in entry.get("texture_hashes", []):
                for kind, _, textureHash in objectTextures:
                    names.setdefault(textureHash, f"{character}.{entry.get('component_name')}.{kind}")
    return names


def faceDraws(dump: str, names):
    # one line per distinct (pixel shader, ib, bindings) among the draws that bind a face texture
    textures = collections.defaultdict(dict)
    shaders, ibs = {}, {}
    for fileName in os.listdir(dump):
        match = TextureFile.match(fileName)
        if (match):
            textures[match.group(1)][int(match.group(2))] = match.group(3)
            shaders[match.group(1)] = match.group(5)
            continue
        match = IbFile.match(fileName)
        if (match):
            ibs[match.group(1)] = match.group(2)

    lines = set()
    for draw, slots in textures.items():
        if (not any(".Face." in names.get(h, "") for h in slots.values())):
            continue
        bound = " ".join(f"t{register}={names.get(h, h)}" for register, h in sorted(slots.items()) if register < 4)
        lines.add(f"ps={shaders[draw][:8]} ib={ibs.get(draw)} {bound}")
    return sorted(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description = "which registers a GIMI frame dump binds each face texture to")
    parser.add_argument("assets", help = "GI-Model-Importer-Assets' PlayerCharacterData folder")
    parser.add_argument("dumps", help = "a FrameAnalysis-* folder, or a folder holding several")
    args = parser.parse_args()

    names = readTextureNames(args.assets)
    isDump = os.path.basename(os.path.normpath(args.dumps)).startswith("FrameAnalysis")
    dumps = [args.dumps] if (isDump) else sorted(glob.glob(os.path.join(args.dumps, "FrameAnalysis*")))
    found = False
    for dump in dumps:
        lines = faceDraws(dump, names)
        if (lines):
            found = True
            print(os.path.basename(dump))
            for line in lines:
                print("   ", line)

    if (not found):
        print("no draw binds a face texture listed in hash.json")
    return 0 if (found) else 1


if (__name__ == "__main__"):
    sys.exit(main())
