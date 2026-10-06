import os
import unittest

from UnitTester.src.UnitTestProgram import UnitTestProgram
from UnitTester.src.AGRemapUtils import TesterFailed


UnitTestResultsFileName = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unitTestResults.txt')
fileEncoding = "utf-8"


if __name__ == '__main__':
    with open(UnitTestResultsFileName, "w", encoding = fileEncoding) as f:
        runner = unittest.TextTestRunner(f)
        unitTester = UnitTestProgram(testRunner = runner, exit = False)
        unitTester.testCommandBuilder.parse()

        from UnitTester.Tests import *
        unitTester.run()

    with open(UnitTestResultsFileName, "r", encoding = fileEncoding) as f:
        fileTxt = f.read()
        print(fileTxt)

        # a run that found no tests (a mistyped name) is a failure, not a pass
        testScore = fileTxt.split("\n", 1)[0]
        if (testScore.find("F") > -1 or testScore.find("E") > -1 or fileTxt.find("Ran 0 tests") > -1):
            raise TesterFailed("unit")
