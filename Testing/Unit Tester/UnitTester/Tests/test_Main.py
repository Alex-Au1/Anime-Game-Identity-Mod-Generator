import os
import tempfile

from .baseUnitTest import BaseUnitTest, IDMG
from .captureLogger import CaptureLogger
from . import gimiAssetsFixture as gimi

from AGIDMGen.main import main, askArgs, LogFileName


class ScriptedLogger(CaptureLogger):
    """A logger that answers each question with the next of its answers, as a user typing them would"""

    def __init__(self, answers):
        super().__init__()
        self.answers = list(answers)
        self.questions = []

    def read(self, desc: str) -> str:
        self.questions.append(desc)
        if (not self.answers):
            raise EOFError()
        return self.answers.pop(0)


class MainTest(BaseUnitTest):
    def setUp(self):
        super().setUp()
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.patch("builtins.print")

    def path(self, *parts) -> str:
        return os.path.join(self._temp.name, *parts)

    # =============== main ==================================================

    def test_assetFolders_exitCodes(self):
        good = self.path("Assets", "Tester")
        gimi.writeAssets(good, "Tester", gimi.oneComponent())
        tests = [([good], 0), ([good, self.path("Assets", "Missing")], 1), ([], 1)]
        for sources, expected in tests:
            self.assertEqual(main(["gimi"] + sources + ["--out", self.path("Out"), "--quiet"]), expected, sources)
        self.assertTrue(os.path.isfile(self.path("Out", "Tester", "Tester.ini")))

    def test_logFile_writtenWithEverything(self):
        good = self.path("Assets", "Tester")
        gimi.writeAssets(good, "Tester", gimi.oneComponent())
        self.assertEqual(main(["GIMI", good, "--out", self.path("Out"), "--log", self.path("Log"), "--quiet", "--noFix"]), 0)
        with open(self.path("Log", LogFileName), encoding = "utf-8") as f:
            txt = f.read()
        self.assertIn("Summary", txt)
        self.assertIn("ENJOY", txt)

    def test_badArguments_exit1(self):
        tests = [["gimi", "Yelan", "--all"], ["gimi", "Yelan", "--download", "--localData", "Nowhere=x"]]
        for argv in tests:
            self.assertEqual(main(argv + ["--quiet"]), 1, argv)

    # =============== no arguments: the script double-clicked ===============

    def test_askArgs_reaskUntilValid(self):
        tests = [(["genshin", "WWMI", "", "Sanhua  Aalto"], ["wwmi", "Sanhua", "Aalto", "--download"]),
                 (["gimi", "ALL"], ["gimi", "--download", "--all"]),
                 (["GIMI", "Yelan"], ["gimi", "Yelan", "--download"])]
        for answers, expected in tests:
            logger = ScriptedLogger(answers)
            self.assertEqual(askArgs(logger), expected, answers)
            self.assertFalse(logger.answers, answers)
            self.assertTrue(all("-->" not in question for question in logger.questions), logger.questions)
            self.assertTrue(logger.includePrefix)

    def test_noArguments_asksRunsThenWaitsForEnter(self):
        self.patch("AGIDMGen.main.run", return_value = 0)
        logger = ScriptedLogger(["gimi", "Yelan", ""])
        self.assertEqual(main([], logger = logger), 0)
        args = self.patches["AGIDMGen.main.run"].call_args[0][0]
        self.assertEqual((args.loader, args.sources, args.download), ("gimi", ["Yelan"], True))
        self.assertIn("Press ENTER", logger.questions[-1])

    def test_noArguments_noInput_exit1(self):
        self.patch("AGIDMGen.main.run", return_value = 0)
        self.assertEqual(main([], logger = ScriptedLogger([])), 1)
        self.patches["AGIDMGen.main.run"].assert_not_called()

    def test_arguments_neverAsk(self):
        logger = ScriptedLogger([])
        self.assertEqual(main(["gimi", "Yelan", "--all", "--quiet"], logger = logger), 1)
        self.assertEqual(logger.questions, [])
