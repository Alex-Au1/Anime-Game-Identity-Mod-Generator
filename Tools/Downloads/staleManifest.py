#
# ===== staleManifest =====
#
# Names the characters whose download folders AG Remap changed on its GitHub master since the manifest
# (AGIDMGen/data/ModDownloadData.py) was built:
#
#   py -3 Tools/Downloads/staleManifest.py [--ref master]
#
# The manifest records the AG Remap commit it was built from (ModDownloadAGRemapCommit). This compares AG Remap's
# Data/Mod Downloads at that commit with the ref, file by file, through GitHub's API. A file's git blob hash
# changes with its content, so a file replaced under the same name is found too: Lynae's foils were, on 2026-10-15.
# That is the change modsCheck.py would otherwise only report as "Textures/... differs".
#
# A changed folder is STALE when the library uses it: a version folder the manifest lists, or a new one it would list
# (it holds files). A file outside any version folder (eg. a README, a <Name>LiveHashes.json) is listed as unused.
# The fix is Downloads' "BUILD THE MANIFEST FROM AGREMAP'S master", then regenerating the stale characters' Mods/.
#
# Set GITHUB_TOKEN to raise GitHub's rate limit (60 requests an hour without one; a run makes five).
#
# Exits 1 when a character is stale, 2 when GitHub cannot be asked.
#

import argparse
import json
import os
import re
import sys
import urllib.request
from typing import Dict, List, Optional, Tuple

RepoRoot = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(RepoRoot, "AGIDMGen", "api", "src", "py"))
import AGIDMGen as IDMG
from AGIDMGen.data import ModDownloadData as ManifestModule

DownloadsPath = "Data/Mod Downloads"


class GithubError(Exception):
    pass


def getRepo() -> str:
    # "owner/name" of AG Remap's repository, out of the library's address for its download folders
    match = re.match(r"https://github\.com/([^/]+/[^/]+)/", IDMG.ModDownloadRepos.AGRemap.value)
    return match.group(1)


def getJson(url: str):
    request = urllib.request.Request(url, headers = {"Accept": "application/vnd.github+json", "User-Agent": "AGIDMGen-staleManifest"})
    token = os.environ.get("GITHUB_TOKEN")
    if (token):
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout = 60) as response:
            return json.load(response)
    except Exception as e:
        raise GithubError(f"{url}: {e}") from e


def getCommit(repo: str, ref: str) -> str:
    return getJson(f"https://api.github.com/repos/{repo}/commits/{ref}")["sha"]


def getDownloadsTree(repo: str, commit: str) -> Dict[str, str]:
    """Every file under Data/Mod Downloads at a commit: its path below that folder, and its git blob hash"""
    parent, folder = DownloadsPath.rsplit("/", 1)
    entries = getJson(f"https://api.github.com/repos/{repo}/contents/{parent}?ref={commit}")
    treeHash = next((e["sha"] for e in entries if e["name"] == folder and e["type"] == "dir"), None)
    if (treeHash is None):
        raise GithubError(f"{repo} has no {DownloadsPath} at {commit}")

    tree = getJson(f"https://api.github.com/repos/{repo}/git/trees/{treeHash}?recursive=1")
    if (tree.get("truncated")):
        raise GithubError(f"GitHub truncated the listing of {DownloadsPath} at {commit}")
    return {e["path"]: e["sha"] for e in tree["tree"] if e["type"] == "blob"}


def diffTrees(old: Dict[str, str], new: Dict[str, str]) -> Dict[Tuple[str, ...], List[str]]:
    """
    What changed between two listings, by folder: (game, name, version) for a file in a version folder, (game, name)
    for a file beside the version folders, () for anything else. Each change is "added <file>", "removed <file>" or
    "changed <file>"
    """

    changes = {}
    for path in sorted(set(old) | set(new)):
        if (old.get(path) == new.get(path)):
            continue
        kind = "added" if (path not in old) else "removed" if (path not in new) else "changed"
        parts = path.split("/")
        key = tuple(parts[:3]) if (len(parts) >= 4) else tuple(parts[:2]) if (len(parts) == 3) else ()
        changes.setdefault(key, []).append(f"{kind} {parts[-1]}")
    return changes


def describe(changes: List[str], limit: int = 4) -> str:
    return ", ".join(changes[:limit]) + (f" and {len(changes) - limit} more" if (len(changes) > limit) else "")


def findStale(ref: str = "master", built: Optional[str] = None):
    """
    The stale and the unused changes since the manifest's commit: ``(built, head, stale, unused)``, where ``stale`` and
    ``unused`` map a folder key (see :func:`diffTrees`) to its changes

    Raises
    ------
    GithubError
        If GitHub cannot be asked
    """

    repo = getRepo()
    built = ManifestModule.ModDownloadAGRemapCommit if (built is None) else built
    head = getCommit(repo, ref)
    if (head.startswith(built) or built.startswith(head)):
        return built, head, {}, {}

    changes = diffTrees(getDownloadsTree(repo, built), getDownloadsTree(repo, head))
    # the library depends on every version folder, listed in the manifest or not yet
    stale = {k: v for k, v in changes.items() if (len(k) == 3)}
    unused = {k: v for k, v in changes.items() if k not in stale}
    return built, head, stale, unused


def staleCharacters(stale) -> List[str]:
    """``game:Name`` for each stale character, named by its mod (eg. ``gi:Raiden`` for the folder ``RaidenShogun``) as modsCheck.py names them"""
    result = set()
    for game, folder, *_ in stale:
        loader = next((l for l, g in IDMG.ModDownloadGameFolders.items() if g == game), None)
        if (loader is None):
            continue
        try:
            name = IDMG.ModNames.find(folder, [loader]).name
        except IDMG.Error:
            name = folder
        result.add(f"{'gi' if (loader == IDMG.ModLoaders.GIMI) else 'wuwa'}:{name}")
    return sorted(result)


def report(built: str, head: str, stale, unused, ref: str = "master") -> List[str]:
    lines = [f"the manifest was built from AG Remap's {built[:8]}; its {ref} is {head[:8]}"]
    if (not stale and not unused):
        lines.append("  nothing in Data/Mod Downloads changed since: the manifest is up to date")
        return lines

    for key, changes in sorted(stale.items()):
        listed = key[1] in IDMG.ModDownloadData.get(key[0], {}) and key[2] in IDMG.ModDownloadData[key[0]][key[1]]
        lines.append(f"  STALE {'/'.join(key)}{'' if listed else ' (not in the manifest yet)'}: {describe(changes)}")
    for key, changes in sorted(unused.items()):
        lines.append(f"  unused {'/'.join(key) or DownloadsPath}: {describe(changes)}")
    if (stale):
        lines.append(f"stale characters: {', '.join(staleCharacters(stale))} -- rebuild the manifest on a fresh export of AG Remap's {ref} "
                     "(AI Agent Help/Downloads, \"BUILD THE MANIFEST FROM AGREMAP'S master\") and regenerate them")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description = "name the characters whose download folders AG Remap changed since the manifest was built")
    parser.add_argument("--ref", default = "master", help = "AG Remap's ref to compare with (default: master)")
    parser.add_argument("--since", default = None, help = "compare from this AG Remap commit instead of the manifest's")
    args = parser.parse_args()

    try:
        built, head, stale, unused = findStale(args.ref, args.since)
    except GithubError as e:
        print(f"could not ask GitHub: {e}")
        return 2

    print("\n".join(report(built, head, stale, unused, args.ref)))
    return 1 if (stale) else 0


if (__name__ == "__main__"):
    sys.exit(main())
