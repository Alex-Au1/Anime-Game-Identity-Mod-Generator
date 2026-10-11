import sys

from .AGRemapUtils import BuildEnvCommandBuilder
from .constants.Paths import ScriptToolPath

sys.path.insert(1, ScriptToolPath)
from Script.constants.BuildEnvs import BuildEnv


# CommandBuilder: Handles the options for building the script
#
# note: BuildEnv comes from the script's own source rather than from here. It is what a compiled
#   script reads to know how to reach the API, so the script has to carry it -- and having the
#   builder import the same enum keeps the two from drifting apart.
class CommandBuilder(BuildEnvCommandBuilder):
    Envs = BuildEnv
    DefaultEnv = BuildEnv.Dev
    EnvSubject = "the script"

    EnvDescriptions = {
        BuildEnv.Dev.value: "The script reaches the API by a path on this machine, the way the tools in this repo reach each other",
        BuildEnv.Prod.value: "The script downloads the API, AGIDMGen, from pypi when it runs, and gains the options for controlling that download. The committed script is a prod build"
    }

    def _addArguments(self):
        super()._addArguments()
        self._argParser.add_argument("--check", action = "store_true",
                                     help = "build nothing; exit 1 if the committed script build is not what the source builds for the environment given")
