##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import math
import numpy as np
from typing import List, Union
##### EndExtImports


##### LocalImports
from ...constants.DumpDataKinds import DumpDataKinds
from ...tools.DumpValueTools import DumpValueTools
##### EndLocalImports


##### Script
class DumpDataType():
    """
    Class for the type of one channel of a buffer element (eg. one of the three 32-bit floats of a
    ``R32G32B32_FLOAT`` position): how its text value in a 3DMigoto dump is read, and how it is stored
    as bytes (little-endian)

    Parameters
    ----------
    kind: :class:`DumpDataKinds`
        The kind of value the channel holds

    size: :class:`int`
        The number of bytes the channel takes

    Attributes
    ----------
    kind: :class:`DumpDataKinds`
        The kind of value the channel holds

    size: :class:`int`
        The number of bytes the channel takes
    """

    def __init__(self, kind: DumpDataKinds, size: int):
        self.kind = kind
        self.size = size

    def __eq__(self, other) -> bool:
        if (not isinstance(other, DumpDataType)):
            return NotImplemented
        return (self.kind, self.size) == (other.kind, other.size)

    def __repr__(self) -> str:
        return f"DumpDataType({self.kind}, {self.size})"

    def parse(self, txt: str) -> Union[int, float]:
        """
        Reads the text of one value in a dump

        Parameters
        ----------
        txt: :class:`str`
            The text of the value

        Returns
        -------
        Union[:class:`int`, :class:`float`]
            The value. See :class:`DumpValueTools` for how text that is not a valid number is read
        """

        if (self.kind == DumpDataKinds.SignedInt):
            return DumpValueTools.parseSignedInt(txt)
        if (self.kind == DumpDataKinds.UnsignedInt):
            return DumpValueTools.parseUnsignedInt(txt)
        return DumpValueTools.parseDouble(txt)

    def getZero(self) -> Union[int, float]:
        """
        Retrieves the value a missing value is read as

        Returns
        -------
        Union[:class:`int`, :class:`float`]
            0, as the kind of number the channel holds
        """

        return 0 if (self.kind in (DumpDataKinds.SignedInt, DumpDataKinds.UnsignedInt)) else 0.0

    def _encodeInts(self, values: List[int]) -> np.ndarray:
        # the value's lowest 'size' bytes, in two's complement for a negative value
        mask = (1 << (8 * self.size)) - 1
        raw = np.array([value & mask for value in values], dtype = "<u8")
        return raw.view(np.uint8).reshape(-1, 8)[:, :self.size]

    def encode(self, values: List[Union[int, float]]) -> np.ndarray:
        """
        Stores values as bytes

        .. note::
            - A 32-bit float is rounded to the nearest float
            - A 16-bit float is TRUNCATED (not rounded), a value too small for a normal 16-bit float becomes 0, and a value too large (or not a number) becomes infinity
            - An integer keeps its lowest bytes
            - A ``UNORM`` value is multiplied by the channel's largest integer and truncated towards 0

        Parameters
        ----------
        values: List[Union[:class:`int`, :class:`float`]]
            The values, one per line of the buffer

        Returns
        -------
        numpy.ndarray
            The bytes, one row of :attr:`size` bytes per value
        """

        if (self.kind == DumpDataKinds.Float):
            with np.errstate(over = "ignore", invalid = "ignore"):
                floats = np.array(values, dtype = np.float64).astype("<f4")

            if (self.size == 4):
                return floats.view(np.uint8).reshape(-1, 4)

            bits = floats.view("<u4").astype(np.int64)
            sign = (bits >> 16) & 0x8000
            exponent = ((bits >> 23) & 0xFF) - 127 + 15
            mantissa = bits & 0x7FFFFF
            half = np.where(exponent <= 0, sign, np.where(exponent >= 0x1F, sign | 0x7C00, sign | (exponent << 10) | (mantissa >> 13)))
            return half.astype("<u2").view(np.uint8).reshape(-1, 2)

        if (self.kind == DumpDataKinds.Unorm):
            maxValue = float((1 << (8 * self.size)) - 1)
            ints = []
            for value in values:
                scaled = value * maxValue
                ints.append(0 if (math.isnan(scaled) or math.isinf(scaled)) else math.trunc(scaled))
            return self._encodeInts(ints)

        return self._encodeInts(values)
##### EndScript
