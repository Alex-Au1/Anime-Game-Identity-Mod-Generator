##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits

##### ExtImports
import importlib
import importlib.machinery
import subprocess
import sys
from typing import Any, List
##### EndExtImports

##### LocalImports
from ..controller.CommandOption import CommandOption
from ..controller.enums.CommandOpts import CommandOpts
from ..controller.enums.ShortCommandOpts import ShortCommandOpts
from ..constants.Links import DocsCommandOptsUrl
from .BaseApiRef import BaseApiRef
##### EndLocalImports


##### Script
class PackageApiRef(BaseApiRef):
    """
    This class inherits from :class:`BaseApiRef`

    :raw-html:`<br />`

    Downloads the API from `pypi`_ at runtime with `pip`_, which also brings the API's own dependencies
    (numpy, FixRaidenBoss2)

    Parameters
    ----------
    package: :class:`str`
        The API, both as a module to import and as an installation name
    """

    def getOptions(self) -> List[CommandOption]:
        return [
            CommandOption((ShortCommandOpts.DisableUpdate.value, CommandOpts.DisableUpdate.value),
                          {"action": "store_true",
                           "help": f"Skips updating '{self.package}' to its latest version before running. With this option, the package is only downloaded when it is not already installed."}),

            CommandOption((ShortCommandOpts.PreRelease.value, CommandOpts.PreRelease.value),
                          {"action": "store_true",
                           "help": f"Also considers prereleases of '{self.package}' when downloading it"})
        ]

    def getInstallCommand(self, args: Any) -> List[str]:
        """
        The `pip`_ command that downloads the API

        Parameters
        ----------
        args: `Namespace`_
            This script's own options, already read

        Returns
        -------
        List[:class:`str`]
            The command, starting with the running python
        """

        result = [sys.executable, "-m", "pip", "install", "-U"]

        if (getattr(args, "preRelease", False)):
            result.append("--pre")

        return result + [self.package]

    def isInstalled(self) -> bool:
        """
        Whether the API can already be imported

        Returns
        -------
        :class:`bool`
            Whether the API is available
        """

        # a search of the import path rather than an import: importing an old version here would leave it
        #   cached in sys.modules, and the script would keep running it after pip has upgraded the package
        return importlib.machinery.PathFinder.find_spec(self.package, self.getImportPath()) is not None

    def canShowFullHelp(self, args: Any) -> bool:
        # printing help never downloads or updates the API, so the full help needs it already installed
        return self.isInstalled()

    def getHelpNote(self) -> str:
        return f"""NOTE:
'{self.package}', the library that makes the identity mods, is not installed on this computer yet,
so only this script's own options are shown above. It is downloaded the first time you run this
script without {CommandOpts.Help.value}.

The full list of options is at:
{DocsCommandOptsUrl}"""

    def prepare(self, args: Any):
        # printing help is not a generating session, so it does not update an installed API either
        skipUpdate = getattr(args, "disableUpdate", False) or getattr(args, "help", False)

        if (skipUpdate and self.isInstalled()):
            return

        command = self.getInstallCommand(args)
        print(f"Getting the latest version of '{self.package}' (pass {CommandOpts.DisableUpdate.value} to skip this)...")
        try:
            subprocess.check_call(command)
        except (OSError, subprocess.CalledProcessError):
            # an installed copy still runs when it only could not be updated (eg. no internet)
            if (self.isInstalled()):
                print(f"Could not update '{self.package}'; running the version already installed")
                return

            # quoted, since a shell reads the '>' of a requirement as a redirection
            commandStr = " ".join(f'"{part}"' for part in command)
            print(f"Could not download '{self.package}'. Install it yourself with: {commandStr}")
            sys.exit(1)

        # a package installed during this run is not on any import path that was cached before it
        #   arrived, so the caches have to be dropped before the import can find it
        importlib.invalidate_caches()
##### EndScript