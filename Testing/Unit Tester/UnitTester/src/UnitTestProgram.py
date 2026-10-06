from .AGRemapUtils import BaseTestProgram
from .Config import Configs, SysPaths
from .constants.ConfigKeys import ConfigKeys


# UnitTestProgram: Framework for running the overall unit tests
class UnitTestProgram(BaseTestProgram[ConfigKeys]):
    def __init__(self, *args, **kwargs):
        description = "Unit Tester for the Anime Game Identity Mod Generator"
        super().__init__(description, cmdBuilderArgs = [description, Configs, SysPaths, ConfigKeys.SysPath, ConfigKeys.System], *args, **kwargs)

    def runTests(self):
        # unittest applies -v / -q / -f only to a runner CLASS; 'main.py' passes an instance that writes to a file
        if (not self._isInit and not isinstance(self.testRunner, type)):
            self.testRunner.verbosity = self.verbosity
            self.testRunner.failfast = self.failfast

        super().runTests()
