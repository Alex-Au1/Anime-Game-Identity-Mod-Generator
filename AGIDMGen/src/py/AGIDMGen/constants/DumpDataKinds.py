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
class DumpDataKinds(Enum):
    """
    The kinds of value one channel of a buffer element can hold, as named by the suffix of its DXGI format

    Attributes
    ----------
    Float: :class:`str`
        A floating point number (``FLOAT``)

    SignedInt: :class:`str`
        A signed integer (``SINT``)

    UnsignedInt: :class:`str`
        An unsigned integer (``UINT``)

    Unorm: :class:`str`
        An unsigned number from 0 to 1, stored as an unsigned integer scaled to its largest value (``UNORM``)
    """

    Float = "FLOAT"
    SignedInt = "SINT"
    UnsignedInt = "UINT"
    Unorm = "UNORM"
##### EndScript
