import sys
import unittest
from unittest import mock
from typing import Dict, Any, Hashable, List, Optional, Callable

from ..src.constants.Paths import SrcPath

sys.path.insert(0, SrcPath)
import AGIDMGen as IDMG


class PatchService:
    def _cleanup(self, patch, target):
        patch.stop()
        self.patches.pop(target)

    def patch(self, target, *args, **kwargs):
        p = mock.patch(target, *args, **kwargs)
        patchedMock = p.start()
        self.addCleanup(self._cleanup, *[p, target])
        self.patches[target] = patchedMock

    def patchObj(self, target, *args, **kwargs):
        p = mock.patch.object(target, *args, **kwargs)
        patchedMock = p.start()
        self.addCleanup(self._cleanup, *[p, target])
        self.patches[target] = patchedMock


class BaseUnitTest(unittest.TestCase, PatchService):
    @classmethod
    def setUpClass(cls):
        cls.patches: Dict[str, mock.Mock] = {}

    def getDataFailMsg(self, result: Any, expected: Any, msg: str):
        return f"{msg}\n\nresult: {result}\n\nexpected: {expected}"

    def compareDict(self, resultDict: Dict[Hashable, Any], expectedDict: Dict[Hashable, Any], compareValues: Optional[Callable[[Any, Any], None]] = None):
        resultDictLen = len(resultDict)
        expectedDictLen = len(expectedDict)
        if (resultDictLen != expectedDictLen):
            self.fail(self.getDataFailMsg(resultDict, expectedDict, f"Dictionaries have different lengths: resultDict: {resultDictLen}, expectedDict: {expectedDictLen}"))

        for resultKey in resultDict:
            if (resultKey not in expectedDict):
                self.fail(self.getDataFailMsg(resultDict, expectedDict, f"The key, '{resultKey}', is not in the expected dictionary"))

            resultValue = resultDict[resultKey]
            expectedValue = expectedDict[resultKey]

            if (compareValues is None and resultValue != expectedValue):
                self.fail(self.getDataFailMsg(resultDict, expectedDict, f"Different values for the key, {resultKey}, in both dictionaries: resultDict: {resultValue}, expectedDict: {expectedValue}"))
            elif (compareValues is not None):
                compareValues(resultValue, expectedValue)

    def compareList(self, resultLst: List[Any], expectedLst: List[Any], compareValues: Optional[Callable[[Any, Any], None]] = None):
        resultLstLen = len(resultLst)
        expectedLstLen = len(expectedLst)
        if (resultLstLen != expectedLstLen):
            self.fail(self.getDataFailMsg(resultLst, expectedLst, f"Lists have different lengths: resultLst: {resultLstLen}, expectedLst: {expectedLstLen}"))

        for i in range(resultLstLen):
            if (compareValues is None and resultLst[i] != expectedLst[i]):
                self.fail(self.getDataFailMsg(resultLst, expectedLst, f"Different values at index {i}: resultLst: {resultLst[i]}, expectedLst: {expectedLst[i]}"))
            elif (compareValues is not None):
                compareValues(resultLst[i], expectedLst[i])
