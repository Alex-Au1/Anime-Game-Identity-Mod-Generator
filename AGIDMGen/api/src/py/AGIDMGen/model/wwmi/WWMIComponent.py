##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import os
import numpy as np
from typing import Dict, Any, Tuple
##### EndExtImports


##### LocalImports
from .WWMIDrawRange import WWMIDrawRange
from ..files.FmtFile import FmtFile
from ...exceptions.BadAssetData import BadAssetData
from ...tools.FormatTools import FormatTools
##### EndLocalImports


##### Script
class WWMIComponent(WWMIDrawRange):
    """
    Class for one ``Component N`` of a Wuthering Waves character's asset folder: one draw range of the
    character's mesh, with its own interleaved vertex buffer (``Component N.vb``), its layout
    (``Component N.fmt``) and its index buffer (``Component N.ib``)

    Parameters
    ----------
    folder: :class:`str`
        The asset folder

    index: :class:`int`
        The number of the component

    entry: Dict[:class:`str`, Any]
        The component's entry in the ``components`` list of the asset folder's ``Metadata.json``

    Raises
    ------
    :class:`BadAssetData`
        If one of the component's files is missing, or its files disagree with each other or with ``entry``

    Attributes
    ----------
    index: :class:`int`
        The number of the component

    entry: Dict[:class:`str`, Any]
        The component's entry in the ``components`` list of the asset folder's ``Metadata.json``

    fmt: :class:`FmtFile`
        The layout of the component's vertex buffer

    rows: numpy.ndarray
        The component's vertex buffer, one row of bytes per vertex

    indices: numpy.ndarray
        The component's indices (local to the component), as ``uint32``

    vertexOffset: :class:`int`
        Where the component's vertices start in the whole mesh

    indexOffset: :class:`int`
        Where the component's indices start in the whole mesh's index buffer
    """

    def __init__(self, folder: str, index: int, entry: Dict[str, Any]):
        super().__init__(index, entry)

        base = os.path.join(folder, f"Component {index}")
        for ext in (".fmt", ".vb", ".ib"):
            if (not os.path.isfile(base + ext)):
                raise BadAssetData(f"'{base + ext}' is missing for component {index} of Metadata.json")

        self.fmt = FmtFile.read(base + ".fmt")
        stride = self.stride
        raw = np.fromfile(base + ".vb", dtype = np.uint8)
        if (stride <= 0 or raw.size % stride != 0):
            raise BadAssetData(f"'Component {index}.vb' is {raw.size} bytes, not a whole number of {stride}-byte vertices")

        self.rows = raw.reshape(-1, stride)
        vertexCount = self.vertexCount
        if (int(entry.get("vertex_count", vertexCount)) != vertexCount):
            raise BadAssetData(f"'Component {index}.vb' holds {vertexCount} vertices but Metadata.json declares {entry.get('vertex_count')}")

        ibDtype, _ = FormatTools.decode(self.fmt.header.get("format", "R16_UINT"))
        self.indices = np.fromfile(base + ".ib", dtype = ibDtype).astype(np.uint32)
        if (int(entry.get("index_count", self.indices.size)) != self.indices.size):
            raise BadAssetData(f"'Component {index}.ib' holds {self.indices.size} indices but Metadata.json declares {entry.get('index_count')}")

        if (self.indices.size and int(self.indices.max()) >= vertexCount):
            raise BadAssetData(f"'Component {index}.ib' references vertex {int(self.indices.max())} of {vertexCount}")

    @property
    def stride(self) -> int:
        """
        The number of bytes of one vertex in the component's vertex buffer

        :getter: Retrieves the stride
        :type: :class:`int`
        """

        return self.fmt.stride

    @property
    def vertexCount(self) -> int:
        """
        The number of vertices in the component

        :getter: Retrieves the vertex count
        :type: :class:`int`
        """

        return self.rows.shape[0]

    @property
    def indexCount(self) -> int:
        """
        The number of indices in the component

        :getter: Retrieves the index count
        :type: :class:`int`
        """

        return int(self.indices.size)

    def hasElement(self, semanticName: str, semanticIndex: int = 0) -> bool:
        """
        Whether the component's vertex buffer has some element

        Parameters
        ----------
        semanticName: :class:`str`
            The semantic name of the element (eg. ``POSITION``), in any case

        semanticIndex: :class:`int`
            The semantic index of the element :raw-html:`<br />` :raw-html:`<br />`

            **Default**: 0

        Returns
        -------
        :class:`bool`
            Whether the element exists
        """

        return self.fmt.getElement(semanticName, semanticIndex) is not None

    def getElementBytes(self, semanticName: str, semanticIndex: int, width: int) -> np.ndarray:
        """
        Retrieves the first bytes of an element, for every vertex of the component

        .. note::
            A character with eight bone influences a vertex declares its ``BLENDINDICES`` / ``BLENDWEIGHT``
            as a single-channel format while each spans 8 bytes. A single-channel element is therefore as
            wide as the space up to the next element.

        Parameters
        ----------
        semanticName: :class:`str`
            The semantic name of the element (eg. ``POSITION``), in any case

        semanticIndex: :class:`int`
            The semantic index of the element

        width: :class:`int`
            The number of bytes to retrieve per vertex

        Raises
        ------
        :class:`BadAssetData`
            If the component has no such element, or the element is narrower than ``width``

        Returns
        -------
        numpy.ndarray
            The bytes, one row per vertex, as a view of :attr:`rows`
        """

        element = self.fmt.getElement(semanticName, semanticIndex)
        if (element is None):
            raise BadAssetData(f"Component {self.index}: the .fmt declares no {semanticName}{semanticIndex} element")

        dtype, count = FormatTools.decode(element.get("Format", ""))
        offset = int(element.get("AlignedByteOffset", "0"))

        following = [int(e.get("AlignedByteOffset", "0")) for e in self.fmt.elements if int(e.get("AlignedByteOffset", "0")) > offset]
        span = (min(following) if following else self.stride) - offset
        available = max(np.dtype(dtype).itemsize * count, span if count == 1 else 0)
        if (width > available):
            raise BadAssetData(f"Component {self.index}: {semanticName}{semanticIndex} is {available} bytes in the .fmt, {width} wanted")

        return self.rows[:, offset:offset + width]

    def getShapeKeys(self) -> Dict[int, Tuple[np.ndarray, np.ndarray]]:
        """
        Retrieves the shape keys of the component: every ``SHAPEKEY`` element that moves at least one vertex

        Raises
        ------
        :class:`BadAssetData`
            If a ``SHAPEKEY`` element does not have three channels

        Returns
        -------
        Dict[:class:`int`, Tuple[numpy.ndarray, numpy.ndarray]]
            For each shape key, the local ids of the vertices it moves and their position deltas as ``float16`` (one row of 3 per vertex)
        """

        result = {}
        for element in self.fmt.elements:
            if (element.get("SemanticName", "").upper() != "SHAPEKEY"):
                continue

            key = int(element.get("SemanticIndex", "0"))
            dtype, count = FormatTools.decode(element.get("Format", ""))
            if (count != 3):
                raise BadAssetData(f"Component {self.index}: SHAPEKEY{key} is {element.get('Format')}, expected three channels")

            offset = int(element.get("AlignedByteOffset", "0"))
            width = np.dtype(dtype).itemsize * 3
            deltas = np.ascontiguousarray(self.rows[:, offset:offset + width]).view(dtype).reshape(-1, 3)
            used = np.nonzero((deltas != 0).any(axis = 1))[0]
            if (used.size):
                result[key] = (used, deltas[used].astype("<f2"))

        return result
##### EndScript
