import os
import tempfile

from .baseUnitTest import BaseUnitTest, IDMG
from .captureLogger import CaptureLogger
from FixRaidenBoss2 import BaseLogger
from . import gimiAssetsFixture as gimi
from . import wwmiAssetsFixture as wwmi


class IDModGenServiceTest(BaseUnitTest):
    def setUp(self):
        super().setUp()
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.out = self.path("Out")

    def path(self, *parts) -> str:
        return os.path.join(self._temp.name, *parts)

    def gimiAssets(self, name: str = "Tester") -> str:
        folder = self.path("Assets", name)
        gimi.writeAssets(folder, name, gimi.oneComponent())
        return folder

    # =============== generate ==============================================

    def test_assetFolders_eachMod_badOneRecordedNotRaised(self):
        good = self.gimiAssets("Tester")
        other = self.gimiAssets("Other")
        bad = self.path("Assets", "Missing")
        logger = CaptureLogger()

        service = IDMG.IDModGenService(IDMG.ModLoaders.GIMI, assetsFolders = [good, bad, other], outputFolder = self.out, logger = logger)
        service.generate()

        self.assertEqual(sorted(service.stats.generated), ["Other", "Tester"])
        self.assertEqual(list(service.stats.skipped), ["Missing"])
        self.assertIsInstance(service.stats.skipped["Missing"], IDMG.BadAssetData)
        self.assertFalse(service.stats.noErrors)
        self.assertTrue(os.path.isfile(os.path.join(self.out, "Tester", "Tester.ini")))
        self.assertTrue(os.path.isfile(os.path.join(self.out, "Other", "Other.ini")))

        txt = "\n".join(logger.lines)
        self.assertIn("===== Tester =====", txt)
        self.assertIn("Could not generate 1:", txt)
        self.assertNotIn("ENJOY", txt)
        # a library error is reported by its message, not its traceback
        self.assertNotIn("Traceback", txt)

    def test_allGenerated_enjoy(self):
        logger = CaptureLogger()
        service = IDMG.IDModGenService(IDMG.ModLoaders.GIMI, assetsFolders = [self.gimiAssets()], outputFolder = self.out, logger = logger)
        service.generate()
        self.assertTrue(service.stats.noErrors)
        self.assertEqual(logger.lines[-1], "ENJOY")

    def test_noLogger_silentStatsStillKept(self):
        self.patch("builtins.print")
        service = IDMG.IDModGenService(IDMG.ModLoaders.GIMI, assetsFolders = [self.gimiAssets()], outputFolder = self.out)
        service.generate()
        self.assertEqual(list(service.stats.generated), ["Tester"])
        self.patches["builtins.print"].assert_not_called()

    def test_wwmiAndModName(self):
        folder = self.path("Assets", "Sanhua")
        wwmi.writeAssets(folder, wwmi.twoComponents())
        service = IDMG.IDModGenService(IDMG.ModLoaders.WWMI, assetsFolders = [folder], outputFolder = self.out, modName = "Renamed")
        service.generate()
        self.assertTrue(os.path.isfile(os.path.join(self.out, "Renamed", "mod.ini")))
        self.assertEqual(service.stats.generated["Sanhua"].name, "Renamed")

    def test_names_downloadedThroughTheDownloader(self):
        self.patchObj(IDMG.GIMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        downloader = IDMG.ModDownloader()
        service = IDMG.IDModGenService(IDMG.ModLoaders.GIMI, names = ["Yelan"], outputFolder = self.out, version = "4.0", downloader = downloader, downloadFolder = self.path("Dl"))
        service.generate()
        IDMG.GIMIIdentityModGenerator.generateFromRepo.assert_called_once_with("Yelan", os.path.join(self.out, "Yelan"), version = "4.0", downloader = downloader,
                                                                                downloadFolder = os.path.join(self.path("Dl"), "Yelan"), modName = None)
        self.assertEqual(list(service.stats.generated), ["Yelan"])

    # =============== bad options ===========================================

    def test_badOptions_raiseOrReported(self):
        folder = self.gimiAssets()
        tests = [("nothing to do", dict()),
                 ("mod name for two", dict(assetsFolders = [folder, folder], modName = "X")),
                 ("prefix for a name", dict(names = ["Yelan"], assetPrefix = "X")),
                 ("wrong generator", dict(assetsFolders = [folder], generator = IDMG.WWMIIdentityModGenerator()))]

        for name, kwargs in tests:
            with self.assertRaises(IDMG.Error, msg = name):
                IDMG.IDModGenService(IDMG.ModLoaders.GIMI, outputFolder = self.out, **kwargs).generate()

            logger = CaptureLogger()
            service = IDMG.IDModGenService(IDMG.ModLoaders.GIMI, outputFolder = self.out, handleExceptions = True, logger = logger, **kwargs)
            service.generate()
            self.assertTrue(any(line.endswith(BaseLogger.ErrorHeader) for line in logger.lines), name)
            self.assertFalse(any("Traceback" in line for line in logger.lines), name)
            self.assertEqual(service.stats.generated, {}, name)


def mock_mod():
    from unittest import mock
    mod = mock.Mock()
    mod.getSummary.return_value = ["summary"]
    return mod
