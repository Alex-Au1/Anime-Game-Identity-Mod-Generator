##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Dict, List, Optional
##### EndExtImports


##### LocalImports
from ...constants.FileEncodings import FileEncodings
##### EndLocalImports


##### Script
class FmtFile():
    """
    Class for a ``.fmt`` file: the layout of a vertex buffer, as 3DMigoto writes it beside a buffer
    in a frame dump

    .. code-block::

        stride: 48
        topology: trianglelist
        format: DXGI_FORMAT_R16_UINT
        element[0]:
          SemanticName: POSITION
          SemanticIndex: 0
          Format: R32G32B32_FLOAT
          AlignedByteOffset: 0
          ...

    Parameters
    ----------
    header: Optional[Dict[:class:`str`, :class:`str`]]
        The top-level keys of the file (``stride``, ``topology``, ``format``) :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    elements: Optional[List[Dict[:class:`str`, :class:`str`]]]
        The keys of each ``element[N]`` of the file, in order :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    header: Dict[:class:`str`, :class:`str`]
        The top-level keys of the file (``stride``, ``topology``, ``format``)

    elements: List[Dict[:class:`str`, :class:`str`]]
        The keys of each ``element[N]`` of the file, in order
    """

    def __init__(self, header: Optional[Dict[str, str]] = None, elements: Optional[List[Dict[str, str]]] = None):
        self.header = {} if (header is None) else header
        self.elements = [] if (elements is None) else elements

    @classmethod
    def fromTxt(cls, txt: str):
        """
        Reads a ``.fmt`` file's text

        Parameters
        ----------
        txt: :class:`str`
            The text of the file

        Returns
        -------
        :class:`FmtFile`
            The file read
        """

        header = {}
        elements = []
        current = None

        for line in txt.splitlines():
            if (not line.strip()):
                continue

            if (line.startswith("element[")):
                current = {}
                elements.append(current)
                continue

            key, separator, value = line.partition(":")
            if (not separator):
                continue

            if (line[0] in " \t" and current is not None):
                current[key.strip()] = value.strip()
            else:
                header[key.strip()] = value.strip()

        return cls(header = header, elements = elements)

    @classmethod
    def read(cls, path: str):
        """
        Reads a ``.fmt`` file

        Parameters
        ----------
        path: :class:`str`
            The path to the file

        Returns
        -------
        :class:`FmtFile`
            The file read
        """

        with open(path, "r", encoding = FileEncodings.UTF8.value) as f:
            return cls.fromTxt(f.read())

    @property
    def stride(self) -> int:
        """
        The number of bytes of one vertex in the buffer, or 0 if the file declares none

        :getter: Retrieves the stride
        :type: :class:`int`
        """

        return int(self.header.get("stride", "0"))

    def getElement(self, semanticName: str, semanticIndex: int = 0) -> Optional[Dict[str, str]]:
        """
        Retrieves an element of the buffer

        Parameters
        ----------
        semanticName: :class:`str`
            The semantic name of the element (eg. ``POSITION``), in any case

        semanticIndex: :class:`int`
            The semantic index of the element :raw-html:`<br />` :raw-html:`<br />`

            **Default**: 0

        Returns
        -------
        Optional[Dict[:class:`str`, :class:`str`]]
            The element, or ``None`` if the buffer has no such element
        """

        semanticName = semanticName.upper()
        for element in self.elements:
            if (element.get("SemanticName", "").upper() == semanticName and int(element.get("SemanticIndex", "0")) == semanticIndex):
                return element

        return None
##### EndScript
