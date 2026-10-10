##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import os
import glob
import shutil
from typing import List, Optional, Tuple
##### EndExtImports


##### LocalImports
from .GIMIIdentityModGenerator import GIMIIdentityModGenerator
from ...constants.GIMIBuffers import GIMIHashFileSuffix
from ...exceptions.BadAssetData import BadAssetData
from ...model.files.VbDumpFile import VbDumpFile
from ...model.files.IbDumpFile import IbDumpFile
##### EndLocalImports


##### Script
class GIMIDownloadFolderBuilder():
    """
    Writes a GI character's download folder from its asset folder, laid out as Anime Game
    Remap's ``Data/Mod Downloads/GI/<Name>/<version>`` folders are (the same files Anime Game Remap's
    ``giDownloadFolder.py`` writes), plus a copy of the asset folder's ``hash.json``:

    - ``<name><component>Position.buf``, ``Blend.buf`` and ``Texcoord.buf``: each skinned component's vertex buffer, split as GIMI lays it out
    - ``<name><component><object>.ib``: each object's indices, as ``R32_UINT``
    - ``<name><component><object><kind>.dds``: every texture ``hash.json`` lists, and ``<name>Face<kind>.dds`` for the face's
    - ``<name>Hash.json``: the asset folder's ``hash.json``

    The asset folder's files are found by how their names END, so their prefix does not have to be the
    folder's name.

    :meth:`GIMIIdentityModGenerator.generateFromDownload` generates the identity mod from such a folder.

    Attributes
    ----------
    notes: List[:class:`str`]
        What the last :meth:`build` left out, and why (eg. an unskinned component, or a texture the asset folder does not have)
    """

    def __init__(self):
        self.notes: List[str] = []

    @classmethod
    def findOne(cls, folder: str, suffix: str, required: bool = True) -> Optional[str]:
        """
        Retrieves the file of a folder whose name ends with some text

        .. note::
            A longer name can end with the same text (``FooBodyDiffuse.dds`` and ``FooBangBodyDiffuse.dds``),
            so the shortest name is taken, and two shortest names of the same length are an error.

        Parameters
        ----------
        folder: :class:`str`
            The folder

        suffix: :class:`str`
            What the file's name ends with

        required: :class:`bool`
            Whether a missing file is an error :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``True``

        Raises
        ------
        :class:`BadAssetData`
            If several files are equally short, or no file matches and ``required`` is ``True``

        Returns
        -------
        Optional[:class:`str`]
            The path to the file, or ``None`` if no file matches
        """

        hits = sorted(glob.glob(os.path.join(glob.escape(folder), "*" + suffix)))
        hits.sort(key = lambda path: len(os.path.basename(path)))
        if (not hits):
            if (required):
                raise BadAssetData(f"no asset file ends in {suffix!r}")
            return None

        if (len(hits) > 1 and len(os.path.basename(hits[0])) == len(os.path.basename(hits[1]))):
            raise BadAssetData(f"several asset files end in {suffix!r}: {', '.join(os.path.basename(hit) for hit in hits)}")
        return hits[0]

    def build(self, assetsFolder: str, downloadFolder: str, name: str) -> List[str]:
        """
        Writes the download folder

        Parameters
        ----------
        assetsFolder: :class:`str`
            The character's asset folder

        downloadFolder: :class:`str`
            The folder to write. It is created if it does not exist

        name: :class:`str`
            What the names of the download folder's files start with

        Raises
        ------
        :class:`BadAssetData`
            If the asset folder is missing a file, or its data does not agree with itself

        Returns
        -------
        List[:class:`str`]
            The names of the files written. What was left out is in :attr:`notes`
        """

        self.notes = []
        hashes = GIMIIdentityModGenerator.readHashes(assetsFolder)

        # ---- read everything before writing anything ----
        files: List[Tuple[str, bytes]] = []
        copies: List[Tuple[str, str]] = []

        for entry in hashes:
            comp = entry.get("component_name", "")
            objects = list(entry.get("object_classifications", []))

            if (entry.get("position_vb") and entry.get("blend_vb")):
                vbPath = self.findOne(assetsFolder, f"{comp}{objects[0]}-vb0={entry['position_vb']}.txt")
                vbDump = VbDumpFile.read(vbPath)
                if (vbDump is None):
                    raise BadAssetData(f"{os.path.basename(vbPath)}: its header's elements cannot be read")

                buffers, _ = GIMIIdentityModGenerator.buildBuffers(vbDump, os.path.basename(vbPath))
                for buffer, data in buffers.items():
                    files.append((f"{name}{comp}{buffer.value}.buf", data))

                for obj in objects:
                    ib = IbDumpFile.read(self.findOne(assetsFolder, f"{comp}{obj}-ib={entry['ib']}.txt")).indices
                    if (ib.size and int(ib.max()) >= vbDump.vertexCount):
                        raise BadAssetData(f"{comp}{obj}: index {int(ib.max())} beyond the {vbDump.vertexCount} vertices")
                    files.append((f"{name}{comp}{obj}.ib", ib.astype("<u4").tobytes()))

            elif (entry.get("position_vb")):
                missing = ["blend_vb"] + ([] if entry.get("root_vs") else ["root_vs"])
                self.notes.append(f"unskinned component {comp!r} (objects {', '.join(objects)}): no buffers written -- hash.json has no {', '.join(missing)}")

            for obj, textureList in zip(objects, entry.get("texture_hashes", [])):
                if (not textureList and entry.get("position_vb")):
                    self.notes.append(f"component {comp!r} object {obj!r}: hash.json lists NO textures")

                for kind, ext, _ in textureList:
                    if (ext.lower() != ".dds"):
                        continue

                    suffix, dst = (f"Face{obj}{kind}{ext}", f"{name}Face{kind}{ext}") if (comp == "Face") else (f"{comp}{obj}{kind}{ext}", f"{name}{comp}{obj}{kind}{ext}")
                    src = self.findOne(assetsFolder, suffix, required = False)
                    if (src is None):
                        self.notes.append(f"missing texture: *{suffix} (hash.json lists it, the asset folder has no file)")
                    else:
                        copies.append((src, dst))

        with open(os.path.join(assetsFolder, "hash.json"), "rb") as f:
            files.append((f"{name}{GIMIHashFileSuffix}", f.read()))

        # ---- write the folder ----
        os.makedirs(downloadFolder, exist_ok = True)
        written = []
        for fileName, data in files:
            with open(os.path.join(downloadFolder, fileName), "wb") as f:
                f.write(data)
            written.append(fileName)

        for src, dst in copies:
            shutil.copyfile(src, os.path.join(downloadFolder, dst))
            written.append(dst)

        return written
##### EndScript
