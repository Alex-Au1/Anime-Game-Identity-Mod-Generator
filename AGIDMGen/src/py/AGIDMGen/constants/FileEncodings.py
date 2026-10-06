##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from enum import Enum
##### EndExtImports


##### Script
class FileEncodings(Enum):
    """
    The text encodings used when reading and writing the files of a mod

    Attributes
    ----------
    UTF8: :class:`str`
        The `utf-8` encoding

    Latin1: :class:`str`
        The `latin1` encoding
    """

    UTF8 = "utf-8"
    Latin1 = "latin1"


#: The encoding a ``.ini`` file is written in
IniFileEncoding = FileEncodings.UTF8.value
#: The encodings tried, in order, when reading a text file
ReadEncodings = [IniFileEncoding, FileEncodings.Latin1.value]
##### EndScript
