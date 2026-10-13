from unittest import mock

import FixRaidenBoss2 as FRB

from .baseUnitTest import BaseUnitTest, IDMG


GIMI = IDMG.ModLoaders.GIMI
WWMI = IDMG.ModLoaders.WWMI

Data = {"GI": {"RaidenShogun": {}, "Lumine": {}, "LumineHeaven": {}, "KaedeharaKazuha": {}, "Unnamed": {}, "Albedo": {}},
        "WuWa": {"SanhuaExorcist": {}}}
Names = {"GI": {"Raiden": ("RaidenShogun", []), "Kazuha": ("KaedeharaKazuha", ["Kaedehara"]), "Albedo": ("Albedo", ["Kazuha"]),
                "NoFolder": ("NoFolder", ["Ghost"])},
         "WuWa": {}}


class ModNamesTest(BaseUnitTest):
    def setUp(self):
        super().setUp()
        for target, values in ((IDMG.ModDownloadData, Data), (IDMG.ModNameData, Names)):
            patcher = mock.patch.dict(target, values, clear = True)
            patcher.start()
            self.addCleanup(patcher.stop)

    def assertFinds(self, loader, txt: str, name: str):
        modName = IDMG.ModNames.search(txt, [loader])
        self.assertIsNotNone(modName, txt)
        self.assertEqual(modName.name, name, txt)

    # =============== search ================================================

    def test_search_byNameFolderOrAlias(self):
        tests = [(GIMI, "Raiden", "Raiden"), (GIMI, "RaidenShogun", "Raiden"), (GIMI, "Ei", "Raiden"), (GIMI, "Kazuha", "Kazuha"),
                 (GIMI, "KaedeharaKazuha", "Kazuha"), (GIMI, "Kaedehara", "Kazuha"), (GIMI, "TravelerGirl", "Lumine"), (WWMI, "SanhuaSkin1", "SanhuaExorcist")]
        for loader, txt, name in tests:
            self.assertFinds(loader, txt, name)

    def test_search_anyCaseSpacesUnderscoresDashes(self):
        for txt in ("raiden", "RAIDEN SHOGUN", " raiden_shogun ", "Raiden-Shogun", "rAiDeN\tEi"):
            self.assertFinds(GIMI, txt, "Raiden")

    def test_search_longestNameFoundWins(self):
        # as in AG Remap: the longest name or alias inside the text is the one chosen
        tests = [("LumineHeaven", "LumineHeaven"), ("Lumine", "Lumine"), ("RaidenShogunMod", "Raiden"), ("myLumineHeavenSkin", "LumineHeaven")]
        for txt, name in tests:
            self.assertFinds(GIMI, txt, name)

    def test_search_noName_none(self):
        for txt in ("", "   ", "Yelan", "NoFolder", "Ghost"):
            self.assertIsNone(IDMG.ModNames.search(txt, [GIMI]), txt)
        self.assertIsNone(IDMG.ModNames.search("Raiden", [WWMI]))

    def test_find_noName_raises(self):
        with self.assertRaises(IDMG.Error):
            IDMG.ModNames.find("Yelan", [GIMI])
        self.assertEqual(IDMG.ModNames.find("ei", [GIMI]).folder, "RaidenShogun")

    def test_search_everyGameByDefault(self):
        self.assertEqual(IDMG.ModNames.find("SanhuaSkin1").loader, WWMI)
        self.assertEqual(IDMG.ModNames.find("ei").loader, GIMI)
        self.assertIsNone(IDMG.ModNames.search("ei", [WWMI]))

    def test_search_longestAcrossGames_tieIsNotGuessed(self):
        with mock.patch.dict(IDMG.ModDownloadData["WuWa"], {"Lumi": {}}):
            self.assertEqual(IDMG.ModNames.find("Lumine").loader, GIMI)
            self.assertEqual(IDMG.ModNames.find("Lumi").loader, WWMI)
        with mock.patch.dict(IDMG.ModDownloadData["WuWa"], {"Albedo": {}}):
            self.assertIsNone(IDMG.ModNames.search("Albedo"))
            with self.assertRaisesRegex(IDMG.Error, "names both"):
                IDMG.ModNames.find("Albedo")
            self.assertEqual(IDMG.ModNames.find("Albedo", [WWMI]).loader, WWMI)

    def test_aliasNeverTakesAName(self):
        # Albedo's alias 'Kazuha' is Kazuha's name
        self.assertFinds(GIMI, "Kazuha", "Kazuha")
        self.assertIn("Kazuha", IDMG.ModNames.find("Albedo", [GIMI]).aliases)

    # =============== getAll ================================================

    def test_getAll_everyFolderSortedByName(self):
        modNames = IDMG.ModNames.getAll([GIMI])
        self.assertEqual([m.name for m in modNames], ["Albedo", "Kazuha", "Lumine", "LumineHeaven", "Raiden", "Unnamed"])
        self.assertEqual({m.name: m.folder for m in modNames}["Unnamed"], "Unnamed")

    def test_aliases_ownThenAGRemapThenFolder(self):
        raiden = IDMG.ModNames.find("Raiden", [GIMI])
        # AG Remap already calls Raiden RaidenShogun, so the folder's name is not repeated
        self.assertEqual(raiden.aliases.count("RaidenShogun"), 1)
        self.assertIn("Ei", raiden.aliases)
        self.assertEqual(len(raiden.aliases), len(set(IDMG.ModNames.normalize(a) for a in raiden.aliases)))
        self.assertEqual(IDMG.ModNames.find("Kazuha", [GIMI]).aliases, ["Kaedehara", "KaedeharaKazuha"])
        self.assertEqual(str(raiden), "Raiden")

    def test_dataChanged_rebuilt(self):
        self.assertIsNone(IDMG.ModNames.search("Yelan", [GIMI]))
        with mock.patch.dict(IDMG.ModDownloadData["GI"], {"Yelan": {}}):
            self.assertFinds(GIMI, "yelan", "Yelan")
        self.assertIsNone(IDMG.ModNames.search("Yelan", [GIMI]))

        with mock.patch.dict(IDMG.ModNameData["GI"], {"Raiden": ("RaidenShogun", ["Baal"])}):
            self.assertFinds(GIMI, "Baal", "Raiden")


class ModNameDataTest(BaseUnitTest):
    """The library's own name table, against its download folders and AG Remap's mod types"""

    def test_everyFolderNamedOnce(self):
        for loader, game in IDMG.ModDownloadGameFolders.items():
            folders = [folder for folder, _ in IDMG.ModNameData[game].values()]
            self.assertEqual(len(folders), len(set(folders)), game)
            self.assertEqual(sorted(set(folders) - set(IDMG.ModDownloadData[game])), [], f"{game}: named folders with no download folder")
            self.assertEqual(sorted(m.folder for m in IDMG.ModNames.getAll([loader])), sorted(IDMG.ModDownloadData[game]), game)

    def test_everyNameAndAliasFindsItsOwnMod(self):
        # an alias filed for two mods would find only one of them
        for loader in IDMG.ModLoaders:
            for modName in IDMG.ModNames.getAll([loader]):
                for name in modName.names:
                    self.assertIs(IDMG.ModNames.search(name, [loader]), modName, f"{loader.value} {name}")

    def test_everyPartIsAModOfItsGame(self):
        for loader, game in IDMG.ModDownloadGameFolders.items():
            names = {modName.name for modName in IDMG.ModNames.getAll([loader])}
            for part, base in IDMG.ModNamePartData[game].items():
                self.assertIn(part, names, f"{game}: the part {part} is no mod")
                self.assertTrue(part.startswith(base) and part != base, f"{game}: {part} does not start with {base}")
        self.assertEqual(IDMG.ModNames.match("CarlottaHairCrystal").part, "HairCrystal")

    def test_getParts_byBaseNameOrAWholeCharactersName(self):
        tests = [("carlotta", ["CarlottaBody", "CarlottaHairCrystal", "CarlottaHairNormal"]),
                 ("Carlotta Summer", ["CarlottaSummerBody", "CarlottaSummerHairNormal"]),
                 ("Augusta", ["AugustaHelm"]),
                 # a part, a character with no parts, a name found only inside the text: no parts
                 ("CarlottaBody", []), ("Yelan", []), ("carlottax", [])]
        for txt, expected in tests:
            self.assertEqual([modName.name for modName in IDMG.ModNames.getParts(txt)], expected, txt)
        self.assertEqual(IDMG.ModNames.getParts("carlotta", [IDMG.ModLoaders.GIMI]), [])

    def test_noNameOrAliasInTwoGames(self):
        # a character's game is found from its name alone, so no name may be two games'
        games = {}
        for modName in IDMG.ModNames.getAll():
            for name in modName.names:
                games.setdefault(IDMG.ModNames.normalize(name), set()).add(modName.loader)
        self.assertEqual({name: loaders for name, loaders in games.items() if (len(loaders) > 1)}, {})

    def test_namedAsAGRemapNamesItsModTypes(self):
        # a mod whose name or folder is one of AG Remap's mod types, or one of their aliases, is named as AG Remap names that mod type
        for loader, gameTypeId in IDMG.ModNameGameTypeIds.items():
            agRemapNames = {}
            for modTypeEnum in FRB.ModTypes:
                modType = modTypeEnum.value
                if (int(modType.gameTypeId) == gameTypeId):
                    for name in [modType.name] + list(modType.aliases):
                        agRemapNames[IDMG.ModNames.normalize(name)] = modType.name

            for modName in IDMG.ModNames.getAll([loader]):
                for name in (modName.name, modName.folder):
                    expected = agRemapNames.get(IDMG.ModNames.normalize(name))
                    if (expected is not None):
                        self.assertEqual(modName.name, expected, f"{loader.value}: AG Remap calls {name} {expected}")
