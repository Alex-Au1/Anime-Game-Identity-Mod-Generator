import math

from .baseUnitTest import BaseUnitTest, IDMG


class DumpValueToolsTest(BaseUnitTest):
    # the expected values are C++ std::from_chars': the longest valid prefix is the value, and no valid
    #   prefix (or a value out of range) is 0

    # =============== parseSignedInt ========================================

    def test_parseSignedInt_fromCharsPrefix(self):
        tests = [("12", 12), (" -7\t", -7), ("12abc", 12), ("1.9", 1), ("+5", 0), ("abc", 0), ("", 0), ("1_0", 1),
                 ("9223372036854775807", 9223372036854775807), ("9223372036854775808", 0)]
        for txt, expected in tests:
            self.assertEqual(IDMG.DumpValueTools.parseSignedInt(txt), expected, repr(txt))

    # =============== parseUnsignedInt ======================================

    def test_parseUnsignedInt_fromCharsPrefix(self):
        tests = [("5988", 5988), ("5988\r", 5988), ("-1", 0), ("+1", 0), ("4294967296", 4294967296),
                 ("18446744073709551615", 18446744073709551615), ("18446744073709551616", 0), ("١", 0)]
        for txt, expected in tests:
            self.assertEqual(IDMG.DumpValueTools.parseUnsignedInt(txt), expected, repr(txt))

    # =============== parseDouble ===========================================

    def test_parseDouble_fromCharsPrefix(self):
        tests = [("0.5", 0.5), (" -1.25e2 ", -125.0), (".5", 0.5), ("5.", 5.0), ("1e", 1.0), ("1e+", 1.0), ("2abc", 2.0),
                 ("+1", 0.0), ("0x1p3", 0.0), ("abc", 0.0), ("", 0.0), ("1e999", 0.0), ("-inf", float("-inf")), ("Infinity", float("inf"))]
        for txt, expected in tests:
            self.assertEqual(IDMG.DumpValueTools.parseDouble(txt), expected, repr(txt))

    def test_parseDouble_nan(self):
        for txt in ("nan", "-NaN", "nan(123)"):
            self.assertTrue(math.isnan(IDMG.DumpValueTools.parseDouble(txt)), repr(txt))
