import struct

from .baseUnitTest import BaseUnitTest, IDMG


Header = """stride: 20
first vertex: 0
vertex count: 2
topology: trianglelist
element[0]:
  SemanticName: POSITION
  SemanticIndex: 0
  Format: R32G32B32_FLOAT
  InputSlot: 0
  AlignedByteOffset: 0
  InputSlotClass: per-vertex
  InstanceDataStepRate: 0
element[1]:
  SemanticName: COLOR
  SemanticIndex: 0
  Format: R8G8B8A8_UNORM
  InputSlot: 0
  AlignedByteOffset: 12
  InputSlotClass: per-vertex
  InstanceDataStepRate: 0
element[2]:
  SemanticName: BLENDINDICES
  SemanticIndex: 0
  Format: R16G16_SINT
  InputSlot: 0
  AlignedByteOffset: 16
  InputSlotClass: per-vertex
  InstanceDataStepRate: 0

vertex-data:

"""


class VbDumpFileTest(BaseUnitTest):
    def vertex(self, position, color, bones) -> bytes:
        return struct.pack("<3f", *position) + bytes(color) + struct.pack("<2h", *bones)

    # =============== fromTxt ===============================================

    def test_dump_verticesEncodedInElementOrder(self):
        txt = Header + ("vb0[0]+000 POSITION: 1, 2.5, -3\nvb0[0]+012 COLOR: 1, 0.5, 0, 0\nvb0[0]+016 BLENDINDICES: 3, -1\n\n"
                        "vb0[1]+000 POSITION: 0, 0, 0\nvb0[1]+012 COLOR: 0, 0, 0, 1\nvb0[1]+016 BLENDINDICES: 0, 7\n")
        dump = IDMG.VbDumpFile.fromTxt(txt)
        self.assertEqual([element.name for element in dump.elements], ["POSITION", "COLOR", "BLENDINDICES"])
        self.assertEqual((dump.bytesPerLine, dump.vertexCount), (20, 2))
        self.assertEqual(dump.data, self.vertex((1, 2.5, -3), (255, 127, 0, 0), (3, -1)) + self.vertex((0, 0, 0), (0, 0, 0, 255), (0, 7)))

    def test_shortVertex_zeroFilled_longVertex_truncated(self):
        txt = Header + "vb0[0]+000 POSITION: 1, 2, 3\n\nvb0[1]+000 POSITION: 1, 2, 3, 0, 0, 0, 0, 5, 6, 99, 99\n"
        dump = IDMG.VbDumpFile.fromTxt(txt)
        self.assertEqual(dump.data, self.vertex((1, 2, 3), (0, 0, 0, 0), (0, 0)) + self.vertex((1, 2, 3), (0, 0, 0, 0), (5, 6)))

    def test_noBlankLines_oneVertex(self):
        txt = Header + "vb0[0]+000 POSITION: 1, 2, 3\nvb0[0]+012 COLOR: 0, 0, 0, 0\nvb0[0]+016 BLENDINDICES: 1, 2\nvb0[1]+000 POSITION: 4, 5, 6\n"
        self.assertEqual(IDMG.VbDumpFile.fromTxt(txt).vertexCount, 1)

    def test_valuesAfterLastColon_unparseableIsZero(self):
        txt = Header + "a: b: 1, x, 3\n  \t\nc: 4, 5, 6\n"
        dump = IDMG.VbDumpFile.fromTxt(txt)
        self.assertEqual(dump.data[:12], struct.pack("<3f", 1, 0, 3))
        self.assertEqual(dump.vertexCount, 2)

    def test_noVertices_emptyData(self):
        dump = IDMG.VbDumpFile.fromTxt(Header)
        self.assertEqual((dump.data, dump.vertexCount), (b"", 0))

    def test_unreadableHeader_none(self):
        tests = [("no marker", Header.replace("vertex-data:", "")),
                 ("SNORM", Header.replace("R8G8B8A8_UNORM", "R8G8B8A8_SNORM")),
                 ("unpaired", Header.replace("  Format: R16G16_SINT\n", ""))]
        for name, txt in tests:
            self.assertIsNone(IDMG.VbDumpFile.fromTxt(txt), name)

