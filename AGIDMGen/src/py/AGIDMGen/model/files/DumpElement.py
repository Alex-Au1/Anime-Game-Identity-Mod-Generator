##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import re
from typing import List, Optional
##### EndExtImports


##### LocalImports
from .DumpDataType import DumpDataType
from ...constants.DXGIFormats import DXGIFormatPrefix
from ...constants.DumpDataKinds import DumpDataKinds
##### EndLocalImports


##### Script
# the channels of a format: a letter and its bit width each, eg. "R32G32B32" is three 32-bit channels
_ChannelPattern = re.compile(r"[A-Za-z]([0-9]+)")


class DumpElement():
    """
    Class for one element of a vertex buffer in a 3DMigoto dump (eg. the ``POSITION`` of every vertex)

    Parameters
    ----------
    name: :class:`str`
        The semantic name of the element (eg. ``POSITION``)

    formatName: :class:`str`
        The DXGI format of the element (eg. ``R32G32B32_FLOAT``)

    dataTypes: List[:class:`DumpDataType`]
        The type of each channel of the element, in order

    Attributes
    ----------
    name: :class:`str`
        The semantic name of the element (eg. ``POSITION``)

    formatName: :class:`str`
        The DXGI format of the element (eg. ``R32G32B32_FLOAT``)

    dataTypes: List[:class:`DumpDataType`]
        The type of each channel of the element, in order
    """

    def __init__(self, name: str, formatName: str, dataTypes: List[DumpDataType]):
        self.name = name
        self.formatName = formatName
        self.dataTypes = dataTypes

    @property
    def size(self) -> int:
        """
        The number of bytes the element takes in one vertex

        :getter: Retrieves the size
        :type: :class:`int`
        """

        return sum(dataType.size for dataType in self.dataTypes)

    @classmethod
    def parseFormat(cls, formatName: str) -> Optional[List[DumpDataType]]:
        """
        Retrieves the channel types of a DXGI format

        Parameters
        ----------
        formatName: :class:`str`
            The DXGI format, with or without the ``DXGI_FORMAT_`` prefix (eg. ``R32G32B32_FLOAT``)

        Returns
        -------
        Optional[List[:class:`DumpDataType`]]
            The type of each channel, or ``None`` if any channel of the format cannot be read (eg. a ``SNORM``, or a channel narrower than a byte)
        """

        if (formatName.upper().startswith(DXGIFormatPrefix)):
            formatName = formatName[len(DXGIFormatPrefix):]

        channels, separator, suffix = formatName.partition("_")
        if (not separator):
            return None

        try:
            kind = DumpDataKinds(suffix)
        except ValueError:
            return None

        result = []
        for bits in _ChannelPattern.findall(channels):
            size = int(bits) // 8
            if (size == 0 or size > 8 or (kind == DumpDataKinds.Float and size not in (2, 4))):
                return None
            result.append(DumpDataType(kind, size))

        return result if (result) else None
##### EndScript
