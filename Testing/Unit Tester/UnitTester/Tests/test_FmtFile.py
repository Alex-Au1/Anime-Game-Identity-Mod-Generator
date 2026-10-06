from .baseUnitTest import BaseUnitTest, IDMG


FmtTxt = """stride: 20
topology: trianglelist
format: DXGI_FORMAT_R16_UINT
element[0]:
  SemanticName: POSITION
  SemanticIndex: 0
  Format: R32G32B32_FLOAT
  AlignedByteOffset: 0
element[1]:
  SemanticName: TEXCOORD
  SemanticIndex: 1
  Format: R16G16_FLOAT
  AlignedByteOffset: 12

element[2]:
\tSemanticName: TEXCOORD
\tSemanticIndex: 2
\tFormat: R16G16_FLOAT
\tAlignedByteOffset: 16
"""


class FmtFileTest(BaseUnitTest):
    # =============== fromTxt ===============================================

    def test_fmtTxt_headerAndElementsRead(self):
        fmt = IDMG.FmtFile.fromTxt(FmtTxt)
        self.compareDict(fmt.header, {"stride": "20", "topology": "trianglelist", "format": "DXGI_FORMAT_R16_UINT"})
        self.assertEqual(len(fmt.elements), 3)
        self.compareDict(fmt.elements[1], {"SemanticName": "TEXCOORD", "SemanticIndex": "1", "Format": "R16G16_FLOAT", "AlignedByteOffset": "12"})
        self.assertEqual(fmt.stride, 20)

    def test_crlfTxt_sameAsLf(self):
        fmt = IDMG.FmtFile.fromTxt(FmtTxt.replace("\n", "\r\n"))
        self.assertEqual(fmt.elements, IDMG.FmtFile.fromTxt(FmtTxt).elements)

    def test_emptyTxt_noStride(self):
        fmt = IDMG.FmtFile.fromTxt("")
        self.assertEqual((fmt.stride, fmt.elements), (0, []))

    # =============== getElement ============================================

    def test_getElement_matchesNameAnyCaseAndIndex(self):
        fmt = IDMG.FmtFile.fromTxt(FmtTxt)
        tests = [(("position", 0), "0"), (("TEXCOORD", 2), "16"), (("TEXCOORD", 0), None), (("NORMAL", 0), None)]

        for (name, index), offset in tests:
            element = fmt.getElement(name, index)
            self.assertEqual(None if element is None else element["AlignedByteOffset"], offset, f"{name}{index}")

