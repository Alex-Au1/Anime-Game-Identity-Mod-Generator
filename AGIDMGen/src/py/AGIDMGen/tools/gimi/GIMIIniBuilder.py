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
from ...constants.GIMIBuffers import GIMIBuffers
from ...constants.GIMITextureLayouts import GIMITextureLayouts
from ...model.gimi.GIMIComponent import GIMIComponent
##### EndLocalImports


##### Script
class GIMIIniBuilder():
    """
    Writes the ``.ini`` of a GIMI identity mod, in the shape GIMI generates

    Parameters
    ----------
    name: :class:`str`
        The name of the character in the mod's files and sections

    components: List[:class:`GIMIComponent`]
        The skinned components of the character, with their bound textures

    source: :class:`str`
        What the mod was generated from, as the end of the sentence "the game's own model out of ..." (eg. ``its asset folder (Yelan)``)

    faceDiffuse: Optional[:class:`str`]
        The file name in the mod of the face's diffuse texture, or ``None`` if the mod has none :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    faceHash: Optional[:class:`str`]
        The hash the game binds the face's diffuse texture under, or ``None`` if it is not known :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    faceRegister: :class:`str`
        The register the face's diffuse texture is bound to :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``"ps-t0"``

    includeFix: :class:`bool`
        Whether an object that binds textures runs the ``ORFix`` command list of its layout :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``True``

    Attributes
    ----------
    name: :class:`str`
        The name of the character in the mod's files and sections

    components: List[:class:`GIMIComponent`]
        The skinned components of the character, with their bound textures

    source: :class:`str`
        What the mod was generated from, as the end of the sentence "the game's own model out of ..." (eg. ``its asset folder (Yelan)``)

    faceDiffuse: Optional[:class:`str`]
        The file name in the mod of the face's diffuse texture, or ``None`` if the mod has none

    faceHash: Optional[:class:`str`]
        The hash the game binds the face's diffuse texture under, or ``None`` if it is not known

    faceRegister: :class:`str`
        The register the face's diffuse texture is bound to

    includeFix: :class:`bool`
        Whether an object that binds textures runs the ``ORFix`` command list of its layout
    """

    def __init__(self, name: str, components: List[GIMIComponent], source: str, faceDiffuse: Optional[str] = None,
                 faceHash: Optional[str] = None, faceRegister: str = "ps-t0", includeFix: bool = True):
        self.name = name
        self.components = components
        self.source = source
        self.faceDiffuse = faceDiffuse
        self.faceHash = faceHash
        self.faceRegister = faceRegister
        self.includeFix = includeFix

    def build(self) -> str:
        """
        Writes the text of the ``.ini``

        Returns
        -------
        :class:`str`
            The text, with ``\\n`` line endings
        """

        name = self.name
        L = [f"; {name}", "", "; Constants -------------------------", "", "; Overrides -------------------------", ""]

        for component in self.components:
            comp = component.name
            entry = component.entry
            L += [f"[TextureOverride{name}{comp}Position]", f"hash = {entry['position_vb']}", f"vb0 = Resource{name}{comp}Position", ""]
            L += [f"[TextureOverride{name}{comp}Blend]", f"hash = {entry['blend_vb']}", f"vb1 = Resource{name}{comp}Blend", "handling = skip", f"draw = {component.vertexCount},0", ""]
            L += [f"[TextureOverride{name}{comp}Texcoord]", f"hash = {entry['texcoord_vb']}", f"vb1 = Resource{name}{comp}Texcoord", ""]
            L += [f"[TextureOverride{name}{comp}VertexLimitRaise]", f"hash = {entry['draw_vb']}", ""]
            L += [f"[TextureOverride{name}{comp}IB]", f"hash = {entry['ib']}", "handling = skip", "drawindexed = auto", ""]

            for obj, first in zip(component.objects, component.firstIndices):
                L += [f"[TextureOverride{name}{comp}{obj}]", f"hash = {entry['ib']}", f"match_first_index = {first}", f"ib = Resource{name}{comp}{obj}IB"]
                sourceComponent, sourceObj, bound = component.boundTextures[obj]
                layout = GIMITextureLayouts.NormalMap if ("NormalMap" in bound) else GIMITextureLayouts.Plain

                for register, kind in layout.registers:
                    if (kind in bound):
                        L.append(f"{register} = Resource{name}{sourceComponent}{sourceObj}{kind}")

                # no textures to bind, so no fix call either: ORFix / NNFix re-slot whatever is bound,
                #   and the game's own textures are already in the registers the shader wants
                if (bound and self.includeFix):
                    L.append(f"run = {layout.fixCommand}")
                L.append("")

        if (self.faceDiffuse and self.faceHash):
            L += [f"[TextureOverride{name}FaceHeadDiffuse]", f"hash = {self.faceHash}", f"{self.faceRegister} = Resource{name}FaceHeadDiffuse", ""]

        L += ["", "; CommandList -----------------------", "", "; Resources -------------------------", ""]
        for component in self.components:
            for buffer in GIMIBuffers:
                L += [f"[Resource{name}{component.name}{buffer.value}]", "type = Buffer", f"stride = {component.strides[buffer]}", f"filename = {name}{component.name}{buffer.value}.buf", ""]

        for component in self.components:
            for obj in component.objects:
                L += [f"[Resource{name}{component.name}{obj}IB]", "type = Buffer", "format = DXGI_FORMAT_R32_UINT", f"filename = {name}{component.name}{obj}.ib", ""]

        for component in self.components:
            for obj in component.objects:
                for kind, fileName in component.textures.get(obj, {}).items():
                    L += [f"[Resource{name}{component.name}{obj}{kind}]", f"filename = {fileName}", ""]

        if (self.faceDiffuse):
            L += [f"[Resource{name}FaceHeadDiffuse]", f"filename = {self.faceDiffuse}", ""]

        L += ["", f"; the identity mod of {name}: the game's own model out of {self.source}, built by AGIDMGen", ""]
        return "\n".join(L)
##### EndScript
