##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import os
import re
import json
import shutil
import tempfile
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from FixRaidenBoss2 import BaseLogger, Model
##### EndExtImports


##### LocalImports
from ..ModDownloader import ModDownloader
from ...constants.ModLoaders import ModLoaders
from .WWMIIniBuilder import WWMIIniBuilder
from ...constants.FileEncodings import FileEncodings
from ...constants.WWMIBuffers import WWMIBuffers, WWMIBlendRemapBuffers, WWMIShapeKeySlots, WWMIBlendRemapSize, WWMIBlendIndexLimit, WWMIDownloadNames, WWMIDownloadTextureSuffix
from ...exceptions.BadAssetData import BadAssetData
from ...model.wwmi.WWMIComponent import WWMIComponent
from ...model.wwmi.WWMIDrawRange import WWMIDrawRange
from ...model.wwmi.WWMIMesh import WWMIMesh
from ...model.wwmi.WWMIBlendRemap import WWMIBlendRemap
from ...model.wwmi.WWMIShapeKeys import WWMIShapeKeys
from ...model.wwmi.WWMIIdentityMod import WWMIIdentityMod
##### EndLocalImports


##### Script
#: The file names of an asset folder's textures: ``Components-<components> t=<hash>.dds``, named by the components that use them and the hash the game binds them under
WWMITexturePattern = re.compile(r"^Components-[0-9-]+ t=(?P<hash>[0-9a-fA-F]{8})\.dds$")


class WWMIIdentityModGenerator(Model):
    """
    Generates the identity mod of a WuWa character: the game's own model, written out as a
    WWMI mod from the character's asset folder

    The asset folder is laid out as `WWMI-Assets <https://github.com/SpectrumQT/WWMI-Assets>`_'s
    ``PlayerCharacterData/<Name>`` folders are:

    - ``Metadata.json``, with the mesh's hashes, its components and the layout of the mod's buffers (``export_format``)
    - ``Component N.fmt``, ``Component N.vb`` and ``Component N.ib`` for each component
    - the textures, named ``Components-<components> t=<hash>.dds``

    The mod is written as:

    - ``mod.ini``
    - ``Meshes/``: the buffers of :class:`WWMIBuffers` (the blend remap buffers only for a character whose merged skeleton needs them)
    - ``Textures/``: every texture of the asset folder

    Examples
    --------
    .. code-block:: python
        :linenos:

        import AGIDMGen as IDMG

        generator = IDMG.WWMIIdentityModGenerator()
        mod = generator.generate("WWMI-Assets/PlayerCharacterData/Sanhua", "Mods/SanhuaIdentity")
        print("\\n".join(mod.getSummary()))

    Parameters
    ----------
    author: :class:`str`
        The mod author that WWMI shows :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``"Anime Game Remap"``

    includeTextures: :class:`bool`
        Whether to copy the textures into the mod :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``True``

    useVgMap: :class:`bool`
        Whether to write each bone index through its component's ``vg_map`` (the bone indices every real mod uses), rather than as the component's ``vg_offset`` plus the local index (which points into the merged skeleton's duplicate slots) :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``True``

    logger: Optional[:class:`BaseLogger`]
        Where to report what is done. If this value is ``None``, nothing is reported :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    author: :class:`str`
        The mod author that WWMI shows

    includeTextures: :class:`bool`
        Whether to copy the textures into the mod

    useVgMap: :class:`bool`
        Whether to write each bone index through its component's ``vg_map``
    """

    def __init__(self, author: str = "Anime Game Remap", includeTextures: bool = True, useVgMap: bool = True, logger: Optional[BaseLogger] = None):
        super().__init__(logger = logger)
        self.author = author
        self.includeTextures = includeTextures
        self.useVgMap = useVgMap

    @classmethod
    def readMetadata(cls, assetsFolder: str) -> Dict[str, Any]:
        """
        Reads the ``Metadata.json`` of an asset folder

        Parameters
        ----------
        assetsFolder: :class:`str`
            The asset folder

        Raises
        ------
        :class:`BadAssetData`
            If the asset folder has no ``Metadata.json``

        Returns
        -------
        Dict[:class:`str`, Any]
            The metadata
        """

        path = os.path.join(assetsFolder, "Metadata.json")
        if (not os.path.isfile(path)):
            raise BadAssetData(f"'{path}' is missing")

        with open(path, "r", encoding = FileEncodings.UTF8.value) as f:
            return json.load(f)

    @classmethod
    def readComponents(cls, assetsFolder: str, metadata: Dict[str, Any]) -> List[WWMIComponent]:
        """
        Reads the components of an asset folder, and checks that they lie end to end in the order ``Metadata.json`` lists them

        Parameters
        ----------
        assetsFolder: :class:`str`
            The asset folder

        metadata: Dict[:class:`str`, Any]
            The asset folder's ``Metadata.json``

        Raises
        ------
        :class:`BadAssetData`
            If ``Metadata.json`` lists no components, a component's files are missing or wrong, or the components' offsets or totals disagree with ``Metadata.json``

        Returns
        -------
        List[:class:`WWMIComponent`]
            The components, in order
        """

        components = [WWMIComponent(assetsFolder, i, entry) for i, entry in enumerate(metadata.get("components") or [])]
        cls.checkDrawRanges(components, metadata, assetsFolder)
        return components

    @classmethod
    def checkDrawRanges(cls, drawRanges: List[WWMIDrawRange], metadata: Dict[str, Any], folder: str):
        """
        Checks that the components lie end to end in the order ``Metadata.json`` lists them, and add up to its totals

        Parameters
        ----------
        drawRanges: List[:class:`WWMIDrawRange`]
            The components, in order

        metadata: Dict[:class:`str`, Any]
            The ``Metadata.json``

        folder: :class:`str`
            The folder the components were read from, for the error messages

        Raises
        ------
        :class:`BadAssetData`
            If there are no components, or their offsets or totals disagree with ``Metadata.json``
        """

        if (not drawRanges):
            raise BadAssetData(f"'{folder}': Metadata.json lists no components")

        vertexOffset = 0
        indexOffset = 0
        for drawRange in drawRanges:
            if (drawRange.vertexOffset != vertexOffset or drawRange.indexOffset != indexOffset):
                raise BadAssetData(f"Component {drawRange.index}: Metadata's offsets ({drawRange.vertexOffset}, {drawRange.indexOffset}) do not follow the previous components ({vertexOffset}, {indexOffset})")
            vertexOffset += drawRange.vertexCount
            indexOffset += drawRange.indexCount

        if (int(metadata.get("vertex_count", vertexOffset)) != vertexOffset or int(metadata.get("index_count", indexOffset)) != indexOffset):
            raise BadAssetData(f"'{folder}': the components total {vertexOffset} vertices / {indexOffset} indices but Metadata.json says {metadata.get('vertex_count')} / {metadata.get('index_count')}")

    @classmethod
    def getExportSemantics(cls, metadata: Dict[str, Any], buffer: WWMIBuffers) -> List[Tuple[str, int, str, int]]:
        """
        Retrieves the layout of one of the mod's buffers, from the ``export_format`` of ``Metadata.json``

        Parameters
        ----------
        metadata: Dict[:class:`str`, Any]
            The asset folder's ``Metadata.json``

        buffer: :class:`WWMIBuffers`
            The buffer

        Raises
        ------
        :class:`BadAssetData`
            If ``Metadata.json`` has no ``export_format`` for the buffer

        Returns
        -------
        List[Tuple[:class:`str`, :class:`int`, :class:`str`, :class:`int`]]
            The semantic name, semantic index, format and number of bytes of each element of a vertex, in order
        """

        exportFormat = metadata.get("export_format") or {}
        entry = exportFormat.get(buffer.name)
        if (entry is None):
            raise BadAssetData(f"Metadata.json's export_format has no '{buffer.name}' buffer")

        return [(s["name"], int(s.get("index", 0)), s["format"], int(s["stride"])) for s in entry["semantics"]]

    @classmethod
    def buildIndex(cls, components: List[WWMIComponent]) -> np.ndarray:
        """
        Builds the index buffer of the whole mesh: each component's indices, offset by where its vertices start

        Parameters
        ----------
        components: List[:class:`WWMIComponent`]
            The components, in order

        Returns
        -------
        numpy.ndarray
            The indices, as little-endian ``uint32``
        """

        return np.concatenate([component.indices + np.uint32(component.vertexOffset) for component in components]).astype("<u4")

    @classmethod
    def buildVertexBuffer(cls, components: List[WWMIComponent], semantics: List[Tuple[str, int, str, int]]) -> bytes:
        """
        Builds one of the mod's vertex buffers: for every vertex of every component, the listed elements' bytes side by side

        Parameters
        ----------
        components: List[:class:`WWMIComponent`]
            The components, in order

        semantics: List[Tuple[:class:`str`, :class:`int`, :class:`str`, :class:`int`]]
            The layout of the buffer, from :meth:`getExportSemantics`

        Raises
        ------
        :class:`BadAssetData`
            If a component lacks one of the elements

        Returns
        -------
        :class:`bytes`
            The buffer
        """

        parts = []
        for component in components:
            columns = []
            for name, semanticIndex, fmt, stride in semantics:
                if (name.upper() == "BITANGENTSIGN" and not component.hasElement(name, semanticIndex)):
                    # WWMI Tools splits the dump's four-byte NORMAL into a three-byte normal and the
                    #   bitangent sign; the sign is the NORMAL element's fourth byte
                    normal = component.getElementBytes("NORMAL", 0, 4)
                    columns.append(normal[:, 3:4])
                    continue
                columns.append(component.getElementBytes(name, semanticIndex, stride))
            parts.append(np.ascontiguousarray(np.concatenate(columns, axis = 1)))

        return b"".join(part.tobytes() for part in parts)

    def buildBlend(self, components: List[WWMIComponent], semantics: List[Tuple[str, int, str, int]]) -> Tuple[bytes, np.ndarray, np.ndarray]:
        """
        Builds the Blend buffer, with the bone indices sent into the merged skeleton

        .. note::
            A merged bone index of 256 or more is written into the 8-bit Blend buffer truncated, as WWMI Tools does.
            The full indices are returned for :meth:`buildBlendRemaps`.

        Parameters
        ----------
        components: List[:class:`WWMIComponent`]
            The components, in order

        semantics: List[Tuple[:class:`str`, :class:`int`, :class:`str`, :class:`int`]]
            The layout of the Blend buffer, from :meth:`getExportSemantics`

        Raises
        ------
        :class:`BadAssetData`
            If a component uses a bone its ``vg_map`` does not have, or a merged bone index is past WWMI's limit

        Returns
        -------
        Tuple[:class:`bytes`, numpy.ndarray, numpy.ndarray]
            The Blend buffer, the full merged bone indices of every vertex (``uint16``) and the bone weights of every vertex
        """

        parts = []
        allIds = []
        allWeights = []

        for component in components:
            columns = []
            for name, semanticIndex, fmt, stride in semantics:
                data = np.ascontiguousarray(component.getElementBytes(name, semanticIndex, stride)).copy()

                if (name.upper() == "BLENDINDICES"):
                    vgMap = component.entry.get("vg_map") or {}
                    if (self.useVgMap and vgMap):
                        table = np.array([int(vgMap[str(local)]) for local in range(len(vgMap))], dtype = np.int64)
                        if (int(data.max()) >= len(table)):
                            raise BadAssetData(f"Component {component.index} uses bone {int(data.max())} but its vg_map has {len(table)} entries")
                        mapped = table[data.astype(np.int64)]
                    else:
                        mapped = data.astype(np.int64) + int(component.entry.get("vg_offset", 0))

                    if (int(mapped.max()) >= WWMIBlendRemapSize):
                        raise BadAssetData(f"Component {component.index}: a merged bone index of {int(mapped.max())} is past WWMI's {WWMIBlendRemapSize}-bone limit")

                    allIds.append(mapped.astype(np.uint16))
                    data = mapped.astype(np.uint8)

                elif (name.upper() == "BLENDWEIGHT"):
                    allWeights.append(data)

                columns.append(data)
            parts.append(np.ascontiguousarray(np.concatenate(columns, axis = 1)))

        if (not allIds or not allWeights):
            raise BadAssetData("Metadata.json's export_format has no BLENDINDICES or no BLENDWEIGHT in its 'Blend' buffer")

        return b"".join(part.tobytes() for part in parts), np.concatenate(allIds), np.concatenate(allWeights)

    # ---- WWMI's blend remap: a merged skeleton of more than 256 bones ----
    #
    # The Blend buffer's bone indices are 8 bits, and a character whose merged skeleton passes 256 slots
    # (Chisa: 420; WWMI-Assets' Augusta, Iuno, Galbrena) has vertices weighted to bones the byte cannot
    # name. WWMI's answer, as WWMI Tools writes it (blender_export/data_models/data_model_wwmi.py's
    # build_blend_remap, identical in 1.3.3 and 1.7.3 except that 1.3.3 hard-codes four ids a vertex):
    #   * per COMPONENT whose vertices (those its index range reaches) carry a non-zero weight on a bone
    #     >= 256, a remap: the sorted distinct bones it uses (at most 256) get local ids 0..n-1;
    #     'BlendRemapForward.buf' holds 512 uint16s per remap, local -> merged, and
    #     'BlendRemapReverse.buf' 512 per remap, merged -> local. Remaps are numbered in component order.
    #   * 'BlendRemapVertexVG.buf' holds every vertex's FULL merged ids as uint16s, as many a vertex as
    #     the Blend buffer has weights (8 for Chisa).
    #   * at load, WWMI's BlendRemapper.hlsl writes a copy of Blend.buf per remapped component with each
    #     id replaced by reverse[full id]; each frame SkeletonRemapper.hlsl builds that component's own
    #     skeleton by gathering forward[local] out of the merged one; the component's draw binds both.
    #     The merged skeleton buffers grow to 512 bones (array = 1536).
    # The Blend.buf bytes themselves stay the merged ids truncated to 8 bits -- what a component with no
    # remap reads, correctly, since its ids are all below 256.
    @classmethod
    def buildBlendRemaps(cls, components: List[WWMIDrawRange], ids: np.ndarray, weights: np.ndarray, indexBuffer: np.ndarray) -> Tuple[List[WWMIBlendRemap], Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Builds the blend remaps of the components that weight a merged bone past the 256 the Blend buffer can name

        Parameters
        ----------
        components: List[:class:`WWMIDrawRange`]
            The components, in order

        ids: numpy.ndarray
            The full merged bone indices of every vertex, from :meth:`buildBlend`

        weights: numpy.ndarray
            The bone weights of every vertex, from :meth:`buildBlend`

        indexBuffer: numpy.ndarray
            The index buffer of the whole mesh, from :meth:`buildIndex`

        Raises
        ------
        :class:`BadAssetData`
            If a component weights more distinct bones than one remap can hold

        Returns
        -------
        Tuple[List[:class:`WWMIBlendRemap`], Optional[numpy.ndarray], Optional[numpy.ndarray]]
            The remaps, then the forward and reverse tables of every remap laid end to end (``uint16``), or ``None`` for both if no component needs a remap
        """

        remaps = []
        forward = []
        reverse = []

        for component in components:
            vertexIds = np.unique(indexBuffer[component.indexOffset:component.indexOffset + component.indexCount])
            used = ids[vertexIds].ravel()
            if (used.size == 0 or int(used.max()) < WWMIBlendIndexLimit):
                continue

            used = np.unique(used[weights[vertexIds].ravel() > 0])
            if (used.size == 0 or int(used.max()) < WWMIBlendIndexLimit):
                continue

            if (used.size > WWMIBlendIndexLimit):
                raise BadAssetData(f"Component {component.index} weights {used.size} distinct bones, past the {WWMIBlendIndexLimit} one remap can hold")

            f = np.zeros(WWMIBlendRemapSize, dtype = "<u2")
            f[np.arange(used.size)] = used
            r = np.zeros(WWMIBlendRemapSize, dtype = "<u2")
            r[used] = np.arange(used.size)

            remaps.append(WWMIBlendRemap(component.index, len(remaps), int(used.size)))
            forward.append(f)
            reverse.append(r)

        if (not remaps):
            return [], None, None
        return remaps, np.concatenate(forward), np.concatenate(reverse)

    @classmethod
    def buildShapeKeys(cls, components: List[WWMIComponent]) -> WWMIShapeKeys:
        """
        Builds the sparse shape keys of the mod from the components' ``SHAPEKEY`` elements

        Parameters
        ----------
        components: List[:class:`WWMIComponent`]
            The components, in order

        Raises
        ------
        :class:`BadAssetData`
            If a shape key does not fit WWMI's shape key slots

        Returns
        -------
        :class:`WWMIShapeKeys`
            The shape keys
        """

        perKey = {}
        for component in components:
            for key, (used, deltas) in component.getShapeKeys().items():
                perKey.setdefault(key, []).append((used.astype(np.uint32) + np.uint32(component.vertexOffset), deltas))

        if (perKey and max(perKey) >= WWMIShapeKeySlots - 1):
            raise BadAssetData(f"shape key {max(perKey)} does not fit WWMI's {WWMIShapeKeySlots} slots")

        ids = []
        deltas = []
        counts = [0] * WWMIShapeKeySlots
        for key in sorted(perKey):
            keyIds = np.concatenate([u for u, _ in perKey[key]])
            keyDeltas = np.concatenate([d for _, d in perKey[key]])
            order = np.argsort(keyIds, kind = "stable")
            ids.append(keyIds[order])
            deltas.append(keyDeltas[order])
            counts[key] = int(keyIds.size)

        total = sum(counts)
        offsets = np.zeros(WWMIShapeKeySlots, dtype = "<u4")
        running = 0
        for key in range(WWMIShapeKeySlots):
            offsets[key] = running
            running += counts[key]

        vertexIds = np.concatenate(ids).astype("<u4") if (ids) else np.zeros(0, dtype = "<u4")
        six = np.zeros((total, 6), dtype = "<f2")
        if (total):
            six[:, :3] = np.concatenate(deltas)

        return WWMIShapeKeys(offsets, vertexIds, six, counts)

    def generate(self, assetsFolder: str, modFolder: str, name: Optional[str] = None) -> WWMIIdentityMod:
        """
        Generates the identity mod of a character

        Parameters
        ----------
        assetsFolder: :class:`str`
            The character's asset folder

        modFolder: :class:`str`
            The folder to write the mod into. It is created if it does not exist

        name: Optional[:class:`str`]
            The name of the character in the mod. If this value is ``None``, the name of ``assetsFolder`` is used :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Raises
        ------
        :class:`BadAssetData`
            If the asset folder is missing a file, or its data does not agree with itself

        :class:`UnknownDXGIFormat`
            If a component's ``.fmt`` declares a format that cannot be decoded

        Returns
        -------
        :class:`WWMIIdentityMod`
            The mod generated
        """

        if (name is None):
            name = os.path.basename(os.path.normpath(assetsFolder))

        mesh = self.buildMesh(assetsFolder)
        textures = []
        if (self.includeTextures):
            textures = [(os.path.join(assetsFolder, fileName), fileName, textureHash) for fileName, textureHash in self.getTextures(assetsFolder)]
        return self._write(name, modFolder, mesh, textures)

    def buildMesh(self, assetsFolder: str) -> WWMIMesh:
        """
        Builds the buffers of a character's identity mod from its asset folder

        Parameters
        ----------
        assetsFolder: :class:`str`
            The character's asset folder

        Raises
        ------
        :class:`BadAssetData`
            If the asset folder is missing a file, or its data does not agree with itself

        :class:`UnknownDXGIFormat`
            If a component's ``.fmt`` declares a format that cannot be decoded

        Returns
        -------
        :class:`WWMIMesh`
            The mesh
        """

        self.print("log", f"Reading the asset folder {assetsFolder}")
        metadata = self.readMetadata(assetsFolder)
        components = self.readComponents(assetsFolder, metadata)
        for key in ("vb0_hash", "cb4_hash"):
            if (key not in metadata):
                raise BadAssetData(f"'{assetsFolder}': Metadata.json has no '{key}'")

        buffers: Dict[WWMIBuffers, bytes] = {}
        index = self.buildIndex(components)
        buffers[WWMIBuffers.Index] = index.tobytes()

        for buffer in (WWMIBuffers.Position, WWMIBuffers.Vector, WWMIBuffers.Color, WWMIBuffers.TexCoord):
            buffers[buffer] = self.buildVertexBuffer(components, self.getExportSemantics(metadata, buffer))

        blendSemantics = self.getExportSemantics(metadata, WWMIBuffers.Blend)
        blend, boneIds, weights = self.buildBlend(components, blendSemantics)
        buffers[WWMIBuffers.Blend] = blend
        blendStride = sum(stride for _, _, _, stride in blendSemantics)

        remaps, forward, reverse = self.buildBlendRemaps(components, boneIds, weights, index)
        if (remaps):
            buffers[WWMIBuffers.BlendRemapVertexVG] = boneIds.astype("<u2").tobytes()
            buffers[WWMIBuffers.BlendRemapForward] = forward.tobytes()
            buffers[WWMIBuffers.BlendRemapReverse] = reverse.tobytes()

        shapeKeys = self.buildShapeKeys(components)
        buffers[WWMIBuffers.ShapeKeyOffset] = shapeKeys.offsets.tobytes()
        buffers[WWMIBuffers.ShapeKeyVertexId] = shapeKeys.vertexIds.tobytes()
        buffers[WWMIBuffers.ShapeKeyVertexOffset] = shapeKeys.deltas.tobytes()

        return WWMIMesh(metadata, components, buffers, shapeKeys, remaps, blendStride, int(boneIds.shape[1]), int(boneIds.max()))

    @classmethod
    def getTextures(cls, assetsFolder: str) -> List[Tuple[str, str]]:
        """
        Retrieves the textures of an asset folder (every ``Components-<components> t=<hash>.dds``)

        Parameters
        ----------
        assetsFolder: :class:`str`
            The asset folder

        Returns
        -------
        List[Tuple[:class:`str`, :class:`str`]]
            The file name of each texture and the hash the game binds it under (lowercase), in file name order
        """

        textures = []
        for fileName in sorted(os.listdir(assetsFolder)):
            match = WWMITexturePattern.match(fileName)
            if (match is not None):
                textures.append((fileName, match.group("hash").lower()))
        return textures

    def generateFromRepo(self, name: str, modFolder: str, version: Optional[str] = None, downloader: Optional[ModDownloader] = None,
                         downloadFolder: Optional[str] = None, modName: Optional[str] = None) -> WWMIIdentityMod:
        """
        Generates the identity mod of a character from its download folder, downloaded from the repositories
        of :class:`ModDownloadRepos`, so no asset folder is needed

        Parameters
        ----------
        name: :class:`str`
            The character's name (see :meth:`ModDownloader.getName`)

        modFolder: :class:`str`
            The folder to write the mod into. It is created if it does not exist

        version: Optional[:class:`str`]
            The game version wanted (eg. ``4.0``). If this value is ``None``, the newest download folder is used (see :meth:`ModDownloader.find`) :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        downloader: Optional[:class:`ModDownloader`]
            What downloads the files (eg. one given local copies of the repositories). If this value is ``None``, every file is downloaded :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        downloadFolder: Optional[:class:`str`]
            The folder to keep the downloaded files in. If this value is ``None``, they are downloaded into a temporary folder that is deleted afterwards :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        modName: Optional[:class:`str`]
            The name of the character in the mod. If this value is ``None``, the prefix of the download folder's files is used :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Raises
        ------
        :class:`Error`
            If no character has that name, or ``version`` is not a game version

        :class:`DownloadFailed`
            If a file cannot be downloaded

        :class:`BadAssetData`
            If the downloaded files do not agree with each other

        Returns
        -------
        :class:`WWMIIdentityMod`
            The mod generated
        """

        downloader = ModDownloader(logger = self.logger) if (downloader is None) else downloader
        download = downloader.find(ModLoaders.WWMI, name, version)

        with tempfile.TemporaryDirectory() as temp:
            downloader.download(download, temp if (downloadFolder is None) else downloadFolder)
            return self.generateFromDownload(download.folder, modFolder, download.prefix, name = modName)

    def generateFromDownload(self, downloadFolder: str, modFolder: str, prefix: str, name: Optional[str] = None) -> WWMIIdentityMod:
        """
        Generates the identity mod of a character from its download folder, laid out as Anime Game Remap's
        ``Data/Mod Downloads/WuWa/<Name>/<version>`` folders are:

        - ``<prefix>Metadata.json``: the asset folder's ``Metadata.json``
        - ``<prefix><buffer>.buf``: the buffers of the identity mod's ``Meshes`` folder (with ``Texcoord`` for ``TexCoord``)
        - ``<prefix>Texture<hash>.dds``: the textures

        :class:`WWMIDownloadFolderBuilder` writes such a folder from an asset folder.

        .. note::
            The mod's textures keep their download folder names (``<prefix>Texture<hash>.dds``), since the
            asset folder's names cannot be rebuilt from the download folder. That changes only the
            textures' file names and the order of their sections in ``mod.ini``.

        Parameters
        ----------
        downloadFolder: :class:`str`
            The download folder

        modFolder: :class:`str`
            The folder to write the mod into. It is created if it does not exist

        prefix: :class:`str`
            What the names of the download folder's files start with

        name: Optional[:class:`str`]
            The name of the character in the mod. If this value is ``None``, ``prefix`` is used :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Raises
        ------
        :class:`BadAssetData`
            If the download folder is missing a file, or its data does not agree with itself

        Returns
        -------
        :class:`WWMIIdentityMod`
            The mod generated
        """

        name = prefix if (name is None) else name
        mesh = self.readDownloadMesh(downloadFolder, prefix)

        textures = []
        if (self.includeTextures):
            pattern = re.compile(re.escape(prefix) + WWMIDownloadTextureSuffix.pattern)
            for fileName in sorted(os.listdir(downloadFolder)):
                match = pattern.fullmatch(fileName)
                if (match is not None):
                    textures.append((os.path.join(downloadFolder, fileName), fileName, match.group("hash").lower()))

        return self._write(name, modFolder, mesh, textures)

    def readDownloadMesh(self, downloadFolder: str, prefix: str) -> WWMIMesh:
        """
        Reads the buffers of a character's identity mod from its download folder

        Parameters
        ----------
        downloadFolder: :class:`str`
            The download folder

        prefix: :class:`str`
            What the names of the download folder's files start with

        Raises
        ------
        :class:`BadAssetData`
            If the download folder is missing a file, or its data does not agree with itself

        Returns
        -------
        :class:`WWMIMesh`
            The mesh
        """

        self.print("log", f"Reading the download folder {downloadFolder}")
        metadataPath = os.path.join(downloadFolder, f"{prefix}Metadata.json")
        if (not os.path.isfile(metadataPath)):
            raise BadAssetData(f"'{metadataPath}' is missing")

        with open(metadataPath, "r", encoding = FileEncodings.UTF8.value) as f:
            metadata = json.load(f)
        for key in ("vb0_hash", "cb4_hash"):
            if (key not in metadata):
                raise BadAssetData(f"'{metadataPath}' has no '{key}'")

        drawRanges = [WWMIDrawRange(i, entry) for i, entry in enumerate(metadata.get("components") or [])]
        self.checkDrawRanges(drawRanges, metadata, downloadFolder)
        vertexCount = sum(drawRange.vertexCount for drawRange in drawRanges)
        indexCount = sum(drawRange.indexCount for drawRange in drawRanges)

        buffers: Dict[WWMIBuffers, bytes] = {}
        for buffer in WWMIBuffers:
            path = os.path.join(downloadFolder, f"{prefix}{WWMIDownloadNames[buffer]}.buf")
            if (os.path.isfile(path)):
                with open(path, "rb") as f:
                    buffers[buffer] = f.read()
            elif (buffer not in WWMIBlendRemapBuffers):
                raise BadAssetData(f"'{path}' is missing")

        # every buffer's size, against the counts Metadata.json gives
        expectedSizes = {WWMIBuffers.Index: indexCount * 4}
        for buffer in (WWMIBuffers.Position, WWMIBuffers.Vector, WWMIBuffers.Color, WWMIBuffers.TexCoord, WWMIBuffers.Blend):
            expectedSizes[buffer] = vertexCount * sum(stride for _, _, _, stride in self.getExportSemantics(metadata, buffer))
        expectedSizes[WWMIBuffers.ShapeKeyOffset] = WWMIShapeKeySlots * 4
        for buffer, size in expectedSizes.items():
            if (len(buffers[buffer]) != size):
                raise BadAssetData(f"{prefix}{WWMIDownloadNames[buffer]}.buf is {len(buffers[buffer])} bytes, but Metadata.json makes it {size}")

        # the Blend buffer's bone ids (truncated to 8 bits past 255) and weights
        blendSemantics = self.getExportSemantics(metadata, WWMIBuffers.Blend)
        blendStride = sum(stride for _, _, _, stride in blendSemantics)
        rows = np.frombuffer(buffers[WWMIBuffers.Blend], dtype = np.uint8).reshape(vertexCount, blendStride)
        offset = 0
        ids = weights = None
        for semanticName, _, _, stride in blendSemantics:
            if (semanticName.upper() == "BLENDINDICES"):
                ids = rows[:, offset:offset + stride].astype(np.uint16)
            elif (semanticName.upper() == "BLENDWEIGHT"):
                weights = rows[:, offset:offset + stride]
            offset += stride
        if (ids is None or weights is None):
            raise BadAssetData("Metadata.json's export_format has no BLENDINDICES or no BLENDWEIGHT in its 'Blend' buffer")
        weightsPerVertex = ids.shape[1]

        # the full ids, when the merged skeleton needed a blend remap
        hasRemap = [buffer in buffers for buffer in WWMIBlendRemapBuffers]
        if (any(hasRemap) and not all(hasRemap)):
            raise BadAssetData(f"'{downloadFolder}' has only some of the blend remap buffers")

        if (all(hasRemap)):
            vertexVG = buffers[WWMIBuffers.BlendRemapVertexVG]
            if (len(vertexVG) != vertexCount * weightsPerVertex * 2):
                raise BadAssetData(f"{prefix}BlendRemapVertexVG.buf is {len(vertexVG)} bytes, not {weightsPerVertex} 16-bit bone ids for each of {vertexCount} vertices")
            ids = np.frombuffer(vertexVG, dtype = "<u2").reshape(vertexCount, weightsPerVertex)

        index = np.frombuffer(buffers[WWMIBuffers.Index], dtype = "<u4")
        remaps, forward, reverse = self.buildBlendRemaps(drawRanges, ids, weights, index)
        remapsAgree = (forward.tobytes() == buffers.get(WWMIBuffers.BlendRemapForward) and reverse.tobytes() == buffers.get(WWMIBuffers.BlendRemapReverse)) if (remaps) else (not any(hasRemap))
        if (not remapsAgree):
            raise BadAssetData(f"'{downloadFolder}': the blend remap buffers do not match the blend remaps its Blend and Index buffers need")

        offsets = np.frombuffer(buffers[WWMIBuffers.ShapeKeyOffset], dtype = "<u4")
        vertexIds = np.frombuffer(buffers[WWMIBuffers.ShapeKeyVertexId], dtype = "<u4")
        deltas = np.frombuffer(buffers[WWMIBuffers.ShapeKeyVertexOffset], dtype = "<f2")
        if (deltas.size != vertexIds.size * 6):
            raise BadAssetData(f"{prefix}ShapeKeyVertexOffset.buf does not hold six 16-bit floats for each of the {vertexIds.size} shape key entries")

        ends = list(offsets[1:]) + [vertexIds.size]
        counts = [int(end) - int(start) for start, end in zip(offsets, ends)]
        shapeKeys = WWMIShapeKeys(offsets, vertexIds, deltas.reshape(-1, 6), counts)

        return WWMIMesh(metadata, drawRanges, buffers, shapeKeys, remaps, blendStride, weightsPerVertex, int(ids.max()) if (ids.size) else 0)

    def _write(self, name: str, modFolder: str, mesh: WWMIMesh, textures: List[Tuple[str, str, str]]) -> WWMIIdentityMod:
        self.print("log", f"Writing the mod into {modFolder}")
        meshes = os.path.join(modFolder, "Meshes")
        os.makedirs(meshes, exist_ok = True)

        # a blend remap left by an earlier run into the same folder would not match this mesh
        for buffer in WWMIBlendRemapBuffers:
            stalePath = os.path.join(meshes, buffer.value)
            if (buffer not in mesh.buffers and os.path.isfile(stalePath)):
                os.remove(stalePath)

        for buffer, data in mesh.buffers.items():
            with open(os.path.join(meshes, buffer.value), "wb") as f:
                f.write(data)

        textureList = []
        if (textures):
            textureFolder = os.path.join(modFolder, "Textures")
            os.makedirs(textureFolder, exist_ok = True)
            for src, fileName, textureHash in textures:
                shutil.copy2(src, os.path.join(textureFolder, fileName))
                textureList.append((fileName, textureHash))

        iniBuilder = WWMIIniBuilder(name, self.author, mesh.metadata, mesh.drawRanges, mesh.shapeKeys.entryCount, textureList,
                                    blendStride = mesh.blendStride, blendRemaps = mesh.blendRemaps, weightsPerVertex = mesh.weightsPerVertex)
        with open(os.path.join(modFolder, "mod.ini"), "w", encoding = FileEncodings.UTF8.value, newline = "\r\n") as f:
            f.write(iniBuilder.build())

        return WWMIIdentityMod(name, modFolder, mesh.metadata, mesh.drawRanges, mesh.shapeKeys, mesh.blendRemaps, mesh.weightsPerVertex, mesh.blendStride,
                               mesh.highestBone, {buffer: len(data) for buffer, data in mesh.buffers.items()}, textureList)
##### EndScript
