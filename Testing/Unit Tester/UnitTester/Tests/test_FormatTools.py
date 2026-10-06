from .baseUnitTest import BaseUnitTest, IDMG


class FormatToolsTest(BaseUnitTest):
    # =============== decode ================================================

    def test_decode_withOrWithoutPrefix(self):
        tests = [("R32G32B32_FLOAT", ("<f4", 3)), ("DXGI_FORMAT_R16_UINT", ("<u2", 1)), ("r8g8b8a8_snorm", ("i1", 4))]
        for format, expected in tests:
            self.assertEqual(IDMG.FormatTools.decode(format), expected)

    def test_unknownFormat_raises(self):
        with self.assertRaises(IDMG.UnknownDXGIFormat) as context:
            IDMG.FormatTools.decode("BC7_UNORM")
        self.assertEqual(context.exception.format, "BC7_UNORM")
