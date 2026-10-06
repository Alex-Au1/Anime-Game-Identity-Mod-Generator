##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import os
from typing import Any, List, Optional, Union
from FixRaidenBoss2 import BaseLogger, Model
##### EndExtImports


##### LocalImports
from .constants.ModLoaders import ModLoaders
from .exceptions.Error import Error
from .model.IDModGenStats import IDModGenStats
from .tools.ModDownloader import ModDownloader
from .tools.gimi.GIMIIdentityModGenerator import GIMIIdentityModGenerator
from .tools.wwmi.WWMIIdentityModGenerator import WWMIIdentityModGenerator
##### EndLocalImports


##### Script
class IDModGenService(Model):
    """
    The library's entry point: generates the identity mods of several characters at once, from their asset
    folders or from their download folders, and reports what it did

    It is the model half, with no user interface of its own: progress and the summary go to the
    :attr:`logger` (nothing is reported without one), and the results are in :attr:`stats`. A character that
    cannot be generated does not stop the others: its exception is recorded in :attr:`IDModGenStats.skipped`.

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

        # every character's newest download folder, printed as it goes
        service = IDMG.IDModGenService(IDMG.ModLoaders.GIMI, names = ["Yelan", "Ayaka"], outputFolder = "Mods", logger = FRB.Logger())
        service.generate()
        print(sorted(service.stats.generated), service.stats.skipped)

        # from asset folders, collecting the output instead of printing it (eg. in a server)
        logger = FRB.Logger(logTxt = True, verbose = False)
        service = IDMG.IDModGenService(IDMG.ModLoaders.WWMI, assetsFolders = ["WWMI-Assets/PlayerCharacterData/Sanhua"], logger = logger)
        service.generate()
        print(logger.loggedTxt)

    Parameters
    ----------
    loader: :class:`ModLoaders`
        The mod loader the mods are for

    assetsFolders: Optional[List[:class:`str`]]
        The characters' asset folders to generate from. If this value is ``None``, no asset folder is used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    names: Optional[List[:class:`str`]]
        The characters to generate from their download folders (see :meth:`ModDownloader.getName`). If this value is ``None``, no download folder is used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    outputFolder: Optional[:class:`str`]
        The folder each mod is written into, as ``<outputFolder>/<name>``. If this value is ``None``, the current folder is used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    version: Optional[:class:`str`]
        The game version wanted for the download folders (see :meth:`ModDownloader.find`). If this value is ``None``, the newest :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    downloader: Optional[:class:`ModDownloader`]
        What downloads the download folders. If this value is ``None``, one that downloads every file :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    downloadFolder: Optional[:class:`str`]
        The folder to keep the downloaded files in, as ``<downloadFolder>/<name>``. If this value is ``None``, temporary folders are used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    generator: Optional[Union[:class:`GIMIIdentityModGenerator`, :class:`WWMIIdentityModGenerator`]]
        The generator, with its options. If this value is ``None``, one for ``loader`` with its default options :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    modName: Optional[:class:`str`]
        The name of the character in the mod, when there is only one character. If this value is ``None``, the generator's default :raw-html:`<br />` :raw-html:`<br />`

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
    loader: :class:`ModLoaders`
        The mod loader the mods are for

    assetsFolders: List[:class:`str`]
        The characters' asset folders to generate from

    names: List[:class:`str`]
        The characters to generate from their download folders

    outputFolder: :class:`str`
        The folder each mod is written into

    version: Optional[:class:`str`]
        The game version wanted for the download folders

    downloader: :class:`ModDownloader`
        What downloads the download folders

    downloadFolder: Optional[:class:`str`]
        The folder to keep the downloaded files in

    generator: Union[:class:`GIMIIdentityModGenerator`, :class:`WWMIIdentityModGenerator`]
        The generator

    modName: Optional[:class:`str`]
        The name of the character in the mod, when there is only one character

    assetPrefix: Optional[:class:`str`]
        What a GIMI asset folder's files start with, when there is only one asset folder

    handleExceptions: :class:`bool`
        Whether a failure of the whole run is reported rather than raised
    """

    def __init__(self, loader: ModLoaders, assetsFolders: Optional[List[str]] = None, names: Optional[List[str]] = None, outputFolder: Optional[str] = None,
                 version: Optional[str] = None, downloader: Optional[ModDownloader] = None, downloadFolder: Optional[str] = None,
                 generator: Optional[Union[GIMIIdentityModGenerator, WWMIIdentityModGenerator]] = None, modName: Optional[str] = None,
                 assetPrefix: Optional[str] = None, handleExceptions: bool = False, logger: Optional[BaseLogger] = None):
        super().__init__(logger = logger)
        self.loader = loader
        self.assetsFolders = [] if (assetsFolders is None) else list(assetsFolders)
        self.names = [] if (names is None) else list(names)
        self.outputFolder = os.getcwd() if (outputFolder is None) else outputFolder
        self.version = version
        self.downloader = ModDownloader(logger = logger) if (downloader is None) else downloader
        self.downloadFolder = downloadFolder
        self.generator = generator
        self.modName = modName
        self.assetPrefix = assetPrefix
        self.handleExceptions = handleExceptions
        self._stats = IDModGenStats()

    @property
    def stats(self) -> IDModGenStats:
        """
        What the last :meth:`generate` did

        :getter: Retrieves the stats
        :type: :class:`IDModGenStats`
        """

        return self._stats

    def _getGenerator(self) -> Union[GIMIIdentityModGenerator, WWMIIdentityModGenerator]:
        expected = GIMIIdentityModGenerator if (self.loader == ModLoaders.GIMI) else WWMIIdentityModGenerator
        if (self.generator is None):
            return expected(logger = self.logger)
        if (not isinstance(self.generator, expected)):
            raise Error(f"a {type(self.generator).__name__} cannot generate {self.loader.value} mods")
        if (self.generator.logger is None):
            self.generator.logger = self.logger
        return self.generator

    def _checkOptions(self):
        sourceCount = len(self.assetsFolders) + len(self.names)
        if (sourceCount == 0):
            raise Error("there is nothing to generate: give asset folders or character names")
        if (self.modName is not None and sourceCount > 1):
            raise Error("a mod name can only be given for one character")
        if (self.assetPrefix is not None and (len(self.assetsFolders) != 1 or self.names)):
            raise Error("an asset prefix can only be given for one asset folder")
        if (self.assetPrefix is not None and self.loader != ModLoaders.GIMI):
            raise Error("an asset prefix is only for GIMI asset folders")

    def _reportException(self, error: BaseException):
        # the library's own errors explain themselves; anything else is a bug, and gets its traceback
        if (isinstance(error, Error)):
            self.print("error", str(error))
        else:
            self.print("handleException", error)

    def _generateOne(self, generator, label: str, generate) -> Optional[Any]:
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
            generator = self._getGenerator()
        except Exception as e:
            if (not self.handleExceptions):
                raise
            self._reportException(e)
            return

        prevPrefix = None if (self.logger is None) else self.logger.prefix
        for assetsFolder in self.assetsFolders:
            label = os.path.basename(os.path.normpath(assetsFolder))
            if (self.logger is not None):
                self.logger.prefix = label

            kwargs = {"name": self.modName}
            if (self.loader == ModLoaders.GIMI):
                kwargs["assetPrefix"] = self.assetPrefix
            modFolder = os.path.join(self.outputFolder, self.modName if (self.modName is not None) else label)
            self._generateOne(generator, label, lambda: generator.generate(assetsFolder, modFolder, **kwargs))

        for name in self.names:
            if (self.logger is not None):
                self.logger.prefix = name

            modFolder = os.path.join(self.outputFolder, self.modName if (self.modName is not None) else name)
            downloadFolder = None if (self.downloadFolder is None) else os.path.join(self.downloadFolder, name)
            self._generateOne(generator, name, lambda: generator.generateFromRepo(name, modFolder, version = self.version, downloader = self.downloader,
                                                                                  downloadFolder = downloadFolder, modName = self.modName))

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
