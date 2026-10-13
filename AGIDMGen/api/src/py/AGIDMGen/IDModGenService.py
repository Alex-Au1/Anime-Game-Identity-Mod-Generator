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
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
from FixRaidenBoss2 import BaseLogger, Model
##### EndExtImports


##### LocalImports
from .constants.ModLoaders import ModLoaders
from .constants.ModNames import ModNames
from .constants.ModDownloadRepos import ModDownloadGameFolders
from .exceptions.BadAssetData import BadAssetData
from .exceptions.Error import Error
from .model.IDModGenStats import IDModGenStats
from .model.ModDownloader import ModDownloader
from .model.gimi.GIMIIdentityModGenerator import GIMIIdentityModGenerator
from .model.wwmi.WWMIIdentityModGenerator import WWMIIdentityModGenerator
##### EndLocalImports


##### Script
# what a mod's name may be made of: it names the mod's folder, and a GI mod's files and .ini sections
_ValidModName = re.compile(r"[A-Za-z0-9_\-]+")

#: The file that tells each mod loader's asset folders apart
AssetsFolderFiles = {ModLoaders.GIMI: "hash.json", ModLoaders.WWMI: "Metadata.json"}


class IDModGenService(Model):
    """
    The library's entry point: generates the identity mods of several characters at once, of any of the games, from
    their asset folders or from their download folders, and reports what it did

    :raw-html:`<br />`

    Each character's game is found from the character: a name or alias is looked up in every game (see :class:`ModNames`),
    and an asset folder's game is told by its files (see :meth:`getAssetsLoader`). So ``Zani`` (WuWa) and ``Ayaka`` (GI)
    can be generated in one run.

    It is the model half, with no user interface of its own: progress and the summary go to the
    :attr:`logger` (nothing is reported without one), and the results are in :attr:`stats`. A character that
    cannot be generated does not stop the others: its exception is recorded in :attr:`IDModGenStats.skipped`.
    The command line's half is :class:`IDModGenServiceCLI`.

    .. note::
        Like Anime Game Remap's ``RemapService``, :meth:`generate` returns nothing; read :attr:`stats` after it.
        For one character, a generator (:class:`GIMIIdentityModGenerator` or :class:`WWMIIdentityModGenerator`)
        can be used directly instead, and raises when it fails.

    Examples
    --------
    .. code-block:: python
        :linenos:

        import AGIDMGen as IDMG
        import FixRaidenBoss2 as FRB          # Anime Game Remap's API: its logger serves both libraries

        # every character's newest download folder, of both games, printed as it goes
        service = IDMG.IDModGenService(names = ["Zani", "Ayaka", "ei"], outputFolder = "Mods", logger = FRB.Logger())
        service.generate()
        print(sorted(service.stats.generated), service.stats.skipped)     # ['Ayaka', 'Raiden', 'Zani'] {}

        # from asset folders, collecting the output instead of printing it (eg. in a server)
        logger = FRB.Logger(logTxt = True, verbose = False)
        service = IDMG.IDModGenService(assetsFolders = ["WWMI-Assets/PlayerCharacterData/Sanhua"], logger = logger)
        service.generate()
        print(logger.loggedTxt)

    Parameters
    ----------
    names: Optional[List[:class:`str`]]
        The characters to generate from their download folders, by name or alias, of any of the games (see :class:`ModNames`). A character's base name is each of its parts (eg. ``Carlotta`` is ``CarlottaBody``, ``CarlottaHairCrystal`` and ``CarlottaHairNormal``; see :meth:`ModNames.getParts`). Each mod is named, and reported, by its mod's name (``ei`` makes ``Raiden``), and a character asked for twice is generated once. If this value is ``None``, no download folder is used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    assetsFolders: Optional[List[:class:`str`]]
        The characters' asset folders to generate from, of any of the games (see :meth:`getAssetsLoader`). If this value is ``None``, no asset folder is used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    outputFolder: Optional[:class:`str`]
        The folder each mod is written into, as ``<outputFolder>/<name>``, where a downloaded character's ``<name>`` is its mod's name (or its new name, see :attr:`nameReplace`). If this value is ``None``, the current folder is used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    version: Optional[:class:`str`]
        The game version wanted for the download folders (see :meth:`ModDownloader.find`), for every game. If this value is ``None``, the newest :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    downloader: Optional[:class:`ModDownloader`]
        What downloads the download folders. If this value is ``None``, one that downloads every file :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    downloadFolder: Optional[:class:`str`]
        The folder to keep the downloaded files in, as ``<downloadFolder>/<name>``. If this value is ``None``, temporary folders are used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    loaders: Optional[Iterable[:class:`ModLoaders`]]
        The games, by their mod loaders, that :attr:`names` are looked up in (eg. to choose between two games' characters that one name fits equally well). If this value is ``None``, every game :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    gimiGenerator: Optional[:class:`GIMIIdentityModGenerator`]
        The generator of GI's mods, with its options. If this value is ``None``, one with its default options :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    wwmiGenerator: Optional[:class:`WWMIIdentityModGenerator`]
        The generator of WuWa's mods, with its options. If this value is ``None``, one with its default options :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    nameReplace: Optional[Dict[:class:`str`, :class:`str`]]
        New names for some of the characters, each written into its mod (its folder, and a GI mod's files and sections) instead of its usual name, by the character: a name or alias of one of :attr:`names` (eg. ``ei`` for ``Raiden``), a character's base name for all its parts (eg. ``Carlotta``), or the name of one of :attr:`assetsFolders`, in any case. The later new name of a character wins, and a pair that renames no character being generated, or cannot be used, is skipped and reported (see :meth:`getNameReplacements`). If this value is ``None``, every character keeps its name :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    assetPrefix: Optional[:class:`str`]
        What a GIMI asset folder's files start with, when there is only one asset folder (see :meth:`GIMIIdentityModGenerator.generate`) :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    handleExceptions: :class:`bool`
        Whether a failure of the whole run (eg. options that contradict each other) is reported to the logger and :meth:`generate` returns, rather than raised :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``False``

    logger: Optional[:class:`BaseLogger`]
        Where the run reports progress. If this value is ``None``, nothing is reported :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    names: List[:class:`str`]
        The characters to generate from their download folders

    assetsFolders: List[:class:`str`]
        The characters' asset folders to generate from

    outputFolder: :class:`str`
        The folder each mod is written into

    version: Optional[:class:`str`]
        The game version wanted for the download folders

    downloader: :class:`ModDownloader`
        What downloads the download folders

    downloadFolder: Optional[:class:`str`]
        The folder to keep the downloaded files in

    loaders: Optional[List[:class:`ModLoaders`]]
        The games that :attr:`names` are looked up in, or ``None`` for every game

    gimiGenerator: Optional[:class:`GIMIIdentityModGenerator`]
        The generator of GI's mods, or ``None`` for one with its default options

    wwmiGenerator: Optional[:class:`WWMIIdentityModGenerator`]
        The generator of WuWa's mods, or ``None`` for one with its default options

    nameReplace: Dict[:class:`str`, :class:`str`]
        New names for some of the characters, by the character

    assetPrefix: Optional[:class:`str`]
        What a GIMI asset folder's files start with, when there is only one asset folder

    handleExceptions: :class:`bool`
        Whether a failure of the whole run is reported rather than raised
    """

    def __init__(self, names: Optional[List[str]] = None, assetsFolders: Optional[List[str]] = None, outputFolder: Optional[str] = None,
                 version: Optional[str] = None, downloader: Optional[ModDownloader] = None, downloadFolder: Optional[str] = None,
                 loaders: Optional[Iterable[ModLoaders]] = None, gimiGenerator: Optional[GIMIIdentityModGenerator] = None,
                 wwmiGenerator: Optional[WWMIIdentityModGenerator] = None, nameReplace: Optional[Dict[str, str]] = None, assetPrefix: Optional[str] = None,
                 handleExceptions: bool = False, logger: Optional[BaseLogger] = None):
        super().__init__(logger = logger)
        self.names = [] if (names is None) else list(names)
        self.assetsFolders = [] if (assetsFolders is None) else list(assetsFolders)
        self.outputFolder = os.getcwd() if (outputFolder is None) else outputFolder
        self.version = version
        self.downloader = ModDownloader(logger = logger) if (downloader is None) else downloader
        self.downloadFolder = downloadFolder
        self.loaders = None if (loaders is None) else list(loaders)
        self.gimiGenerator = gimiGenerator
        self.wwmiGenerator = wwmiGenerator
        self.nameReplace = {} if (nameReplace is None) else dict(nameReplace)
        self.assetPrefix = assetPrefix
        self.handleExceptions = handleExceptions
        self._stats = IDModGenStats()
        self._replacements: Dict[str, str] = {}
        self._ignoredReplacements: List[str] = []

    @property
    def stats(self) -> IDModGenStats:
        """
        What the last :meth:`generate` did

        :getter: Retrieves the stats
        :type: :class:`IDModGenStats`
        """

        return self._stats

    @classmethod
    def getAssetsLoader(cls, assetsFolder: str) -> ModLoaders:
        """
        Tells which game an asset folder is of, by its files: a GI-Model-Importer-Assets folder has a ``hash.json``, and a
        WWMI-Assets folder a ``Metadata.json``

        Parameters
        ----------
        assetsFolder: :class:`str`
            The asset folder

        Raises
        ------
        :class:`BadAssetData`
            If the asset folder is not a folder, or is of neither game

        Returns
        -------
        :class:`ModLoaders`
            The mod loader of the asset folder's game
        """

        if (not os.path.isdir(assetsFolder)):
            raise BadAssetData(f"'{assetsFolder}' is not a folder")

        found = [loader for loader, fileName in AssetsFolderFiles.items() if (os.path.isfile(os.path.join(assetsFolder, fileName)))]
        if (len(found) != 1):
            files = " or a ".join(AssetsFolderFiles.values())
            raise BadAssetData(f"'{assetsFolder}' is not an asset folder of one game: it needs a {files}" if (not found) else
                               f"'{assetsFolder}' has the files of both games' asset folders ({', '.join(AssetsFolderFiles.values())})")
        return found[0]

    def getGenerator(self, loader: ModLoaders) -> Union[GIMIIdentityModGenerator, WWMIIdentityModGenerator]:
        """
        Retrieves the generator of a game's mods: :attr:`gimiGenerator` or :attr:`wwmiGenerator`, or one with its default
        options if that is ``None``

        Parameters
        ----------
        loader: :class:`ModLoaders`
            The mod loader

        Raises
        ------
        :class:`Error`
            If the generator given is not a generator of that game's mods

        Returns
        -------
        Union[:class:`GIMIIdentityModGenerator`, :class:`WWMIIdentityModGenerator`]
            The generator
        """

        expected = GIMIIdentityModGenerator if (loader == ModLoaders.GIMI) else WWMIIdentityModGenerator
        generator = self.gimiGenerator if (loader == ModLoaders.GIMI) else self.wwmiGenerator
        if (generator is None):
            return expected(logger = self.logger)

        if (not isinstance(generator, expected)):
            raise Error(f"a {type(generator).__name__} cannot generate {loader.value} mods")
        if (generator.logger is None):
            generator.logger = self.logger
        return generator

    def _checkOptions(self):
        sourceCount = len(self.assetsFolders) + len(self.names)
        if (sourceCount == 0):
            raise Error("there is nothing to generate: give asset folders or character names")
        if (self.assetPrefix is not None and (len(self.assetsFolders) != 1 or self.names)):
            raise Error("an asset prefix can only be given for one asset folder")

        # a generator of the wrong game is a mistake in the options, found before anything is generated
        for loader in ModLoaders:
            self.getGenerator(loader)
        self._ignoredReplacements = []
        self._replacements = self.getNameReplacements(self._ignoredReplacements)

    @classmethod
    def _getAssetsLabel(cls, assetsFolder: str) -> str:
        return os.path.basename(os.path.normpath(assetsFolder))

    @classmethod
    def isValidName(cls, name: str) -> bool:
        """
        Whether a text can be a mod's name: its folder's, and a GI mod's files' and sections'. It is one or more of the
        letters ``A-Z`` and ``a-z``, the digits, ``_`` and ``-``

        Parameters
        ----------
        name: :class:`str`
            The text

        Returns
        -------
        :class:`bool`
            Whether it can be a mod's name
        """

        return bool(_ValidModName.fullmatch(name))

    def _getNameReplaceTargets(self, key: str, modNames: Dict[str, Any], assetsLabels: Dict[str, str]) -> List[Tuple[str, str]]:
        # the characters a key means, each with what follows the new name: '' for a whole character, or its part
        normalized = ModNames.normalize(key)
        if (normalized in assetsLabels):
            return [(assetsLabels[normalized], "")]

        result = []
        modName = ModNames.match(key, self.loaders)
        if (modName is not None and modName.name in modNames):
            result.append((modName.name, ""))

        # a character's base name (or a whole character with parts of its own, eg. Augusta and AugustaHelm) means each part
        base = normalized if (modName is None) else ModNames.normalize(modName.name)
        for part in modNames.values():
            if (part.base is not None and ModNames.normalize(part.base) == base and part.name not in dict(result)):
                result.append((part.name, part.part))
        return result

    def getNameReplacements(self, ignored: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Finds which characters each key of :attr:`nameReplace` means, and their new names

        :raw-html:`<br />`

        A key means:

        * one of :attr:`assetsFolders`, by its folder's name
        * one of :attr:`names`, by any of its names or aliases, as a whole (see :meth:`ModNames.match`: ``ei`` is Raiden, but
          ``Heizo`` is no one)
        * or every part of a character, by the character's base name (see :attr:`ModName.base`): each part is named the new
          name then the part (``{"Carlotta": "Shorty"}`` names ``CarlottaBody`` ``ShortyBody``)

        Keys are looked at in order, and the later new name of a character wins (``{"ei": "A", "Raiden": "B"}`` names Raiden
        ``B``). A pair is skipped, with its reason added to ``ignored``, when:

        * its key means none of the characters being generated
        * its new name cannot be a mod's name (see :meth:`isValidName`)
        * its new name would write the mod into a folder another of the characters' mods is already written into

        Parameters
        ----------
        ignored: Optional[List[:class:`str`]]
            Where the reason each pair is skipped is added. If this value is ``None``, the reasons are not kept :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Returns
        -------
        Dict[:class:`str`, :class:`str`]
            The new name of each character renamed, by its label: an asset folder's name, or a downloaded character's mod name
        """

        if (ignored is None):
            ignored = []

        assetsLabels = {ModNames.normalize(self._getAssetsLabel(folder)): self._getAssetsLabel(folder) for folder in self.assetsFolders}
        modNames = {modName.name: modName for modName in self._getModNames() if (not isinstance(modName, str))}

        requested = {}
        for key, newName in self.nameReplace.items():
            key, newName = key.strip(), newName.strip()
            if (not self.isValidName(newName)):
                ignored.append(f"'{key}' is not renamed '{newName}': a name is only letters, digits, '_' and '-'")
                continue

            targets = self._getNameReplaceTargets(key, modNames, assetsLabels)
            if (not targets):
                ignored.append(f"'{key}' is not renamed '{newName}': it is none of the characters being generated")
                continue

            # the later new name of a character wins, moved to the end as if given only there
            for label, part in targets:
                requested.pop(label, None)
                requested[label] = newName + part

        # a new name must not write a mod into another's folder: the characters kept as they are hold theirs first
        labels = list(assetsLabels.values()) + list(modNames)
        folders = {label.lower(): label for label in labels if (label not in requested)}
        result = {}
        for label, newName in requested.items():
            other = folders.get(newName.lower())
            if (other is not None and other != label):
                ignored.append(f"'{label}' is not renamed '{newName}': {other}'s mod is written into that folder")
                folders.setdefault(label.lower(), label)
                continue

            folders[newName.lower()] = label
            result[label] = newName
        return result

    def _reportException(self, error: BaseException):
        # the library's own errors explain themselves; anything else is a bug, and gets its traceback
        if (isinstance(error, Error)):
            self.print("error", str(error))
        else:
            self.print("handleException", error)

    def _getModNames(self) -> List[Union[str, Any]]:
        # a character asked for by an alias is generated, filed and written under its mod's name (eg. 'ei' is Raiden), once;
        #   a base name is every part of its character (eg. 'Carlotta' is CarlottaBody, ...), with the whole character if
        #   there is one (Augusta, then AugustaHelm); a name that is no character's (or fits two games' equally) is kept as
        #   typed, and reported when its turn comes
        result = []
        seen = set()
        for name in self.names:
            parts = ModNames.getParts(name, self.loaders)
            if (parts):
                whole = ModNames.match(name, self.loaders)
                found = ([] if (whole is None or whole.base is not None) else [whole]) + parts
            else:
                found = [ModNames.search(name, self.loaders)]

            for modName in found:
                key = name if (modName is None) else (modName.loader, modName.name)
                if (key not in seen):
                    seen.add(key)
                    result.append(name if (modName is None) else modName)
        return result

    def _generateOne(self, label: str, generate: Callable[[], Any]) -> Optional[Any]:
        self.print("openHeading", label, sideLen = 5)
        try:
            mod = generate()
        except Exception as e:
            self._stats.addSkipped(label, e)
            self._reportException(e)
            self.print("closeHeading")
            return None

        self._stats.addGenerated(label, mod)
        for line in mod.getSummary():
            self.print("log", line)
        self.print("closeHeading")
        self.print("space")
        return mod

    def _generateFromFolder(self, assetsFolder: str, modFolder: str, newName: Optional[str]) -> Any:
        loader = self.getAssetsLoader(assetsFolder)
        if (self.assetPrefix is not None and loader != ModLoaders.GIMI):
            raise Error(f"an asset prefix is only for GIMI asset folders, and '{assetsFolder}' is a {ModDownloadGameFolders[loader]} one")

        kwargs = {"name": newName}
        if (loader == ModLoaders.GIMI):
            kwargs["assetPrefix"] = self.assetPrefix
        return self.getGenerator(loader).generate(assetsFolder, modFolder, **kwargs)

    def _generateFromRepo(self, name: str, modFolder: str, downloadFolder: Optional[str], newName: Optional[str]) -> Any:
        # found again, so a name that is no character's raises its reason here, recorded against it
        modName = ModNames.find(name, self.loaders)
        return self.getGenerator(modName.loader).generateFromRepo(modName.name, modFolder, version = self.version, downloader = self.downloader,
                                                                  downloadFolder = downloadFolder, modName = newName)

    def generate(self):
        """
        Generates the identity mods, then reports what was done

        Raises
        ------
        :class:`Error`
            If the options contradict each other, and :attr:`handleExceptions` is ``False``
        """

        self._stats.clear()
        try:
            self._checkOptions()
        except Exception as e:
            if (not self.handleExceptions):
                raise
            self._reportException(e)
            return

        for reason in self._ignoredReplacements:
            self.print("log", f"Not renaming a character: {reason}")
        if (self._ignoredReplacements):
            self.print("space")

        prevPrefix = None if (self.logger is None) else self.logger.prefix
        for assetsFolder in self.assetsFolders:
            label = self._getAssetsLabel(assetsFolder)
            if (self.logger is not None):
                self.logger.prefix = label

            newName = self._replacements.get(label)
            modFolder = os.path.join(self.outputFolder, label if (newName is None) else newName)
            self._generateOne(label, lambda: self._generateFromFolder(assetsFolder, modFolder, newName))

        for modName in self._getModNames():
            name = modName if (isinstance(modName, str)) else modName.name
            if (self.logger is not None):
                self.logger.prefix = name

            newName = self._replacements.get(name)
            modFolder = os.path.join(self.outputFolder, name if (newName is None) else newName)
            downloadFolder = None if (self.downloadFolder is None) else os.path.join(self.downloadFolder, name)
            self._generateOne(name, lambda: self._generateFromRepo(name, modFolder, downloadFolder, newName))

        if (self.logger is not None):
            self.logger.prefix = prevPrefix
        self.report()

    def report(self):
        """
        Reports the summary of the last :meth:`generate` to the logger
        """

        if (self.logger is None):
            return

        includePrefix = self.logger.includePrefix
        self.logger.includePrefix = False
        self.print("openHeading", "Summary", sideLen = 10)
        self.print("log", f"Generated {len(self._stats.generated)} identity mod(s) into {self.outputFolder}")
        if (self._stats.skipped):
            self.print("log", f"Could not generate {len(self._stats.skipped)}:")
            for name, error in self._stats.skipped.items():
                self.print("bulletPoint", f"{name}: {error}")
        self.print("closeHeading")

        if (self._stats.noErrors):
            self.print("space")
            self.print("log", "ENJOY")
        self.logger.includePrefix = includePrefix
##### EndScript
