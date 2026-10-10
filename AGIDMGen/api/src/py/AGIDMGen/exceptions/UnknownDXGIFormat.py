##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### LocalImports
from .Error import Error
from ..constants.DXGIFormats import DXGIFormats
##### EndLocalImports


##### Script
class UnknownDXGIFormat(Error):
    """
    Exception when a buffer element is declared with a DXGI format that cannot be decoded

    Parameters
    ----------
    format: :class:`str`
        The name of the format

    Attributes
    ----------
    format: :class:`str`
        The name of the format
    """

    def __init__(self, format: str):
        super().__init__(f"The format '{format}' cannot be decoded (the formats known are: {', '.join(sorted(DXGIFormats))})")
        self.format = format
##### EndScript
