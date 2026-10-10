##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import os
import json
import shutil
import tempfile
import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Callable
from FixRaidenBoss2 import BaseLogger, Model
##### EndExtImports


##### LocalImports
from ..ModDownloader import ModDownloader
from ...constants.ModLoaders import ModLoaders
from .GIMIIniBuilder import GIMIIniBuilder
from ...constants.FileEncodings import FileEncodings
from ...constants.ModDownloadRepos import ModDownloadGameFolders
from ...constants.GIMIBuffers import GIMIBuffers, GIMISemanticBuffers, GIMIFixedStrides, GIMIHashFileSuffix
from ...constants.GIMITextureLayouts import GIMITextureLayouts
from ...exceptions.BadAssetData import BadAssetData
from ...exceptions.Error import Error
from ...model.files.VbDumpFile import VbDumpFile
from ...model.files.IbDumpFile import IbDumpFile
from ...model.gimi.GIMIComponent import GIMIComponent
from ...model.gimi.GIMIIdentityMod import GIMIIdentityMod
from ...model.gimi.GIMITextureSource import GIMITextureSource
##### EndLocalImports


##### Script
class GIMIIdentityModGenerator(Model):
    """
    Generates the identity mod of a Genshin Impact character: the game's own model, written out as a
    GIMI mod from the character's asset folder

    The asset folder is laid out as `GI-Model-Importer-Assets <https://github.com/SilentNightSound/GI-Model-Importer-Assets>`_'s
    ``PlayerCharacterData/<Name>`` folders are:

    - ``hash.json``, with the hashes, objects and textures of each component
    - ``<prefix><component><object>-vb0=<hash>.txt`` and ``<prefix><component><object>-ib=<hash>.txt``: the 3DMigoto dumps of each object's vertex and index buffers
    - ``<prefix><component><object><kind>.dds``: the textures

    For each skinned component (a ``hash.json`` entry with a ``position_vb`` and a ``blend_vb``) the mod gets:

    - ``<name><component>Position.buf``, ``<name><component>Blend.buf`` and ``<name><component>Texcoord.buf``: the dumped vertex buffer, split as GIMI lays it out
    - ``<name><component><object>.ib``: each object's indices, as ``R32_UINT``
    - ``<name><component><object><kind>.dds``: each object's textures

    and the mod also gets ``<name>FaceHeadDiffuse.dds`` (the face's diffuse) and ``<name>.ini``. ``<component>``
    is the empty string for an older character, which is a single component.

    Examples
    --------
    .. code-block:: python
        :linenos:

        import AGIDMGen as IDMG

        generator = IDMG.GIMIIdentityModGenerator()
        mod = generator.generate("GI-Model-Importer-Assets/PlayerCharacterData/Yelan", "Mods/YelanIdentity")
        print("\\n".join(mod.getSummary()))

        # a component with no textures of its own reads another's
        generator = IDMG.GIMIIdentityModGenerator(faceRegister = "ps-t1", textureSources = {
            "Bang": IDMG.GIMITextureSource("Body", "A"),
            "Eye": IDMG.GIMITextureSource("Body", "A", IDMG.GIMITextureLayouts.Plain)})
        generator.generate("GI-Model-Importer-Assets/PlayerCharacterData/YelanTranquil", "Mods/YelanTranquilIdentity")

    Parameters
    ----------
    includeFix: :class:`bool`
        Whether an object that binds textures runs the ``ORFix`` command list of its layout :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``True``

    faceRegister: :class:`str`
        The register the face's diffuse texture is bound to. Some skins of version 6.0 or newer bind it to ``ps-t1`` :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``"ps-t0"``

    textureSources: Optional[Dict[:class:`str`, :class:`GIMITextureSource`]]
        For each component with no textures of its own, where it reads its textures from. If this value is ``None``, no component borrows textures :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    logger: Optional[:class:`BaseLogger`]
        Where to report what is done. If this value is ``None``, nothing is reported :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    includeFix: :class:`bool`
        Whether an object that binds textures runs the ``ORFix`` command list of its layout

    faceRegister: :class:`str`
        The register the face's diffuse texture is bound to

    textureSources: Dict[:class:`str`, :class:`GIMITextureSource`]
        For each component with no textures of its own, where it reads its textures from
    """

    def __init__(self, includeFix: bool = True, faceRegister: str = "ps-t0", textureSources: Optional[Dict[str, GIMITextureSource]] = None,
                 logger: Optional[BaseLogger] = None):
        super().__init__(logger = logger)
        self.includeFix = includeFix
        self.faceRegister = faceRegister
        self.textureSources = {} if (textureSources is None) else textureSources

    @classmethod
    def readHashes(cls, assetsFolder: str) -> List[Dict[str, Any]]:
        """
        Reads the ``hash.json`` of an asset folder

        Parameters
        ----------
        assetsFolder: :class:`str`
            The asset folder

        Raises
        ------
        :class:`BadAssetData`
            If the asset folder has no ``hash.json``

        Returns
        -------
        List[Dict[:class:`str`, Any]]
            The entries of ``hash.json``
        """

        path = os.path.join(assetsFolder, "hash.json")
        if (not os.path.isfile(path)):
            raise BadAssetData(f"'{path}' is missing")

        with open(path, "r", encoding = FileEncodings.UTF8.value) as f:
            return json.load(f)

    @classmethod
    def buildBuffers(cls, vbDump: VbDumpFile, dumpName: str) -> Tuple[Dict[GIMIBuffers, bytes], Dict[GIMIBuffers, int]]:
        """
        Splits a dumped vertex buffer into GIMI's vertex buffers

        Parameters
        ----------
        vbDump: :class:`VbDumpFile`
            The dumped vertex buffer

        dumpName: :class:`str`
            The file name of the dump, for the error messages

        Raises
        ------
        :class:`BadAssetData`
            If an element belongs to no GIMI buffer, a buffer's elements are not side by side, a buffer is missing, or the Position or Blend buffer is not the size GIMI fixes

        Returns
        -------
        Tuple[Dict[:class:`GIMIBuffers`, :class:`bytes`], Dict[:class:`GIMIBuffers`, :class:`int`]]
            The contents of each buffer, and the number of bytes of one vertex in each
        """

        ranges: Dict[GIMIBuffers, List[int]] = {}
        offset = 0
        for element in vbDump.elements:
            buffer = GIMISemanticBuffers.get(element.name.rstrip("0123456789"))
            if (buffer is None):
                raise BadAssetData(f"{dumpName}: element {element.name} belongs to no .buf file")

            span = ranges.setdefault(buffer, [offset, offset])
            if (span[1] != offset):
                raise BadAssetData(f"{dumpName}: {buffer.value} elements are not contiguous ({element.name} at {offset})")

            span[1] = offset + element.size
            offset += element.size

        for buffer in GIMIBuffers:
            if (buffer not in ranges):
                raise BadAssetData(f"{dumpName}: no element belongs to the {buffer.value} buffer")

        rows = np.frombuffer(vbDump.data, dtype = np.uint8).reshape(vbDump.vertexCount, vbDump.bytesPerLine)
        buffers = {}
        strides = {}
        for buffer in GIMIBuffers:
            start, end = ranges[buffer]
            if (buffer in GIMIFixedStrides and (end - start) != GIMIFixedStrides[buffer]):
                raise BadAssetData(f"{dumpName}: {buffer.value} spans {end - start} bytes, GIMI's stride is {GIMIFixedStrides[buffer]}")

            buffers[buffer] = rows[:, start:end].tobytes()
            strides[buffer] = end - start

        return buffers, strides

    def _getBoundTextures(self, components: Dict[str, GIMIComponent], comp: str, obj: str) -> Tuple[str, str, Dict[str, str]]:
        # the object's own textures; else the source given for its component; else the source its hash.json records for it
        own = components[comp].textures.get(obj, {})
        if (own):
            return comp, obj, own

        source = self.textureSources.get(comp)
        recorded = components[comp].entry.get("texture_sources", {}).get(obj)
        if (source is None and recorded is not None):
            source = GIMITextureSource.fromDict(recorded)
        if (source is None):
            return comp, obj, {}

        borrowed = dict(components[source.component].textures.get(source.obj, {}))
        if (source.layout == GIMITextureLayouts.Plain):
            borrowed.pop("NormalMap", None)
        return source.component, source.obj, borrowed

    def generate(self, assetsFolder: str, modFolder: str, name: Optional[str] = None, assetPrefix: Optional[str] = None) -> GIMIIdentityMod:
        """
        Generates the identity mod of a character

        Parameters
        ----------
        assetsFolder: :class:`str`
            The character's asset folder

        modFolder: :class:`str`
            The folder to write the mod into. It is created if it does not exist

        name: Optional[:class:`str`]
            The name of the character in the mod's files and sections. If this value is ``None``, ``assetPrefix`` is used :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        assetPrefix: Optional[:class:`str`]
            What the names of the asset folder's files start with (eg. ``Citlali_WhisperOfStars``). If this value is ``None``, the name of ``assetsFolder`` is used :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Raises
        ------
        :class:`BadAssetData`
            If the asset folder is missing a file, or its data does not agree with itself

        :class:`Error`
            If a texture source names a component or object the character does not have

        Returns
        -------
        :class:`GIMIIdentityMod`
            The mod generated
        """

        assetsFolderName = os.path.basename(os.path.normpath(assetsFolder))
        prefix = assetsFolderName if (assetPrefix is None) else assetPrefix
        name = prefix if (name is None) else name

        self.print("log", f"Reading the asset folder {assetsFolder}")
        hashes = self.readHashes(assetsFolder)
        entries, unskinned, face = self._getEntries(hashes, name)

        # ---- read everything before writing anything ----
        components: Dict[str, GIMIComponent] = {}
        textureCopies: List[Tuple[str, str]] = []

        for entry in entries:
            comp = entry.get("component_name", "")
            objects = list(entry["object_classifications"])

            # every object's vb0 dump is the component's whole vertex buffer; the first one serves
            dumpName = f"{prefix}{comp}{objects[0]}-vb0={entry['position_vb']}.txt"
            vbPath = os.path.join(assetsFolder, dumpName)
            if (not os.path.isfile(vbPath)):
                raise BadAssetData(f"'{vbPath}' is missing")

            vbDump = VbDumpFile.read(vbPath)
            if (vbDump is None):
                raise BadAssetData(f"{dumpName}: its header's elements cannot be read")

            buffers, strides = self.buildBuffers(vbDump, dumpName)
            vertexCount = vbDump.vertexCount

            indices = {}
            for obj in objects:
                ibPath = os.path.join(assetsFolder, f"{prefix}{comp}{obj}-ib={entry['ib']}.txt")
                if (not os.path.isfile(ibPath)):
                    raise BadAssetData(f"'{ibPath}' is missing")
                indices[obj] = IbDumpFile.read(ibPath).indices

            textures = self._getTextures(assetsFolder, prefix, name, entry, textureCopies)
            components[comp] = self._makeComponent(comp, entry, vertexCount, buffers, strides, indices, textures)

        faceDiffuse, faceHash = self._getFace(face, lambda obj: os.path.join(assetsFolder, f"{prefix}Face{obj}Diffuse.dds"), name, textureCopies)
        return self._write(name, modFolder, components, textureCopies, faceDiffuse, faceHash, unskinned, f"its asset folder ({assetsFolderName})")

    def generateFromRepo(self, name: str, modFolder: str, version: Optional[str] = None, downloader: Optional[ModDownloader] = None,
                         downloadFolder: Optional[str] = None, modName: Optional[str] = None) -> GIMIIdentityMod:
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
        :class:`GIMIIdentityMod`
            The mod generated
        """

        downloader = ModDownloader(logger = self.logger) if (downloader is None) else downloader
        download = downloader.find(ModLoaders.GIMI, name, version)

        with tempfile.TemporaryDirectory() as temp:
            downloader.download(download, temp if (downloadFolder is None) else downloadFolder)
            # named by what it is, not by where it was downloaded to (a temporary folder's name is random)
            sourceName = f"{ModDownloadGameFolders[download.loader]}/{download.name}/{download.version}"
            return self.generateFromDownload(download.folder, modFolder, download.prefix, name = modName, sourceName = sourceName)

    def generateFromDownload(self, downloadFolder: str, modFolder: str, prefix: str, name: Optional[str] = None,
                             sourceName: Optional[str] = None) -> GIMIIdentityMod:
        """
        Generates the identity mod of a character from its download folder, laid out as Anime Game Remap's
        ``Data/Mod Downloads/GI/<Name>/<version>`` folders are:

        - ``<prefix>Hash.json``: the asset folder's ``hash.json``
        - ``<prefix><component>Position.buf``, ``Blend.buf`` and ``Texcoord.buf``: the GIMI vertex buffers of each skinned component
        - ``<prefix><component><object>.ib``: each object's indices, as ``R32_UINT``
        - ``<prefix><component><object><kind>.dds`` and ``<prefix>FaceDiffuse.dds``: the textures

        :class:`GIMIDownloadFolderBuilder` writes such a folder from an asset folder.

        Parameters
        ----------
        downloadFolder: :class:`str`
            The download folder

        modFolder: :class:`str`
            The folder to write the mod into. It is created if it does not exist

        prefix: :class:`str`
            What the names of the download folder's files start with

        name: Optional[:class:`str`]
            The name of the character in the mod's files and sections. If this value is ``None``, ``prefix`` is used :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        sourceName: Optional[:class:`str`]
            What the ``.ini``'s last comment calls the download folder (eg. ``GI/Yelan/4_0``). If this value is ``None``, the name of ``downloadFolder`` is used :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Raises
        ------
        :class:`BadAssetData`
            If the download folder is missing a file, or its data does not agree with itself

        :class:`Error`
            If a texture source names a component or object the character does not have

        Returns
        -------
        :class:`GIMIIdentityMod`
            The mod generated
        """

        name = prefix if (name is None) else name
        self.print("log", f"Reading the download folder {downloadFolder}")
        hashPath = os.path.join(downloadFolder, f"{prefix}{GIMIHashFileSuffix}")
        if (not os.path.isfile(hashPath)):
            raise BadAssetData(f"'{hashPath}' is missing")

        with open(hashPath, "r", encoding = FileEncodings.UTF8.value) as f:
            hashes = json.load(f)
        entries, unskinned, face = self._getEntries(hashes, name)

        components: Dict[str, GIMIComponent] = {}
        textureCopies: List[Tuple[str, str]] = []

        for entry in entries:
            comp = entry.get("component_name", "")
            buffers = {}
            for buffer in GIMIBuffers:
                path = os.path.join(downloadFolder, f"{prefix}{comp}{buffer.value}.buf")
                if (not os.path.isfile(path)):
                    raise BadAssetData(f"'{path}' is missing")
                with open(path, "rb") as f:
                    buffers[buffer] = f.read()

            vertexCount = len(buffers[GIMIBuffers.Position]) // GIMIFixedStrides[GIMIBuffers.Position]
            strides = {buffer: (len(data) // vertexCount if (vertexCount) else GIMIFixedStrides.get(buffer, 0)) for buffer, data in buffers.items()}
            for buffer, data in buffers.items():
                if (len(data) != vertexCount * strides[buffer] or (buffer in GIMIFixedStrides and strides[buffer] != GIMIFixedStrides[buffer])):
                    raise BadAssetData(f"{prefix}{comp}{buffer.value}.buf is {len(data)} bytes, which is not {vertexCount} vertices of a GIMI {buffer.value} buffer")

            indices = {}
            for obj in entry["object_classifications"]:
                path = os.path.join(downloadFolder, f"{prefix}{comp}{obj}.ib")
                if (not os.path.isfile(path)):
                    raise BadAssetData(f"'{path}' is missing")
                indices[obj] = np.fromfile(path, dtype = "<u4")

            textures = self._getTextures(downloadFolder, prefix, name, entry, textureCopies)
            components[comp] = self._makeComponent(comp, entry, vertexCount, buffers, strides, indices, textures)

        faceDiffuse, faceHash = self._getFace(face, lambda obj: os.path.join(downloadFolder, f"{prefix}FaceDiffuse.dds"), name, textureCopies)
        return self._write(name, modFolder, components, textureCopies, faceDiffuse, faceHash, unskinned,
                           f"its download folder ({os.path.basename(os.path.normpath(downloadFolder)) if (sourceName is None) else sourceName})")

    def _getEntries(self, hashes: List[Dict[str, Any]], name: str) -> Tuple[List[Dict[str, Any]], List[str], Optional[Dict[str, Any]]]:
        # the skinned components, the names of the unskinned ones and the face entry, checked
        entries = [h for h in hashes if h.get("position_vb") and h.get("blend_vb")]
        unskinned = [h.get("component_name", "") for h in hashes if h.get("position_vb") and not h.get("blend_vb")]
        face = next((h for h in hashes if h.get("component_name") == "Face"), None)
        if (not entries):
            raise BadAssetData(f"{name}: hash.json has no entry with a position_vb and a blend_vb")

        for entry in entries:
            for key in ("texcoord_vb", "draw_vb", "ib", "object_classifications", "object_indexes"):
                if (key not in entry):
                    raise BadAssetData(f"{name}: the hash.json entry of component '{entry.get('component_name', '')}' has no '{key}'")
            if (not entry["object_classifications"]):
                raise BadAssetData(f"{name}: the hash.json entry of component '{entry.get('component_name', '')}' has no objects")

        names = [entry.get("component_name", "") for entry in entries]
        for entry in entries:
            for obj, record in entry.get("texture_sources", {}).items():
                source = GIMITextureSource.fromDict(record)
                lender = next((e for e in entries if e.get("component_name", "") == source.component), None)
                if (obj not in entry["object_classifications"] or lender is None or source.obj not in lender["object_classifications"]):
                    raise BadAssetData(f"{name}: hash.json records a texture source for {entry.get('component_name', '')}{obj} that the character does not have ({record!r})")

        for borrower, source in self.textureSources.items():
            if (borrower not in names):
                raise Error(f"the texture source names {borrower!r}, which is not one of this character's components ({', '.join(names)})")
            if (source.component not in names):
                raise Error(f"the texture source of {borrower!r} reads {source.component!r}, which is not one of this character's components ({', '.join(names)})")
            lender = entries[names.index(source.component)]
            if (source.obj not in lender["object_classifications"]):
                raise Error(f"the texture source of {borrower!r} reads the object {source.obj!r}, which component {source.component!r} does not have ({', '.join(lender['object_classifications'])})")

        return entries, unskinned, face

    @classmethod
    def _getTextures(cls, folder: str, prefix: str, name: str, entry: Dict[str, Any], textureCopies: List[Tuple[str, str]]) -> Dict[str, Dict[str, str]]:
        # the textures of each object that the folder has, as their file names in the mod
        comp = entry.get("component_name", "")
        textures = {}
        for obj, textureList in zip(entry["object_classifications"], entry.get("texture_hashes", [])):
            for kind, ext, _ in textureList:
                if (ext.lower() != ".dds"):
                    continue

                src = os.path.join(folder, f"{prefix}{comp}{obj}{kind}{ext}")
                if (os.path.exists(src)):
                    dst = f"{name}{comp}{obj}{kind}{ext}"
                    textureCopies.append((src, dst))
                    textures.setdefault(obj, {})[kind] = dst
        return textures

    @classmethod
    def _makeComponent(cls, comp: str, entry: Dict[str, Any], vertexCount: int, buffers: Dict[GIMIBuffers, bytes], strides: Dict[GIMIBuffers, int],
                       indices: Dict[str, np.ndarray], textures: Dict[str, Dict[str, str]]) -> GIMIComponent:
        for obj, ib in indices.items():
            if (ib.size and int(ib.max()) >= vertexCount):
                raise BadAssetData(f"{comp}{obj}: index {int(ib.max())} beyond the {vertexCount} vertices")
        return GIMIComponent(comp, entry, vertexCount, buffers, strides, indices, textures)

    @classmethod
    def _getFace(cls, face: Optional[Dict[str, Any]], getSource: Callable[[str], str], name: str, textureCopies: List[Tuple[str, str]]) -> Tuple[Optional[str], Optional[str]]:
        # the face's diffuse texture in the mod and its hash; 'getSource' gives the texture's path from the face's object
        if (face is None):
            return None, None

        faceObj = list(face["object_classifications"])[0]
        src = getSource(faceObj)
        if (not os.path.exists(src)):
            return None, None

        faceDiffuse = f"{name}Face{faceObj}Diffuse.dds"
        textureCopies.append((src, faceDiffuse))
        faceHash = next((h for kind, _, h in face["texture_hashes"][0] if kind == "Diffuse"), None)
        return faceDiffuse, faceHash

    def _write(self, name: str, modFolder: str, components: Dict[str, GIMIComponent], textureCopies: List[Tuple[str, str]],
               faceDiffuse: Optional[str], faceHash: Optional[str], unskinned: List[str], source: str) -> GIMIIdentityMod:
        for component in components.values():
            for obj in component.objects:
                component.boundTextures[obj] = self._getBoundTextures(components, component.name, obj)

        self.print("log", f"Writing the mod into {modFolder}")
        os.makedirs(modFolder, exist_ok = True)
        for component in components.values():
            for buffer, data in component.buffers.items():
                with open(os.path.join(modFolder, f"{name}{component.name}{buffer.value}.buf"), "wb") as f:
                    f.write(data)

            for obj, ib in component.indices.items():
                with open(os.path.join(modFolder, f"{name}{component.name}{obj}.ib"), "wb") as f:
                    f.write(ib.astype("<u4").tobytes())

        for src, dst in textureCopies:
            shutil.copy2(src, os.path.join(modFolder, dst))

        componentList = list(components.values())
        iniBuilder = GIMIIniBuilder(name, componentList, source, faceDiffuse = faceDiffuse, faceHash = faceHash,
                                    faceRegister = self.faceRegister, includeFix = self.includeFix)
        with open(os.path.join(modFolder, f"{name}.ini"), "w", encoding = FileEncodings.UTF8.value, newline = "\r\n") as f:
            f.write(iniBuilder.build())

        return GIMIIdentityMod(name, modFolder, componentList, faceDiffuse, self.faceRegister, unskinned)
##### EndScript
