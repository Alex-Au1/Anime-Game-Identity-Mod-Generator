##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Tuple
##### EndExtImports


##### LocalImports
from ..constants.DXGIFormats import DXGIFormats, DXGIFormatPrefix
from ..exceptions.UnknownDXGIFormat import UnknownDXGIFormat
##### EndLocalImports


##### Script
class FormatTools():
    """
    Tools for handling the DXGI formats of buffer elements
    """

    @classmethod
    def decode(cls, format: str) -> Tuple[str, int]:
        """
        Retrieves how an element of some DXGI format is decoded

        Parameters
        ----------
        format: :class:`str`
            The name of the format, with or without the ``DXGI_FORMAT_`` prefix (eg. ``R32G32B32_FLOAT`` or ``DXGI_FORMAT_R32G32B32_FLOAT``)

        Raises
        ------
        :class:`UnknownDXGIFormat`
            If the format cannot be decoded

        Returns
        -------
        Tuple[:class:`str`, :class:`int`]
            The numpy dtype of one channel and the number of channels
        """

        key = format.strip().upper()
        if (key.startswith(DXGIFormatPrefix)):
            key = key[len(DXGIFormatPrefix):]

        try:
            return DXGIFormats[key]
        except KeyError:
            raise UnknownDXGIFormat(format) from None
##### EndScript
