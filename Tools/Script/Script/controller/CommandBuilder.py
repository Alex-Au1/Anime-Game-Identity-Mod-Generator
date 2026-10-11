##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits

##### ExtImports
import argparse
from typing import Any, List, Optional, Tuple
##### EndExtImports

##### LocalImports
from .CommandFormatter import CommandFormatter
from .CommandOption import CommandOption
from .enums.CommandOpts import CommandOpts
from .enums.ShortCommandOpts import ShortCommandOpts
##### EndLocalImports


##### Script
class CommandBuilder():
    """
    Handles the options this script adds on top of the API's own

    Parameters
    ----------
    options: Optional[List[:class:`CommandOption`]]
        The options to add :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``
    """

    Description = "Generates the identity mods of characters: the game's own models, written out as mods"
    """
    The description at the top of the help page, the same as the API's
    """

    HelpOpts = (ShortCommandOpts.Help.value, CommandOpts.Help.value)
    """
    The options that ask for the help page
    """

    def __init__(self, options: Optional[List[CommandOption]] = None):
        self.options = [] if (options is None) else options

    def preParse(self, argv: List[str]) -> Tuple[Any, List[str]]:
        """
        Reads only this script's own options, leaving everything else for the API

        :raw-html:`<br />`

        .. note::
            Abbreviations are off. With them on, argparse would happily match a shortened form of an
            *API* option onto one of ours and swallow it.

        Parameters
        ----------
        argv: List[:class:`str`]
            The command line arguments to read

        Returns
        -------
        Tuple[`Namespace`_, List[:class:`str`]]
            The options that were read, with ``help`` set if the help page was asked for, and the arguments
            left over for the API, the help option among them
        """

        parser = argparse.ArgumentParser(add_help = False, allow_abbrev = False)
        for option in self.options:
            option.add(parser.add_argument)

        args, remainingArgs = parser.parse_known_args(argv)

        # the help option is left for the API, which prints the help of whichever game it is given after
        args.help = any(arg in self.HelpOpts for arg in remainingArgs)
        return args, remainingArgs

    def makeParser(self, note: Optional[str] = None, **kwargs) -> argparse.ArgumentParser:
        """
        Makes a parser holding only this script's own options, for printing them

        Parameters
        ----------
        note: Optional[:class:`str`]
            Text to show below the options :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        **kwargs
            More arguments for `argparse's ArgumentParser`_

        Returns
        -------
        `argparse's ArgumentParser`_
            The parser
        """

        parser = argparse.ArgumentParser(epilog = note, formatter_class = CommandFormatter, **kwargs)
        for option in self.options:
            option.add(parser.add_argument)
        return parser

    def printHelp(self, note: Optional[str] = None):
        """
        Prints a help page of only this script's own options

        :raw-html:`<br />`

        For when the API, which owns every other option, is not there to print its own

        Parameters
        ----------
        note: Optional[:class:`str`]
            Text to show below the options :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``
        """

        self.makeParser(note = note, description = self.Description).print_help()

    def printOwnOptions(self):
        """
        Prints this script's own options, below the API's help page

        :raw-html:`<br />`

        The API's command has no place to register them into, so they are printed after its help, and can
        be given anywhere on the command line
        """

        if (not self.options):
            return

        parser = self.makeParser(usage = argparse.SUPPRESS, add_help = False,
                                 description = "This script also takes these options, anywhere on the command line:")
        print(f"\n{parser.format_help()}")
##### EndScript