import os
import json
import tempfile

from .baseUnitTest import BaseUnitTest, IDMG
from .wwmiAssetsFixture import FixtureComponent, FixtureVertex, writeAssets, twoComponents


class WWMIComponentTest(BaseUnitTest):
    def setUp(self):
        super().setUp()
        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.assets = self._temp.name

    def load(self, index: int = 0, components = None, entryEdits = None) -> "IDMG.WWMIComponent":
        metadata = writeAssets(self.assets, twoComponents() if components is None else components)
        entry = dict(metadata["components"][index])
        entry.update(entryEdits or {})
        return IDMG.WWMIComponent(self.assets, index, entry)

    # =============== __init__ ===============================================

    def test_component_countsAndOffsets(self):
        component = self.load(1)
        self.assertEqual((component.vertexCount, component.indexCount, component.vertexOffset, component.indexOffset, component.stride), (4, 6, 3, 3, 54))

    def test_r32IndexBuffer_read(self):
        components = twoComponents()
        components[0].ibFormat = "R32_UINT"
        component = self.load(0, components = components)
        self.assertEqual(component.indices.tolist(), [0, 1, 2])

    def test_missingFile_raises(self):
        writeAssets(self.assets, twoComponents())
        os.remove(os.path.join(self.assets, "Component 1.ib"))
        with open(os.path.join(self.assets, "Metadata.json"), "r", encoding = "utf-8") as f:
            entry = json.load(f)["components"][1]

        with self.assertRaises(IDMG.BadAssetData):
            IDMG.WWMIComponent(self.assets, 1, entry)

    def test_disagreeingData_raises(self):
        badIndex = twoComponents()
        badIndex[0].indices = [0, 1, 3]

        tests = [("vertex count", None, {"vertex_count": 4}),
                 ("index count", None, {"index_count": 4}),
                 ("index past the vertices", badIndex, None)]

        for name, components, edits in tests:
            with self.assertRaises(IDMG.BadAssetData, msg = name):
                self.load(0, components = components, entryEdits = edits)

    def test_noVertexOffset_raises(self):
        metadata = writeAssets(self.assets, twoComponents())
        entry = dict(metadata["components"][0])
        entry.pop("vertex_offset")
        with self.assertRaises(IDMG.BadAssetData):
            IDMG.WWMIComponent(self.assets, 0, entry)

    # =============== getElementBytes ========================================

    def test_elementBytes_columnOfEveryVertex(self):
        component = self.load(0)
        self.assertEqual(component.getElementBytes("blendindices", 0, 4).tolist(), [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0]])

    def test_singleChannelElement_spansToNextElement(self):
        # an eight-influence character declares BLENDINDICES as R8_UINT while it spans 8 bytes
        component = self.load(0)
        component.fmt.getElement("BLENDINDICES")["Format"] = "R8_UINT"
        component.fmt.elements = [e for e in component.fmt.elements if e["SemanticName"] != "BLENDWEIGHT"]
        self.assertEqual(component.getElementBytes("BLENDINDICES", 0, 8)[0].tolist(), [0, 1, 0, 0, 200, 55, 0, 0])

    def test_tooWideOrMissingElement_raises(self):
        component = self.load(0)
        tests = [("BLENDINDICES", 0, 8), ("SHAPEKEY", 0, 6)]
        for name, index, width in tests:
            with self.assertRaises(IDMG.BadAssetData, msg = name):
                component.getElementBytes(name, index, width)

    # =============== getShapeKeys ===========================================

    def test_shapeKeys_onlyMovedVertices(self):
        shapeKeys = self.load(1).getShapeKeys()
        self.assertEqual(list(shapeKeys), [5])
        used, deltas = shapeKeys[5]
        self.assertEqual(used.tolist(), [1, 3])
        self.assertEqual(deltas.tolist(), [[0.5, 0.0, -0.25], [0.0, 1.0, 0.0]])

    def test_noShapeKeyElement_empty(self):
        self.assertEqual(self.load(0).getShapeKeys(), {})
