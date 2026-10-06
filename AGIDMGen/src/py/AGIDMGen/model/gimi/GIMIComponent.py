##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import numpy as np
from typing import Dict, Any, List, Tuple
##### EndExtImports


##### LocalImports
from ...constants.GIMIBuffers import GIMIBuffers
##### EndLocalImports


##### Script
class GIMIComponent():
    """
    Class for one component of a Genshin Impact character's GIMI identity mod: one skinned mesh with its
    own vertex buffers, index buffer and objects (eg. YelanTranquil's Body, Bang and Eye). An older
    character is a single component whose name is the empty string

    Parameters
    ----------
    name: :class:`str`
        The name of the component (its ``component_name`` in ``hash.json``)

    entry: Dict[:class:`str`, Any]
        The component's entry in the asset folder's ``hash.json``

    vertexCount: :class:`int`
        The number of vertices of the component

    buffers: Dict[:class:`GIMIBuffers`, :class:`bytes`]
        The contents of each vertex buffer

    strides: Dict[:class:`GIMIBuffers`, :class:`int`]
        The number of bytes of one vertex in each vertex buffer

    indices: Dict[:class:`str`, numpy.ndarray]
        The indices of each object, as ``uint32``

    textures: Dict[:class:`str`, Dict[:class:`str`, :class:`str`]]
        For each object with textures of its own, the file name in the mod of each kind of texture (eg. ``Diffuse``)

    Attributes
    ----------
    name: :class:`str`
        The name of the component (its ``component_name`` in ``hash.json``)

    entry: Dict[:class:`str`, Any]
        The component's entry in the asset folder's ``hash.json``

    vertexCount: :class:`int`
        The number of vertices of the component

    buffers: Dict[:class:`GIMIBuffers`, :class:`bytes`]
        The contents of each vertex buffer

    strides: Dict[:class:`GIMIBuffers`, :class:`int`]
        The number of bytes of one vertex in each vertex buffer

    indices: Dict[:class:`str`, numpy.ndarray]
        The indices of each object, as ``uint32``

    textures: Dict[:class:`str`, Dict[:class:`str`, :class:`str`]]
        For each object with textures of its own, the file name in the mod of each kind of texture (eg. ``Diffuse``)

    boundTextures: Dict[:class:`str`, Tuple[:class:`str`, :class:`str`, Dict[:class:`str`, :class:`str`]]]
        For each object, the component and object whose textures it binds and the file name of each kind of texture bound. An object with no textures to bind has an empty dictionary of textures
    """

    def __init__(self, name: str, entry: Dict[str, Any], vertexCount: int, buffers: Dict[GIMIBuffers, bytes],
                 strides: Dict[GIMIBuffers, int], indices: Dict[str, np.ndarray], textures: Dict[str, Dict[str, str]]):
        self.name = name
        self.entry = entry
        self.vertexCount = vertexCount
        self.buffers = buffers
        self.strides = strides
        self.indices = indices
        self.textures = textures
        self.boundTextures: Dict[str, Tuple[str, str, Dict[str, str]]] = {}

    @property
    def objects(self) -> List[str]:
        """
        The names of the component's objects (eg. ``Head``, ``Body``), in order

        :getter: Retrieves the objects
        :type: List[:class:`str`]
        """

        return list(self.entry["object_classifications"])

    @property
    def firstIndices(self) -> List[int]:
        """
        Where each object's indices start in the game's index buffer, in the order of :attr:`objects`

        :getter: Retrieves the first indices
        :type: List[:class:`int`]
        """

        return list(self.entry["object_indexes"])
##### EndScript
