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
from urllib.parse import quote
from typing import Dict, List, Optional, Tuple
import FixRaidenBoss2 as FRB
from FixRaidenBoss2 import BaseLogger, Model
##### EndExtImports


##### LocalImports
from .VersionTools import VersionTools
from ..constants.ModLoaders import ModLoaders
from ..constants.ModDownloadRepos import ModDownloadRepos, ModDownloadGameFolders
from ..data.ModDownloadData import ModDownloadData, ModDownloadAliases
from ..exceptions.Error import Error
from ..exceptions.DownloadFailed import DownloadFailed
from ..model.ModDownload import ModDownload
##### EndLocalImports


##### Script
#: What a Git LFS pointer file starts with
LfsPointerHeader = b"version https://git-lfs.github.com/spec/v1"

#: The largest a Git LFS pointer file can be, in bytes (a real one is about 130)
LfsPointerMaxSize = 1024


class ModDownloader(Model):
    """
    Finds and downloads characters' download folders. Each file is taken from the first of
    :class:`ModDownloadRepos` that keeps it: Anime Game Remap's repository, then this library's

    .. note::
        Files are downloaded with Anime Game Remap's ``FixRaidenBoss2.FileDownload``, which retries a
        failed download and follows GitHub's redirects.

    Parameters
    ----------
    localFolders: Optional[Dict[:class:`ModDownloadRepos`, :class:`str`]]
        Local copies of the repositories' ``Data/Mod Downloads`` folders (eg. a clone of Anime Game Remap). A file found in its repository's local folder is copied from there instead of downloaded. If this value is ``None``, every file is downloaded :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    proxy: Optional[:class:`str`]
        The proxy to download through. If this value is ``None``, no proxy is used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    logger: Optional[:class:`BaseLogger`]
        Where to report what is done. If this value is ``None``, nothing is reported :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    localFolders: Dict[:class:`ModDownloadRepos`, :class:`str`]
        Local copies of the repositories' ``Data/Mod Downloads`` folders

    proxy: Optional[:class:`str`]
        The proxy to download through
    """

    def __init__(self, localFolders: Optional[Dict[ModDownloadRepos, str]] = None, proxy: Optional[str] = None, logger: Optional[BaseLogger] = None):
        super().__init__(logger = logger)
        self.localFolders = {} if (localFolders is None) else localFolders
        self.proxy = proxy

    @classmethod
    def getCharacters(cls, loader: ModLoaders) -> List[str]:
        """
        Retrieves the characters that have a download folder an identity mod can be generated from

        Parameters
        ----------
        loader: :class:`ModLoaders`
            The mod loader

        Returns
        -------
        List[:class:`str`]
            The names of the characters' folders, in alphabetical order
        """

        return sorted(ModDownloadData.get(ModDownloadGameFolders[loader], {}), key = str.lower)

    @classmethod
    def getName(cls, loader: ModLoaders, name: str) -> str:
        """
        Retrieves the name of a character's folder, from its name or another name it is known by (eg. ``KamisatoAyaka`` for ``Ayaka``), in any case

        Parameters
        ----------
        loader: :class:`ModLoaders`
            The mod loader

        name: :class:`str`
            The character's name

        Raises
        ------
        :class:`Error`
            If no character has that name

        Returns
        -------
        :class:`str`
            The name of the character's folder
        """

        game = ModDownloadGameFolders[loader]
        characters = ModDownloadData.get(game, {})
        if (name in characters):
            return name

        # an alias may name a character with no listed folder (eg. one whose asset folder cannot be built)
        aliases = {alias.lower(): folder for alias, folder in ModDownloadAliases.get(game, {}).items() if folder in characters}
        folders = {folder.lower(): folder for folder in characters}
        result = aliases.get(name.lower(), folders.get(name.lower()))
        if (result is None):
            raise Error(f"no {game} character called '{name}' has a download folder")
        return result

    @classmethod
    def getVersions(cls, loader: ModLoaders, name: str) -> List[str]:
        """
        Retrieves the versions of a character's download folder

        Parameters
        ----------
        loader: :class:`ModLoaders`
            The mod loader

        name: :class:`str`
            The character's name

        Raises
        ------
        :class:`Error`
            If no character has that name

        Returns
        -------
        List[:class:`str`]
            The version folders, oldest first
        """

        folder = cls.getName(loader, name)
        return sorted(ModDownloadData[ModDownloadGameFolders[loader]][folder], key = VersionTools.parse)

    @classmethod
    def find(cls, loader: ModLoaders, name: str, version: Optional[str] = None) -> ModDownload:
        """
        Finds a version of a character's download folder

        Parameters
        ----------
        loader: :class:`ModLoaders`
            The mod loader

        name: :class:`str`
            The character's name

        version: Optional[:class:`str`]
            The game version wanted (eg. ``4.0`` or ``4_0``). The newest folder not newer than it is chosen, or the oldest if every folder is newer (see :meth:`VersionTools.getClosest`). If this value is ``None``, the newest folder is chosen :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Raises
        ------
        :class:`Error`
            If no character has that name, or ``version`` is not a game version

        Returns
        -------
        :class:`ModDownload`
            The download folder, not downloaded yet
        """

        folder = cls.getName(loader, name)
        versions = ModDownloadData[ModDownloadGameFolders[loader]][folder]
        chosen = VersionTools.getClosest(versions, version)
        prefix, files = versions[chosen]
        return ModDownload(loader, folder, chosen, prefix, {fileName: ModDownloadRepos[repo] for fileName, repo in files.items()})

    @classmethod
    def getUrl(cls, download: ModDownload, fileName: str) -> str:
        """
        Retrieves the address of a file of a download folder

        Parameters
        ----------
        download: :class:`ModDownload`
            The download folder

        fileName: :class:`str`
            The name of the file

        Returns
        -------
        :class:`str`
            The address
        """

        repo = download.files[fileName]
        path = "/".join(quote(part) for part in (ModDownloadGameFolders[download.loader], download.name, download.version, fileName))
        return f"{repo.value}/{path}"

    @classmethod
    def isLfsPointer(cls, path: str) -> bool:
        """
        Whether a file is a Git LFS pointer: the small text file Git keeps in place of a file stored in Git LFS

        Parameters
        ----------
        path: :class:`str`
            The path to the file

        Returns
        -------
        :class:`bool`
            Whether the file is a Git LFS pointer
        """

        if (os.path.getsize(path) > LfsPointerMaxSize):
            return False
        with open(path, "rb") as f:
            return f.read(len(LfsPointerHeader)) == LfsPointerHeader

    def _getLocalPath(self, download: ModDownload, fileName: str) -> Optional[str]:
        root = self.localFolders.get(download.files[fileName])
        if (root is None):
            return None

        path = os.path.join(root, ModDownloadGameFolders[download.loader], download.name, download.version, fileName)
        return path if (os.path.isfile(path)) else None

    def _downloadFile(self, url: str, fileName: str, folder: str):
        try:
            FRB.FileDownload(url, fileName, cache = False).download(folder, self.proxy)
        except Exception as e:
            raise DownloadFailed(url, str(e)) from None

    def download(self, download: ModDownload, folder: str) -> ModDownload:
        """
        Downloads a download folder's files

        Parameters
        ----------
        download: :class:`ModDownload`
            The download folder, from :meth:`find`

        folder: :class:`str`
            The folder to put the files in. It is created if it does not exist

        Raises
        ------
        :class:`DownloadFailed`
            If a file cannot be downloaded, or what arrives is a Git LFS pointer instead of the file

        Returns
        -------
        :class:`ModDownload`
            ``download``, with its :attr:`ModDownload.folder` set to ``folder``
        """

        os.makedirs(folder, exist_ok = True)
        self.print("log", f"Getting {len(download.files)} files of {download.name}'s {download.version} download folder")
        for fileName in sorted(download.files):
            localPath = self._getLocalPath(download, fileName)
            if (localPath is not None):
                source = localPath
                shutil.copyfile(localPath, os.path.join(folder, fileName))
            else:
                source = self.getUrl(download, fileName)
                self.print("log", f"Downloading {source}")
                self._downloadFile(source, fileName, folder)

            # the download folders' binaries are kept in Git LFS: a clone made without git-lfs, or an address that
            #   bypasses LFS, gives the small pointer file instead of the file, which no generator could read
            if (not os.path.isfile(os.path.join(folder, fileName))):
                raise DownloadFailed(source, "the file did not arrive")
            if (self.isLfsPointer(os.path.join(folder, fileName))):
                raise DownloadFailed(source, "it is a Git LFS pointer, not the file (a clone needs 'git lfs install' then 'git lfs pull')")

        download.folder = folder
        return download
##### EndScript
