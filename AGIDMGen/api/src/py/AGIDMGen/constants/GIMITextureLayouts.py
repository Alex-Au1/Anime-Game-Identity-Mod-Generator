##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from enum import Enum
from typing import Tuple
##### EndExtImports


##### Script
class GIMITextureLayouts(Enum):
    """
    The two layouts a GIMI mod binds an object's textures in, chosen by whether the object's shader reads a
    normal map. Each value is the (register, texture kind) pairs of the layout, and the command list of
    ``ORFix`` that moves the textures to the registers the shader actually reads

    Attributes
    ----------
    NormalMap: Tuple[Tuple[Tuple[:class:`str`, :class:`str`], ...], :class:`str`]
        ``ps-t0`` normal map, ``ps-t1`` diffuse and ``ps-t2`` light map, fixed by ``ORFix``

    Plain: Tuple[Tuple[Tuple[:class:`str`, :class:`str`], ...], :class:`str`]
        ``ps-t0`` diffuse and ``ps-t1`` light map, fixed by ``NNFix``
    """

    NormalMap = ((("ps-t0", "NormalMap"), ("ps-t1", "Diffuse"), ("ps-t2", "LightMap")), "CommandList\\global\\ORFix\\ORFix")
    Plain = ((("ps-t0", "Diffuse"), ("ps-t1", "LightMap")), "CommandList\\global\\ORFix\\NNFix")

    @property
    def registers(self) -> Tuple[Tuple[str, str], ...]:
        """
        The (register, texture kind) pairs of the layout

        :getter: Retrieves the registers
        :type: Tuple[Tuple[:class:`str`, :class:`str`], ...]
        """

        return self.value[0]

    @property
    def fixCommand(self) -> str:
        """
        The command list that moves the layout's textures to the registers the shader reads

        :getter: Retrieves the command list
        :type: :class:`str`
        """

        return self.value[1]
##### EndScript
