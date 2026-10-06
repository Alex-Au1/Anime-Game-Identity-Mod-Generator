from .baseUnitTest import BaseUnitTest, IDMG


class VersionToolsTest(BaseUnitTest):
    # =============== parse =================================================

    def test_parse_folderOrDottedTrailingZerosIgnored(self):
        tests = [("4_0", "4"), ("4.0", "4"), ("6_10", "6.10"), ("5.4.0", "5.4"), (" 3_7 ", "3.7"), ("0", "0.0")]
        for txt, same in tests:
            self.assertEqual(IDMG.VersionTools.parse(txt), IDMG.VersionTools.parse(same), txt)
        self.assertLess(IDMG.VersionTools.parse("6_8"), IDMG.VersionTools.parse("6_10"))

    def test_notAVersion_raises(self):
        for txt in ("", "v4", "4..0", "4_", "latest", "4-0"):
            with self.assertRaises(IDMG.Error, msg = txt):
                IDMG.VersionTools.parse(txt)

    # =============== getClosest ============================================

    def test_getClosest_agRemapsRule(self):
        versions = ["4_0", "5_4", "4_6", "6_10", "6_8"]
        tests = [(None, "6_10"), ("5.4", "5_4"), ("5.0", "4_6"), ("6.9", "6_8"), ("99", "6_10"), ("3.0", "4_0"), ("4", "4_0")]
        for version, expected in tests:
            self.assertEqual(IDMG.VersionTools.getClosest(versions, version), expected, version)

    def test_noVersions_none(self):
        self.assertIsNone(IDMG.VersionTools.getClosest([], "4.0"))
