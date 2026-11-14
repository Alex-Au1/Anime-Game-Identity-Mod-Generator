##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Dict, Optional
##### EndExtImports


##### LocalImports
from ..constants.ModLoaders import ModLoaders
from ..constants.ModDownloadRepos import ModDownloadRepos, ModDownloadLiveHashesSuffix
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

    liveHashes: Optional[:class:`ModDownloadRepos`]
        The repository that keeps the character's table of live texture hashes (:attr:`liveHashesFile`, beside the version folders), or ``None`` if neither does :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

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

    liveHashes: Optional[:class:`ModDownloadRepos`]
        The repository that keeps the character's table of live texture hashes, or ``None`` if neither does

    folder: Optional[:class:`str`]
        Where the files were downloaded to, or ``None`` if they have not been
    """

    def __init__(self, loader: ModLoaders, name: str, version: str, prefix: str, files: Dict[str, ModDownloadRepos], liveHashes: Optional[ModDownloadRepos] = None):
        self.loader = loader
        self.name = name
        self.version = version
        self.prefix = prefix
        self.files = files
        self.liveHashes = liveHashes
        self.folder = None

    @property
    def liveHashesFile(self) -> str:
        """
        The name of the character's table of live texture hashes: ``<name>LiveHashes.json``, kept in the character's folder
        beside its version folders. It holds, for each texture, the hash the game binds it under once it has fully loaded
        (WuWa streams its textures, and the hash changes as one loads), by the hash the download folder files it under

        :getter: Retrieves the file name
        :type: :class:`str`
        """

        return f"{self.name}{ModDownloadLiveHashesSuffix}"
##### EndScript
