##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Dict
##### EndExtImports


##### LocalImports
from ..constants.ModLoaders import ModLoaders
from ..constants.ModDownloadRepos import ModDownloadRepos
##### EndLocalImports


##### Script
class ModDownload():
    """
    Class for one version of a character's download folder: which files it has, and which repository each
    one is kept in

    Parameters
    ----------
    loader: :class:`ModLoaders`
        The mod loader the character's mods are for

    name: :class:`str`
        The name of the character's folder (eg. ``Yelan``)

    version: :class:`str`
        The name of the version folder (eg. ``4_0``)

    prefix: :class:`str`
        What the names of the folder's files start with. It is usually :attr:`name`, but not always (the ``Raiden`` folder's files start with ``RaidenShogun``)

    files: Dict[:class:`str`, :class:`ModDownloadRepos`]
        The repository each file is kept in, by file name

    Attributes
    ----------
    loader: :class:`ModLoaders`
        The mod loader the character's mods are for

    name: :class:`str`
        The name of the character's folder (eg. ``Yelan``)

    version: :class:`str`
        The name of the version folder (eg. ``4_0``)

    prefix: :class:`str`
        What the names of the folder's files start with

    files: Dict[:class:`str`, :class:`ModDownloadRepos`]
        The repository each file is kept in, by file name

    folder: Optional[:class:`str`]
        Where the files were downloaded to, or ``None`` if they have not been
    """

    def __init__(self, loader: ModLoaders, name: str, version: str, prefix: str, files: Dict[str, ModDownloadRepos]):
        self.loader = loader
        self.name = name
        self.version = version
        self.prefix = prefix
        self.files = files
        self.folder = None
##### EndScript
