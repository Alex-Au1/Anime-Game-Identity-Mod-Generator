#
# ===== wwmiLiveHashes =====
#
# Measures a WuWa character's LIVE texture hashes off a frame dump, and writes them as AG Remap's
# <Name>LiveHashes.json: {asset hash: live hash}, the hash a download folder files a texture under -> the hash
# the game binds it under.
#
#   py -3 Tools/Downloads/wwmiLiveHashes.py <download version folder> <FrameAnalysis folder> --out <json> [--note <text>]
#
# Why: WuWa streams its textures, and 3DMigoto rehashes a texture as its mips load, so the hash an asset repo
# (WWMI-Assets) files a texture under is not the one the game binds. An identity mod's [TextureOverrideTexture]
# on the asset hash then never fires, silently: the game's own texture is drawn, which looks the same. Zani at
# WuWa 3.8 (2026-11-14): none of her 18 asset hashes was bound on any of her draws; her textures painted flat
# purple stayed unpainted until the overrides were pointed at the dump's hashes.
#
# How: the character's draws are the dump's draws whose vb0 is the folder's Metadata.json 'vb0_hash'. Every
# '.dds' bound on one of their ps-t registers is a candidate. Both sides are decoded (AG Remap's
# FixRaidenBoss2.TextureFile), box-averaged to 64 x 64 RGBA, and correlated channel by channel over the channels
# that vary in both; the score is the mean. An asset texture pairs with its best candidate when that scores
# >= MinScore and beats the next candidate by >= MinMargin -- AG Remap's Jinhsi table was measured the same way
# (0.998 - 1.0 with margins over 0.37). An asset hash the dump binds as it is needs no pair. Anything else is
# printed and left out, for a person to judge: a texture whose pass the frame did not draw, a near-tie, or the
# same image with a channel inverted (two of Zani's normal maps: the game's copy is not the asset file there, so
# binding the file on the live hash would flip the lighting).
#
# Take the dump from the CHARACTER MENU, with the in-game LOD bias (ImageDetail in the game's LocalStorage.db)
# at its maximum, and with no mod of the character loaded (a mod's textures replace the game's in the dump).
# Needs AG Remap's API on PYTHONPATH, as every tool here does.
#

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from downloadTools import RepoRoot     # noqa: E402,F401  (puts AGIDMGen on sys.path, as the other tools do)
import FixRaidenBoss2 as FRB           # noqa: E402

#: the side both textures are box-averaged to before they are compared
Side = 64

#: the lowest score a pair is accepted at
MinScore = 0.95

#: how far the best candidate must score above the next one
MinMargin = 0.1

AssetName = re.compile(r"Texture([0-9a-f]{8})\.dds$", re.IGNORECASE)
DumpTexture = re.compile(r"^(\d{6})-ps-t\d+=([0-9a-f]{8})(?:\([0-9a-f]{8}\))?-.*\.dds$", re.IGNORECASE)
DumpVb0 = re.compile(r"^(\d{6})-vb0=([0-9a-f]{8})-", re.IGNORECASE)


def thumbnail(path: str) -> Optional[np.ndarray]:
    """the texture's pixels box-averaged to Side x Side RGBA (floats), or None if it cannot be decoded"""
    tex = FRB.TextureFile(path)
    tex.open()
    if (not tex.hasImage):
        return None

    w, h = tex.width, tex.height
    px = np.frombuffer(tex.getPixels(), dtype = np.uint8).reshape(h, w, 4).astype(np.float64)
    if (w < Side or h < Side):
        px = px.repeat(max(1, Side // h), axis = 0).repeat(max(1, Side // w), axis = 1)
        h, w = px.shape[:2]

    bh, bw = h // Side, w // Side
    return px[:bh * Side, :bw * Side].reshape(Side, bh, Side, bw, 4).mean(axis = (1, 3))


def correlations(a: np.ndarray, b: np.ndarray) -> Dict[str, float]:
    """the correlation of each channel that varies in both thumbnails, by its letter"""
    result = {}
    for c in range(4):
        x, y = a[..., c].ravel(), b[..., c].ravel()
        if (x.std() < 1 or y.std() < 1):
            continue
        result["RGBA"[c]] = float(np.corrcoef(x, y)[0, 1])
    return result


def score(a: np.ndarray, b: np.ndarray) -> float:
    """the mean correlation of the channels that vary in both thumbnails (0 if none does)"""
    scores = list(correlations(a, b).values())
    return sum(scores) / len(scores) if (scores) else 0.0


def invertedChannels(a: np.ndarray, b: np.ndarray) -> List[str]:
    """the channels in which 'b' is 'a' inverted, when every varying channel is the same image up to its sign
    (Zani's game normal maps had green inverted against WWMI-Assets' files: binding the file there would flip the
    lighting, so such a pair is never written)"""
    found = correlations(a, b)
    if (not found or any(abs(r) < MinScore for r in found.values())):
        return []
    return [c for c, r in found.items() if r < 0]


def readAssets(folder: str) -> Tuple[str, Dict[str, str]]:
    """the folder's vb0 hash, and its textures: {hash: path}"""
    metadata = [f for f in os.listdir(folder) if f.endswith("Metadata.json")]
    if (len(metadata) != 1):
        raise SystemExit(f"'{folder}' is not a WuWa download folder: it has {len(metadata)} Metadata.json")
    with open(os.path.join(folder, metadata[0]), "r", encoding = "utf-8") as f:
        vb0 = json.load(f)["vb0_hash"].lower()

    assets = {}
    for fileName in sorted(os.listdir(folder)):
        m = AssetName.search(fileName)
        if (m):
            assets[m.group(1).lower()] = os.path.join(folder, fileName)
    return vb0, assets


def readDump(dump: str, vb0: str) -> Dict[str, str]:
    """the textures bound on the character's draws: {hash: path of one dumped copy}"""
    names = os.listdir(dump)
    draws = {m.group(1) for m in map(DumpVb0.match, names) if m and m.group(2).lower() == vb0}
    if (not draws):
        raise SystemExit(f"no draw in '{dump}' has vb0 = {vb0}: is the character on screen, and the dump taken with textures?")

    found = {}
    for fileName in sorted(names):
        m = DumpTexture.match(fileName)
        if (m and m.group(1) in draws):
            found.setdefault(m.group(2).lower(), os.path.join(dump, fileName))
    print(f"{len(draws)} draws of vb0 {vb0}, binding {len(found)} distinct .dds textures")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description = "measure a WuWa character's live texture hashes off a frame dump")
    parser.add_argument("folder", help = "the character's download version folder (Data/Mod Downloads/WuWa/<Name>/<ver>)")
    parser.add_argument("dump", help = "a FrameAnalysis folder of the character menu, at maximum LOD bias, with no mod of the character")
    parser.add_argument("--out", required = True, help = "the <Name>LiveHashes.json to write")
    parser.add_argument("--note", default = "", help = "what the table's '_' entry says about where it was measured")
    args = parser.parse_args()

    vb0, assets = readAssets(args.folder)
    candidates = readDump(args.dump, vb0)

    thumbs = {h: thumbnail(p) for h, p in candidates.items()}
    thumbs = {h: t for h, t in thumbs.items() if t is not None}

    pairs = {}
    scores: List[float] = []
    margins: List[float] = []
    for assetHash, path in assets.items():
        if (assetHash in candidates):
            print(f"  {assetHash}: bound as it is -- no live twin needed")
            continue

        a = thumbnail(path)
        if (a is None):
            print(f"  {assetHash}: cannot be decoded -- left out")
            continue

        ranked = sorted(((score(a, t), h) for h, t in thumbs.items()), reverse = True)
        best, bestHash = ranked[0] if ranked else (0.0, None)
        second = ranked[1][0] if len(ranked) > 1 else 0.0
        if (best >= MinScore and best - second >= MinMargin):
            pairs[assetHash] = bestHash
            scores.append(best)
            margins.append(best - second)
            print(f"  {assetHash} -> {bestHash}  ({best:.4f}, next {second:.4f})")
        else:
            flipped = [(h, invertedChannels(a, t)) for h, t in thumbs.items()]
            flipped = [(h, chans) for h, chans in flipped if chans]
            if (flipped):
                for h, chans in flipped:
                    print(f"  {assetHash}: {h} is the same image with {', '.join(chans)} inverted -- left out (the game's texture is not the asset file)")
            else:
                print(f"  {assetHash}: no clear match (best {bestHash} {best:.4f}, next {second:.4f}) -- left out")

    taken: Dict[str, List[str]] = {}
    for assetHash, liveHash in pairs.items():
        taken.setdefault(liveHash, []).append(assetHash)
    for liveHash, owners in taken.items():
        if (len(owners) > 1):
            print(f"  WARNING: {liveHash} is the best match of {', '.join(owners)} -- check them by eye")

    note = (f"{args.note} " if args.note else "") + (
        f"Paired by Tools/Downloads/wwmiLiveHashes.py (pixel correlation of every channel that varies, at {Side} x {Side}) off "
        f"{os.path.basename(os.path.normpath(args.dump))}: {len(pairs)} of {len(assets)} textures"
        + (f", scores {min(scores):.3f} - {max(scores):.3f}, margins over {min(margins):.2f}" if pairs else "") + ".")
    table = {"_": note}
    table.update(sorted(pairs.items()))
    with open(args.out, "w", encoding = "utf-8", newline = "\n") as f:
        json.dump(table, f, indent = 2)
        f.write("\n")

    print(f"wrote {args.out}: {len(pairs)} of {len(assets)} textures paired")
    return 0


if (__name__ == "__main__"):
    sys.exit(main())
