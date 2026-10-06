import struct

from .baseUnitTest import BaseUnitTest, IDMG


class DumpDataTypeTest(BaseUnitTest):
    def encode(self, kind, size, values) -> bytes:
        return IDMG.DumpDataType(kind, size).encode(values).tobytes()

    # =============== encode ================================================

    def test_float32_roundedToNearest(self):
        self.assertEqual(self.encode(IDMG.DumpDataKinds.Float, 4, [0.1, -2.5]), struct.pack("<2f", 0.1, -2.5))

    def test_float16_truncatedNotRounded(self):
        # 1 + 3 * 2^-11 is halfway between the halves 0x3C01 and 0x3C02: rounding gives 0x3C02, truncating 0x3C01
        tests = [(1.0, 0x3C00), (1 + 3 * 2 ** -11, 0x3C01), (-2.0, 0xC000), (2 ** -20, 0x0000), (1e6, 0x7C00), (float("nan"), 0x7C00)]
        for value, expected in tests:
            self.assertEqual(self.encode(IDMG.DumpDataKinds.Float, 2, [value]), struct.pack("<H", expected), repr(value))

    def test_ints_lowestBytesKept(self):
        tests = [(IDMG.DumpDataKinds.SignedInt, 4, -1, b"\xff\xff\xff\xff"), (IDMG.DumpDataKinds.SignedInt, 2, 258, b"\x02\x01"),
                 (IDMG.DumpDataKinds.UnsignedInt, 4, (1 << 32) + 5, b"\x05\x00\x00\x00"), (IDMG.DumpDataKinds.UnsignedInt, 8, (1 << 64) - 1, b"\xff" * 8)]
        for kind, size, value, expected in tests:
            self.assertEqual(self.encode(kind, size, [value]), expected, repr((kind, size, value)))

    def test_unorm_scaledAndTruncated(self):
        tests = [(0.0, 0), (0.5, 127), (1.0, 255), (0.999, 254)]
        for value, expected in tests:
            self.assertEqual(self.encode(IDMG.DumpDataKinds.Unorm, 1, [value]), bytes([expected]), repr(value))
        self.assertEqual(self.encode(IDMG.DumpDataKinds.Unorm, 2, [0.5]), struct.pack("<H", 32767))

    def test_values_oneRowEach(self):
        result = IDMG.DumpDataType(IDMG.DumpDataKinds.UnsignedInt, 2).encode([1, 2, 3])
        self.assertEqual(result.shape, (3, 2))

    # =============== parse =================================================

    def test_parse_byKind(self):
        tests = [(IDMG.DumpDataKinds.SignedInt, "-3", -3), (IDMG.DumpDataKinds.UnsignedInt, "-3", 0), (IDMG.DumpDataKinds.Float, "-3.5", -3.5), (IDMG.DumpDataKinds.Unorm, "0.25", 0.25)]
        for kind, txt, expected in tests:
            self.assertEqual(IDMG.DumpDataType(kind, 4).parse(txt), expected)

