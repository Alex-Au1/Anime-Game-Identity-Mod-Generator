from .baseUnitTest import BaseUnitTest, IDMG


class DumpElementTest(BaseUnitTest):
    # =============== parseFormat ===========================================

    def test_parseFormat_channelPerBitWidth(self):
        F, S, U, N = IDMG.DumpDataKinds.Float, IDMG.DumpDataKinds.SignedInt, IDMG.DumpDataKinds.UnsignedInt, IDMG.DumpDataKinds.Unorm
        tests = [("R32G32B32_FLOAT", [(F, 4)] * 3), ("DXGI_FORMAT_R16_UINT", [(U, 2)]), ("R32G32B32A32_SINT", [(S, 4)] * 4),
                 ("R8G8B8A8_UNORM", [(N, 1)] * 4), ("R16G16_FLOAT", [(F, 2)] * 2)]
        for formatName, expected in tests:
            self.assertEqual(IDMG.DumpElement.parseFormat(formatName), [IDMG.DumpDataType(kind, size) for kind, size in expected], formatName)

    def test_unreadableFormat_none(self):
        for formatName in ("R8G8B8A8_SNORM", "R10G10B10A2_UNORM", "R64_FLOAT", "R8G8B8A8_UNORM_SRGB", "UNKNOWN", "R32"):
            self.assertIsNone(IDMG.DumpElement.parseFormat(formatName), formatName)

    def test_size_sumOfChannels(self):
        element = IDMG.DumpElement("TANGENT", "R32G32B32A32_FLOAT", IDMG.DumpElement.parseFormat("R32G32B32A32_FLOAT"))
        self.assertEqual(element.size, 16)
