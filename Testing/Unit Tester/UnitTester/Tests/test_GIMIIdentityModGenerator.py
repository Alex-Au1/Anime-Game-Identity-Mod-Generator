import os
import json
import struct
import tempfile

from .baseUnitTest import BaseUnitTest, IDMG
from .gimiAssetsFixture import FixtureComponent, FixtureObject, GameElements, writeAssets, oneComponent, twoComponents


class GIMIIdentityModGeneratorTest(BaseUnitTest):
    def setUp(self):
        super().setUp()
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.assets = os.path.join(self._temp.name, "Assets", "Tester")
        self.mod = os.path.join(self._temp.name, "Mod")

    def read(self, fileName: str) -> bytes:
        with open(os.path.join(self.mod, fileName), "rb") as f:
            return f.read()

    def ini(self, name: str = "Tester") -> str:
        return self.read(f"{name}.ini").decode("utf-8")

    def generate(self, components = None, generator = None, face = True, prefix = "Tester", **kwargs):
        writeAssets(self.assets, prefix, oneComponent() if components is None else components, face = face)
        return (IDMG.GIMIIdentityModGenerator() if generator is None else generator).generate(self.assets, self.mod, **kwargs)

    # =============== buffers ===============================================

    def test_vertexBuffer_splitIntoGIMIBuffers(self):
        self.generate()
        # vertex i has every value i, and COLOR 1 (255)
        position = b"".join(struct.pack("<10f", *([v] * 10)) for v in range(4))
        blend = b"".join(struct.pack("<4f4i", *([v] * 8)) for v in range(4))
        texcoord = b"".join(bytes([255] * 4) + struct.pack("<4f", *([v] * 4)) for v in range(4))
        self.assertEqual(self.read("TesterPosition.buf"), position)
        self.assertEqual(self.read("TesterBlend.buf"), blend)
        self.assertEqual(self.read("TesterTexcoord.buf"), texcoord)

    def test_indices_r32PerObject(self):
        self.generate()
        self.assertEqual(self.read("TesterHead.ib"), struct.pack("<3I", 0, 1, 2))
        self.assertEqual(self.read("TesterBody.ib"), struct.pack("<6I", 1, 2, 3, 3, 2, 0))

    def test_noTexcoord1_texcoordStride12(self):
        mod = self.generate(components = twoComponents())
        bang = next(c for c in mod.components if c.name == "Bang")
        self.assertEqual(bang.strides[IDMG.GIMIBuffers.Texcoord], 12)
        self.assertEqual(len(self.read("TesterBangTexcoord.buf")), 3 * 12)
        self.assertIn("[ResourceTesterBangTexcoord]\r\ntype = Buffer\r\nstride = 12\r\n", self.ini().replace("\n", "\r\n").replace("\r\r", "\r"))

    # =============== components ============================================

    def test_unskinnedComponent_skipped(self):
        mod = self.generate(components = twoComponents())
        self.assertEqual([c.name for c in mod.components], ["Body", "Bang"])
        self.assertEqual(mod.unskinned, ["Mouth"])
        self.assertFalse(os.path.exists(os.path.join(self.mod, "TesterMouthPosition.buf")))

    def test_assetPrefixAndName_separate(self):
        self.generate(prefix = "Tester_Skin", name = "TesterSkin", assetPrefix = "Tester_Skin")
        self.assertTrue(os.path.isfile(os.path.join(self.mod, "TesterSkinHeadDiffuse.dds")))
        self.assertIn("[TextureOverrideTesterSkinHead]", self.ini("TesterSkin"))

    # =============== .ini ==================================================

    def test_ini_crlfAndSections(self):
        self.generate()
        raw = self.read("Tester.ini")
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
        ini = raw.decode("utf-8").replace("\r\n", "\n")
        self.assertIn("[TextureOverrideTesterBlend]\nhash = aab0000\nvb1 = ResourceTesterBlend\nhandling = skip\ndraw = 4,0\n", ini)
        self.assertIn("[TextureOverrideTesterBody]\nhash = aai0000\nmatch_first_index = 3\nib = ResourceTesterBodyIB\n", ini)
        self.assertIn("[ResourceTesterBodyIB]\ntype = Buffer\nformat = DXGI_FORMAT_R32_UINT\nfilename = TesterBody.ib\n", ini)

    def test_textureLayout_byNormalMap(self):
        self.generate()
        ini = self.ini().replace("\r\n", "\n")
        self.assertIn("ib = ResourceTesterHeadIB\nps-t0 = ResourceTesterHeadDiffuse\nps-t1 = ResourceTesterHeadLightMap\nrun = CommandList\\global\\ORFix\\NNFix\n", ini)
        self.assertIn("ib = ResourceTesterBodyIB\nps-t0 = ResourceTesterBodyNormalMap\nps-t1 = ResourceTesterBodyDiffuse\nps-t2 = ResourceTesterBodyLightMap\nrun = CommandList\\global\\ORFix\\ORFix\n", ini)

    def test_noFix_noRunLines(self):
        self.generate(generator = IDMG.GIMIIdentityModGenerator(includeFix = False))
        self.assertNotIn("run = ", self.ini())

    def test_face_onFaceRegister(self):
        mod = self.generate(generator = IDMG.GIMIIdentityModGenerator(faceRegister = "ps-t1"))
        self.assertEqual(mod.faceDiffuse, "TesterFaceHeadDiffuse.dds")
        self.assertEqual(self.read("TesterFaceHeadDiffuse.dds"), b"face")
        self.assertIn("[TextureOverrideTesterFaceHeadDiffuse]\nhash = facef00d\nps-t1 = ResourceTesterFaceHeadDiffuse\n", self.ini().replace("\r\n", "\n"))

    def test_noFace_noFaceSection(self):
        mod = self.generate(face = False)
        self.assertIsNone(mod.faceDiffuse)
        self.assertNotIn("FaceHeadDiffuse", self.ini())

    # =============== borrowed textures =====================================

    def test_noTextures_geometryOnlyNoRunLine(self):
        mod = self.generate(components = twoComponents())
        self.assertEqual(mod.unbound, ["BangA"])
        self.assertIn("[TextureOverrideTesterBangA]\nhash = cci0000\nmatch_first_index = 0\nib = ResourceTesterBangAIB\n\n", self.ini().replace("\r\n", "\n"))

    def test_textureSource_bindsLendersTexturesInBorrowersLayout(self):
        tests = [(None, "ps-t0 = ResourceTesterBodyANormalMap\nps-t1 = ResourceTesterBodyADiffuse\nps-t2 = ResourceTesterBodyALightMap\nrun = CommandList\\global\\ORFix\\ORFix\n"),
                 (IDMG.GIMITextureLayouts.Plain, "ps-t0 = ResourceTesterBodyADiffuse\nps-t1 = ResourceTesterBodyALightMap\nrun = CommandList\\global\\ORFix\\NNFix\n")]

        for layout, expected in tests:
            generator = IDMG.GIMIIdentityModGenerator(textureSources = {"Bang": IDMG.GIMITextureSource("Body", "A", layout)})
            mod = self.generate(components = twoComponents(), generator = generator)
            self.assertEqual(mod.unbound, [])
            self.assertIn("ib = ResourceTesterBangAIB\n" + expected, self.ini().replace("\r\n", "\n"))
            # the borrowed textures are the lender's resources, not copies
            self.assertFalse(os.path.exists(os.path.join(self.mod, "TesterBangADiffuse.dds")))

    def recordSources(self, sources):
        # what Tools/Downloads/hashFromAGRemap.py records from AG Remap's parser configs
        path = os.path.join(self.assets, "hash.json")
        with open(path, encoding = "utf-8") as f:
            entries = json.load(f)
        next(e for e in entries if e.get("component_name") == "Bang")["texture_sources"] = sources
        with open(path, "w", encoding = "utf-8") as f:
            json.dump(entries, f)

    def test_recordedTextureSource_usedUnlessTheCallerGivesOne(self):
        writeAssets(self.assets, "Tester", twoComponents())
        self.recordSources({"A": {"component": "Body", "object": "A", "layout": "plain"}})

        mod = IDMG.GIMIIdentityModGenerator().generate(self.assets, self.mod)
        self.assertEqual(mod.unbound, [])
        self.assertIn("ib = ResourceTesterBangAIB\nps-t0 = ResourceTesterBodyADiffuse\nps-t1 = ResourceTesterBodyALightMap\nrun = CommandList\\global\\ORFix\\NNFix\n",
                      self.ini().replace("\r\n", "\n"))

        # a source the caller gives for the component wins
        generator = IDMG.GIMIIdentityModGenerator(textureSources = {"Bang": IDMG.GIMITextureSource("Body", "A")})
        generator.generate(self.assets, self.mod)
        self.assertIn("ib = ResourceTesterBangAIB\nps-t0 = ResourceTesterBodyANormalMap\n", self.ini().replace("\r\n", "\n"))

    def test_badRecordedTextureSource_raises(self):
        for sources in ({"A": {"component": "Hat", "object": "A"}}, {"Z": {"component": "Body", "object": "A"}}, {"A": {"component": "Body"}}, {"A": {"component": "Body", "object": "A", "layout": "shiny"}}):
            writeAssets(self.assets, "Tester", twoComponents())
            self.recordSources(sources)
            with self.assertRaises(IDMG.BadAssetData, msg = repr(sources)):
                IDMG.GIMIIdentityModGenerator().generate(self.assets, self.mod)

    def test_badTextureSource_raises(self):
        tests = [{"Hat": IDMG.GIMITextureSource("Body", "A")}, {"Bang": IDMG.GIMITextureSource("Hat", "A")}, {"Bang": IDMG.GIMITextureSource("Body", "Z")}]
        for textureSources in tests:
            with self.assertRaises(IDMG.Error, msg = repr(textureSources)):
                self.generate(components = twoComponents(), generator = IDMG.GIMIIdentityModGenerator(textureSources = textureSources))

    # =============== bad asset data ========================================

    def test_indexPastVertices_raisesAndWritesNothing(self):
        components = oneComponent()
        components[0].objects[1].indices = [0, 1, 4]
        with self.assertRaises(IDMG.BadAssetData):
            self.generate(components = components)
        self.assertFalse(os.path.exists(self.mod))

    def test_wrongPositionLayout_raises(self):
        # a NORMAL of four floats makes the Position buffer 44 bytes, not GIMI's 40
        elements = [("NORMAL", 0, "R32G32B32A32_FLOAT") if e[0] == "NORMAL" else e for e in GameElements]
        with self.assertRaises(IDMG.BadAssetData):
            self.generate(components = [FixtureComponent("", 3, [FixtureObject("Head", 0, [0, 1, 2])], "aa", elements = elements)])

    def test_missingFiles_raise(self):
        writeAssets(self.assets, "Tester", oneComponent())
        os.remove(os.path.join(self.assets, "TesterBody-ib=aai0000.txt"))
        with self.assertRaises(IDMG.BadAssetData):
            IDMG.GIMIIdentityModGenerator().generate(self.assets, self.mod)

        os.remove(os.path.join(self.assets, "hash.json"))
        with self.assertRaises(IDMG.BadAssetData):
            IDMG.GIMIIdentityModGenerator().generate(self.assets, self.mod)

