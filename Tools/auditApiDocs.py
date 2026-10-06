#
# ===== auditApiDocs =====
#
# Checks that Docs/src/api.rst has an entry for every name in AGIDMGen.__all__, and none for a name
#   that is not exported:
#
#   py -3 Tools/auditApiDocs.py
#
# Exits 1 when the two disagree.
#

import os
import re
import sys

RepoRoot = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(RepoRoot, "AGIDMGen", "src", "py"))
import AGIDMGen as IDMG


def main() -> int:
    with open(os.path.join(RepoRoot, "Docs", "src", "api.rst"), "r", encoding = "utf-8") as f:
        documented = set(re.findall(r"^(\w+)\n~+\n", f.read(), re.MULTILINE))

    exported = set(IDMG.__all__)
    missing = sorted(exported - documented)
    extra = sorted(documented - exported)
    print(f"{len(exported)} exported names, {len(documented)} documented")
    if (missing):
        print(f"no api.rst entry: {', '.join(missing)}")
    if (extra):
        print(f"documented but not exported: {', '.join(extra)}")
    return 1 if (missing or extra) else 0


if (__name__ == "__main__"):
    sys.exit(main())
