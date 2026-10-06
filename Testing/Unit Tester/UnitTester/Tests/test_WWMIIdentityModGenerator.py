import os
import json
import struct
import tempfile

from .baseUnitTest import BaseUnitTest, IDMG
from .wwmiAssetsFixture import FixtureComponent, FixtureVertex, writeAssets, twoComponents


class WWMIIdentityModGeneratorTest(BaseUnitTest):
    def setUp(self):
        super().setUp()
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.assets = os.path.join(self._temp.name, "Assets", "Tester")
        self.mod = os.path.join(self._temp.name, "Mod")

    def readBuffer(self, buffer) -> bytes:
        with open(os.path.join(self.mod, "Meshes", buffer.value), "rb") as f:
            return f.read()

    def readIni(self) -> bytes:
        with open(os.path.join(self.mod, "mod.ini"), "rb") as f:
            return f.read()

    def generate(self, components = None, metadataEdits = None, textures = None, **kwargs):
        writeAssets(self.assets, twoComponents() if components is None else components, metadataEdits = metadataEdits, textures = textures)
        return IDMG.WWMIIdentityModGenerator(**kwargs).generate(self.assets, self.mod)

    def highBoneComponents(self, highWeight: int = 127):
        # component 1's local bone 1 is merged bone 300: past the 256 the Blend buffer's bytes can name
        c0 = FixtureComponent([FixtureVertex(), FixtureVertex(), FixtureVertex()], [0, 1, 2], {"0": 0}, vgOffset = 0)
        c1 = FixtureComponent([FixtureVertex(bones = (0, 1, 0, 0), weights = (255 - highWeight, highWeight, 0, 0)),
                               FixtureVertex(bones = (0, 1, 0, 0), weights = (255, 0, 0, 0)),
                               FixtureVertex()],
                              [0, 1, 2], {"0": 0, "1": 300}, vgOffset = 1)
        return [c0, c1]

    # =============== buffers ===============================================

    def test_twoComponents_indicesOffsetByVertexOffset(self):
        self.generate()
        self.assertEqual(self.readBuffer(IDMG.WWMIBuffers.Index), struct.pack("<9I", 0, 1, 2, 3, 4, 5, 5, 4, 6))

    def test_twoComponents_positionsConcatenated(self):
        self.generate()
        expected = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (2, 0, 0), (3, 0, 0), (2, 1, 0), (3, 1, 0)]
        self.assertEqual(self.readBuffer(IDMG.WWMIBuffers.Position), b"".join(struct.pack("<3f", *p) for p in expected))

    def test_vgMap_boneIndicesInMergedSkeleton(self):
        self.generate()
        expected = [((0, 1, 0, 0), (200, 55, 0, 0)), ((1, 0, 0, 0), (255, 0, 0, 0)), ((0, 0, 0, 0), (255, 0, 0, 0)),
                    ((3, 0, 0, 0), (255, 0, 0, 0)), ((0, 0, 0, 0), (255, 0, 0, 0)), ((0, 0, 0, 0), (255, 0, 0, 0)), ((0, 0, 0, 0), (255, 0, 0, 0))]
        self.assertEqual(self.readBuffer(IDMG.WWMIBuffers.Blend), b"".join(bytes(b) + bytes(w) for b, w in expected))

    def test_rawBones_boneIndicesOffsetByVgOffset(self):
        self.generate(useVgMap = False)
        blend = self.readBuffer(IDMG.WWMIBuffers.Blend)
        self.assertEqual(blend[:8], bytes((0, 1, 0, 0, 200, 55, 0, 0)))
        self.assertEqual(blend[3 * 8:4 * 8], bytes((3, 2, 2, 2, 255, 0, 0, 0)))
        self.assertEqual(blend[4 * 8:4 * 8 + 4], bytes((2, 2, 2, 2)))

    def test_vector_bitangentSignIsNormalsFourthByte(self):
        self.generate()
        vector = self.readBuffer(IDMG.WWMIBuffers.Vector)
        self.assertEqual(len(vector), 7 * 8)
        self.assertEqual(vector[:8], struct.pack("<8b", 1, 2, 3, 4, 5, 6, 7, -1))
        self.assertEqual(vector[16:24], struct.pack("<8b", 1, 2, 3, 4, 5, 6, 7, 1))

    def test_texCoord_fourUVSetsPerVertex(self):
        self.generate()
        texCoord = self.readBuffer(IDMG.WWMIBuffers.TexCoord)
        self.assertEqual(len(texCoord), 7 * 16)
        self.assertEqual(texCoord[:16], struct.pack("<2e2H2e2e", 0, 0, 7, 8, 0.5, 0.25, 1.0, 2.0))

    # =============== shape keys ============================================

    def test_shapeKey_onlyMovedVerticesListed(self):
        mod = self.generate()
        self.assertEqual(self.readBuffer(IDMG.WWMIBuffers.ShapeKeyVertexId), struct.pack("<2I", 4, 6))
        self.assertEqual(self.readBuffer(IDMG.WWMIBuffers.ShapeKeyVertexOffset), struct.pack("<12e", 0.5, 0, -0.25, 0, 0, 0, 0, 1, 0, 0, 0, 0))
        self.assertEqual(mod.shapeKeys.keys, [5])
        self.assertEqual(mod.shapeKeys.entryCount, 2)

    def test_shapeKey_offsetsCountKeysBefore(self):
        self.generate()
        offsets = struct.unpack("<128I", self.readBuffer(IDMG.WWMIBuffers.ShapeKeyOffset))
        self.assertEqual(list(offsets[:6]), [0] * 6)
        self.assertEqual(set(offsets[6:]), {2})

    def test_noShapeKeys_emptyBuffersAndSummary(self):
        components = twoComponents()
        components[1].shapeKey = None
        mod = self.generate(components = components)
        self.assertEqual(self.readBuffer(IDMG.WWMIBuffers.ShapeKeyVertexId), b"")
        self.assertEqual(self.readBuffer(IDMG.WWMIBuffers.ShapeKeyOffset), bytes(128 * 4))
        self.assertIn("0 keys (none)", "\n".join(mod.getSummary()))

    def test_checksum_comparedWithMetadata(self):
        tests = [({"checksum": 0, "dispatch_y": 1}, True, True),
                 ({"checksum": 5, "dispatch_y": 2}, False, False),
                 ({}, None, None)]

        for shapeKeys, checksumMatches, dispatchYMatches in tests:
            mod = self.generate(metadataEdits = {"shapekeys": shapeKeys})
            self.assertEqual(mod.checksumMatches, checksumMatches)
            self.assertEqual(mod.dispatchYMatches, dispatchYMatches)

    # =============== blend remap ===========================================

    def test_lowBones_noBlendRemap(self):
        mod = self.generate()
        self.assertEqual(mod.blendRemaps, [])
        self.assertFalse(os.path.exists(os.path.join(self.mod, "Meshes", IDMG.WWMIBuffers.BlendRemapForward.value)))
        self.assertNotIn(b"BlendRemap", self.readIni())

    def test_weightedBoneOver255_remapForThatComponent(self):
        mod = self.generate(components = self.highBoneComponents())
        self.assertEqual(mod.blendRemaps, [IDMG.WWMIBlendRemap(1, 0, 2)])

        forward = struct.unpack("<512H", self.readBuffer(IDMG.WWMIBuffers.BlendRemapForward))
        reverse = struct.unpack("<512H", self.readBuffer(IDMG.WWMIBuffers.BlendRemapReverse))
        self.assertEqual(forward[:3], (0, 300, 0))
        self.assertEqual((reverse[0], reverse[300]), (0, 1))

        # the full ids of every vertex, and the Blend buffer's ids truncated to 8 bits (300 -> 44)
        vertexVG = struct.unpack("<24H", self.readBuffer(IDMG.WWMIBuffers.BlendRemapVertexVG))
        self.assertEqual(vertexVG[12:16], (0, 300, 0, 0))
        self.assertEqual(self.readBuffer(IDMG.WWMIBuffers.Blend)[3 * 8:3 * 8 + 4], bytes((0, 44, 0, 0)))

        ini = self.readIni()
        self.assertIn(b"[ResourceRemappedBlendBufferComponent1]", ini)
        self.assertNotIn(b"[ResourceRemappedBlendBufferComponent0]", ini)
        self.assertIn(b"array = 1536", ini)

    def test_boneOver255WithNoWeight_noBlendRemap(self):
        mod = self.generate(components = self.highBoneComponents(highWeight = 0))
        self.assertEqual(mod.blendRemaps, [])

    def test_staleBlendRemapFromEarlierRun_removed(self):
        self.generate(components = self.highBoneComponents())
        self.generate()
        for buffer in IDMG.WWMIBlendRemapBuffers:
            self.assertFalse(os.path.exists(os.path.join(self.mod, "Meshes", buffer.value)))

    # =============== mod.ini and textures ===================================

    def test_ini_crlfAndOneDrawPerComponent(self):
        self.generate()
        ini = self.readIni()
        self.assertNotIn(b"\n", ini.replace(b"\r\n", b""))
        self.assertIn(b"[TextureOverrideComponent1]\r\nhash = aaaa0000\r\nmatch_first_index = 3\r\nmatch_index_count = 6\r\n", ini)
        self.assertIn(b"        drawindexed = 6, 3, 0\r\n", ini)
        self.assertIn(b"global $mesh_vertex_count = 7\r\n", ini)
        self.assertIn(b'data = "Tester Identity"', ini)

    def test_textures_copiedAndOverriddenByHash(self):
        textures = ["Components-0-1 t=ABCD1234.dds", "Components-1 t=00ff00ff.dds", "notATexture.dds"]
        mod = self.generate(textures = textures)
        self.assertEqual(mod.textures, [("Components-0-1 t=ABCD1234.dds", "abcd1234"), ("Components-1 t=00ff00ff.dds", "00ff00ff")])
        self.assertEqual(sorted(os.listdir(os.path.join(self.mod, "Textures"))), textures[:2])
        self.assertIn(b"[TextureOverrideTexture0]\r\nhash = abcd1234\r\n", self.readIni())

    def test_noTextures_noTexturesFolder(self):
        mod = self.generate(textures = ["Components-0 t=abcd1234.dds"], includeTextures = False)
        self.assertEqual(mod.textures, [])
        self.assertFalse(os.path.exists(os.path.join(self.mod, "Textures")))

    # =============== bad asset data =========================================

    def test_badAssetData_raisesAndWritesNothing(self):
        components = twoComponents()
        tests = [("offsets", {"vertex_count": 99}),
                 ("export_format", {"export_format": {}}),
                 ("vb0_hash", None)]

        for name, edits in tests:
            writeAssets(self.assets, components, metadataEdits = edits)
            if (edits is None):
                with open(os.path.join(self.assets, "Metadata.json"), "r", encoding = "utf-8") as f:
                    metadata = json.load(f)
                metadata.pop("vb0_hash")
                with open(os.path.join(self.assets, "Metadata.json"), "w", encoding = "utf-8") as f:
                    json.dump(metadata, f)

            with self.assertRaises(IDMG.BadAssetData, msg = name):
                IDMG.WWMIIdentityModGenerator().generate(self.assets, self.mod)
            self.assertFalse(os.path.exists(self.mod), name)

    def test_vgMapTooShort_raises(self):
        components = twoComponents()
        components[1].vgMap = {"0": 0}
        with self.assertRaises(IDMG.BadAssetData):
            self.generate(components = components)

    def test_noMetadata_raises(self):
        os.makedirs(self.assets)
        with self.assertRaises(IDMG.BadAssetData):
            IDMG.WWMIIdentityModGenerator().generate(self.assets, self.mod)
