#
# ===== ScriptBuilder =====
#
# Compiles AGIDMGen's source into a single script, 'AGIDMGen/script build/src/AGIDMGen/AGIDMGen.py', for users who do not
#   know how to install a python package:
#
#   py -3 Tools/ScriptBuilder/main.py            build the script
#   py -3 Tools/ScriptBuilder/main.py --check    exit 1 if the committed script is not what the source builds
#
# Every .py file under 'AGIDMGen/script build/' is GENERATED: rerun this tool, never edit them. See README.md.
#

import argparse
import os
import re
import sys
from types import SimpleNamespace
from typing import Dict, List, Tuple

from ScriptBuilder.constants.Paths import SrcPath, PackageName, PackageFolder, PyProjectPath, ScriptFolder, ScriptName
from ScriptBuilder.constants.BoilerPlate import ScriptPreamble, ScriptPreambleScriptStats, ScriptDependencies, ScriptMainDriver, ScriptPostamble, \
    VolatilePreambleLines, DependenciesReplace, MainFuncReplace, ScriptBuilderVersion
from ScriptBuilder.AGRemapUtils import BuildMetadata, VersionReplace, RanDateTimeReplace, RanHashReplace, BuiltDateTimeReplace, BuildHashReplace
from ScriptBuilder.IDModGenScriptBuilder import IDModGenScriptBuilder

MainModule = "main"
MainFunc = "main"


# getModules(): Retrieves every module of the package, by its module path
#
# note: the package is found by its files rather than imported, so building the script never needs the
#   library's own dependencies (numpy, FixRaidenBoss2)
def getModules() -> Dict[str, SimpleNamespace]:
    result = {}
    for folder, dirs, files in os.walk(PackageFolder):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files:
            if (not file.endswith(".py")):
                continue

            path = os.path.join(folder, file)
            parts = os.path.relpath(path, SrcPath)[:-len(".py")].split(os.sep)
            if (parts[-1] == "__init__"):
                parts.pop()
            result[".".join(parts)] = SimpleNamespace(__file__ = path)
    return result


# readPyProject(): Retrieves the package's version, and its dependencies as (module to import, pip requirement)
def readPyProject() -> Tuple[str, List[Tuple[str, str]]]:
    with open(PyProjectPath, encoding = "utf-8") as f:
        txt = f.read()

    version = re.search(r'^version\s*=\s*"([^"]+)"', txt, re.MULTILINE).group(1)
    requirements = re.findall(r'"([^"]+)"', re.search(r"^dependencies\s*=\s*\[([^\]]*)\]", txt, re.MULTILINE).group(1))
    dependencies = [(re.match(r"[A-Za-z0-9_.\-]+", requirement).group(0), requirement) for requirement in requirements]
    return version, dependencies


# readCredits(): Retrieves the library's credits, as the lines of its main module's credits section
def readCredits() -> List[str]:
    with open(os.path.join(PackageFolder, f"{MainModule}.py"), encoding = "utf-8") as f:
        txt = f.read()
    return re.search(r"##### Credits\n(.*?)##### EndCredits", txt, re.DOTALL).group(1).splitlines(keepends = True)


def makeBuilder() -> IDModGenScriptBuilder:
    version, dependencies = readPyProject()
    creditsLines = readCredits()

    builderStats = BuildMetadata(version = ScriptBuilderVersion)
    scriptStats = BuildMetadata(version = version)

    front = ScriptPreamble.replace(VersionReplace, builderStats.version)
    front = front.replace(RanDateTimeReplace, builderStats.getFormattedDatetime()).replace(RanHashReplace, builderStats.buildHash)

    back = ScriptPreambleScriptStats.replace(VersionReplace, scriptStats.version)
    back = back.replace(BuiltDateTimeReplace, scriptStats.getFormattedDatetime()).replace(BuildHashReplace, scriptStats.buildHash)

    credits = "".join(creditsLines).strip("\n")
    preamble = f"{front}\n\n{credits}\n{back}{ScriptDependencies}\n\n"
    postamble = f"{ScriptMainDriver}\n{ScriptPostamble}\n"

    replacements = {DependenciesReplace: repr(dependencies), MainFuncReplace: MainFunc}
    return IDModGenScriptBuilder(ScriptFolder, ScriptName, getModules(), f"{PackageName}.{MainModule}", PackageFolder,
                                 creditsLines = creditsLines, mainFunc = MainFunc,
                                 scriptPreamble = preamble, scriptPostAmble = postamble, replacements = replacements)


# withoutVolatileLines(txt): The text without the preamble lines that change on every build
def withoutVolatileLines(txt: str) -> List[str]:
    return [line for line in txt.splitlines() if not line.startswith(VolatilePreambleLines)]


# check(builder): Whether every committed file of the script build is what the source builds now
def check(builder: IDModGenScriptBuilder) -> bool:
    stale = []
    for path, txt in builder.getFiles().items():
        if (not os.path.isfile(path)):
            stale.append(f"{path} is missing")
            continue

        with open(path, encoding = "utf-8", newline = "") as f:
            committed = f.read()
        if (withoutVolatileLines(committed) != withoutVolatileLines(txt)):
            stale.append(f"{path} is out of date")

    for line in stale:
        print(line)
    print("The script build is out of date: rerun Tools/ScriptBuilder/main.py" if (stale) else "The script build is up to date")
    return not stale


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Compiles AGIDMGen's source into a single script")
    parser.add_argument("--check", action = "store_true", help = "build nothing; exit 1 if the committed script build is not what the source builds")
    args = parser.parse_args()

    builder = makeBuilder()
    if (args.check):
        sys.exit(0 if check(builder) else 1)

    os.makedirs(ScriptFolder, exist_ok = True)
    builder.build()
