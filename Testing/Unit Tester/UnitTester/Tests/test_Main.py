import os
import tempfile

from .baseUnitTest import BaseUnitTest, IDMG
from .captureLogger import CaptureLogger
from . import gimiAssetsFixture as gimi
from . import wwmiAssetsFixture as wwmi

from AGIDMGen.main import main, askArgs, makeArgParser, makeServiceCLI
from AGIDMGen.IDModGenServiceCLI import IDModGenServiceCLI, LogFileName


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


def mock_mod():
    from unittest import mock
    mod = mock.Mock()
    mod.getSummary.return_value = ["summary"]
    mod.checksumMatches = None
    mod.dispatchYMatches = None
    return mod


class MainTest(BaseUnitTest):
    def setUp(self):
        super().setUp()
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.patch("builtins.print")

    def path(self, *parts) -> str:
        return os.path.join(self._temp.name, *parts)

    def gimiAssets(self) -> str:
        folder = self.path("Assets", "Tester")
        gimi.writeAssets(folder, "Tester", gimi.oneComponent())
        return folder

    def serviceOf(self, argv):
        return makeServiceCLI(makeArgParser().parse_args(argv), CaptureLogger()).service

    # =============== main ==================================================

    def test_assetFolders_exitCodes(self):
        good = self.gimiAssets()
        tests = [([good], 0), ([good, self.path("Assets", "Missing")], 1), ([], 1)]
        for sources, expected in tests:
            self.assertEqual(main(sources + ["--out", self.path("Out"), "--quiet"]), expected, sources)
        self.assertTrue(os.path.isfile(self.path("Out", "Tester", "Tester.ini")))

    def test_assetFolders_ofBothGames_inOneRun(self):
        sanhua = self.path("Assets", "Sanhua")
        wwmi.writeAssets(sanhua, wwmi.twoComponents())
        # 2: the fixture's Metadata.json records no real shape key checksum, which the exit code reports
        self.assertEqual(main([self.gimiAssets(), sanhua, "--out", self.path("Out"), "--quiet"]), 2)
        self.assertTrue(os.path.isfile(self.path("Out", "Tester", "Tester.ini")))
        self.assertTrue(os.path.isfile(self.path("Out", "Sanhua", "mod.ini")))

    def test_logFile_writtenWithEverything(self):
        self.assertEqual(main([self.gimiAssets(), "--out", self.path("Out"), "--log", self.path("Log"), "--quiet", "--noFix"]), 0)
        with open(self.path("Log", LogFileName), encoding = "utf-8") as f:
            txt = f.read()
        self.assertIn("Summary", txt)
        self.assertIn("ENJOY", txt)
        self.assertIn("Tips", txt)

    def test_logFile_writtenOnABadRunToo(self):
        self.assertEqual(main(["Yelan", "--game", "Nowhere", "--log", self.path("Log"), "--quiet"]), 1)
        with open(self.path("Log", LogFileName), encoding = "utf-8") as f:
            self.assertIn("no game is called 'Nowhere'", f.read())

    def test_faceRegister_psT1ByDefault(self):
        good = self.gimiAssets()
        tests = [([], "ps-t1"), (["--faceRegister", "ps-t0"], "ps-t0")]
        for opts, expected in tests:
            out = self.path("Out" + expected)
            self.assertEqual(main([good, "--out", out, "--quiet"] + opts), 0, opts)
            with open(os.path.join(out, "Tester", "Tester.ini"), encoding = "utf-8") as f:
                self.assertIn(f"{expected} = ResourceTesterFaceHeadDiffuse", f.read(), opts)

    def test_badArguments_exit1(self):
        tests = [["Yelan", "--localData", "Nowhere=x"], ["Yelan", "--game", "Nowhere"],
                 ["Yelan", "--textureFrom", "bad"], ["NotACharacterXYZ"]]
        self.patchObj(IDMG.GIMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        for argv in tests:
            self.assertEqual(main(argv + ["--quiet"]), 1, argv)

    # =============== names of any game =====================================

    def test_names_ofBothGames_noGameGiven(self):
        self.patchObj(IDMG.GIMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        self.patchObj(IDMG.WWMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        self.assertEqual(main(["Zani", "Ayaka", "--out", self.path("Out"), "--quiet"]), 0)
        self.assertEqual([c.args[0] for c in IDMG.GIMIIdentityModGenerator.generateFromRepo.call_args_list], ["Ayaka"])
        self.assertEqual([c.args[0] for c in IDMG.WWMIIdentityModGenerator.generateFromRepo.call_args_list], ["Zani"])

    def test_splitSources_pathsAndAssetFoldersThenNames(self):
        folder = self.path("Yelan")
        os.makedirs(folder)
        missing = self.path("Missing")
        tests = [[folder, "Yelan", "yelan", "NotACharacterXYZ", missing, "typo/Yelan"],
                 [folder, missing, "typo/Yelan"], ["Yelan", "yelan", "NotACharacterXYZ"]]
        self.assertEqual(IDModGenServiceCLI.splitSources(tests[0]), (tests[1], tests[2]))
        self.assertEqual(IDModGenServiceCLI.splitSources([]), ([], []))

    def test_splitSources_aBareFolderNamedAsACharacter(self):
        # run where a folder called Yelan (eg. an old mod) and an asset folder called Tester sit: Yelan is still the
        #   character, while Tester (an asset folder) and Empty (no character's name) are folders
        tester = self.gimiAssets()
        os.makedirs(self.path("Yelan"))
        os.makedirs(self.path("Empty"))
        cwd = os.getcwd()
        os.chdir(self._temp.name)
        try:
            os.rename(tester, self.path("Tester"))
            self.assertEqual(IDModGenServiceCLI.splitSources(["Yelan", "Tester", "Empty"]), (["Tester", "Empty"], ["Yelan"]))
            # a name of a game not looked up is no name
            self.assertEqual(IDModGenServiceCLI.splitSources(["Yelan"], [IDMG.ModLoaders.WWMI]), (["Yelan"], []))
        finally:
            os.chdir(cwd)

    def test_download_isNoOption(self):
        # a name is always downloaded, so there is no option for it; nor is it read as '--downloadFolder' (abbreviated)
        for argv in (["Yelan", "--download"], ["--download", "Yelan"], ["Yelan", "--out"[:4]]):
            with self.assertRaises(SystemExit, msg = argv):
                makeArgParser().parse_args(argv)

    def test_game_namesOrAliasesOrLoaders(self):
        tests = [("GI", [IDMG.ModLoaders.GIMI]), ("genshin,wuwa", [IDMG.ModLoaders.GIMI, IDMG.ModLoaders.WWMI]),
                 ("WWMI", [IDMG.ModLoaders.WWMI]), ("Wuthering Waves", [IDMG.ModLoaders.WWMI]), ("gimi, GI", [IDMG.ModLoaders.GIMI])]
        for game, expected in tests:
            self.assertEqual(self.serviceOf(["Yelan", "--game", game]).loaders, expected, game)
        self.assertIsNone(self.serviceOf(["Yelan"]).loaders)

    def test_gameWord_isNoGame(self):
        # the game is no longer the first word: 'gimi' is a name like any other, and names no character
        service = self.serviceOf(["gimi", "Yelan"])
        self.assertEqual((service.loaders, service.names), (None, ["gimi", "Yelan"]))

    def test_all_everyCharacterOfTheGamesAsked(self):
        self.assertEqual(self.serviceOf(["--all", "--game", "WuWa"]).names, IDMG.ModDownloader.getCharacters(IDMG.ModLoaders.WWMI))
        self.assertEqual(len(self.serviceOf(["--all"]).names), len(IDMG.ModNames.getAll()))

    def test_nameReplace_parsed_laterKeyWins(self):
        tests = [("ei:Raiden1,carlotta:shorty", {"ei": "Raiden1", "carlotta": "shorty"}, 0),
                 (" ei : Raiden1 , EI:Raiden2,\tZani:Shorty,", {"EI": "Raiden2", "Zani": "Shorty"}, 0),
                 # one key, as names are looked up: case, spaces, '_' and '-' aside
                 ("hu tao:A, Hu_Tao:B", {"Hu_Tao": "B"}, 0),
                 ("ei:Raiden1, Zani:shorty, zibai:liyuemoongoddess, someNonExistentchar:fooo",
                  {"ei": "Raiden1", "Zani": "shorty", "zibai": "liyuemoongoddess", "someNonExistentchar": "fooo"}, 0),
                 # not CHARACTER:NEWNAME: skipped, the rest kept
                 ("ei=Raiden1, ei:, :Raiden1, Zani, Yelan:Y", {"Yelan": "Y"}, 4),
                 ("", {}, 0), (None, {}, 0)]
        for txt, expected, ignoredCount in tests:
            ignored = []
            result = IDModGenServiceCLI.parseNameReplace(txt, ignored)
            self.assertEqual((result, list(result)), (expected, list(expected)), txt)
            self.assertEqual(len(ignored), ignoredCount, (txt, ignored))

    def test_nameReplace_reachesTheService(self):
        self.assertEqual(self.serviceOf(["ei", "--nameReplace", "ei:Raiden1,raiden:Raiden2"]).nameReplace, {"ei": "Raiden1", "raiden": "Raiden2"})
        self.patchObj(IDMG.GIMIIdentityModGenerator, "generateFromRepo", return_value = mock_mod())
        # a pair for no character being made, or that is not a pair, is skipped: the run is still clean
        logger = CaptureLogger()
        self.assertEqual(main(["Yelan", "--nameReplace", "ei:Raiden1, yelan, yelan:Y", "--out", self.path("Out")], logger = logger), 0)
        self.assertEqual(IDMG.GIMIIdentityModGenerator.generateFromRepo.call_args.args[1], os.path.join(self.path("Out"), "Y"))
        self.assertEqual(sum("Not renaming a character" in line for line in logger.lines), 2)
        with self.assertRaises(SystemExit):
            makeArgParser().parse_args(["Yelan", "--name", "X"])

    def test_generatorOptions_reachEachGamesGenerator(self):
        service = self.serviceOf(["Yelan", "--noFix", "--faceRegister", "ps-t0", "--author", "Me", "--noTextures"])
        self.assertEqual((service.gimiGenerator.includeFix, service.gimiGenerator.faceRegister), (False, "ps-t0"))
        self.assertEqual((service.wwmiGenerator.author, service.wwmiGenerator.includeTextures), ("Me", False))

    # =============== the front end ==========================================

    def test_serviceCLI_fromAService(self):
        service = IDMG.IDModGenService(assetsFolders = [self.gimiAssets()], outputFolder = self.path("Out"))
        serviceCLI = IDModGenServiceCLI(service = service, log = self.path("Log"), logger = CaptureLogger())
        serviceCLI.generate()
        self.assertIs(service.logger, serviceCLI.logger)
        self.assertEqual(serviceCLI.exitCode, 0)
        self.assertTrue(os.path.isfile(serviceCLI.logFile))

    def test_serviceCLI_badStringRaisedWhenNotHandled(self):
        serviceCLI = IDModGenServiceCLI(sources = ["Yelan"], games = ["Nowhere"], handleExceptions = False, logger = CaptureLogger())
        self.assertTrue(serviceCLI.hasErrorsBeforeGenerate)
        with self.assertRaises(IDMG.Error):
            serviceCLI.generate()

    def test_tips_onlyAfterACleanRun(self):
        logger = CaptureLogger()
        IDModGenServiceCLI(sources = [self.gimiAssets()], outputFolder = self.path("Out"), logger = logger).generate()
        self.assertTrue(any("--all option" in line for line in logger.lines))

        logger = CaptureLogger()
        IDModGenServiceCLI(sources = [self.path("Assets", "Missing")], outputFolder = self.path("Out"), logger = logger).generate()
        self.assertFalse(any("Tips" in line for line in logger.lines))

    # =============== no arguments: the script double-clicked ===============

    def test_askArgs_reaskUntilValid(self):
        tests = [(["", "Zani  Ayaka"], ["Zani", "Ayaka"]),
                 (["ALL"], ["--all"]),
                 (["Yelan"], ["Yelan"])]
        for answers, expected in tests:
            logger = ScriptedLogger(answers)
            self.assertEqual(askArgs(logger), expected, answers)
            self.assertFalse(logger.answers, answers)
            self.assertTrue(all("-->" not in question for question in logger.questions), logger.questions)
            self.assertTrue(logger.includePrefix)

    def test_noArguments_asksRunsThenWaitsForEnter(self):
        self.patchObj(IDModGenServiceCLI, "generate")
        logger = ScriptedLogger(["Zani Ayaka", ""])
        main([], logger = logger)
        self.patches[IDModGenServiceCLI].assert_called_once()
        self.assertIn("Press ENTER", logger.questions[-1])

    def test_noArguments_noInput_exit1(self):
        self.patchObj(IDModGenServiceCLI, "generate")
        self.assertEqual(main([], logger = ScriptedLogger([])), 1)
        self.patches[IDModGenServiceCLI].assert_not_called()

    def test_arguments_neverAsk(self):
        logger = ScriptedLogger([])
        self.assertEqual(main(["Yelan", "--game", "Nowhere", "--quiet"], logger = logger), 1)
        self.assertEqual(logger.questions, [])
