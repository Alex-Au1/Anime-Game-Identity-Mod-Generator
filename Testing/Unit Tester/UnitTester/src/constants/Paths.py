import os


# Paths are resolved from this file, not from the launch directory, so the tester runs from anywhere
TesterRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RepoRoot = os.path.abspath(os.path.join(TesterRoot, "..", ".."))

# the folder holding the 'AGIDMGen' package source. Tests import the package from here, never from
#   site-packages, so a pip-installed release can never be the copy under test
SrcPath = os.path.join(RepoRoot, "AGIDMGen", "api", "src", "py")

# AG Remap's own source of AGRemapUtils ('<AGRemap>/Tools/Utilities/src/AGRemapUtils'), for a machine
#   where the AGRemapUtils package is not pip-installed
UtilitiesSrcEnvVar = "AGREMAP_UTILS_SRC"
