#
# ===== ScriptBuilder =====
#
# Compiles the script's source (Tools/Script) into a single script, 'AGIDMGen/script build/src/AGIDMGen/AGIDMGen.py', for
#   users who do not know how to install a python package:
#
#   py -3 Tools/ScriptBuilder/main.py --env prod            build the script that is committed (downloads AGIDMGen from pypi)
#   py -3 Tools/ScriptBuilder/main.py                       build a dev script (reaches AGIDMGen/api by a path)
#   py -3 Tools/ScriptBuilder/main.py --env prod --check    exit 1 if the committed script is not what the source builds
#
# Every .py file under 'AGIDMGen/script build/' is GENERATED: rerun this tool, never edit them. See README.md.
#

import os
import re
import sys
from types import SimpleNamespace
from typing import Dict, List

from ScriptBuilder.constants.Paths import SrcPath, APIPackage, PyProjectPath, APIMainPath, ScriptToolPath, ScriptPackageName, ScriptPackageFolder, \
    ScriptFolder, ScriptName
from ScriptBuilder.constants.BoilerPlate import ScriptPreamble, ScriptPreambleScriptStats, ScriptPostamble, VolatilePreambleLines, \
    BuildEnvReplace, APIRelPathReplace, APIPackageReplace, ScriptBuilderVersion
from ScriptBuilder.AGRemapUtils import BuildMetadata, VersionReplace, RanDateTimeReplace, RanHashReplace, BuiltDateTimeReplace, BuildHashReplace
from ScriptBuilder.CommandBuilder import CommandBuilder
from ScriptBuilder.IDModGenScriptBuilder import IDModGenScriptBuilder

MainModule = "main"
MainFunc = "main"


# getModules(): Retrieves every module of the script's source, by its module path
#
# note: the source is found by its files rather than imported, so building never runs any of it
def getModules() -> Dict[str, SimpleNamespace]:
    result = {}
    for folder, dirs, files in os.walk(ScriptPackageFolder):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files:
            if (not file.endswith(".py")):
                continue

            path = os.path.join(folder, file)
            parts = os.path.relpath(path, ScriptToolPath)[:-len(".py")].split(os.sep)
            if (parts[-1] == "__init__"):
                parts.pop()
            result[".".join(parts)] = SimpleNamespace(__file__ = path)
    return result


# readVersion(): Retrieves the API's version, which is also the script's
def readVersion() -> str:
    with open(PyProjectPath, encoding = "utf-8") as f:
        return re.search(r'^version\s*=\s*"([^"]+)"', f.read(), re.MULTILINE).group(1)


# readCredits(): Retrieves the API's credits, as the lines of its main module's credits section
def readCredits() -> List[str]:
    with open(APIMainPath, encoding = "utf-8") as f:
        txt = f.read()
    return re.search(r"##### Credits\n(.*?)##### EndCredits", txt, re.DOTALL).group(1).splitlines(keepends = True)


# getApiRelPath(): Retrieves where the API's package sits, relative to the compiled script
#
# note: written with '/' rather than os.sep, so a script compiled on one OS still finds the API on another
def getApiRelPath() -> str:
    return os.path.relpath(SrcPath, ScriptFolder).replace(os.sep, "/")


def makeBuilder(env) -> IDModGenScriptBuilder:
    creditsLines = readCredits()

    builderStats = BuildMetadata(version = ScriptBuilderVersion)
    scriptStats = BuildMetadata(version = readVersion())

    front = ScriptPreamble.replace(VersionReplace, builderStats.version)
    front = front.replace(RanDateTimeReplace, builderStats.getFormattedDatetime()).replace(RanHashReplace, builderStats.buildHash)

    back = ScriptPreambleScriptStats.replace(VersionReplace, scriptStats.version)
    back = back.replace(BuiltDateTimeReplace, scriptStats.getFormattedDatetime()).replace(BuildHashReplace, scriptStats.buildHash)

    credits = "".join(creditsLines).strip("\n")
    preamble = f"{front}\n\n{credits}\n{back}"
    postamble = f"\n\n{ScriptPostamble}\n"

    # what this build of the script needs to know about reaching the API
    replacements = {BuildEnvReplace: env.value, APIRelPathReplace: getApiRelPath(), APIPackageReplace: APIPackage}
    return IDModGenScriptBuilder(ScriptFolder, ScriptName, getModules(), f"{ScriptPackageName}.{MainModule}", ScriptPackageFolder,
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
    print("The script build is out of date: rerun Tools/ScriptBuilder/main.py --env prod" if (stale) else "The script build is up to date")
    return not stale


if __name__ == "__main__":
    args = CommandBuilder().parse()
    builder = makeBuilder(args.env)

    if (args.check):
        sys.exit(0 if check(builder) else 1)

    print(f"Building the script for the '{args.env.value}' environment")
    os.makedirs(ScriptFolder, exist_ok = True)
    builder.build()
