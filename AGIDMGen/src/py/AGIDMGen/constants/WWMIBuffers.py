##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import re
from enum import Enum
from typing import Dict
##### EndExtImports


##### Script
class WWMIBuffers(Enum):
    """
    The buffer files of a WWMI mod, in the order the mod's ``Metadata.json`` export format lists them,
    and the file name each one is written to inside the mod's ``Meshes`` folder

    Attributes
    ----------
    Index: :class:`str`
        The index buffer of the whole mesh

    Position: :class:`str`
        The positions of the vertices

    Blend: :class:`str`
        The bone indices and bone weights of the vertices

    Vector: :class:`str`
        The tangents, normals and bitangent signs of the vertices

    Color: :class:`str`
        The vertex colours

    TexCoord: :class:`str`
        The texture coordinates of the vertices

    ShapeKeyOffset: :class:`str`
        Where each shape key's entries start in :attr:`ShapeKeyVertexId` and :attr:`ShapeKeyVertexOffset`

    ShapeKeyVertexId: :class:`str`
        The vertex of each shape key entry

    ShapeKeyVertexOffset: :class:`str`
        The position delta of each shape key entry

    BlendRemapVertexVG: :class:`str`
        Every vertex's full bone indices, for a mod that needs a blend remap

    BlendRemapForward: :class:`str`
        The local to merged bone index table of each blend remap

    BlendRemapReverse: :class:`str`
        The merged to local bone index table of each blend remap
    """

    Index = "Index.buf"
    Position = "Position.buf"
    Blend = "Blend.buf"
    Vector = "Vector.buf"
    Color = "Color.buf"
    TexCoord = "TexCoord.buf"
    ShapeKeyOffset = "ShapeKeyOffset.buf"
    ShapeKeyVertexId = "ShapeKeyVertexId.buf"
    ShapeKeyVertexOffset = "ShapeKeyVertexOffset.buf"
    BlendRemapVertexVG = "BlendRemapVertexVG.buf"
    BlendRemapForward = "BlendRemapForward.buf"
    BlendRemapReverse = "BlendRemapReverse.buf"


#: The buffers written only for a character whose merged skeleton needs WWMI's blend remap
WWMIBlendRemapBuffers = [WWMIBuffers.BlendRemapVertexVG, WWMIBuffers.BlendRemapForward, WWMIBuffers.BlendRemapReverse]

#: The number of shape key slots WWMI's shape key loader has
WWMIShapeKeySlots = 128

#: The most merged bones WWMI can skin, and so the length of each blend remap table
WWMIBlendRemapSize = 512

#: The number of bones the 8-bit bone indices of the Blend buffer can name, without a blend remap
WWMIBlendIndexLimit = 256

#: What each buffer's file name in a download folder ends with, before ``.buf`` (``<prefix><name>.buf``)
WWMIDownloadNames: Dict[WWMIBuffers, str] = {buffer: ("Texcoord" if (buffer == WWMIBuffers.TexCoord) else buffer.name) for buffer in WWMIBuffers}

#: What a texture's file name in a download folder ends with, after its prefix: ``Texture<hash>.dds``
WWMIDownloadTextureSuffix = re.compile(r"Texture(?P<hash>[0-9a-fA-F]{8})\.dds")
##### EndScript
