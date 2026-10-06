##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import re
##### EndExtImports


##### Script
# The grammar of C++'s std::from_chars, which is how AG Remap's dump readers (FixRaidenBoss2's
#   VbFile / IbFile.readDumpStr) parse every value: the LONGEST valid prefix of the text is the value,
#   and text with no valid prefix is 0. Unlike Python's int() / float(), it takes no leading '+', no
#   '_' digit separators, no hex, and only ASCII digits -- so "+1" is 0, "1_0" is 1 and "12abc" is 12.
_SignedIntPrefix = re.compile(r"-?[0-9]+")
_UnsignedIntPrefix = re.compile(r"[0-9]+")
_DoublePrefix = re.compile(r"-?(?:(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][+-]?[0-9]+)?|(?i:inf(?:inity)?)|(?i:nan(?:\([0-9A-Za-z_]*\))?))")

_LongLongMin = -(1 << 63)
_LongLongMax = (1 << 63) - 1
_UnsignedLongLongMax = (1 << 64) - 1

# the characters a dump value is trimmed of on both sides
DumpValueWhitespace = " \t\r"


class DumpValueTools():
    """
    Tools for parsing the text values of a 3DMigoto buffer dump, the way AG Remap's dump readers parse them

    .. note::
        A value is read from the longest valid prefix of its text, and text with no valid prefix (or a
        number too large for its type) is read as 0, rather than raising an error.
    """

    @classmethod
    def parseSignedInt(cls, txt: str) -> int:
        """
        Parses a signed integer

        Parameters
        ----------
        txt: :class:`str`
            The text of the value

        Returns
        -------
        :class:`int`
            The value, or 0 if the text has no valid prefix or the value does not fit a 64-bit signed integer
        """

        match = _SignedIntPrefix.match(txt.strip(DumpValueWhitespace))
        if (match is None):
            return 0

        value = int(match.group())
        return value if (_LongLongMin <= value <= _LongLongMax) else 0

    @classmethod
    def parseUnsignedInt(cls, txt: str) -> int:
        """
        Parses an unsigned integer

        Parameters
        ----------
        txt: :class:`str`
            The text of the value

        Returns
        -------
        :class:`int`
            The value, or 0 if the text has no valid prefix (eg. a negative number) or the value does not fit a 64-bit unsigned integer
        """

        match = _UnsignedIntPrefix.match(txt.strip(DumpValueWhitespace))
        if (match is None):
            return 0

        value = int(match.group())
        return value if (value <= _UnsignedLongLongMax) else 0

    @classmethod
    def parseDouble(cls, txt: str) -> float:
        """
        Parses a floating point number

        Parameters
        ----------
        txt: :class:`str`
            The text of the value

        Returns
        -------
        :class:`float`
            The value, or 0 if the text has no valid prefix or the value is too large for a double
        """

        match = _DoublePrefix.match(txt.strip(DumpValueWhitespace))
        if (match is None):
            return 0.0

        text = match.group()
        try:
            value = float(text)
        except ValueError:
            # "nan(...)": Python's float() takes no payload
            value = float(text.split("(", 1)[0])

        # too large for a double: from_chars reports it out of range and leaves the value at 0
        if (value in (float("inf"), float("-inf")) and "n" not in text.lower()):
            return 0.0
        return value
##### EndScript
