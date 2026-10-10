##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from enum import Enum
from typing import Dict
##### EndExtImports


##### Script
class GIMIBuffers(Enum):
    """
    The vertex buffers of one component of a GIMI mod, in the order GIMI lays a vertex out. Each one is
    written to ``<name><component><buffer>.buf``

    Attributes
    ----------
    Position: :class:`str`
        The ``POSITION``, ``NORMAL`` and ``TANGENT`` of the vertices

    Blend: :class:`str`
        The ``BLENDWEIGHT(S)`` and ``BLENDINDICES`` of the vertices

    Texcoord: :class:`str`
        The ``COLOR`` and ``TEXCOORD`` (``TEXCOORD1``, ...) of the vertices
    """

    Position = "Position"
    Blend = "Blend"
    Texcoord = "Texcoord"


#: The buffer each element of a dumped vertex belongs to, by its semantic name
GIMISemanticBuffers: Dict[str, GIMIBuffers] = {
    "POSITION": GIMIBuffers.Position, "NORMAL": GIMIBuffers.Position, "TANGENT": GIMIBuffers.Position,
    "BLENDWEIGHT": GIMIBuffers.Blend, "BLENDWEIGHTS": GIMIBuffers.Blend, "BLENDINDICES": GIMIBuffers.Blend,
    "COLOR": GIMIBuffers.Texcoord, "TEXCOORD": GIMIBuffers.Texcoord
}

#: The number of bytes per vertex GIMI fixes for a buffer. The Texcoord buffer's is not fixed: it is 20 with a second UV set and 12 without, and can differ between the components of one character
GIMIFixedStrides: Dict[GIMIBuffers, int] = {GIMIBuffers.Position: 40, GIMIBuffers.Blend: 32}

#: What the name of a download folder's copy of the asset folder's ``hash.json`` ends with: ``<prefix>Hash.json``
GIMIHashFileSuffix = "Hash.json"
##### EndScript
