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

        service = IDMG.IDModGenService(assetsFolders = [good, bad, other], outputFolder = self.out, logger = logger)
        service.generate()

        self.assertEqual(sorted(service.stats.generated), ["Other", "Tester"])
        self.assertEqual(list(service.stats.skipped), ["Missing"])
        self.assertIsInstance(service.stats.skipped["Missing"], IDMG.BadAssetData)
        self.assertIn("is not a folder", str(service.stats.skipped["Missing"]))
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
        service = IDMG.IDModGenService(assetsFolders = [self.gimiAssets()], outputFolder = self.out, logger = logger)
        service.generate()
        self.assertTrue(service.stats.noErrors)
        self.assertEqual(logger.lines[-1], "ENJOY")

    def test_noLogger_silentStatsStillKept(self):
        self.patch("builtins.print")
        service = IDMG.IDModGenService(assetsFolders = [self.gimiAssets()], outputFolder = self.out)
        service.generate()
        self.assertEqual(list(service.stats.generated), ["Tester"])
        self.patches["builtins.print"].assert_not_called()

    def test_wwmiAndNameReplace(self):
        folder = self.path("Assets", "Sanhua")
        wwmi.writeAssets(folder, wwmi.twoComponents())
        service = IDMG.IDModGenService(assetsFolders = [folder, self.gimiAssets()], outputFolder = self.out, nameReplace = {"sanhua": "Renamed"})
        service.generate()
        self.assertTrue(os.path.isfile(os.path.join(self.out, "Renamed", "mod.ini")))
        with open(os.path.join(self.out, "Renamed", "mod.ini"), encoding = "utf-8") as f:
            lines = f.read().splitlines()
        self.assertEqual(lines[-2:], ["; Authors: Albert Gold#2696", "; Github: https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator"])
        self.assertTrue(os.path.isfile(os.path.join(self.out, "Tester", "Tester.ini")))
        self.assertEqual(service.stats.generated["Sanhua"].name, "Renamed")

    def test_names_aBaseNameIsEveryPart(self):
        tests = [(["carlotta"], ["CarlottaBody", "CarlottaHairCrystal", "CarlottaHairNormal"]),
                 (["Augusta"], ["Augusta", "AugustaHelm"]),
                 (["carlotta", "CarlottaBody", "lupa"], ["CarlottaBody", "CarlottaHairCrystal", "CarlottaHairNormal", "LupaBody", "LupaTail"]),
                 (["CarlottaBody"], ["CarlottaBody"])]
        self.patchObj(IDMG.WWMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        for names, expected in tests:
            IDMG.WWMIIdentityModGenerator.generateFromRepo.reset_mock()
            service = IDMG.IDModGenService(names = names, outputFolder = self.out)
            service.generate()
            self.assertEqual([c.args[0] for c in IDMG.WWMIIdentityModGenerator.generateFromRepo.call_args_list], expected, names)
            self.assertEqual(list(service.stats.generated), expected, names)

    def test_nameReplace_partsByBaseName_laterWins(self):
        names = ["CarlottaBody", "CarlottaHairCrystal", "CarlottaSummerBody", "Augusta", "AugustaHelm", "Yelan"]
        tests = [({"carlotta": "Shorty"}, {"CarlottaBody": "ShortyBody", "CarlottaHairCrystal": "ShortyHairCrystal"}),
                 ({"Carlotta": "Shorty", "carlottabody": "Body2"}, {"CarlottaHairCrystal": "ShortyHairCrystal", "CarlottaBody": "Body2"}),
                 ({"carlottabody": "Body2", "Carlotta": "Shorty"}, {"CarlottaBody": "ShortyBody", "CarlottaHairCrystal": "ShortyHairCrystal"}),
                 ({"CarlottaSummer": "Beach"}, {"CarlottaSummerBody": "BeachBody"}),
                 # a whole character with parts of its own renames them too
                 ({"augusta": "Aug"}, {"Augusta": "Aug", "AugustaHelm": "AugHelm"}),
                 ({"augustahelm": "Hat"}, {"AugustaHelm": "Hat"})]
        for nameReplace, expected in tests:
            service = IDMG.IDModGenService(names = names, outputFolder = self.out, nameReplace = nameReplace)
            self.assertEqual(service.getNameReplacements(), expected, nameReplace)

    def test_nameReplace_unusablePairsSkippedWithAReason(self):
        tests = [({"zibai": "X", "someNonExistentchar": "fooo"}, {}, ["none of the characters", "none of the characters"]),
                 # a name found inside a key is not the key's (Raiden's 'Ei' is in 'Heizo')
                 ({"Heizo": "X"}, {}, ["none of the characters"]),
                 ({"yelan": "a/b", "ei": "has space"}, {}, ["only letters", "only letters"]),
                 # two characters cannot share a folder: the later is skipped, as is one taking a kept character's folder
                 ({"yelan": "Same", "ei": "same"}, {"Yelan": "Same"}, ["Yelan's mod"]),
                 ({"ei": "Yelan"}, {}, ["Yelan's mod"]),
                 # swapping two names is fine
                 ({"ei": "Yelan", "yelan": "Raiden"}, {"Raiden": "Yelan", "Yelan": "Raiden"}, [])]
        for nameReplace, expected, reasons in tests:
            service = IDMG.IDModGenService(names = ["ei", "Yelan"], outputFolder = self.out, nameReplace = nameReplace)
            ignored = []
            self.assertEqual(service.getNameReplacements(ignored), expected, nameReplace)
            self.assertEqual(len(ignored), len(reasons), (nameReplace, ignored))
            for reason, expectedReason in zip(ignored, reasons):
                self.assertIn(expectedReason, reason, nameReplace)

    def test_nameReplace_skippedPairsReportedRunStillClean(self):
        self.patchObj(IDMG.GIMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        logger = CaptureLogger()
        service = IDMG.IDModGenService(names = ["Yelan"], outputFolder = self.out, nameReplace = {"zibai": "X", "yelan": "Y"}, logger = logger)
        service.generate()
        self.assertTrue(service.stats.noErrors)
        self.assertEqual(IDMG.GIMIIdentityModGenerator.generateFromRepo.call_args.args[1], os.path.join(self.out, "Y"))
        self.assertTrue(any("Not renaming a character: 'zibai'" in line for line in logger.lines))

    def test_nameReplace_byAnyNameOrAlias_laterKeyWins(self):
        self.patchObj(IDMG.GIMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        self.patchObj(IDMG.WWMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        service = IDMG.IDModGenService(names = ["ei", "Zani", "Yelan"], outputFolder = self.out,
                                       nameReplace = {"ei": "Raiden1", "zaniarchive": "Shorty", "RaidenShogun": "Raiden2"})
        self.assertEqual(service.getNameReplacements(), {"Zani": "Shorty", "Raiden": "Raiden2"})
        service.generate()

        calls = [(c.args[0], c.args[1], c.kwargs["modName"]) for loader in (IDMG.GIMIIdentityModGenerator, IDMG.WWMIIdentityModGenerator)
                 for c in loader.generateFromRepo.call_args_list]
        self.assertEqual(sorted(calls), [("Raiden", os.path.join(self.out, "Raiden2"), "Raiden2"), ("Yelan", os.path.join(self.out, "Yelan"), None),
                                         ("Zani", os.path.join(self.out, "Shorty"), "Shorty")])
        # the stats keep each character's own name
        self.assertEqual(sorted(service.stats.generated), ["Raiden", "Yelan", "Zani"])

    def test_names_downloadedThroughTheDownloader(self):
        self.patchObj(IDMG.GIMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        downloader = IDMG.ModDownloader()
        service = IDMG.IDModGenService(names = ["Yelan"], outputFolder = self.out, version = "4.0", downloader = downloader, downloadFolder = self.path("Dl"))
        service.generate()
        IDMG.GIMIIdentityModGenerator.generateFromRepo.assert_called_once_with("Yelan", os.path.join(self.out, "Yelan"), version = "4.0", downloader = downloader,
                                                                                downloadFolder = os.path.join(self.path("Dl"), "Yelan"), modName = None)
        self.assertEqual(list(service.stats.generated), ["Yelan"])

    def test_names_byAlias_madeOnceUnderTheModsName(self):
        self.patchObj(IDMG.GIMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        service = IDMG.IDModGenService(names = ["ei", "RaidenShogun", "Raiden", "yelan", "NotACharacterXYZ"], outputFolder = self.out)
        service.generate()
        calls = [(c.args[0], c.args[1]) for c in IDMG.GIMIIdentityModGenerator.generateFromRepo.call_args_list]
        self.assertEqual(calls, [("Raiden", os.path.join(self.out, "Raiden")), ("Yelan", os.path.join(self.out, "Yelan"))])
        # a name that is no character's is recorded against the name typed, with why
        self.assertEqual(list(service.stats.skipped), ["NotACharacterXYZ"])
        self.assertIn("no GI/WuWa character called 'NotACharacterXYZ'", str(service.stats.skipped["NotACharacterXYZ"]))

    def test_names_ofBothGames_eachByItsGamesGenerator(self):
        self.patchObj(IDMG.GIMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        self.patchObj(IDMG.WWMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        service = IDMG.IDModGenService(names = ["Zani", "Ayaka", "SanhuaSkin1", "ei"], outputFolder = self.out)
        service.generate()

        gi = [c.args[0] for c in IDMG.GIMIIdentityModGenerator.generateFromRepo.call_args_list]
        wuwa = [c.args[0] for c in IDMG.WWMIIdentityModGenerator.generateFromRepo.call_args_list]
        self.assertEqual((gi, wuwa), (["Ayaka", "Raiden"], ["Zani", "SanhuaExorcist"]))
        self.assertEqual(list(service.stats.generated), ["Zani", "Ayaka", "SanhuaExorcist", "Raiden"])

    def test_names_onlyTheGamesAsked(self):
        self.patchObj(IDMG.GIMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        self.patchObj(IDMG.WWMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        service = IDMG.IDModGenService(names = ["Zani", "Ayaka"], outputFolder = self.out, loaders = [IDMG.ModLoaders.GIMI])
        service.generate()
        self.assertEqual(list(service.stats.generated), ["Ayaka"])
        self.assertEqual(list(service.stats.skipped), ["Zani"])
        IDMG.WWMIIdentityModGenerator.generateFromRepo.assert_not_called()

    def test_assetFolders_ofBothGames_toldByTheirFiles(self):
        sanhua = self.path("Assets", "Sanhua")
        wwmi.writeAssets(sanhua, wwmi.twoComponents())
        neither = self.path("Assets", "Neither")
        os.makedirs(neither)

        service = IDMG.IDModGenService(assetsFolders = [self.gimiAssets(), sanhua, neither], outputFolder = self.out)
        service.generate()
        self.assertIsInstance(service.stats.generated["Tester"], IDMG.GIMIIdentityMod)
        self.assertIsInstance(service.stats.generated["Sanhua"], IDMG.WWMIIdentityMod)
        self.assertIsInstance(service.stats.skipped["Neither"], IDMG.BadAssetData)
        self.assertEqual(IDMG.IDModGenService.getAssetsLoader(sanhua), IDMG.ModLoaders.WWMI)

    def test_assetPrefix_notForAWuWaFolder(self):
        sanhua = self.path("Assets", "Sanhua")
        wwmi.writeAssets(sanhua, wwmi.twoComponents())
        service = IDMG.IDModGenService(assetsFolders = [sanhua], outputFolder = self.out, assetPrefix = "X")
        service.generate()
        self.assertIn("only for GIMI asset folders", str(service.stats.skipped["Sanhua"]))

    # =============== bad options ===========================================

    def test_badOptions_raiseOrReported(self):
        folder = self.gimiAssets()
        tests = [("nothing to do", dict()),
                 ("prefix for a name", dict(names = ["Yelan"], assetPrefix = "X")),
                 ("wrong generator", dict(assetsFolders = [folder], gimiGenerator = IDMG.WWMIIdentityModGenerator()))]

        for name, kwargs in tests:
            with self.assertRaises(IDMG.Error, msg = name):
                IDMG.IDModGenService(outputFolder = self.out, **kwargs).generate()

            logger = CaptureLogger()
            service = IDMG.IDModGenService(outputFolder = self.out, handleExceptions = True, logger = logger, **kwargs)
            service.generate()
            self.assertTrue(any(line.endswith(BaseLogger.ErrorHeader) for line in logger.lines), name)
            self.assertFalse(any("Traceback" in line for line in logger.lines), name)
            self.assertEqual(service.stats.generated, {}, name)


def mock_mod():
    from unittest import mock
    mod = mock.Mock()
    mod.getSummary.return_value = ["summary"]
    return mod
