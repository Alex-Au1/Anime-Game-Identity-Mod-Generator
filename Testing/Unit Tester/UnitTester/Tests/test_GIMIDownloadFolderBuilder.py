import os
import filecmp
import tempfile

from .baseUnitTest import BaseUnitTest, IDMG
from .gimiAssetsFixture import writeAssets, oneComponent, twoComponents


class GIMIDownloadFolderBuilderTest(BaseUnitTest):
    def setUp(self):
        super().setUp()
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.assets = os.path.join(self._temp.name, "Assets", "Tester")
        self.download = os.path.join(self._temp.name, "Download")

    def path(self, *parts) -> str:
        return os.path.join(self._temp.name, *parts)

    # =============== build =================================================

    def test_build_agRemapsLayoutPlusHash(self):
        writeAssets(self.assets, "Tester", oneComponent())
        builder = IDMG.GIMIDownloadFolderBuilder()
        written = builder.build(self.assets, self.download, "Tester")

        expected = ["TesterBlend.buf", "TesterBody.ib", "TesterBodyDiffuse.dds", "TesterBodyLightMap.dds", "TesterBodyNormalMap.dds", "TesterFaceDiffuse.dds",
                    "TesterHash.json", "TesterHead.ib", "TesterHeadDiffuse.dds", "TesterHeadLightMap.dds", "TesterPosition.buf", "TesterTexcoord.buf"]
        self.assertEqual(sorted(written), expected)
        self.assertEqual(sorted(os.listdir(self.download)), expected)
        self.assertTrue(filecmp.cmp(os.path.join(self.assets, "hash.json"), os.path.join(self.download, "TesterHash.json"), shallow = False))
        self.assertEqual(builder.notes, [])

    def test_otherPrefix_foundBySuffix(self):
        # the asset files start with 'Tester_Skin' while the folder is 'Tester'
        writeAssets(self.assets, "Tester_Skin", oneComponent())
        written = IDMG.GIMIDownloadFolderBuilder().build(self.assets, self.download, "TesterSkin")
        self.assertIn("TesterSkinHead.ib", written)

    def test_unskinnedAndUntextured_noted(self):
        writeAssets(self.assets, "Tester", twoComponents())
        builder = IDMG.GIMIDownloadFolderBuilder()
        written = builder.build(self.assets, self.download, "Tester")
        self.assertNotIn("TesterMouthPosition.buf", written)
        self.assertEqual(len(builder.notes), 3)
        self.assertTrue(any("unskinned component 'Mouth'" in note for note in builder.notes))
        self.assertTrue(any("'Bang' object 'A': hash.json lists NO textures" in note for note in builder.notes))

    def test_ambiguousSuffix_raises(self):
        writeAssets(self.assets, "Tester", oneComponent())
        with open(os.path.join(self.assets, "TestorHead-ib=aai0000.txt"), "w", encoding = "utf-8") as f:
            f.write("")
        with self.assertRaises(IDMG.BadAssetData):
            IDMG.GIMIDownloadFolderBuilder().build(self.assets, self.download, "Tester")
        self.assertFalse(os.path.exists(self.download))

    # =============== GIMIIdentityModGenerator.generateFromDownload =========

    def test_modFromDownload_sameAsFromAssets(self):
        for components in (oneComponent(), twoComponents()):
            fromAssets, fromDownload = self.path("FromAssets"), self.path("FromDownload")
            writeAssets(self.assets, "Tester", components)
            IDMG.GIMIDownloadFolderBuilder().build(self.assets, self.download, "Tester")
            generator = IDMG.GIMIIdentityModGenerator(faceRegister = "ps-t1")
            generator.generate(self.assets, fromAssets)
            generator.generateFromDownload(self.download, fromDownload, "Tester")

            self.assertEqual(sorted(os.listdir(fromAssets)), sorted(os.listdir(fromDownload)))
            for fileName in os.listdir(fromAssets):
                if (fileName.endswith(".ini")):
                    with open(os.path.join(fromAssets, fileName), encoding = "utf-8") as a, open(os.path.join(fromDownload, fileName), encoding = "utf-8") as b:
                        # all but the last comment, which says what the mod was generated from
                        self.assertEqual(a.read().splitlines()[:-2], b.read().splitlines()[:-2])
                else:
                    self.assertTrue(filecmp.cmp(os.path.join(fromAssets, fileName), os.path.join(fromDownload, fileName), shallow = False), fileName)

    def test_badDownload_raises(self):
        writeAssets(self.assets, "Tester", oneComponent())
        IDMG.GIMIDownloadFolderBuilder().build(self.assets, self.download, "Tester")
        with open(os.path.join(self.download, "TesterBlend.buf"), "ab") as f:
            f.write(b"\x00")
        with self.assertRaises(IDMG.BadAssetData):
            IDMG.GIMIIdentityModGenerator().generateFromDownload(self.download, self.path("Mod"), "Tester")

        os.remove(os.path.join(self.download, "TesterHash.json"))
        with self.assertRaises(IDMG.BadAssetData):
            IDMG.GIMIIdentityModGenerator().generateFromDownload(self.download, self.path("Mod"), "Tester")
