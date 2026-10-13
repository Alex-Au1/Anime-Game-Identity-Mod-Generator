##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import os
from typing import Dict, List, Optional, Tuple
import FixRaidenBoss2 as FRB
from FixRaidenBoss2 import BaseLogger, Logger
##### EndExtImports


##### LocalImports
from .constants.FileEncodings import FileEncodings
from .constants.Credits import AGIDMGenGithubLink
from .constants.ModLoaders import ModLoaders
from .constants.ModNames import ModNames, ModNameGameTypeIds
from .constants.ModDownloadRepos import ModDownloadRepos
from .exceptions.Error import Error
from .model.ModDownloader import ModDownloader
from .model.gimi.GIMIIdentityModGenerator import GIMIIdentityModGenerator
from .model.gimi.GIMITextureSource import GIMITextureSource
from .model.wwmi.WWMIIdentityModGenerator import WWMIIdentityModGenerator
from .IDModGenService import IDModGenService, AssetsFolderFiles
##### EndLocalImports


##### Script
#: The name of the log file the command line writes with ``--log``
LogFileName = "IDModGenLog.txt"

#: Where the names and aliases of the characters that can be made are listed
CharacterListLink = f"{AGIDMGenGithubLink}/blob/main/Mods/README.md"


class IDModGenServiceCLI():
    """
    The command line front end of :class:`IDModGenService`, as Anime Game Remap's ``RemapServiceCLI`` is of its
    ``RemapService``

    :raw-html:`<br />`

    :class:`IDModGenService` is the model: it takes already-typed data and knows nothing about where its output goes.
    This class is the other side of that line: it turns what an argument parser produced (strings) into the service's
    options, owns the logger everything is reported through and the log file it is written to, prints tips at the end,
    and gives the run's exit code

    :raw-html:`<br />`

    There are two ways to build one:

    * **From strings**, what an argument parser produced: the parameters from ``sources`` to ``textureFrom``. This is the
      one :func:`main` uses. A string that cannot be converted (eg. an unknown game) does not raise here: it is kept, and
      :meth:`generate` raises or reports it (see :attr:`hasErrorsBeforeGenerate`)
    * **From an already-built service**, ``service``: for a caller that has an :class:`IDModGenService` in hand and only
      wants the reporting, log file and exit code around it. The string parameters are then ignored, and the service's
      logger is replaced by this object's

    .. note::
        Argument parsing itself stays outside this class, in :func:`main`. This class takes values, not an ``argv``

    Parameters
    ----------
    sources: Optional[List[:class:`str`]]
        The characters, by name or alias (of any game), whose files are downloaded, and the asset folders, in any order (see :meth:`splitSources`) :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    all: :class:`bool`
        Whether every character with a download folder is generated (of ``games``, if given) :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``False``

    games: Optional[List[:class:`str`]]
        The games the characters' names are looked up in, by name or alias (eg. ``GI``, ``Genshin``, ``WuWa``, ``gimi``), in any case. If this value is ``None`` or empty, every game :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    outputFolder: Optional[:class:`str`]
        The folder each mod is written into (see :attr:`IDModGenService.outputFolder`). If this value is ``None``, the current folder :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    nameReplace: Optional[:class:`str`]
        New names for some of the characters, as ``CHARACTER:NEWNAME`` pairs separated by commas (eg. ``ei:Raiden1, Zani:Shorty, Carlotta:Shorty``), where ``CHARACTER`` is a name or alias of a character being made, a character's base name for all its parts, or an asset folder's name (see :meth:`parseNameReplace` and :attr:`IDModGenService.nameReplace`). If a character is given twice, the later new name wins, and a pair that renames none of the characters being made, or cannot be used, is skipped and reported :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    version: Optional[:class:`str`]
        The game version wanted for the download folders. If this value is ``None``, the newest :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    localData: Optional[List[:class:`str`]]
        Local copies of the repositories' ``Data/Mod Downloads`` folders, each as ``REPO=FOLDER`` (``REPO`` is a :class:`ModDownloadRepos` name) :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    downloadFolder: Optional[:class:`str`]
        The folder to keep the downloaded files in. If this value is ``None``, temporary folders are used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    proxy: Optional[:class:`str`]
        The proxy to download through :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    author: Optional[:class:`str`]
        The mod author WWMI shows, for WuWa's mods. If this value is ``None``, the generator's default :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    noTextures: :class:`bool`
        Whether WuWa's mods leave their textures out :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``False``

    rawBones: :class:`bool`
        Whether WuWa's mods write bone indices as ``vg_offset`` + local index instead of through the ``vg_map`` :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``False``

    assetPrefix: Optional[:class:`str`]
        What a GIMI asset folder's files start with, when there is only one asset folder :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    noFix: :class:`bool`
        Whether GI's mods leave the ``ORFix`` / ``NNFix`` run lines out :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``False``

    faceRegister: Optional[:class:`str`]
        The register GI's mods bind the face diffuse to. If this value is ``None``, the generator's default :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    textureFrom: Optional[List[:class:`str`]]
        For GI's mods, the components that read another component's textures, each as ``COMP=COMP:OBJ[:LAYOUT]`` (see :meth:`GIMITextureSource.parse`) :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    log: Optional[:class:`str`]
        The folder to write the log file (``IDModGenLog.txt``) into. If this value is ``None``, no log file is written :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    verbose: :class:`bool`
        Whether progress is printed, or only errors. A quiet run still writes the whole log file :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``True``

    handleExceptions: :class:`bool`
        Whether a failure of the whole run is reported rather than raised :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``True``

    logger: Optional[:class:`BaseLogger`]
        Where everything is reported. If this value is ``None``, a console ``Logger`` that keeps its text when ``log`` is given :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    service: Optional[:class:`IDModGenService`]
        An already-built service to run, instead of one built from the strings above :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    service: :class:`IDModGenService`
        The service this runs. Every model-side option lives on it

    logger: :class:`BaseLogger`
        Where everything is reported, shared with :attr:`service`

    logFolder: Optional[:class:`str`]
        The folder the log file is written into, or ``None`` when none is
    """

    def __init__(self, sources: Optional[List[str]] = None, all: bool = False, games: Optional[List[str]] = None,
                 outputFolder: Optional[str] = None, nameReplace: Optional[str] = None, version: Optional[str] = None, localData: Optional[List[str]] = None,
                 downloadFolder: Optional[str] = None, proxy: Optional[str] = None, author: Optional[str] = None, noTextures: bool = False,
                 rawBones: bool = False, assetPrefix: Optional[str] = None, noFix: bool = False, faceRegister: Optional[str] = None,
                 textureFrom: Optional[List[str]] = None, log: Optional[str] = None, verbose: bool = True, handleExceptions: bool = True,
                 logger: Optional[BaseLogger] = None, service: Optional[IDModGenService] = None):
        self.logFolder = log
        self.logger = Logger(logTxt = log is not None, verbose = verbose) if (logger is None) else logger

        # a log file needs the logger to keep what it prints, whoever made the logger
        if (log is not None):
            self.logger.logTxt = True
        self._errorBeforeGenerate: Optional[Error] = None
        self._usedAll = all
        self._ignoredPairs: List[str] = []

        if (service is not None):
            self.service = service
            self.service.logger = self.logger
            self.service.downloader.logger = self.logger
            return

        self.service = IDModGenService(outputFolder = outputFolder, version = version, downloadFolder = downloadFolder,
                                       assetPrefix = assetPrefix, handleExceptions = handleExceptions, logger = self.logger)
        try:
            self._setFromStrings(sources or [], nameReplace, all, games or [], localData or [], proxy, author, noTextures, rawBones,
                                 noFix, faceRegister, textureFrom or [])
        except Error as e:
            self._errorBeforeGenerate = e

    @classmethod
    def parseGames(cls, games: List[str]) -> Optional[List[ModLoaders]]:
        """
        Reads the games named by the command line, by Anime Game Remap's names and aliases for them (``GI``, ``Genshin``,
        ``WuWa``, ``WutheringWaves``) or by their mod loaders (``GIMI``, ``WWMI``), in any case and ignoring spaces

        Parameters
        ----------
        games: List[:class:`str`]
            The games' names

        Raises
        ------
        :class:`Error`
            If a name is no game's

        Returns
        -------
        Optional[List[:class:`ModLoaders`]]
            The games' mod loaders, or ``None`` (every game) if no game is named
        """

        if (not games):
            return None

        byGameTypeId = {gameTypeId: loader for loader, gameTypeId in ModNameGameTypeIds.items()}
        result = []
        for game in games:
            name = ModNames.normalize(game)
            loader = next((loader for loader in ModLoaders if (loader.value.lower() == name)), None)
            if (loader is None):
                gameTypeId = FRB.GameTypeIdTools.findByName(name)
                loader = None if (gameTypeId is None) else byGameTypeId.get(int(gameTypeId))
            if (loader is None):
                raise Error(f"no game is called '{game}' (eg. GI or WuWa)")
            if (loader not in result):
                result.append(loader)
        return result

    @classmethod
    def isAssetsFolder(cls, folder: str) -> bool:
        """
        Whether a folder is an asset folder of one of the games (see :meth:`IDModGenService.getAssetsLoader`)

        Parameters
        ----------
        folder: :class:`str`
            The folder

        Returns
        -------
        :class:`bool`
            Whether it is an asset folder
        """

        return os.path.isdir(folder) and any(os.path.isfile(os.path.join(folder, fileName)) for fileName in AssetsFolderFiles.values())

    @classmethod
    def splitSources(cls, sources: List[str], loaders: Optional[List[ModLoaders]] = None) -> Tuple[List[str], List[str]]:
        """
        Sorts the command line's sources into asset folders and characters to download

        :raw-html:`<br />`

        * A path (it has a ``/`` or ``\\``) is an asset folder, and so is an asset folder of one of the games (see :meth:`isAssetsFolder`)
        * A folder that is not an asset folder is a character's name if it names one (eg. a folder called ``Yelan`` in the
          current folder, holding an old mod), else an asset folder, so it is reported as not being one
        * Anything else is a character's name or alias, of any game

        Parameters
        ----------
        sources: List[:class:`str`]
            The sources

        loaders: Optional[List[:class:`ModLoaders`]]
            The games names are looked up in. If this value is ``None``, every game :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        Tuple[List[:class:`str`], List[:class:`str`]]
            The asset folders, then the characters' names, each in the order given
        """

        assetsFolders = []
        names = []
        for source in sources:
            isPath = "/" in source or "\\" in source
            if (isPath or cls.isAssetsFolder(source) or (os.path.isdir(source) and ModNames.search(source, loaders) is None and not ModNames.getParts(source, loaders))):
                assetsFolders.append(source)
            else:
                names.append(source)
        return assetsFolders, names

    @classmethod
    def parseNameReplace(cls, nameReplace: Optional[str], ignored: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Reads the command line's new names for characters: ``CHARACTER:NEWNAME`` pairs separated by commas, eg.
        ``ei:Raiden1, Zani:Shorty``

        :raw-html:`<br />`

        Whitespace around a pair, a name or the ``:`` is ignored, and so is an empty pair (eg. a comma at the end). A pair
        that is not ``CHARACTER:NEWNAME``, with neither part empty, is skipped, with its reason added to ``ignored``. If a
        ``CHARACTER`` is given twice (in any case, and ignoring spaces, ``_`` and ``-``, as names are looked up), the later
        ``NEWNAME`` wins. Which characters each ``CHARACTER`` means (``ei`` and ``Raiden`` are one; ``Carlotta`` is each of
        her parts) is found when the mods are generated (see :meth:`IDModGenService.getNameReplacements`)

        Parameters
        ----------
        nameReplace: Optional[:class:`str`]
            The pairs. If this value is ``None``, there are none

        ignored: Optional[List[:class:`str`]]
            Where the reason each pair is skipped is added. If this value is ``None``, the reasons are not kept :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        Dict[:class:`str`, :class:`str`]
            The new name of each character, by the ``CHARACTER`` given, in the order given
        """

        if (ignored is None):
            ignored = []

        result = {}
        keys = {}
        for pair in ([] if (nameReplace is None) else nameReplace.split(",")):
            pair = pair.strip()
            if (not pair):
                continue

            key, separator, newName = pair.partition(":")
            key, newName = key.strip(), newName.strip()
            if (not separator or not key or not newName):
                ignored.append(f"'{pair}' is not CHARACTER:NEWNAME")
                continue

            # the later of one key wins
            normalized = ModNames.normalize(key)
            previous = keys.pop(normalized, None)
            if (previous is not None):
                result.pop(previous)
            keys[normalized] = key
            result[key] = newName
        return result

    @classmethod
    def parseLocalData(cls, localData: List[str]):
        """
        Reads the command line's local copies of the repositories' download folders, each as ``REPO=FOLDER``

        Parameters
        ----------
        localData: List[:class:`str`]
            The local copies

        Raises
        ------
        :class:`Error`
            If one is not ``REPO=FOLDER`` with ``REPO`` a :class:`ModDownloadRepos` name

        Returns
        -------
        Dict[:class:`ModDownloadRepos`, :class:`str`]
            The folder of each repository
        """

        result = {}
        for value in localData:
            repo, separator, folder = value.partition("=")
            if (not separator or repo not in ModDownloadRepos.__members__):
                raise Error(f"--localData is REPO=FOLDER with REPO one of {', '.join(ModDownloadRepos.__members__)}, not {value!r}")
            result[ModDownloadRepos[repo]] = folder
        return result

    def _setFromStrings(self, sources: List[str], nameReplace: Optional[str], all: bool, games: List[str], localData: List[str], proxy: Optional[str],
                        author: Optional[str], noTextures: bool, rawBones: bool, noFix: bool, faceRegister: Optional[str], textureFrom: List[str]):
        service = self.service

        service.loaders = self.parseGames(games)
        service.nameReplace = self.parseNameReplace(nameReplace, self._ignoredPairs)
        service.assetsFolders, service.names = self.splitSources(sources, service.loaders)
        if (all):
            service.names = [modName.name for modName in ModNames.getAll(service.loaders)] + service.names

        service.downloader = ModDownloader(localFolders = self.parseLocalData(localData), proxy = proxy, logger = self.logger)

        gimiKwargs = {"includeFix": not noFix, "textureSources": dict(GIMITextureSource.parse(value) for value in textureFrom)}
        if (faceRegister is not None):
            gimiKwargs["faceRegister"] = faceRegister
        service.gimiGenerator = GIMIIdentityModGenerator(logger = self.logger, **gimiKwargs)

        wwmiKwargs = {"includeTextures": not noTextures, "useVgMap": not rawBones}
        if (author is not None):
            wwmiKwargs["author"] = author
        service.wwmiGenerator = WWMIIdentityModGenerator(logger = self.logger, **wwmiKwargs)

    @property
    def hasErrorsBeforeGenerate(self) -> bool:
        """
        Whether a string given to the constructor could not be converted. :meth:`generate` raises (or reports) it

        :getter: Retrieves whether there was such an error
        :type: :class:`bool`
        """

        return self._errorBeforeGenerate is not None

    @property
    def logFile(self) -> Optional[str]:
        """
        The full path of the log file, or ``None`` when none is written

        :getter: Retrieves the path
        :type: Optional[:class:`str`]
        """

        return None if (self.logFolder is None) else os.path.join(self.logFolder, LogFileName)

    @property
    def exitCode(self) -> int:
        """
        The exit code of the last :meth:`generate`: 0 when every mod was generated, 1 when one could not be (or the
        options are not valid), 2 when a WWMI mod's shape keys do not match its ``Metadata.json``

        :getter: Retrieves the exit code
        :type: :class:`int`
        """

        stats = self.service.stats
        if (self.hasErrorsBeforeGenerate or not stats.noErrors or not stats.generated):
            return 1
        if (any(getattr(mod, "checksumMatches", None) is False or getattr(mod, "dispatchYMatches", None) is False for mod in stats.generated.values())):
            return 2
        return 0

    def generate(self):
        """
        Runs the service, prints the tips, then writes the log file

        :raw-html:`<br />`

        The log file is written whatever happened, including when the run raises, since a run that failed is the one whose
        log is worth keeping

        Raises
        ------
        :class:`Error`
            If a string given to the constructor could not be converted, or the options contradict each other, and
            :attr:`IDModGenService.handleExceptions` is ``False``
        """

        service = self.service
        service.stats.clear()
        try:
            if (self._errorBeforeGenerate is not None):
                if (not service.handleExceptions):
                    raise self._errorBeforeGenerate
                self.logger.error(str(self._errorBeforeGenerate))
                return

            for reason in self._ignoredPairs:
                self.logger.log(f"Not renaming a character: {reason}")
            service.generate()
            if (service.stats.noErrors and service.stats.generated):
                self.addTips()
        finally:
            self.createLog()

    def addTips(self):
        """
        Prints what the user might find useful to know next

        :raw-html:`<br />`

        Called by :meth:`generate` after a run that generated everything it was asked to, and before the log file is
        written, so the tips are in the log too
        """

        service = self.service
        logger = self.logger
        tips = []
        if (not self._usedAll):
            tips.append("Want every character's identity mod? Run this again (on CMD) with the --all option")
        if (service.names and service.version is None):
            tips.append("Want a character as an older game version had them? Run this again (on CMD) with the --version option, eg. --version 4.0")
        if (self.logFolder is None):
            tips.append("Want what was printed kept in a file? Run this again (on CMD) with the --log option")

        prevIncludePrefix = logger.includePrefix
        logger.includePrefix = False
        logger.split()
        logger.openHeading("Tips", sideLen = 10)
        for tip in tips:
            logger.bulletPoint(tip)
        logger.space()
        logger.log(f"Every character's name and aliases are listed at {CharacterListLink}")
        logger.log("For more info on command options, run this (on CMD) with the --help option")
        logger.closeHeading()
        logger.includePrefix = prevIncludePrefix

    def createLog(self):
        """
        Writes everything reported so far into the log file. Does nothing when no log folder was given
        """

        if (self.logFolder is None):
            return

        os.makedirs(self.logFolder, exist_ok = True)
        with open(self.logFile, "w", encoding = FileEncodings.UTF8.value) as f:
            f.write(self.logger.loggedTxt)
##### EndScript
