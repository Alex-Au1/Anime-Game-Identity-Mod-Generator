##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Dict, Any
##### EndExtImports


##### LocalImports
from ...exceptions.BadAssetData import BadAssetData
##### EndLocalImports


##### Script
class WWMIDrawRange():
    """
    Class for where one component of a Wuthering Waves character lies in the character's mesh: its range of
    vertices and its range of the mesh's index buffer, as the ``components`` list of the character's
    ``Metadata.json`` records them

    Parameters
    ----------
    index: :class:`int`
        The number of the component

    entry: Dict[:class:`str`, Any]
        The component's entry in the ``components`` list of ``Metadata.json``

    Raises
    ------
    :class:`BadAssetData`
        If ``entry`` lacks one of ``vertex_offset``, ``vertex_count``, ``index_offset`` or ``index_count``

    Attributes
    ----------
    index: :class:`int`
        The number of the component

    entry: Dict[:class:`str`, Any]
        The component's entry in the ``components`` list of ``Metadata.json``

    vertexOffset: :class:`int`
        Where the component's vertices start in the whole mesh

    indexOffset: :class:`int`
        Where the component's indices start in the whole mesh's index buffer
    """

    def __init__(self, index: int, entry: Dict[str, Any]):
        self.index = index
        self.entry = entry

        for key in ("vertex_offset", "index_offset"):
            if (key not in entry):
                raise BadAssetData(f"Component {index} of Metadata.json has no '{key}'")

        self.vertexOffset = int(entry["vertex_offset"])
        self.indexOffset = int(entry["index_offset"])

    @property
    def vertexCount(self) -> int:
        """
        The number of vertices in the component

        :getter: Retrieves the vertex count
        :type: :class:`int`
        """

        if ("vertex_count" not in self.entry):
            raise BadAssetData(f"Component {self.index} of Metadata.json has no 'vertex_count'")
        return int(self.entry["vertex_count"])

    @property
    def indexCount(self) -> int:
        """
        The number of indices in the component

        :getter: Retrieves the index count
        :type: :class:`int`
        """

        if ("index_count" not in self.entry):
            raise BadAssetData(f"Component {self.index} of Metadata.json has no 'index_count'")
        return int(self.entry["index_count"])
##### EndScript
