##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Dict, Any, List, Tuple, Optional
##### EndExtImports


##### LocalImports
from .WWMIDrawRange import WWMIDrawRange
from .WWMIBlendRemap import WWMIBlendRemap
from .WWMIShapeKeys import WWMIShapeKeys
from ...constants.WWMIBuffers import WWMIBuffers
##### EndLocalImports


##### Script
class WWMIIdentityMod():
    """
    Class for a generated WWMI identity mod: what was written, and the numbers that show whether it
    reads the character the way the game does

    Parameters
    ----------
    name: :class:`str`
        The name of the character

    folder: :class:`str`
        The folder the mod was written into

    metadata: Dict[:class:`str`, Any]
        The asset folder's ``Metadata.json``

    components: List[:class:`WWMIDrawRange`]
        The components of the character, in order

    shapeKeys: :class:`WWMIShapeKeys`
        The shape keys of the mod

    blendRemaps: List[:class:`WWMIBlendRemap`]
        The blend remaps of the mod

    weightsPerVertex: :class:`int`
        The number of bone weights of one vertex

    blendStride: :class:`int`
        The number of bytes of one vertex in the Blend buffer

    highestBone: :class:`int`
        The highest merged bone index a vertex refers to

    bufferSizes: Dict[:class:`WWMIBuffers`, :class:`int`]
        The size in bytes of each buffer file written

    textures: List[Tuple[:class:`str`, :class:`str`]]
        The file name of each texture in the mod's ``Textures`` folder and the hash the game binds it under

    Attributes
    ----------
    name: :class:`str`
        The name of the character

    folder: :class:`str`
        The folder the mod was written into

    metadata: Dict[:class:`str`, Any]
        The asset folder's ``Metadata.json``

    components: List[:class:`WWMIDrawRange`]
        The components of the character, in order

    shapeKeys: :class:`WWMIShapeKeys`
        The shape keys of the mod

    blendRemaps: List[:class:`WWMIBlendRemap`]
        The blend remaps of the mod

    weightsPerVertex: :class:`int`
        The number of bone weights of one vertex

    blendStride: :class:`int`
        The number of bytes of one vertex in the Blend buffer

    highestBone: :class:`int`
        The highest merged bone index a vertex refers to

    bufferSizes: Dict[:class:`WWMIBuffers`, :class:`int`]
        The size in bytes of each buffer file written

    textures: List[Tuple[:class:`str`, :class:`str`]]
        The file name of each texture in the mod's ``Textures`` folder and the hash the game binds it under
    """

    def __init__(self, name: str, folder: str, metadata: Dict[str, Any], components: List[WWMIDrawRange], shapeKeys: WWMIShapeKeys,
                 blendRemaps: List[WWMIBlendRemap], weightsPerVertex: int, blendStride: int, highestBone: int,
                 bufferSizes: Dict[WWMIBuffers, int], textures: List[Tuple[str, str]]):
        self.name = name
        self.folder = folder
        self.metadata = metadata
        self.components = components
        self.shapeKeys = shapeKeys
        self.blendRemaps = blendRemaps
        self.weightsPerVertex = weightsPerVertex
        self.blendStride = blendStride
        self.highestBone = highestBone
        self.bufferSizes = bufferSizes
        self.textures = textures

    @property
    def vertexCount(self) -> int:
        """
        The number of vertices of the whole mesh

        :getter: Retrieves the vertex count
        :type: :class:`int`
        """

        return sum(component.vertexCount for component in self.components)

    @property
    def indexCount(self) -> int:
        """
        The number of indices of the whole mesh

        :getter: Retrieves the index count
        :type: :class:`int`
        """

        return sum(component.indexCount for component in self.components)

    @property
    def checksumMatches(self) -> Optional[bool]:
        """
        Whether the shape keys' checksum is the one the asset folder's ``Metadata.json`` records, or ``None`` if it records none

        :getter: Retrieves whether the checksums match
        :type: Optional[:class:`bool`]
        """

        expected = (self.metadata.get("shapekeys") or {}).get("checksum")
        return None if (expected is None) else (self.shapeKeys.checksum == int(expected))

    @property
    def dispatchYMatches(self) -> Optional[bool]:
        """
        Whether the shape keys' dispatch count is the one the asset folder's ``Metadata.json`` records, or ``None`` if it records none

        :getter: Retrieves whether the dispatch counts match
        :type: Optional[:class:`bool`]
        """

        expected = (self.metadata.get("shapekeys") or {}).get("dispatch_y")
        return None if (expected is None) else (self.shapeKeys.dispatchY == int(expected))

    def getSummary(self) -> List[str]:
        """
        Describes the mod: its components, buffers, blend, shape keys and textures

        Returns
        -------
        List[:class:`str`]
            The lines of the description
        """

        metadata = self.metadata
        sk = metadata.get("shapekeys") or {}
        shapeKeys = self.shapeKeys
        vertexCount = self.vertexCount
        indexCount = self.indexCount

        lines = [f"{self.name}: {len(self.components)} components, {vertexCount} vertices, {indexCount} indices ({indexCount // 3} triangles), hash {metadata.get('vb0_hash')}, skeleton cb4 {metadata.get('cb4_hash')}"]
        for component in self.components:
            vgMap = component.entry.get("vg_map") or {}
            vgOffset = int(component.entry.get("vg_offset", 0))
            borrowed = sum(1 for k, v in vgMap.items() if int(v) != vgOffset + int(k))
            lines.append(f"  Component {component.index}: {component.vertexCount} vertices from {component.vertexOffset}, {component.indexCount} indices from {component.indexOffset}, "
                         f"{int(component.entry.get('vg_count', 0))} bones at merged slot {vgOffset}" + (f" ({borrowed} of them another component's)" if (vgMap) else ""))

        lines.append("  buffers: " + ", ".join(f"{buffer.value} {self.bufferSizes[buffer]} B" for buffer in WWMIBuffers if buffer in self.bufferSizes))
        lines.append(f"  blend: {self.weightsPerVertex} bones a vertex ({self.blendStride} B), highest merged bone {self.highestBone}; "
                     + (f"blend remaps for components {', '.join(f'{r.componentIndex} (remap {r.remapId}, {r.boneCount} bones)' for r in self.blendRemaps)}" if self.blendRemaps else "no blend remap needed"))

        keys = shapeKeys.keys
        keyRange = f"{keys[0]}-{keys[-1]}" if (keys) else "none"
        checksumMatches = self.checksumMatches
        dispatchYMatches = self.dispatchYMatches
        lines.append(f"  shape keys: {len(keys)} keys ({keyRange}), {shapeKeys.entryCount} (key, vertex) entries; first offsets {shapeKeys.offsets[:4].tolist()} sum {shapeKeys.checksum} "
                     f"vs Metadata checksum {sk.get('checksum')} ({'OK' if checksumMatches else 'MISMATCH'}); dispatch_y {shapeKeys.dispatchY} vs {sk.get('dispatch_y')} "
                     f"({'OK' if dispatchYMatches else 'MISMATCH'}); entries vs Metadata {sk.get('vertex_count')}")
        lines.append(f"  textures: {len(self.textures)}" + ("" if self.textures else " (none)"))
        lines.append(f"  written to {self.folder}")
        return lines
##### EndScript
