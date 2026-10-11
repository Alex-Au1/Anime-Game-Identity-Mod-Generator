##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits

##### ExtImports
import importlib
import os
import sys
from types import ModuleType
from typing import Any, Callable, List, Set
##### EndExtImports

##### LocalImports
from ..controller.CommandOption import CommandOption
##### EndLocalImports


##### Script
class BaseApiRef():
    """
    Base class for how a build of this script reaches the API

    :raw-html:`<br />`

    .. note::
        The script is only a thin front for the API: it makes the API importable, then hands it the
        command line

    Parameters
    ----------
    package: :class:`str`
        The API, both as a module to import and as an installation name

    Attributes
    ----------
    package: :class:`str`
        The API, both as a module to import and as an installation name
    """

    def __init__(self, package: str):
        self.package = package

    def getOptions(self) -> List[CommandOption]:
        """
        The command line options this way of reaching the API needs

        Returns
        -------
        List[:class:`CommandOption`]
            The options, which are empty for a reference that needs none
        """

        return []

    def canShowFullHelp(self, args: Any) -> bool:
        """
        Whether the API's own ``--help`` page, listing every option, can be shown for this run

        :raw-html:`<br />`

        When it cannot, the script shows a page of only its own options instead, rather than
        fetching the whole API just to print help

        Parameters
        ----------
        args: `Namespace`_
            This script's own options, already read

        Returns
        -------
        :class:`bool`
            Whether the API's help page can be shown
        """

        return True

    def getHelpNote(self) -> str:
        """
        The note shown at the bottom of the script's own help page, when the API's help page cannot
        be shown

        Returns
        -------
        :class:`str`
            The note
        """

        return f"'{self.package}', the library that makes the identity mods, is not available, so only this script's own options are shown above."

    def prepare(self, args: Any):
        """
        Makes the API importable

        Parameters
        ----------
        args: `Namespace`_
            This script's own options, already read
        """

        pass

    def getShadowFolders(self) -> Set[str]:
        """
        The folders the API must not be imported from

        :raw-html:`<br />`

        The compiled script is named after the API (``AGIDMGen.py``), and its folder is a package of the same
        name, so a plain import would find the script itself before the API

        Returns
        -------
        Set[:class:`str`]
            The folders, normalized with `os.path.normcase`_
        """

        scriptFolder = os.path.dirname(os.path.abspath(__file__))
        return {os.path.normcase(scriptFolder), os.path.normcase(os.path.dirname(scriptFolder))}

    def isShadowed(self, path: str) -> bool:
        """
        Whether a folder is one of :meth:`getShadowFolders`

        Parameters
        ----------
        path: :class:`str`
            The folder. An empty string is the current folder, as in ``sys.path``

        Returns
        -------
        :class:`bool`
            Whether the API must not be imported from the folder
        """

        return os.path.normcase(os.path.abspath(path or os.curdir)) in self.getShadowFolders()

    def getImportPath(self) -> List[str]:
        """
        The import path, without the folders of :meth:`getShadowFolders`

        Returns
        -------
        List[:class:`str`]
            The folders to import the API from
        """

        return [path for path in sys.path if not self.isShadowed(path)]

    def importApi(self) -> ModuleType:
        """
        Imports the API, from anywhere but the folders of :meth:`getShadowFolders`

        Returns
        -------
        `Module`_
            The API's module
        """

        # run as a package (python -m), the script build itself is already imported under the API's name
        shadow = sys.modules.get(self.package)
        if (shadow is not None and self.isShadowed(os.path.dirname(getattr(shadow, "__file__", None) or ""))):
            del sys.modules[self.package]

        oldPath = sys.path[:]
        sys.path[:] = self.getImportPath()
        try:
            return importlib.import_module(self.package)
        finally:
            sys.path[:] = oldPath

    def load(self, args: Any) -> ModuleType:
        """
        Retrieves the API

        Parameters
        ----------
        args: `Namespace`_
            This script's own options, already read

        Returns
        -------
        `Module`_
            The API's module
        """

        self.prepare(args)
        return self.importApi()

    def loadMain(self, args: Any) -> Callable[[List[str]], int]:
        """
        Retrieves the API's command line: the ``main`` function of its ``main`` module, the one
        ``python -m AGIDMGen`` runs

        Parameters
        ----------
        args: `Namespace`_
            This script's own options, already read

        Returns
        -------
        Callable[[List[:class:`str`]], :class:`int`]
            The function, taking the arguments without the program name and returning the exit code
        """

        api = self.load(args)

        # imported through the package, which is already loaded, so the import path does not matter here
        return importlib.import_module(f"{api.__name__}.main").main
##### EndScript