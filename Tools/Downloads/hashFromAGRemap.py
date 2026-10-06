#
# ===== hashFromAGRemap =====
#
# Writes the <prefix>Hash.json of AG Remap's GI download folders that have none -- the skins AG Remap built
# from frame dumps (no asset repo has them), and the characters whose asset folder cannot be built -- from
# AG Remap's own hash and index data (FixRaidenBoss2.ModData), so the library can generate them:
#
#   py -3 Tools/Downloads/hashFromAGRemap.py <AGRemap/Data/Mod Downloads> [--only Name ...] [--dryRun] [--olderVersions]
#   py -3 Tools/Downloads/hashFromAGRemap.py <AGRemap/Data/Mod Downloads> --check
#
# The NEWEST version folder of each AG Remap GI character (counting this repo's folders too) that has no
# <prefix>Hash.json in either repo gets one, in this repo's Data/Mod Downloads, beside AG Remap's files.
# --olderVersions also does the older folders; their hashes are the newest rows before the next folder's
# version, which is only right if the model did not change before then -- nothing in the data says when
# it did, since the game also rehashes unchanged models. --check writes nothing: it derives the hash
# file of every folder that already HAS one from the asset repo, and compares the two -- the proof that
# the derivation reads AG Remap's data right.
#
# Where each field comes from:
#
#   components        the folder's <prefix><component>Position.buf files ("" for a one-component character)
#   the 5 hashes      ModData.Hashes, under <prefix><component>, or <prefix>Main / <prefix> for the ""
#                     component: for each, the NEWEST row the folder's model was still current for -- the
#                     newest row of all for a character's newest folder, else the newest row older than the
#                     next folder's version. The game rehashes a model without changing it (Amber's 4_0
#                     buffers are byte-identical to today's assets, her hashes are not 4.0's), so a folder's
#                     own version would give hashes today's game no longer draws with
#   objects           the folder's <prefix><component><object>.ib files, in the order Head, Body, Dress,
#                     Extra, then any others (A, B, C, ...) alphabetically
#   object_indexes    ModData.Indices where AG Remap has rows; otherwise each object's first index is where
#                     the one before it ends (the sum of the earlier .ib files' index counts). Where both
#                     exist they must agree, or the folder is refused
#   texture_hashes    the folder's <prefix><component><object><kind>.dds files; the hash from the tex_<object>_<kind>
#                     row if there is one, else ""
#   Face              <prefix>FaceDiffuse.dds, and the tex_face_diffuse hash
#   texture_sources   (this repo's addition to hash.json) for an object that has no textures of its own and
#                     draws with another's, the slot AG Remap's parser config names as its TEXTURE DONOR:
#                     IniParseData/<Name>/<Name>Parser.cpp, a GIMIComponentParserConfig whose slots read
#                     {name, index, diffuseReg, lightMapReg, normalMapReg, noTextures, textureDonor, donorNormalMap}.
#                     The borrower's layout is "plain" when its own slot reads no normal map. Every slot index
#                     the config lists must equal the derived object_indexes, or the folder is refused
#
#   --overwrite       also re-derive the folders whose Hash.json this tool wrote before (the asset repo's are
#                     never touched: --only names the characters to redo)
#

import argparse
import json
import os
import re
import sys

from downloadTools import OwnDownloads, readAliases, getVersionFolders, findPrefix
import AGIDMGen as IDMG

# the order GIMI characters list their objects in
ObjectOrder = ["head", "body", "dress", "extra"]
HashKeys = ("draw_vb", "position_vb", "blend_vb", "texcoord_vb", "ib")


def importFRB():
    try:
        import FixRaidenBoss2 as FRB
    except ImportError:
        raise SystemExit("FixRaidenBoss2 cannot be imported: pip install FixRaidenBoss2, or put AG Remap's 'api/src/py' on PYTHONPATH") from None
    return FRB


SlotPattern = re.compile(r'\{\s*"(?P<name>[^"]*)"\s*,\s*"(?P<index>[^"]*)"\s*,\s*"(?P<diffuse>[^"]*)"\s*,\s*"(?P<lightMap>[^"]*)"\s*,\s*"(?P<normalMap>[^"]*)"'
                         r'(?:\s*,\s*(?P<noTextures>true|false))?(?:\s*,\s*"(?P<donor>[^"]*)")?(?:\s*,\s*(?P<donorNormalMap>true|false))?\s*\}')


def readParserSlots(agRemapRoot: str, name: str):
    """{component name: [slot, ...]} out of AG Remap's GIMIComponentParserConfig for a character, or {} if it has none"""
    path = os.path.join(agRemapRoot, "Anime Game Remap (for all users)", "api", "src", "cpp", "core", "src", "data", "IniParseData", name, f"{name}Parser.cpp")
    if (not os.path.isfile(path)):
        return {}

    with open(path, "r", encoding = "utf-8") as f:
        code = re.sub(r"//[^\n]*", "", f.read())

    names = dict(re.findall(r'(\w+)\.name\s*=\s*"([^"]*)"\s*;', code))
    result = {}
    for var, body in re.findall(r"(\w+)\.slots\s*=\s*\{(.*?)\}\s*;", code, re.S):
        if (var not in names):
            raise IDMG.Error(f"{os.path.basename(path)}: the slots of '{var}' belong to no named component")
        result[names[var]] = [m.groupdict() for m in SlotPattern.finditer(body + "}")]
    return result


def addTextureSources(entries, slots, label: str):
    """Checks the config's slot indices against the derived ones, and records each slot's texture donor"""
    byComponent = {e["component_name"]: e for e in entries if e["component_name"] != "Face"}
    for component, componentSlots in slots.items():
        entry = byComponent.get(component)
        if (entry is None):
            raise IDMG.Error(f"{label}: AG Remap's parser config has a component '{component}' the download folder does not")

        derived = dict(zip(entry["object_classifications"], entry["object_indexes"]))
        sources = {}
        for slot in componentSlots:
            if (derived.get(slot["name"]) != int(slot["index"])):
                raise IDMG.Error(f"{label}: AG Remap's parser config puts {component} slot {slot['name']} at {slot['index']}, the .ib files at {derived.get(slot['name'])}")
            if (slot["donor"]):
                donorComponent, _, donorObject = slot["donor"].partition(";")
                sources[slot["name"]] = IDMG.GIMITextureSource(donorComponent, donorObject, IDMG.GIMITextureLayouts.NormalMap if (slot["normalMap"]) else IDMG.GIMITextureLayouts.Plain).toDict()
        if (sources):
            entry["texture_sources"] = sources


def getRow(table, mod: str, before = None, key = None):
    """The newest row of a mod, in any case (or, with 'key', the newest row holding that key) older than
    'before', or of all if 'before' is None"""
    rows = {}
    for version, mods in table.items():
        if (before is not None and IDMG.VersionTools.parse(version) >= IDMG.VersionTools.parse(before)):
            continue
        row = next((r for m, r in mods.items() if m.lower() == mod.lower() and (key is None or key in r)), None)
        if (row is not None):
            rows[version] = row
    chosen = IDMG.VersionTools.getClosest(rows) if (rows) else None
    return None if (chosen is None) else rows[chosen]


def orderObjects(objects):
    known = [o for o in objects if o.lower() in ObjectOrder]
    others = [o for o in objects if o.lower() not in ObjectOrder]
    return sorted(known, key = lambda o: ObjectOrder.index(o.lower())) + sorted(others)


def derive(folder: str, prefix: str, name: str, before, hashes, indices):
    files = os.listdir(folder)
    suffix = "Position.buf"
    components = sorted((f[len(prefix):-len(suffix)] for f in files if f.startswith(prefix) and f.endswith(suffix)), key = len, reverse = True)
    if (not components):
        raise IDMG.Error("no <prefix><component>Position.buf: the folder has no buffers")

    # each .ib to the LONGEST component its name starts with
    objects = {component: [] for component in components}
    for f in files:
        if (not f.endswith(".ib") or not f.startswith(prefix)):
            continue
        rest = f[len(prefix):-len(".ib")]
        component = next(c for c in components if rest.startswith(c) and len(rest) > len(c))
        objects[component].append(rest[len(component):])

    faceHash = None
    entries = []
    for component in sorted(components, key = lambda c: (c != "", c)):
        candidates = [prefix + component] if (component) else [prefix + "Main", prefix, name]
        mod = next((m for m in candidates if getRow(hashes, m, before, "position_vb") is not None), None)
        if (mod is None):
            raise IDMG.Error(f"AG Remap has no hashes for {' or '.join(candidates)}" + (f" before {before}" if before else ""))

        entry = {"component_name": component}
        for key in HashKeys:
            row = getRow(hashes, mod, before, key)
            if (row is None):
                raise IDMG.Error(f"AG Remap has no '{key}' hash for {mod}")
            entry[key] = row[key]

        faceRow = getRow(hashes, mod, before, "tex_face_diffuse")
        if (faceRow is not None and faceHash is None):
            faceHash = faceRow["tex_face_diffuse"]

        ordered = orderObjects(objects[component])
        counts = [os.path.getsize(os.path.join(folder, f"{prefix}{component}{obj}.ib")) // 4 for obj in ordered]
        cumulative = [sum(counts[:i]) for i in range(len(ordered))]

        indexRow = getRow(indices, mod, before)
        firstIndices = cumulative
        if (indexRow is not None and "" in indexRow):
            rows = {obj.lower(): int(index) for obj, index in indexRow[""].items()}
            fromRows = [rows.get(obj.lower()) for obj in ordered]
            if (fromRows != cumulative):
                raise IDMG.Error(f"{mod}: AG Remap's indices {dict(zip(ordered, fromRows))} disagree with the .ib files' {dict(zip(ordered, cumulative))}")
            firstIndices = fromRows

        textureLists = []
        hashRow = getRow(hashes, mod, before) or {}
        for obj in ordered:
            start = f"{prefix}{component}{obj}"
            kinds = sorted(f[len(start):-len(".dds")] for f in files if f.startswith(start) and f.endswith(".dds") and f[len(start):-len(".dds")]
                           and not any(f.startswith(f"{prefix}{component}{other}") for other in ordered if other != obj and other.startswith(obj)))
            textureLists.append([[kind, ".dds", hashRow.get(f"tex_{obj.lower()}_{kind.lower()}", "")] for kind in kinds])

        entry.update({"object_indexes": firstIndices, "object_classifications": ordered, "texture_hashes": textureLists})
        entries.append(entry)

    if (os.path.isfile(os.path.join(folder, f"{prefix}FaceDiffuse.dds")) and faceHash is not None):
        entries.append({"component_name": "Face", "object_classifications": ["Head"], "object_indexes": [0], "texture_hashes": [[["Diffuse", ".dds", faceHash]]]})
    return entries


def compare(derived, actual):
    """The differences, in what the generator reads, between a derived hash file and the asset repo's"""
    def summary(entries):
        result = {}
        for e in entries:
            if (e.get("position_vb") and e.get("blend_vb")):
                result[e.get("component_name", "")] = ({k: e[k] for k in HashKeys}, list(e["object_classifications"]), list(e["object_indexes"]))
        face = next((e for e in entries if e.get("component_name") == "Face"), None)
        result["Face"] = None if (face is None) else next((h for kind, _, h in face["texture_hashes"][0] if kind == "Diffuse"), None)
        return result
    a, b = summary(derived), summary(actual)
    return [f"{key}: derived {a.get(key)} != asset {b.get(key)}" for key in sorted(set(a) | set(b)) if a.get(key) != b.get(key)]


def main() -> int:
    parser = argparse.ArgumentParser(description = "write the Hash.json of AG Remap's GI download folders that have none, from AG Remap's hash data")
    parser.add_argument("agRemap", help = "AG Remap's 'Data/Mod Downloads' folder")
    parser.add_argument("--only", nargs = "+", default = None, help = "only these characters")
    parser.add_argument("--check", action = "store_true", help = "write nothing; derive the folders that already have a Hash.json and compare")
    parser.add_argument("--dryRun", action = "store_true", help = "write nothing")
    parser.add_argument("--olderVersions", action = "store_true", help = "also the folders a newer folder of the same character replaces")
    parser.add_argument("--overwrite", action = "store_true", help = "with --only: re-derive the Hash.json this tool wrote before")
    args = parser.parse_args()

    if (args.overwrite and not args.only):
        raise SystemExit("--overwrite needs --only: a Hash.json from the asset repo must never be replaced")

    FRB = importFRB()
    agRemapRoot = os.path.abspath(os.path.join(args.agRemap, "..", ".."))
    hashes, indices = FRB.ModData.Hashes.value, FRB.ModData.Indices.value
    agGame = os.path.join(args.agRemap, "GI")
    results = {"written": [], "agree": [], "differ": [], "failed": []}

    # a folder that is only another name of a character (Raiden for RaidenShogun) is that character's
    aliases = readAliases().get("GI", {})

    for name in (args.only or sorted(os.listdir(agGame), key = str.lower)):
        if (name in aliases and aliases[name] != name):
            print(f"{name}: skipped, it is another name of {aliases[name]} (Aliases.json)", flush = True)
            continue

        # every version folder of the character, in either repo: the next one bounds a folder's hashes
        allVersions = sorted(set(getVersionFolders(os.path.join(agGame, name))) | set(getVersionFolders(os.path.join(OwnDownloads, "GI", name))), key = IDMG.VersionTools.parse)
        for version in getVersionFolders(os.path.join(agGame, name)):
            folder = os.path.join(agGame, name, version)
            prefix = findPrefix(IDMG.ModLoaders.GIMI, os.listdir(folder))
            if (prefix is None):
                continue

            ownHash = os.path.join(OwnDownloads, "GI", name, version, f"{prefix}{IDMG.GIMIHashFileSuffix}")
            hasHash = os.path.isfile(ownHash) or os.path.isfile(os.path.join(folder, f"{prefix}{IDMG.GIMIHashFileSuffix}"))
            if (hasHash != args.check and not (args.overwrite and os.path.isfile(ownHash) and not args.check)):
                continue

            label = f"{name}/{version}"
            later = allVersions[allVersions.index(version) + 1:]
            if (later and not args.check and not args.olderVersions):
                print(f"{label}: skipped, {name}/{later[-1]} is newer (--olderVersions to do it)", flush = True)
                continue

            try:
                derived = derive(folder, prefix, name, later[0].replace("_", ".") if (later) else None, hashes, indices)
                if (not later):
                    addTextureSources(derived, readParserSlots(agRemapRoot, name), label)
            except (IDMG.Error, StopIteration) as e:
                results["failed"].append(f"{label}: {e}")
                print(f"{label}: FAILED -- {e}", flush = True)
                continue

            if (args.check):
                with open(ownHash, "r", encoding = "utf-8") as f:
                    differences = compare(derived, json.load(f))
                results["differ" if differences else "agree"].append(label)
                print(f"{label}: " + ("agrees with the asset repo's hash.json" if not differences else "DIFFERS -- " + "; ".join(differences)), flush = True)
                continue

            objects = ", ".join(f"{e['component_name'] or '-'}: " + "/".join(f"{o} {i}" + (f" <- {e['texture_sources'][o]['component']}{e['texture_sources'][o]['object']}" if o in e.get("texture_sources", {}) else "")
                                                                             for o, i in zip(e["object_classifications"], e["object_indexes"])) for e in derived if e["component_name"] != "Face")
            print(f"{label}: {prefix}{IDMG.GIMIHashFileSuffix} -- {objects}", flush = True)
            results["written"].append(label)
            if (not args.dryRun):
                os.makedirs(os.path.dirname(ownHash), exist_ok = True)
                with open(ownHash, "w", encoding = "utf-8", newline = "\n") as f:
                    json.dump(derived, f, indent = 4)
                    f.write("\n")

    print()
    for kind, labels in results.items():
        if (labels):
            print(f"{kind}: {len(labels)}")
    for failure in results["failed"]:
        print(f"  {failure}")
    return 1 if (results["differ"] or (args.check and not results["agree"])) else 0


if (__name__ == "__main__"):
    sys.exit(main())
