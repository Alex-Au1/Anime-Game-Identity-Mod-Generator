import os
import json
import filecmp
import tempfile

from .baseUnitTest import BaseUnitTest, IDMG
from .wwmiAssetsFixture import FixtureComponent, FixtureVertex, writeAssets, twoComponents


class WWMIDownloadFolderBuilderTest(BaseUnitTest):
    def setUp(self):
        super().setUp()
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.assets = os.path.join(self._temp.name, "Assets", "Tester")
        self.download = os.path.join(self._temp.name, "Download")

    def path(self, *parts) -> str:
        return os.path.join(self._temp.name, *parts)

    def writeAssets(self, components = None):
        writeAssets(self.assets, twoComponents() if components is None else components, textures = ["Components-0-1 t=ABCD1234.dds", "Components-1 t=00ff00ff.dds"])
        with open(os.path.join(self.assets, "TextureUsage.json"), "w", encoding = "utf-8") as f:
            json.dump({"Component 0": {"ps-t0": ["abcd1234-vs=0-ps=0"]}}, f)

    def highBoneComponents(self):
        c0 = FixtureComponent([FixtureVertex(), FixtureVertex(), FixtureVertex()], [0, 1, 2], {"0": 0}, vgOffset = 0)
        c1 = FixtureComponent([FixtureVertex(bones = (0, 1, 0, 0), weights = (128, 127, 0, 0)), FixtureVertex(), FixtureVertex()], [0, 1, 2], {"0": 0, "1": 300}, vgOffset = 1)
        return [c0, c1]

    # =============== build =================================================

    def test_build_agRemapsLayout(self):
        self.writeAssets()
        written = IDMG.WWMIDownloadFolderBuilder().build(self.assets, self.download, "Tester")
        expected = ["TesterBlend.buf", "TesterColor.buf", "TesterIndex.buf", "TesterMetadata.json", "TesterPosition.buf", "TesterShapeKeyOffset.buf",
                    "TesterShapeKeyVertexId.buf", "TesterShapeKeyVertexOffset.buf", "TesterTexcoord.buf", "TesterTexture00ff00ff.dds", "TesterTextureabcd1234.dds",
                    "TesterTextureUsage.json", "TesterVector.buf"]
        self.assertEqual(sorted(written, key = str.lower), sorted(expected, key = str.lower))
        self.assertEqual(sorted(os.listdir(self.download), key = str.lower), sorted(expected, key = str.lower))

    def test_noTextureUsage_raises(self):
        writeAssets(self.assets, twoComponents())
        with self.assertRaises(IDMG.BadAssetData):
            IDMG.WWMIDownloadFolderBuilder().build(self.assets, self.download, "Tester")

    # =============== WWMIIdentityModGenerator.generateFromDownload =========

    def test_modFromDownload_sameMeshesAsFromAssets(self):
        for components, remaps in ((None, 0), (self.highBoneComponents(), 1)):
            fromAssets, fromDownload = self.path("FromAssets"), self.path("FromDownload")
            self.writeAssets(components)
            IDMG.WWMIDownloadFolderBuilder().build(self.assets, self.download, "Tester")
            a = IDMG.WWMIIdentityModGenerator().generate(self.assets, fromAssets)
            b = IDMG.WWMIIdentityModGenerator().generateFromDownload(self.download, fromDownload, "Tester")

            meshes = os.listdir(os.path.join(fromAssets, "Meshes"))
            self.assertEqual(sorted(meshes), sorted(os.listdir(os.path.join(fromDownload, "Meshes"))))
            for fileName in meshes:
                self.assertTrue(filecmp.cmp(os.path.join(fromAssets, "Meshes", fileName), os.path.join(fromDownload, "Meshes", fileName), shallow = False), fileName)

            self.assertEqual(len(b.blendRemaps), remaps)
            self.assertEqual(a.blendRemaps, b.blendRemaps)
            self.assertEqual(a.getSummary()[:-1], b.getSummary()[:-1])
            # the download folder's texture names, the same hashes
            self.assertEqual([h for _, h in b.textures], sorted(h for _, h in a.textures))
            self.assertEqual(sorted(os.listdir(os.path.join(fromDownload, "Textures"))), ["TesterTexture00ff00ff.dds", "TesterTextureabcd1234.dds"])

    def test_badDownload_raises(self):
        tests = [("Index too short", "TesterIndex.buf", lambda data: data[:-4]),
                 ("blend remap table changed", "TesterBlendRemapForward.buf", lambda data: b"\x01" + data[1:]),
                 ("Metadata missing", "TesterMetadata.json", None)]

        for name, fileName, change in tests:
            self.writeAssets(self.highBoneComponents())
            IDMG.WWMIDownloadFolderBuilder().build(self.assets, self.download, "Tester")
            path = os.path.join(self.download, fileName)
            if (change is None):
                os.remove(path)
            else:
                with open(path, "rb") as f:
                    data = f.read()
                with open(path, "wb") as f:
                    f.write(change(data))

            with self.assertRaises(IDMG.BadAssetData, msg = name):
                IDMG.WWMIIdentityModGenerator().generateFromDownload(self.download, self.path("Mod"), "Tester")

    def test_someRemapBuffersMissing_raises(self):
        self.writeAssets(self.highBoneComponents())
        IDMG.WWMIDownloadFolderBuilder().build(self.assets, self.download, "Tester")
        os.remove(os.path.join(self.download, "TesterBlendRemapReverse.buf"))
        with self.assertRaises(IDMG.BadAssetData):
            IDMG.WWMIIdentityModGenerator().generateFromDownload(self.download, self.path("Mod"), "Tester")
