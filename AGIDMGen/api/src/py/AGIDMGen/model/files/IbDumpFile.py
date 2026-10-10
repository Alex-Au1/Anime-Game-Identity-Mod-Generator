##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import numpy as np
##### EndExtImports


##### LocalImports
from ...constants.FileEncodings import FileEncodings
from ...tools.DumpValueTools import DumpValueTools, DumpValueWhitespace
##### EndLocalImports


##### Script
class IbDumpFile():
    """
    Class for an index buffer dumped by 3DMigoto as text (a ``*-ib=<hash>.txt`` file): a header, then
    one triangle's three indices per line

    .. code-block::

        byte offset: 0
        first index: 20913
        index count: 30846
        topology: trianglelist
        format: DXGI_FORMAT_R16_UINT

        5988 5989 5990
        5988 5990 5991
        ...

    .. note::
        The text is read the way AG Remap's ``IbFile.readDumpStr`` reads it, so the indices are the same:

        - a line holding a ``:`` is a header line, and a blank line is skipped
        - every other line is one triangle: its space-separated values fill three indices, missing values are 0 and extra values are ignored
        - a value is read as an unsigned integer, as :class:`DumpValueTools` describes, and kept to 32 bits

    Parameters
    ----------
    indices: numpy.ndarray
        The indices, as ``uint32``

    Attributes
    ----------
    indices: numpy.ndarray
        The indices, as ``uint32``
    """

    def __init__(self, indices: np.ndarray):
        self.indices = indices

    @property
    def indexCount(self) -> int:
        """
        The number of indices

        :getter: Retrieves the index count
        :type: :class:`int`
        """

        return int(self.indices.size)

    @classmethod
    def fromTxt(cls, txt: str):
        """
        Reads a dump's text

        Parameters
        ----------
        txt: :class:`str`
            The text of the dump

        Returns
        -------
        :class:`IbDumpFile`
            The index buffer
        """

        indices = []
        for line in txt.split("\n"):
            trimmed = line.lstrip(DumpValueWhitespace)
            if (not trimmed or ":" in trimmed):
                continue

            values = [value for value in trimmed.split(" ") if value]
            for i in range(3):
                indices.append((DumpValueTools.parseUnsignedInt(values[i]) if (i < len(values)) else 0) & 0xFFFFFFFF)

        return cls(np.array(indices, dtype = "<u4"))

    @classmethod
    def read(cls, path: str):
        """
        Reads a dump

        Parameters
        ----------
        path: :class:`str`
            The path to the dump

        Returns
        -------
        :class:`IbDumpFile`
            The index buffer
        """

        with open(path, "r", encoding = FileEncodings.UTF8.value) as f:
            return cls.fromTxt(f.read())
##### EndScript
