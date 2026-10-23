#
# ===== exportAGRemapDownloads =====
#
# Exports AG Remap's Data/Mod Downloads exactly as a git ref has it (by default origin/master: what the
# library downloads from), without touching the AG Remap checkout's branch or working tree:
#
#   git -C <AGRemap> fetch origin master
#   py -3 Tools/Downloads/exportAGRemapDownloads.py <AGRemap repo> <out folder> [--ref origin/master]
#
# It also writes '<out folder>/AGRemapCommit.txt', the full hash of the exported commit, which buildDownloadManifest.py
# records in the manifest so Tools/Downloads/staleManifest.py can tell what AG Remap changed since.
#
# Then give '<out folder>/Data/Mod Downloads' to buildDownloadManifest.py (and populateDownloads.py,
# hashFromAGRemap.py, downloadsCheck.py) instead of the checkout's own folder, which may be on another
# branch. Files come out as the commit stores them (LF line endings), as GitHub serves them.
#

import argparse
import io
import os
import shutil
import subprocess
import sys
import tarfile

DownloadsPath = "Data/Mod Downloads"
CommitFile = "AGRemapCommit.txt"


def main() -> int:
    parser = argparse.ArgumentParser(description = "export AG Remap's Data/Mod Downloads as a git ref has it")
    parser.add_argument("agRemap", help = "AG Remap's repository (its root folder)")
    parser.add_argument("out", help = "the folder to export into; its 'Data/Mod Downloads' is replaced")
    parser.add_argument("--ref", default = "origin/master", help = "the git ref to export (default: origin/master; fetch it first)")
    args = parser.parse_args()

    commit = subprocess.run(["git", "-C", args.agRemap, "rev-parse", args.ref], capture_output = True, text = True)
    if (commit.returncode != 0):
        raise SystemExit(f"'{args.ref}' is not a ref of {args.agRemap}: {commit.stderr.strip()}")

    archive = subprocess.run(["git", "-C", args.agRemap, "archive", "--format=tar", args.ref, "--", DownloadsPath], capture_output = True)
    if (archive.returncode != 0):
        raise SystemExit(f"git archive failed: {archive.stderr.decode(errors = 'replace').strip()}")

    target = os.path.join(args.out, *DownloadsPath.split("/"))
    if (os.path.isdir(target)):
        shutil.rmtree(target)
    os.makedirs(args.out, exist_ok = True)

    with tarfile.open(fileobj = io.BytesIO(archive.stdout)) as tar:
        members = [m for m in tar.getmembers() if m.isfile()]
        tar.extractall(args.out, members = members)

    with open(os.path.join(args.out, CommitFile), "w", encoding = "utf-8", newline = "\n") as f:
        f.write(commit.stdout.strip() + "\n")

    print(f"exported {len(members)} files of {args.ref} ({commit.stdout.strip()[:8]}) into {target}")
    return 0


if (__name__ == "__main__"):
    sys.exit(main())
