import os
import tempfile

from .baseUnitTest import BaseUnitTest, IDMG
from . import gimiAssetsFixture as gimi

from AGIDMGen.main import main, LogFileName


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
