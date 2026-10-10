##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Dict, Any, List, Tuple
##### EndExtImports


##### LocalImports
from ...constants.WWMIBuffers import WWMIBuffers
from ...model.wwmi.WWMIDrawRange import WWMIDrawRange
from ...model.wwmi.WWMIBlendRemap import WWMIBlendRemap
##### EndLocalImports


##### Script
class WWMIIniBuilder():
    """
    Writes the ``mod.ini`` of a WWMI identity mod, in the WWMI BETA-2 layout that WWMI Tools 1.3.4 generates
    (for WWMI 0.91 or newer)

    Parameters
    ----------
    name: :class:`str`
        The name of the character

    author: :class:`str`
        The mod author that WWMI shows

    metadata: Dict[:class:`str`, Any]
        The asset folder's ``Metadata.json``

    components: List[:class:`WWMIDrawRange`]
        The components of the character, in order

    shapeKeyCount: :class:`int`
        The number of (shape key, vertex) entries of the mod's shape keys

    textures: List[Tuple[:class:`str`, :class:`str`]]
        The file name of each texture in the mod's ``Textures`` folder and the hash the game binds it under

    blendStride: :class:`int`
        The number of bytes of one vertex in the Blend buffer :raw-html:`<br />` :raw-html:`<br />`

        **Default**: 8

    blendRemaps: List[:class:`WWMIBlendRemap`]
        The blend remaps of the mod, if its merged skeleton needs them :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``[]``

    weightsPerVertex: :class:`int`
        The number of bone weights of one vertex :raw-html:`<br />` :raw-html:`<br />`

        **Default**: 4

    Attributes
    ----------
    name: :class:`str`
        The name of the character

    author: :class:`str`
        The mod author that WWMI shows

    metadata: Dict[:class:`str`, Any]
        The asset folder's ``Metadata.json``

    components: List[:class:`WWMIDrawRange`]
        The components of the character, in order

    shapeKeyCount: :class:`int`
        The number of (shape key, vertex) entries of the mod's shape keys

    textures: List[Tuple[:class:`str`, :class:`str`]]
        The file name of each texture in the mod's ``Textures`` folder and the hash the game binds it under

    blendStride: :class:`int`
        The number of bytes of one vertex in the Blend buffer

    blendRemaps: List[:class:`WWMIBlendRemap`]
        The blend remaps of the mod

    weightsPerVertex: :class:`int`
        The number of bone weights of one vertex
    """

    def __init__(self, name: str, author: str, metadata: Dict[str, Any], components: List[WWMIDrawRange], shapeKeyCount: int,
                 textures: List[Tuple[str, str]], blendStride: int = 8, blendRemaps: List[WWMIBlendRemap] = None, weightsPerVertex: int = 4):
        self.name = name
        self.author = author
        self.metadata = metadata
        self.components = components
        self.shapeKeyCount = shapeKeyCount
        self.textures = textures
        self.blendStride = blendStride
        self.blendRemaps = [] if (blendRemaps is None) else blendRemaps
        self.weightsPerVertex = weightsPerVertex

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

    def _buildBlendRemapLines(self) -> List[str]:
        # the blend remap's own sections (WWMI Tools' merged.ini.j2 for blend_remap_count > 0)
        L = ["[ResourceMergedSkeletonRemap]", "[ResourceExtraMergedSkeletonRemap]", "", "[ResourceBlendBufferOverride]", "[ResourceExtraMergedSkeletonOverride]",
             "[ResourceMergedSkeletonOverride]", "", "[ResourceRemappedBlendBufferRW]", "[ResourceRemappedSkeletonRW]", "[ResourceExtraRemappedSkeletonRW]", ""]

        for remap in self.blendRemaps:
            i = remap.componentIndex
            L += [f"[ResourceRemappedBlendBufferComponent{i}]", f"[ResourceRemappedSkeletonComponent{i}]", f"[ResourceExtraRemappedSkeletonComponent{i}]", ""]

        L += ["[CommandListInitializeBlendRemaps]", "local $blend_remaps_initialized", "if !$blend_remaps_initialized",
              "    ResourceRemappedSkeletonRW = copy ResourceMergedSkeletonRW", "    ResourceExtraRemappedSkeletonRW = copy ResourceExtraMergedSkeletonRW",
              "    $\\WWMIv1\\custom_vertex_count = $mesh_vertex_count", f"    $\\WWMIv1\\weights_per_vertex_count = {self.weightsPerVertex}",
              "    cs-t34 = ref ResourceBlendRemapReverseBuffer", "    cs-t35 = ref ResourceBlendRemapVertexVGBuffer"]

        for remap in self.blendRemaps:
            i = remap.componentIndex
            L += [f"    $\\WWMIv1\\blend_remap_id = {remap.remapId}", "    ResourceRemappedBlendBufferRW = copy ResourceBlendBufferNoStride", "    cs-u4 = ref ResourceRemappedBlendBufferRW",
                  "    run = CustomShader\\WWMIv1\\BlendRemapper", f"    ResourceRemappedBlendBufferComponent{i} = copy ResourceRemappedBlendBufferRW",
                  f"    ResourceRemappedBlendBufferComponent{i} = copy_desc ResourceBlendBuffer"]

        L += ["    $blend_remaps_initialized = 1", "endif", ""]
        L += ["[CommandListRemapMergedSkeleton]", "ResourceMergedSkeletonRemap = copy ResourceMergedSkeletonRW", "ResourceExtraMergedSkeletonRemap = copy ResourceExtraMergedSkeletonRW",
              "cs-t37 = ResourceBlendRemapForwardBuffer"]

        for remap in self.blendRemaps:
            i = remap.componentIndex
            L += [f"$\\WWMIv1\\blend_remap_id = {remap.remapId}", f"$\\WWMIv1\\vg_count = {remap.boneCount}", "cs-t38 = ResourceMergedSkeletonRemap", "cs-u5 = ResourceRemappedSkeletonRW",
                  "run = CustomShader\\WWMIv1\\SkeletonRemapper", f"ResourceRemappedSkeletonComponent{i} = copy ResourceRemappedSkeletonRW",
                  "cs-t38 = ResourceExtraMergedSkeletonRemap", "cs-u5 = ResourceExtraRemappedSkeletonRW", "run = CustomShader\\WWMIv1\\SkeletonRemapper",
                  f"ResourceExtraRemappedSkeletonComponent{i} = copy ResourceExtraRemappedSkeletonRW"]

        return L + [""]

    def build(self) -> str:
        """
        Writes the text of the ``mod.ini``

        Returns
        -------
        :class:`str`
            The text, with ``\\n`` line endings
        """

        metadata = self.metadata
        sk = metadata.get("shapekeys") or {}
        remaps = self.blendRemaps
        remapped = {remap.componentIndex for remap in remaps}
        name = self.name

        L = []
        L += ["; WWMI BETA-2 INI", "", "; Mod State -------------------------", "", "[Constants]",
              "global $required_wwmi_version = 0.91", f"global $object_guid = {self.indexCount}", f"global $mesh_vertex_count = {self.vertexCount}",
              f"global $shapekey_vertex_count = {self.shapeKeyCount}", "global $mod_id = -1000", "global $state_id = 0", "global $mod_enabled = 0", "global $object_detected = 0", ""]
        L += ["[Present]", "if $object_detected", "    if $mod_enabled", "        post $object_detected = 0"] + (["        run = CommandListInitializeBlendRemaps"] if remaps else []) + [
              "        run = CommandListUpdateMergedSkeleton", "    else",
              "        if $mod_id == -1000", "            run = CommandListRegisterMod", "        endif", "    endif", "endif", ""]
        L += ["[CommandListRegisterMod]", "$\\WWMIv1\\required_wwmi_version = $required_wwmi_version", "$\\WWMIv1\\object_guid = $object_guid",
              "Resource\\WWMIv1\\ModName = ref ResourceModName", "Resource\\WWMIv1\\ModAuthor = ref ResourceModAuthor", "Resource\\WWMIv1\\ModDesc = ref ResourceModDesc",
              "Resource\\WWMIv1\\ModLink = ref ResourceModLink", "Resource\\WWMIv1\\ModLogo = ref ResourceModLogo", "run = CommandList\\WWMIv1\\RegisterMod",
              "$mod_id = $\\WWMIv1\\mod_id", "if $mod_id >= 0", "    $mod_enabled = 1", "endif", ""]
        L += ["[CommandListUpdateMergedSkeleton]", "if $state_id", "    $state_id = 0", "else", "    $state_id = 1", "endif",
              "ResourceMergedSkeleton = copy ResourceMergedSkeletonRW", "ResourceExtraMergedSkeleton = copy ResourceExtraMergedSkeletonRW"] + (
              ["run = CommandListRemapMergedSkeleton"] if remaps else []) + [""]

        if (remaps):
            L += self._buildBlendRemapLines()

        L += ["; Resources: Mod Info -------------------------", "", "[ResourceModName]", "type = Buffer", f'data = "{name} Identity"', "",
              "[ResourceModAuthor]", "type = Buffer", f'data = "{self.author}"', "", "[ResourceModDesc]", "type = Buffer",
              f'data = "The identity mod of {name}: the game\'s own model out of WWMI-Assets, built by AGIDMGen"', "",
              "[ResourceModLink]", "; type = Buffer", '; data = "Empty Mod Link"', "", "[ResourceModLogo]", "; filename = Textures/Logo.dds", ""]
        L += ["; Shading: Draw Call Stacks Processing -------------------------", "", "[TextureOverrideMarkBoneDataCB]", f"hash = {metadata['cb4_hash']}",
              "match_priority = 0", "filter_index = 3381.7777", ""]
        L += ["[CommandListMergeSkeleton]", "$\\WWMIv1\\custom_mesh_scale = 1.00", "cs-cb8 = ref vs-cb4", "cs-u6 = ResourceMergedSkeletonRW",
              "run = CustomShader\\WWMIv1\\SkeletonMerger", "cs-cb8 = ref vs-cb3", "cs-u6 = ResourceExtraMergedSkeletonRW", "run = CustomShader\\WWMIv1\\SkeletonMerger", ""]
        L += ["[CommandListTriggerResourceOverrides]"] + [f"CheckTextureOverride = ps-t{i}" for i in range(8)] + ["CheckTextureOverride = vs-cb3", "CheckTextureOverride = vs-cb4", ""]
        L += ["[CommandListOverrideSharedResources]", "ResourceBypassVB0 = ref vb0", "ib = ResourceIndexBuffer", "vb0 = ResourcePositionBuffer", "vb1 = ResourceVectorBuffer",
              "vb2 = ResourceTexcoordBuffer", "vb3 = ResourceColorBuffer"]

        if (not remaps):
            L += ["vb4 = ResourceBlendBuffer", "if vs-cb3 == 3381.7777", "    vs-cb3 = ResourceExtraMergedSkeleton", "endif",
                  "if vs-cb4 == 3381.7777", "    vs-cb4 = ResourceMergedSkeleton", "endif", ""]
        else:
            # the 1.3.x form; WWMI Tools 1.7.3 nests the vs-cb3 check inside the vs-cb4 one (with an elif
            #   binding vs-cb3 to the MAIN skeleton), for the plain branch too -- this keeps the form of its
            #   template, which renders on WWMI 1.00
            L += ["if ResourceBlendBufferOverride === null", "    vb4 = ResourceBlendBuffer", "    if vs-cb3 == 3381.7777", "        vs-cb3 = ref ResourceExtraMergedSkeleton", "    endif",
                  "    if vs-cb4 == 3381.7777", "        vs-cb4 = ref ResourceMergedSkeleton", "    endif", "else", "    vb4 = ref ResourceBlendBufferOverride",
                  "    if vs-cb3 == 3381.7777", "        vs-cb3 = ref ResourceExtraMergedSkeletonOverride", "    endif", "    if vs-cb4 == 3381.7777",
                  "        vs-cb4 = ref ResourceMergedSkeletonOverride", "    endif", "endif", ""]

        L += ["[CommandListCleanupSharedResources]", "vb0 = ref ResourceBypassVB0"] + (
              ["if ResourceBlendBufferOverride !== null", "    ResourceBlendBufferOverride = null", "    ResourceMergedSkeletonOverride = null",
               "    ResourceExtraMergedSkeletonOverride = null", "endif"] if remaps else []) + [""]

        for component in self.components:
            i = component.index
            L += [f"[TextureOverrideComponent{i}]", f"hash = {metadata['vb0_hash']}", f"match_first_index = {component.indexOffset}", f"match_index_count = {component.indexCount}",
                  "$object_detected = 1", "if $mod_enabled", f"    local $state_id_{i}", f"    if $state_id_{i} != $state_id", f"        $state_id_{i} = $state_id",
                  f"        $\\WWMIv1\\vg_offset = {int(component.entry['vg_offset'])}", f"        $\\WWMIv1\\vg_count = {int(component.entry['vg_count'])}",
                  "        run = CommandListMergeSkeleton", "    endif", "    if ResourceMergedSkeleton !== null", "        handling = skip"] + (
                  [f"        ResourceBlendBufferOverride = ref ResourceRemappedBlendBufferComponent{i}", f"        ResourceMergedSkeletonOverride = ref ResourceRemappedSkeletonComponent{i}",
                   f"        ResourceExtraMergedSkeletonOverride = ref ResourceExtraRemappedSkeletonComponent{i}"] if i in remapped else []) + [
                  "        run = CommandListTriggerResourceOverrides", "        run = CommandListOverrideSharedResources", f"        ; Draw Component {i}",
                  f"        drawindexed = {component.indexCount}, {component.indexOffset}, 0", "        run = CommandListCleanupSharedResources", "    endif", "endif", ""]

        L += ["; Shading: Textures -------------------------", ""]
        for n, (fileName, textureHash) in enumerate(self.textures):
            L += [f"[ResourceTexture{n}]", f"filename = Textures/{fileName}", "", f"[TextureOverrideTexture{n}]", f"hash = {textureHash}", "match_priority = 0",
                  "if $object_detected", f"    this = ResourceTexture{n}", "endif", ""]

        L += ["; Skinning: Shape Keys Override -------------------------", "", "[TextureOverrideShapeKeyOffsets]", f"hash = {sk.get('offsets_hash', '')}", "match_priority = 0",
              "override_byte_stride = 24", "override_vertex_count = $mesh_vertex_count", "", "[TextureOverrideShapeKeyScale]", f"hash = {sk.get('scale_hash', '')}", "match_priority = 0",
              "override_byte_stride = 4", "override_vertex_count = $mesh_vertex_count", ""]
        L += ["[CommandListSetupShapeKeys]", f"$\\WWMIv1\\shapekey_checksum = {sk.get('checksum', 0)}", "cs-t33 = ResourceShapeKeyOffsetBuffer", "cs-u5 = ResourceCustomShapeKeyValuesRW",
              "cs-u6 = ResourceShapeKeyCBRW", "run = CustomShader\\WWMIv1\\ShapeKeyOverrider", ""]
        L += ["[CommandListLoadShapeKeys]", "$\\WWMIv1\\shapekey_vertex_count = $shapekey_vertex_count", "cs-t0 = ResourceShapeKeyVertexIdBuffer", "cs-t1 = ResourceShapeKeyVertexOffsetBuffer",
              "cs-u6 = ResourceShapeKeyCBRW", "run = CustomShader\\WWMIv1\\ShapeKeyLoader", ""]
        L += ["[TextureOverrideShapeKeyLoaderCallback]", f"hash = {sk.get('offsets_hash', '')}", "match_priority = 0", "if $mod_enabled",
              "    if cs == 3381.3333 && ResourceMergedSkeleton !== null", "        handling = skip", "        run = CommandListSetupShapeKeys", "        run = CommandListLoadShapeKeys",
              "    endif", "endif", ""]
        L += ["[CommandListMultiplyShapeKeys]", "$\\WWMIv1\\custom_vertex_count = $mesh_vertex_count", "run = CustomShader\\WWMIv1\\ShapeKeyMultiplier", ""]
        L += ["[TextureOverrideShapeKeyMultiplierCallback]", f"hash = {sk.get('offsets_hash', '')}", "match_priority = 0", "if $mod_enabled",
              "    if cs == 3381.4444 && ResourceMergedSkeleton !== null", "        handling = skip", "        run = CommandListMultiplyShapeKeys", "    endif", "endif", ""]
        L += ["; Resources: Shape Keys Override -------------------------", "", "[ResourceShapeKeyCBRW]", "type = RWBuffer", "format = R32G32B32A32_UINT", "array = 66", "",
              "[ResourceCustomShapeKeyValuesRW]", "type = RWBuffer", "format = R32G32B32A32_FLOAT", "array = 32", ""]

        # 256 bones, 3 float4s each; 512 with a blend remap
        skeletonArray = 1536 if remaps else 768
        L += ["; Resources: Skeleton Override -------------------------", "", "[ResourceMergedSkeleton]", "", "[ResourceMergedSkeletonRW]", "type = RWBuffer",
              "format = R32G32B32A32_FLOAT", f"array = {skeletonArray}", "", "[ResourceExtraMergedSkeleton]", "", "[ResourceExtraMergedSkeletonRW]", "type = RWBuffer",
              "format = R32G32B32A32_FLOAT", f"array = {skeletonArray}", ""]
        L += ["; Resources: Buffers -------------------------", "", "[ResourceBypassVB0]", ""]

        resources = [("ResourceIndexBuffer", "DXGI_FORMAT_R32_UINT", 12, WWMIBuffers.Index), ("ResourcePositionBuffer", "DXGI_FORMAT_R32G32B32_FLOAT", 12, WWMIBuffers.Position),
                     ("ResourceBlendBuffer", "DXGI_FORMAT_R8_UINT", self.blendStride, WWMIBuffers.Blend), ("ResourceVectorBuffer", "DXGI_FORMAT_R8G8B8A8_SNORM", 8, WWMIBuffers.Vector),
                     ("ResourceColorBuffer", "DXGI_FORMAT_R8G8B8A8_UNORM", 4, WWMIBuffers.Color), ("ResourceTexCoordBuffer", "DXGI_FORMAT_R16G16_FLOAT", 16, WWMIBuffers.TexCoord),
                     ("ResourceShapeKeyOffsetBuffer", "DXGI_FORMAT_R32G32B32A32_UINT", 16, WWMIBuffers.ShapeKeyOffset), ("ResourceShapeKeyVertexIdBuffer", "DXGI_FORMAT_R32_UINT", 4, WWMIBuffers.ShapeKeyVertexId),
                     ("ResourceShapeKeyVertexOffsetBuffer", "DXGI_FORMAT_R16_FLOAT", 2, WWMIBuffers.ShapeKeyVertexOffset)]

        if (remaps):
            # no stride on these: a compute shader cannot address a Buffer declared with one
            resources += [("ResourceBlendRemapVertexVGBuffer", "DXGI_FORMAT_R16_UINT", None, WWMIBuffers.BlendRemapVertexVG),
                          ("ResourceBlendRemapForwardBuffer", "DXGI_FORMAT_R16_UINT", None, WWMIBuffers.BlendRemapForward),
                          ("ResourceBlendRemapReverseBuffer", "DXGI_FORMAT_R16_UINT", None, WWMIBuffers.BlendRemapReverse)]

        for section, fmt, stride, buffer in resources:
            L += [f"[{section}]", "type = Buffer", f"format = {fmt}"] + ([f"stride = {stride}"] if stride is not None else []) + [f"filename = Meshes/{buffer.value}", ""]
            if (buffer == WWMIBuffers.Blend and remaps):
                L += ["[ResourceBlendBufferNoStride]", "type = Buffer", f"format = {fmt}", f"filename = Meshes/{buffer.value}", ""]

        L += ["; Autogenerated -------------------------", "", f"; This mod.ini is the IDENTITY mod of {name}, generated by AGIDMGen (Anime Game Identity Mod Generator) from WWMI-Assets, "
              "in the shape WWMI Tools 1.3.4 generates (WWMI v0.9.1+)", ""]

        return "\n".join(L)
##### EndScript
