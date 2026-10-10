import os


# Paths are resolved from this file, not from the launch directory, so the builder runs from anywhere
ToolRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RepoRoot = os.path.abspath(os.path.join(ToolRoot, "..", ".."))

# the folder holding the 'AGIDMGen' package source, and the package itself
SrcPath = os.path.join(RepoRoot, "AGIDMGen", "api", "src", "py")
PackageName = "AGIDMGen"
PackageFolder = os.path.join(SrcPath, PackageName)

# the package's metadata, which the script's version and dependencies are read from
PyProjectPath = os.path.join(RepoRoot, "AGIDMGen", "api", "pyproject.toml")

# where the compiled script is written, beside the API's folder, as AG Remap's
#   'Anime Game Remap (for all users)/script build/src/FixRaidenBoss2/AGRemap.py' sits beside its 'api'
ScriptFolder = os.path.join(RepoRoot, "AGIDMGen", "script build", "src", PackageName)
ScriptName = f"{PackageName}.py"
ScriptPath = os.path.join(ScriptFolder, ScriptName)

# AG Remap's own source of AGRemapUtils ('<AGRemap>/Tools/Utilities/src/AGRemapUtils'), for a machine
#   where the AGRemapUtils package is not pip-installed
UtilitiesSrcEnvVar = "AGREMAP_UTILS_SRC"
