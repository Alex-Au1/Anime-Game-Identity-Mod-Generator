##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import re
import numpy as np
from typing import List, Optional
##### EndExtImports


##### LocalImports
from .DumpElement import DumpElement
from ...constants.FileEncodings import FileEncodings
from ...tools.DumpValueTools import DumpValueWhitespace
##### EndLocalImports


##### Script
VertexDataMarker = "vertex-data:"


class VbDumpFile():
    """
    Class for a vertex buffer dumped by 3DMigoto as text (a ``*-vb0=<hash>.txt`` file): a header naming
    the buffer's elements, then each vertex's values

    .. code-block::

        stride: 92
        vertex count: 16062
        topology: trianglelist
        element[0]:
          SemanticName: POSITION
          SemanticIndex: 0
          Format: R32G32B32_FLOAT
          ...

        vertex-data:

        vb0[0]+000 POSITION: 0.0136, 1.4219, -0.0476
        vb0[0]+012 NORMAL: 0.4588, 0.2117, -0.8627
        ...

        vb0[1]+000 POSITION: 0.0145, 1.4171, -0.0464
        ...

    .. note::
        The text is read the way AG Remap's ``VbFile.readDumpStr`` reads it, so the bytes are the same:

        - every non-blank line gives the comma-separated values after its last ``:``
        - a blank line ends a vertex, whose values fill the elements' channels in order: missing values are 0 and extra values are ignored
        - a value is read as :class:`DumpValueTools` describes

    Parameters
    ----------
    elements: List[:class:`DumpElement`]
        The elements of one vertex, in order

    data: :class:`bytes`
        The buffer, one vertex after another

    Attributes
    ----------
    elements: List[:class:`DumpElement`]
        The elements of one vertex, in order

    data: :class:`bytes`
        The buffer, one vertex after another
    """

    def __init__(self, elements: List[DumpElement], data: bytes):
        self.elements = elements
        self.data = data

    @property
    def bytesPerLine(self) -> int:
        """
        The number of bytes of one vertex

        :getter: Retrieves the stride
        :type: :class:`int`
        """

        return sum(element.size for element in self.elements)

    @property
    def vertexCount(self) -> int:
        """
        The number of vertices in the buffer

        :getter: Retrieves the vertex count
        :type: :class:`int`
        """

        bytesPerLine = self.bytesPerLine
        return 0 if (bytesPerLine == 0) else len(self.data) // bytesPerLine

    @classmethod
    def _findHeaderValues(cls, header: str, label: str) -> List[str]:
        # every value of a labelled line, in order: the first word after each 'label'
        return [match.group(1) for match in re.finditer(re.escape(label) + r"[ \t]*(\S*)", header)]

    @classmethod
    def parseHeader(cls, txt: str) -> Optional[List[DumpElement]]:
        """
        Reads the elements a dump's header declares

        Parameters
        ----------
        txt: :class:`str`
            The text of the dump

        Returns
        -------
        Optional[List[:class:`DumpElement`]]
            The elements, or ``None`` if the dump has no ``vertex-data:`` marker, its ``SemanticName`` and ``Format`` lines do not pair up, or any element's format cannot be read
        """

        headerEnd = txt.find(VertexDataMarker)
        if (headerEnd == -1):
            return None

        header = txt[:headerEnd]
        names = cls._findHeaderValues(header, "SemanticName:")
        formatNames = cls._findHeaderValues(header, "Format:")
        if (not names or len(names) != len(formatNames)):
            return None

        result = []
        for name, formatName in zip(names, formatNames):
            dataTypes = DumpElement.parseFormat(formatName)
            if (dataTypes is None):
                return None
            result.append(DumpElement(name, formatName, dataTypes))

        return result

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
        Optional[:class:`VbDumpFile`]
            The buffer, or ``None`` if the header's elements cannot be read (see :meth:`parseHeader`)
        """

        elements = cls.parseHeader(txt)
        if (elements is None):
            return None

        dataTypes = [dataType for element in elements for dataType in element.dataTypes]
        columns = [[] for _ in dataTypes]

        start = txt.find(VertexDataMarker)
        lineEnd = txt.find("\n", start)
        lines = [] if (lineEnd == -1) else txt[lineEnd + 1:].split("\n")

        block = []

        def addBlock():
            if (not block):
                return

            for i, dataType in enumerate(dataTypes):
                columns[i].append(dataType.parse(block[i]) if (i < len(block)) else dataType.getZero())
            block.clear()

        for line in lines:
            if (not line.strip(DumpValueWhitespace)):
                addBlock()
                continue

            # the values are whatever follows the last ':', which skips the "vb0[i]+offset NAME:" part
            block.extend(line.rpartition(":")[2].split(","))

        addBlock()

        if (not columns or not columns[0]):
            return cls(elements, b"")

        rows = np.concatenate([dataType.encode(column) for dataType, column in zip(dataTypes, columns)], axis = 1)
        return cls(elements, np.ascontiguousarray(rows).tobytes())

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
        Optional[:class:`VbDumpFile`]
            The buffer, or ``None`` if the header's elements cannot be read (see :meth:`parseHeader`)
        """

        with open(path, "r", encoding = FileEncodings.UTF8.value) as f:
            return cls.fromTxt(f.read())
##### EndScript
