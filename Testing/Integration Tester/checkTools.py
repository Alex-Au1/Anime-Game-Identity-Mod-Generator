#
# ===== checkTools =====
#
# What wwmiCheck.py and gimiCheck.py share: running AG Remap's prototype beside this library, and
# comparing the two mod folders they write file by file.
#

import filecmp
import re
import os
import subprocess
import sys
from typing import List, Optional, Tuple

RepoRoot = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(RepoRoot, "AGIDMGen", "src", "py"))


def readIniLines(path: str, generatorLines: Tuple[str, ...]) -> List[bytes]:
    """The .ini's lines, without the ones that name the program that wrote it"""
    with open(path, "rb") as f:
        lines = f.read().split(b"\r\n")
    return [line for line in lines if not line.decode("utf-8").startswith(generatorLines)]


def compareTrees(expectedRoot: str, resultRoot: str, generatorLines: Tuple[str, ...]) -> Tuple[List[str], int]:
    """Every difference between two mod folders, and the number of files both have. A .ini may differ
    only in the lines starting with one of 'generatorLines'"""
    differences = []
    expectedFiles = {os.path.relpath(os.path.join(d, f), expectedRoot) for d, _, fs in os.walk(expectedRoot) for f in fs}
    resultFiles = {os.path.relpath(os.path.join(d, f), resultRoot) for d, _, fs in os.walk(resultRoot) for f in fs}
    for missing in sorted(expectedFiles ^ resultFiles):
        differences.append(f"{missing} written by only one of the two")

    for path in sorted(expectedFiles & resultFiles):
        expected = os.path.join(expectedRoot, path)
        result = os.path.join(resultRoot, path)
        if (path.lower().endswith(".ini")):
            same = (readIniLines(expected, generatorLines) == readIniLines(result, generatorLines))
        else:
            same = filecmp.cmp(expected, result, shallow = False)
        if (not same):
            differences.append(f"{path} differs")
    return differences, len(expectedFiles & resultFiles)


def runPrototype(prototype: str, args: List[str]) -> Tuple[Optional[str], str]:
    """Runs a prototype script: (its error, the last line it printed to stderr, or None if it succeeded; all of its stderr)"""
    run = subprocess.run([sys.executable, prototype] + args, capture_output = True, text = True)
    error = None if (run.returncode == 0) else (run.stderr.strip().splitlines() or ["(no message)"])[-1]
    return error, run.stderr


def sameRefusal(prototypeError: Optional[str], libraryError: Optional[str]) -> bool:
    """Whether both programs refused for the same reason: the prototype exits through
    SystemExit(message), and the library raises Error("ERROR: " + message). A prototype that crashed
    opening a file it composed the name of (FileNotFoundError) agrees with a library that reported the
    same file missing"""
    if (prototypeError is None or libraryError is None):
        return False
    if (libraryError.endswith(prototypeError)):
        return True

    missing = re.match(r"FileNotFoundError: \[Errno 2\] No such file or directory: '(.*)'$", prototypeError)
    return (missing is not None and f"'{missing.group(1).replace(chr(92) * 2, chr(92))}' is missing" in libraryError)
