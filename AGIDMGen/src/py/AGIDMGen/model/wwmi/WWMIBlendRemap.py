##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### Script
class WWMIBlendRemap():
    """
    Class for one blend remap of a WWMI mod: the table that lets one component of a character, whose
    merged skeleton has more bones than the 8-bit indices of the Blend buffer can name, address the
    bones it uses

    Parameters
    ----------
    componentIndex: :class:`int`
        The number of the component that the remap is for

    remapId: :class:`int`
        The number of the remap. Remaps are numbered in component order, from 0

    boneCount: :class:`int`
        The number of distinct bones the component uses

    Attributes
    ----------
    componentIndex: :class:`int`
        The number of the component that the remap is for

    remapId: :class:`int`
        The number of the remap. Remaps are numbered in component order, from 0

    boneCount: :class:`int`
        The number of distinct bones the component uses
    """

    def __init__(self, componentIndex: int, remapId: int, boneCount: int):
        self.componentIndex = componentIndex
        self.remapId = remapId
        self.boneCount = boneCount

    def __eq__(self, other) -> bool:
        if (not isinstance(other, WWMIBlendRemap)):
            return NotImplemented
        return (self.componentIndex, self.remapId, self.boneCount) == (other.componentIndex, other.remapId, other.boneCount)

    def __repr__(self) -> str:
        return f"WWMIBlendRemap(componentIndex = {self.componentIndex}, remapId = {self.remapId}, boneCount = {self.boneCount})"
##### EndScript
