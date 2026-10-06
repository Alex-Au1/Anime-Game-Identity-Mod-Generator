##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import numpy as np
from typing import List
##### EndExtImports


##### Script
class WWMIShapeKeys():
    """
    Class for the sparse shape keys of a WWMI mod, as WWMI's shape key loader reads them

    Parameters
    ----------
    offsets: numpy.ndarray
        Where each shape key slot's entries start in ``vertexIds`` and ``deltas``, as ``uint32``. A slot past the last shape key holds the total number of entries

    vertexIds: numpy.ndarray
        The vertex of each entry, shape key by shape key, as ``uint32``

    deltas: numpy.ndarray
        Six ``float16`` per entry: the position delta of the entry's vertex, then three zeros

    counts: List[:class:`int`]
        The number of entries of each shape key slot

    Attributes
    ----------
    offsets: numpy.ndarray
        Where each shape key slot's entries start in :attr:`vertexIds` and :attr:`deltas`, as ``uint32``. A slot past the last shape key holds the total number of entries

    vertexIds: numpy.ndarray
        The vertex of each entry, shape key by shape key, as ``uint32``

    deltas: numpy.ndarray
        Six ``float16`` per entry: the position delta of the entry's vertex, then three zeros

    counts: List[:class:`int`]
        The number of entries of each shape key slot
    """

    def __init__(self, offsets: np.ndarray, vertexIds: np.ndarray, deltas: np.ndarray, counts: List[int]):
        self.offsets = offsets
        self.vertexIds = vertexIds
        self.deltas = deltas
        self.counts = counts

    @property
    def entryCount(self) -> int:
        """
        The number of (shape key, vertex) entries

        :getter: Retrieves the number of entries
        :type: :class:`int`
        """

        return int(self.vertexIds.size)

    @property
    def keys(self) -> List[int]:
        """
        The shape keys that move at least one vertex, in order

        :getter: Retrieves the shape keys
        :type: List[:class:`int`]
        """

        return [key for key, count in enumerate(self.counts) if count]

    @property
    def checksum(self) -> int:
        """
        The sum of the first four offsets: the number the game's ``Metadata.json`` records as the shape keys' ``checksum``

        :getter: Retrieves the checksum
        :type: :class:`int`
        """

        return int(self.offsets[:4].sum())

    @property
    def dispatchY(self) -> int:
        """
        The number of entries in groups of 32, rounded up: the number the game's ``Metadata.json`` records as the shape keys' ``dispatch_y``

        :getter: Retrieves the dispatch count
        :type: :class:`int`
        """

        return -(-self.entryCount // 32)
##### EndScript
