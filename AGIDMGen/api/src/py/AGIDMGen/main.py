##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import argparse
import sys
from typing import List, Optional
from FixRaidenBoss2 import BaseLogger, Logger
##### EndExtImports


##### LocalImports
from .IDModGenServiceCLI import IDModGenServiceCLI, LogFileName, CharacterListLink
##### EndLocalImports


##### Script
def makeArgParser() -> argparse.ArgumentParser:
    """
    Builds the command line's argument parser

    Returns
    -------
    :class:`argparse.ArgumentParser`
        The parser
    """

    # no abbreviated options: '--download' (an option no more) would otherwise be read as '--downloadFolder'
    parser = argparse.ArgumentParser(prog = "AGIDMGen", description = "Generates the identity mods of characters: the game's own models, written out as mods", allow_abbrev = False,
                                     epilog = "A character can be asked for by its mod's name (eg. Raiden), its download folder's name (RaidenShogun) or an alias (Ei), "
                                              "as Anime Game Remap names its mod types, and of any game: Zani (WuWa) and Ayaka (GI) can be made in one run. "
                                              "The names are not case sensitive, and each mod is written under its mod's name. "
                                              f"For the names and aliases, see {CharacterListLink}")

    parser.add_argument("sources", nargs = "*", help = "the characters' names or aliases, of any game, in any case (eg. Zani Ayaka ei), whose files are downloaded, and/or asset folders (a GI-Model-Importer-Assets or WWMI-Assets character folder, or any path)")
    parser.add_argument("--game", default = None, help = "look the names up only in these games, separated by commas (eg. GI, WuWa, Genshin; default: every game)")
    parser.add_argument("--out", default = None, help = "the folder each mod is written into, as <out>/<name> (default: the current folder)")
    parser.add_argument("--nameReplace", default = None, metavar = "CHARACTER:NEWNAME,...",
                        help = "new names for some of the characters, written into their mods instead of their usual names, eg. \"ei:Raiden1, Zani:Shorty, Carlotta:Shorty\" (CHARACTER is any name or alias of a character being made, a character's base name for all its parts (CarlottaBody becomes ShortyBody), or an asset folder's name; if a character is given twice, the later new name wins; a pair for no character being made, or that cannot be used, is skipped)")
    parser.add_argument("--all", action = "store_true", help = "every character that has a download folder (of --game's games, if given)")
    parser.add_argument("--version", default = None, help = "for downloaded characters: the game version wanted, eg. 4.0 (default: the newest)")
    parser.add_argument("--localData", action = "append", default = None, metavar = "REPO=FOLDER",
                        help = "for downloaded characters: copy a repository's files from a local copy of its 'Data/Mod Downloads' folder instead (REPO is AGRemap or AGIDMGen); repeatable")
    parser.add_argument("--downloadFolder", default = None, help = "for downloaded characters: keep the downloaded files in <downloadFolder>/<name> (default: temporary folders)")
    parser.add_argument("--proxy", default = None, help = "for downloaded characters: the proxy to download through")
    parser.add_argument("--log", default = None, help = f"write everything printed into <log>/{LogFileName}")
    parser.add_argument("--quiet", action = "store_true", help = "print only errors")

    gi = parser.add_argument_group("GI (GIMI) mods")
    gi.add_argument("--assetPrefix", default = None, help = "what the asset folder's files start with, when that is not the folder's name (one asset folder only)")
    gi.add_argument("--noFix", action = "store_true", help = "leave the ORFix / NNFix run lines out of the object sections")
    gi.add_argument("--faceRegister", default = None, help = "the register the face diffuse is bound to (default ps-t1, where GI 6.0 and newer read it; ps-t0 is for older versions)")
    gi.add_argument("--textureFrom", action = "append", default = None, metavar = "COMP=COMP:OBJ[:LAYOUT]",
                    help = "a component with no textures of its own reads another component object's, in the borrower's own normalMap / plain layout (e.g. Bang=Body:A, Eye=Body:A:plain); repeatable")

    wuwa = parser.add_argument_group("WuWa (WWMI) mods")
    wuwa.add_argument("--author", default = None, help = "the mod author WWMI shows (default: AGIDMGen)")
    wuwa.add_argument("--noTextures", action = "store_true", help = "leave the textures out (geometry, skeleton and shape keys only)")
    wuwa.add_argument("--rawBones", action = "store_true", help = "write bone indices as vg_offset + local instead of through the vg_map (the merged skeleton's duplicate slots; every real mod uses the vg_map)")

    return parser


def makeServiceCLI(args: argparse.Namespace, logger: Optional[BaseLogger] = None) -> IDModGenServiceCLI:
    """
    Builds the command line front end from the parsed arguments

    Parameters
    ----------
    args: :class:`argparse.Namespace`
        The parsed arguments, from :func:`makeArgParser`

    logger: Optional[:class:`BaseLogger`]
        Where everything is reported. If this value is ``None``, the front end makes a console ``Logger`` :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Returns
    -------
    :class:`IDModGenServiceCLI`
        The front end
    """

    games = None if (args.game is None) else [game for game in args.game.split(",") if (game.strip())]
    return IDModGenServiceCLI(sources = args.sources, all = args.all, games = games, outputFolder = args.out,
                              nameReplace = args.nameReplace, version = args.version, localData = args.localData, downloadFolder = args.downloadFolder,
                              proxy = args.proxy, author = args.author, noTextures = args.noTextures, rawBones = args.rawBones,
                              assetPrefix = args.assetPrefix, noFix = args.noFix, faceRegister = args.faceRegister, textureFrom = args.textureFrom,
                              log = args.log, verbose = not args.quiet, handleExceptions = True, logger = logger)


def askArgs(logger: BaseLogger) -> List[str]:
    """
    Asks the user which characters to make the identity mods of, for a run with no arguments (eg. the script
    double-clicked)

    :raw-html:`<br />`

    The characters may be of any game, and their mods are made from their download folders, into the current folder

    Parameters
    ----------
    logger: :class:`BaseLogger`
        Where the questions are asked

    Returns
    -------
    List[:class:`str`]
        The arguments the answers stand for, eg. ``["Zani", "Ayaka"]``
    """

    # the questions are shown without the logger's '# prefix -->', as BaseLogger.waitExit shows its own
    prevIncludePrefix = logger.includePrefix
    logger.includePrefix = False
    try:
        logger.log(f"The characters' names and aliases are listed at {CharacterListLink}")
        names = []
        while (not names):
            names = logger.input("Which characters, of any game? Type their names with a space between each (eg. Zani Ayaka), or 'all' for every character: ").split()
        logger.log("")
    finally:
        logger.includePrefix = prevIncludePrefix

    if (len(names) == 1 and names[0].lower() == "all"):
        return ["--all"]
    return names


def main(argv: Optional[List[str]] = None, logger: Optional[BaseLogger] = None) -> int:
    """
    Runs the command line: ``python -m AGIDMGen SOURCE ... [--out FOLDER] [options]``

    :raw-html:`<br />`

    With no arguments (eg. the script double-clicked), asks which characters to make the mods of (see :func:`askArgs`),
    then waits for ENTER before it ends, so the window stays open to be read

    Parameters
    ----------
    argv: Optional[List[:class:`str`]]
        The arguments, without the program name. If this value is ``None``, the arguments of the running program are used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    logger: Optional[:class:`BaseLogger`]
        Where everything is printed and asked. If this value is ``None``, a console ``Logger`` is used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Returns
    -------
    :class:`int`
        The exit code (see :attr:`IDModGenServiceCLI.exitCode`): 0 when every mod was generated, 1 when one could not be (or the arguments are not valid), 2 when a WWMI mod's shape keys do not match its ``Metadata.json``
    """

    if (argv is None):
        argv = sys.argv[1:]

    interactive = not argv
    if (interactive):
        if (logger is None):
            logger = Logger()

        try:
            argv = askArgs(logger)
        except EOFError:
            return 1

    args = makeArgParser().parse_args(argv)
    serviceCLI = makeServiceCLI(args, logger)
    serviceCLI.generate()

    if (interactive):
        try:
            serviceCLI.logger.waitExit()
        except EOFError:
            pass

    return serviceCLI.exitCode
##### EndScript
