from .baseUnitTest import BaseUnitTest, IDMG


class IbDumpFileTest(BaseUnitTest):
    # =============== fromTxt ===============================================

    def test_dump_headerSkippedTrianglesRead(self):
        txt = "byte offset: 0\nfirst index: 6\nindex count: 6\ntopology: trianglelist\nformat: DXGI_FORMAT_R16_UINT\n\n0 1 2\n2  1 70000\n"
        self.assertEqual(IDMG.IbDumpFile.fromTxt(txt).indices.tolist(), [0, 1, 2, 2, 1, 70000])

    def test_shortLine_zeroFilled_longLine_truncated(self):
        self.assertEqual(IDMG.IbDumpFile.fromTxt("5\n1 2 3 4\n").indices.tolist(), [5, 0, 0, 1, 2, 3])

    def test_valuesKeptTo32Bits(self):
        self.assertEqual(IDMG.IbDumpFile.fromTxt("4294967297 -1 x\n").indices.tolist(), [1, 0, 0])

    def test_empty_noIndices(self):
        self.assertEqual(IDMG.IbDumpFile.fromTxt("byte offset: 0\n").indexCount, 0)
