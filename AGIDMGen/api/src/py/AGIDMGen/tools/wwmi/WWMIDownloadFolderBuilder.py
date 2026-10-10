##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import os
import shutil
from typing import List, Optional
##### EndExtImports


##### LocalImports
from .WWMIIdentityModGenerator import WWMIIdentityModGenerator
from ...constants.WWMIBuffers import WWMIDownloadNames
from ...exceptions.BadAssetData import BadAssetData
##### EndLocalImports


##### Script
class WWMIDownloadFolderBuilder():
    """
    Writes a WuWa character's download folder from its asset folder, laid out as Anime Game
    Remap's ``Data/Mod Downloads/WuWa/<Name>/<version>`` folders are (the same files Anime Game Remap's
    ``wwmiDownloadFolder.py`` writes):

    - ``<name><buffer>.buf``: the buffers of the character's identity mod, with ``Texcoord`` for ``TexCoord``
    - ``<name>Texture<hash>.dds``: every texture of the asset folder
    - ``<name>Metadata.json`` and ``<name>TextureUsage.json``: the asset folder's manifests

    :meth:`WWMIIdentityModGenerator.generateFromDownload` generates the identity mod from such a folder.

    Parameters
    ----------
    generator: Optional[:class:`WWMIIdentityModGenerator`]
        What builds the buffers. If this value is ``None``, a generator with its default options is used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    generator: :class:`WWMIIdentityModGenerator`
        What builds the buffers
    """

    def __init__(self, generator: Optional[WWMIIdentityModGenerator] = None):
        self.generator = WWMIIdentityModGenerator() if (generator is None) else generator

    def build(self, assetsFolder: str, downloadFolder: str, name: str, texturesFrom: Optional[str] = None) -> List[str]:
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

        texturesFrom: Optional[:class:`str`]
            Another asset folder of the same character to take the textures and ``TextureUsage.json`` from (eg. a second frame dump, taken at a higher texture detail). If this value is ``None``, ``assetsFolder`` is used :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Raises
        ------
        :class:`BadAssetData`
            If the asset folder is missing a file, or its data does not agree with itself

        Returns
        -------
        List[:class:`str`]
            The names of the files written
        """

        textureSource = assetsFolder if (texturesFrom is None) else texturesFrom
        mesh = self.generator.buildMesh(assetsFolder)

        manifests = [(os.path.join(assetsFolder, "Metadata.json"), f"{name}Metadata.json"),
                     (os.path.join(textureSource, "TextureUsage.json"), f"{name}TextureUsage.json")]
        for src, _ in manifests:
            if (not os.path.isfile(src)):
                raise BadAssetData(f"'{src}' is missing")

        os.makedirs(downloadFolder, exist_ok = True)
        written = []
        for buffer, data in mesh.buffers.items():
            fileName = f"{name}{WWMIDownloadNames[buffer]}.buf"
            with open(os.path.join(downloadFolder, fileName), "wb") as f:
                f.write(data)
            written.append(fileName)

        for src, fileName in manifests:
            shutil.copyfile(src, os.path.join(downloadFolder, fileName))
            written.append(fileName)

        for fileName, textureHash in self.generator.getTextures(textureSource):
            dst = f"{name}Texture{textureHash}.dds"
            shutil.copyfile(os.path.join(textureSource, fileName), os.path.join(downloadFolder, dst))
            written.append(dst)

        return written
##### EndScript
