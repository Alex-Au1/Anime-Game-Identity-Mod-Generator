##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Any, Dict, Optional, Tuple
##### EndExtImports


##### LocalImports
from ...constants.GIMITextureLayouts import GIMITextureLayouts
from ...exceptions.Error import Error
from ...exceptions.BadAssetData import BadAssetData
##### EndLocalImports


##### Script
class GIMITextureSource():
    """
    Class for where a component with no textures of its own reads its textures from: one object of
    another component (eg. YelanTranquil's Bang and Eye read her Body's slot A)

    Parameters
    ----------
    component: :class:`str`
        The name of the component that lends its textures

    obj: :class:`str`
        The name of the object of ``component`` whose textures are read

    layout: Optional[:class:`GIMITextureLayouts`]
        The layout the BORROWING component binds the textures in, which depends on the borrower's shader. If this value is ``None``, the textures are bound as they are: the normal map layout if the lender has a normal map :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    component: :class:`str`
        The name of the component that lends its textures

    obj: :class:`str`
        The name of the object of :attr:`component` whose textures are read

    layout: Optional[:class:`GIMITextureLayouts`]
        The layout the borrowing component binds the textures in
    """

    def __init__(self, component: str, obj: str, layout: Optional[GIMITextureLayouts] = None):
        self.component = component
        self.obj = obj
        self.layout = layout

    def __eq__(self, other) -> bool:
        if (not isinstance(other, GIMITextureSource)):
            return NotImplemented
        return (self.component, self.obj, self.layout) == (other.component, other.obj, other.layout)

    def __repr__(self) -> str:
        return f"GIMITextureSource({self.component!r}, {self.obj!r}, {self.layout})"

    def toDict(self) -> Dict[str, Any]:
        """
        Writes the source as a ``hash.json`` entry's ``texture_sources`` records it

        Returns
        -------
        Dict[:class:`str`, Any]
            ``{"component": ..., "object": ..., "layout": "normalMap" | "plain" | None}``
        """

        layout = {GIMITextureLayouts.NormalMap: "normalMap", GIMITextureLayouts.Plain: "plain"}.get(self.layout)
        return {"component": self.component, "object": self.obj, "layout": layout}

    @classmethod
    def fromDict(cls, data: Dict[str, Any]):
        """
        Reads a source as a ``hash.json`` entry's ``texture_sources`` records it (see :meth:`toDict`)

        Parameters
        ----------
        data: Dict[:class:`str`, Any]
            The record

        Raises
        ------
        :class:`BadAssetData`
            If the record is not a texture source

        Returns
        -------
        :class:`GIMITextureSource`
            The source
        """

        layouts = {None: None, "normalMap": GIMITextureLayouts.NormalMap, "plain": GIMITextureLayouts.Plain}
        if (not isinstance(data, dict) or "component" not in data or "object" not in data or data.get("layout") not in layouts):
            raise BadAssetData(f"{data!r} is not a texture source: {{\"component\": ..., \"object\": ..., \"layout\": \"normalMap\" | \"plain\" | null}}")
        return cls(data["component"], data["object"], layouts[data.get("layout")])

    @classmethod
    def parse(cls, txt: str) -> Tuple[str, "GIMITextureSource"]:
        """
        Reads a texture source written as ``<borrower>=<component>:<object>[:normalMap|plain]`` (eg. ``Bang=Body:A`` or ``Eye=Body:A:plain``)

        Parameters
        ----------
        txt: :class:`str`
            The text

        Raises
        ------
        :class:`Error`
            If the text is not in that form

        Returns
        -------
        Tuple[:class:`str`, :class:`GIMITextureSource`]
            The name of the borrowing component, and where it reads its textures from
        """

        usage = f"a texture source is <component>=<component>:<object>[:normalMap|plain], not {txt!r}"
        borrower, separator, source = txt.partition("=")
        if (not separator or ":" not in source):
            raise Error(usage)

        fields = source.split(":")
        if (len(fields) not in (2, 3)):
            raise Error(usage)

        layout = None
        if (len(fields) == 3):
            layouts = {"normalMap": GIMITextureLayouts.NormalMap, "plain": GIMITextureLayouts.Plain}
            if (fields[2] not in layouts):
                raise Error(f"a texture source's layout is normalMap or plain, not {fields[2]!r}")
            layout = layouts[fields[2]]

        return borrower, cls(fields[0], fields[1], layout)
##### EndScript
