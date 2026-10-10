##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Dict, Any, List
##### EndExtImports


##### LocalImports
from .WWMIDrawRange import WWMIDrawRange
from .WWMIBlendRemap import WWMIBlendRemap
from .WWMIShapeKeys import WWMIShapeKeys
from ...constants.WWMIBuffers import WWMIBuffers
##### EndLocalImports


##### Script
class WWMIMesh():
    """
    Class for a Wuthering Waves character's mesh, as a WWMI mod carries it: the contents of every buffer of
    the mod's ``Meshes`` folder, and what the mod's ``mod.ini`` needs to know about them

    Parameters
    ----------
    metadata: Dict[:class:`str`, Any]
        The character's ``Metadata.json``

    drawRanges: List[:class:`WWMIDrawRange`]
        Where each component lies in the mesh, in order

    buffers: Dict[:class:`WWMIBuffers`, :class:`bytes`]
        The contents of each buffer

    shapeKeys: :class:`WWMIShapeKeys`
        The shape keys of the mesh

    blendRemaps: List[:class:`WWMIBlendRemap`]
        The blend remaps of the mesh, if its merged skeleton needs them

    blendStride: :class:`int`
        The number of bytes of one vertex in the Blend buffer

    weightsPerVertex: :class:`int`
        The number of bone weights of one vertex

    highestBone: :class:`int`
        The highest merged bone index a vertex refers to

    Attributes
    ----------
    metadata: Dict[:class:`str`, Any]
        The character's ``Metadata.json``

    drawRanges: List[:class:`WWMIDrawRange`]
        Where each component lies in the mesh, in order

    buffers: Dict[:class:`WWMIBuffers`, :class:`bytes`]
        The contents of each buffer

    shapeKeys: :class:`WWMIShapeKeys`
        The shape keys of the mesh

    blendRemaps: List[:class:`WWMIBlendRemap`]
        The blend remaps of the mesh

    blendStride: :class:`int`
        The number of bytes of one vertex in the Blend buffer

    weightsPerVertex: :class:`int`
        The number of bone weights of one vertex

    highestBone: :class:`int`
        The highest merged bone index a vertex refers to
    """

    def __init__(self, metadata: Dict[str, Any], drawRanges: List[WWMIDrawRange], buffers: Dict[WWMIBuffers, bytes], shapeKeys: WWMIShapeKeys,
                 blendRemaps: List[WWMIBlendRemap], blendStride: int, weightsPerVertex: int, highestBone: int):
        self.metadata = metadata
        self.drawRanges = drawRanges
        self.buffers = buffers
        self.shapeKeys = shapeKeys
        self.blendRemaps = blendRemaps
        self.blendStride = blendStride
        self.weightsPerVertex = weightsPerVertex
        self.highestBone = highestBone
##### EndScript
