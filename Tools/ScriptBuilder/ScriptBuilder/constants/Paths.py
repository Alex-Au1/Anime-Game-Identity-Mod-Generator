import os


# Paths are resolved from this file, not from the launch directory, so the builder runs from anywhere
ToolRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RepoRoot = os.path.abspath(os.path.join(ToolRoot, "..", ".."))

# the folder holding the API's 'AGIDMGen' package source, which a 'dev' build of the script puts onto its import
#   path -- the package folder itself would be one level too deep to import from
SrcPath = os.path.join(RepoRoot, "AGIDMGen", "api", "src", "py")
APIPackage = "AGIDMGen"

# the API's metadata, which the script's version is read from
PyProjectPath = os.path.join(RepoRoot, "AGIDMGen", "api", "pyproject.toml")

# the API's main module, which the script's credits are read from
APIMainPath = os.path.join(SrcPath, APIPackage, "main.py")

# the script's own source, which is what actually gets compiled
ScriptToolPath = os.path.join(RepoRoot, "Tools", "Script")
ScriptPackageName = "Script"
ScriptPackageFolder = os.path.join(ScriptToolPath, ScriptPackageName)

# where the compiled script is written, beside the API's folder, as AG Remap's
#   'Anime Game Remap (for all users)/script build/src/FixRaidenBoss2/AGRemap.py' sits beside its 'api'
ScriptFolder = os.path.join(RepoRoot, "AGIDMGen", "script build", "src", APIPackage)
ScriptName = f"{APIPackage}.py"
ScriptPath = os.path.join(ScriptFolder, ScriptName)

# AG Remap's own source of AGRemapUtils ('<AGRemap>/Tools/Utilities/src/AGRemapUtils'), for a machine
#   where the AGRemapUtils package is not pip-installed
UtilitiesSrcEnvVar = "AGREMAP_UTILS_SRC"
