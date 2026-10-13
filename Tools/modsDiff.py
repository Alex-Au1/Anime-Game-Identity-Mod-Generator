#
# ===== modsDiff =====
#
# Proves a regeneration of Mods/ changed only what it was meant to. Take a snapshot BEFORE regenerating, then compare:
#
#   py -3 Tools/modsDiff.py snapshot <scratch folder> [--mods Mods/WuWa]
#   py -3 Tools/populateMods.py ...                                   (or any other change to Mods/)
#   py -3 Tools/modsDiff.py compare <scratch folder> [--mods Mods/WuWa]
#
# The snapshot copies every .ini and hashes every other file (about a minute for all of Mods/). The comparison fails
# (exit 1) on any binary that changed, appeared or vanished, and lists every distinct line added to or removed from the
# .ini files, with the number of mods it changed in. The mod's own name is written <Name>, so one change made to every
# mod shows as ONE line: eg. "+ ; Github: https://..." in 198 mods. Read that list: a line you did not mean to change is
# a bug report, not a refresh (see AI Agent Help/Overview, "Working a feature or bug request here").
#
# Keep the snapshot in a scratch folder outside the repo. Files are read as they are on disk (an LFS pointer, in a clone
# without LFS, is compared as the pointer).
#

import argparse
import collections
import difflib
import hashlib
import json
import os
import shutil
import sys

RepoRoot = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def walk(root: str):
    for folder, _, files in os.walk(root):
        for fileName in files:
            yield os.path.relpath(os.path.join(folder, fileName), root).replace("\\", "/")


def sha1(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(mods: str, out: str) -> int:
    hashes = {}
    iniCount = 0
    for rel in walk(mods):
        src = os.path.join(mods, rel)
        if (rel.lower().endswith(".ini")):
            dst = os.path.join(out, "ini", rel)
            os.makedirs(os.path.dirname(dst), exist_ok = True)
            shutil.copyfile(src, dst)
            iniCount += 1
        else:
            hashes[rel] = sha1(src)

    with open(os.path.join(out, "hashes.json"), "w", encoding = "utf-8") as f:
        json.dump({"mods": os.path.abspath(mods), "hashes": hashes}, f)
    print(f"snapshot of {mods}: {len(hashes)} files hashed, {iniCount} .ini copied into {out}")
    return 0


def modName(rel: str) -> str:
    # Mods/<GI|WuWa>/<Name>/... or <Name>/... when --mods is one game's folder
    parts = rel.split("/")
    return parts[1] if (len(parts) > 2 and parts[0] in ("GI", "WuWa")) else parts[0]


def compare(mods: str, out: str, show: int) -> int:
    with open(os.path.join(out, "hashes.json"), encoding = "utf-8") as f:
        before = json.load(f)["hashes"]
    iniRoot = os.path.join(out, "ini")
    beforeIni = set(walk(iniRoot)) if (os.path.isdir(iniRoot)) else set()
    now = set(walk(mods))

    problems = []
    for rel in sorted((set(before) | beforeIni) - now):
        problems.append(f"vanished: {rel}")
    for rel in sorted(now - set(before) - beforeIni):
        problems.append(f"appeared: {rel}")
    binaries = sorted(set(before) & now)
    for rel in binaries:
        if (sha1(os.path.join(mods, rel)) != before[rel]):
            problems.append(f"binary changed: {rel}")

    # every added / removed .ini line, with the mod's own name made <Name>, counted once per mod
    changes = collections.Counter()
    changedIni = 0
    for rel in sorted(beforeIni & now):
        with open(os.path.join(iniRoot, rel), "rb") as f:
            a = f.read().decode("utf-8", "replace").split("\r\n")
        with open(os.path.join(mods, rel), "rb") as f:
            b = f.read().decode("utf-8", "replace").split("\r\n")
        if (a == b):
            continue

        changedIni += 1
        name = modName(rel)
        seen = set()
        for line in difflib.ndiff(a, b):
            if (line[:2] in ("+ ", "- ")):
                seen.add(line[:2] + line[2:].replace(name, "<Name>"))
        changes.update(seen)

    print(f"{len(binaries)} binaries compared; {changedIni} of {len(beforeIni & now)} .ini changed")
    for line, count in sorted(changes.items(), key = lambda item: (-item[1], item[0]))[:show]:
        print(f"  {count:4} mods  {line}")
    if (len(changes) > show):
        print(f"  ... and {len(changes) - show} more distinct lines (--show)")

    for problem in problems[:40]:
        print(f"PROBLEM {problem}")
    if (len(problems) > 40):
        print(f"... and {len(problems) - 40} more problems")
    return 1 if (problems) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description = "prove a regeneration of Mods/ changed only what it was meant to")
    parser.add_argument("command", choices = ["snapshot", "compare"])
    parser.add_argument("out", help = "the scratch folder the snapshot is kept in (outside the repo)")
    parser.add_argument("--mods", default = os.path.join(RepoRoot, "Mods"), help = "the folder to snapshot or compare (default: Mods/)")
    parser.add_argument("--show", type = int, default = 30, help = "how many distinct changed .ini lines to list (default 30)")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok = True)
    return snapshot(args.mods, args.out) if (args.command == "snapshot") else compare(args.mods, args.out, args.show)


if (__name__ == "__main__"):
    sys.exit(main())
