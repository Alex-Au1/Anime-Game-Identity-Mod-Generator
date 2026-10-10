##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import List, Optional
##### EndExtImports


##### LocalImports
from .GIMIComponent import GIMIComponent
from ...constants.GIMIBuffers import GIMIBuffers
##### EndLocalImports


##### Script
class GIMIIdentityMod():
    """
    Class for a generated GIMI identity mod: what was written, and what was left out

    Parameters
    ----------
    name: :class:`str`
        The name of the character in the mod's files and sections

    folder: :class:`str`
        The folder the mod was written into

    components: List[:class:`GIMIComponent`]
        The skinned components of the character, in the order of ``hash.json``

    faceDiffuse: Optional[:class:`str`]
        The file name in the mod of the face's diffuse texture, or ``None`` if the mod has none

    faceRegister: :class:`str`
        The register the face's diffuse texture is bound to

    unskinned: List[:class:`str`]
        The names of the components left out because they are not skinned

    Attributes
    ----------
    name: :class:`str`
        The name of the character in the mod's files and sections

    folder: :class:`str`
        The folder the mod was written into

    components: List[:class:`GIMIComponent`]
        The skinned components of the character, in the order of ``hash.json``

    faceDiffuse: Optional[:class:`str`]
        The file name in the mod of the face's diffuse texture, or ``None`` if the mod has none

    faceRegister: :class:`str`
        The register the face's diffuse texture is bound to

    unskinned: List[:class:`str`]
        The names of the components left out because they are not skinned
    """

    def __init__(self, name: str, folder: str, components: List[GIMIComponent], faceDiffuse: Optional[str], faceRegister: str, unskinned: List[str]):
        self.name = name
        self.folder = folder
        self.components = components
        self.faceDiffuse = faceDiffuse
        self.faceRegister = faceRegister
        self.unskinned = unskinned

    @property
    def unbound(self) -> List[str]:
        """
        The objects (``<component><object>``) drawn with the game's own textures, because they have no textures to bind

        :getter: Retrieves the objects
        :type: List[:class:`str`]
        """

        return [f"{component.name}{obj}" for component in self.components for obj in component.objects if not component.boundTextures[obj][2]]

    def getSummary(self) -> List[str]:
        """
        Describes the mod: its components, objects, textures and what was left out

        Returns
        -------
        List[:class:`str`]
            The lines of the description
        """

        lines = []
        for component in self.components:
            triangles = ", ".join(f"{obj} {component.indices[obj].size // 3} triangles from index {first}" for obj, first in zip(component.objects, component.firstIndices))
            lines.append(f"{self.name}{component.name}: {component.vertexCount} vertices (texcoord stride {component.strides[GIMIBuffers.Texcoord]}); {triangles}")

            drawn = []
            for obj in component.objects:
                sourceComponent, sourceObj, bound = component.boundTextures[obj]
                if (bound):
                    borrowed = "" if ((sourceComponent, sourceObj) == (component.name, obj)) else f" <- {sourceComponent}{sourceObj}"
                    drawn.append(f"{obj} {'/'.join(bound)}{borrowed}")
            lines.append("  textures: " + (", ".join(drawn) or "none"))

        if (self.faceDiffuse):
            lines.append(f"  face: {self.faceDiffuse} on {self.faceRegister}")
        if (self.unskinned):
            lines.append(f"  skipped, unskinned (no blend_vb): {', '.join(self.unskinned)}")

        unbound = self.unbound
        if (unbound):
            lines.append(f"  NO textures bound (geometry only, no fix call): {', '.join(unbound)} -- point them at another component's textures")

        lines.append(f"  written to {self.folder}")
        return lines
##### EndScript
