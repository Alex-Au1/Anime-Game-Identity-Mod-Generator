##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import argparse
import os
import sys
from typing import List, Optional
from FixRaidenBoss2 import Logger
##### EndExtImports


##### LocalImports
from .IDModGenService import IDModGenService
from .constants.FileEncodings import FileEncodings
from .constants.ModDownloadRepos import ModDownloadRepos
from .constants.ModLoaders import ModLoaders
from .exceptions.Error import Error
from .model.gimi.GIMITextureSource import GIMITextureSource
from .tools.ModDownloader import ModDownloader
from .tools.gimi.GIMIIdentityModGenerator import GIMIIdentityModGenerator
from .tools.wwmi.WWMIIdentityModGenerator import WWMIIdentityModGenerator
##### EndLocalImports


##### Script
#: The name of the log file the command line writes with ``--log``
LogFileName = "IDModGenLog.txt"


def makeArgParser() -> argparse.ArgumentParser:
    """
    Builds the command line's argument parser

    Returns
    -------
    :class:`argparse.ArgumentParser`
        The parser
    """

    parser = argparse.ArgumentParser(prog = "AGIDMGen", description = "Generates the identity mods of characters: the game's own models, written out as mods")
    loaders = parser.add_subparsers(dest = "loader", required = True)

    wwmi = loaders.add_parser(ModLoaders.WWMI.value.lower(), aliases = [ModLoaders.WWMI.value], help = "Wuthering Waves characters, from WWMI-Assets folders or download folders")
    wwmi.add_argument("sources", nargs = "*", help = "the asset folders (Metadata.json, Component N.fmt/.vb/.ib, *.dds), or with --download the characters' names")
    wwmi.add_argument("--author", default = "Anime Game Remap", help = "the mod author WWMI shows")
    wwmi.add_argument("--noTextures", action = "store_true", help = "leave the textures out (geometry, skeleton and shape keys only)")
    wwmi.add_argument("--rawBones", action = "store_true", help = "write bone indices as vg_offset + local instead of through the vg_map (the merged skeleton's duplicate slots; every real mod uses the vg_map)")

    gimi = loaders.add_parser(ModLoaders.GIMI.value.lower(), aliases = [ModLoaders.GIMI.value], help = "Genshin Impact characters, from GI-Model-Importer-Assets folders or download folders")
    gimi.add_argument("sources", nargs = "*", help = "the asset folders (hash.json, *-vb0=*.txt, *-ib=*.txt, *.dds), or with --download the characters' names")
    gimi.add_argument("--assetPrefix", default = None, help = "what the asset folder's files start with, when that is not the folder's name (one asset folder only)")
    gimi.add_argument("--noFix", action = "store_true", help = "leave the ORFix / NNFix run lines out of the object sections")
    gimi.add_argument("--faceRegister", default = "ps-t0", help = "the register the face diffuse is bound to (GI 6.x swapped it to ps-t1 on some skins; default ps-t0)")
    gimi.add_argument("--textureFrom", action = "append", default = None, metavar = "COMP=COMP:OBJ[:LAYOUT]",
                      help = "a component with no textures of its own reads another component object's, in the borrower's own normalMap / plain layout (e.g. Bang=Body:A, Eye=Body:A:plain); repeatable")

    for subparser in (wwmi, gimi):
        subparser.add_argument("--out", default = None, help = "the folder each mod is written into, as <out>/<name> (default: the current folder)")
        subparser.add_argument("--name", default = None, help = "the character's name in the mod (one character only)")
        subparser.add_argument("--download", action = "store_true", help = "the sources are characters' names: generate from their download folders (from AG Remap's repository, then this library's)")
        subparser.add_argument("--all", action = "store_true", help = "with --download: every character that has a download folder")
        subparser.add_argument("--version", default = None, help = "with --download: the game version wanted, eg. 4.0 (default: the newest)")
        subparser.add_argument("--localData", action = "append", default = None, metavar = "REPO=FOLDER",
                               help = "with --download: copy a repository's files from a local copy of its 'Data/Mod Downloads' folder instead (REPO is AGRemap or AGIDMGen); repeatable")
        subparser.add_argument("--downloadFolder", default = None, help = "with --download: keep the downloaded files in <downloadFolder>/<name> (default: temporary folders)")
        subparser.add_argument("--proxy", default = None, help = "with --download: the proxy to download through")
        subparser.add_argument("--log", default = None, help = f"write everything printed into <log>/{LogFileName}")
        subparser.add_argument("--quiet", action = "store_true", help = "print only errors")

    return parser


def makeService(args: argparse.Namespace, logger: Logger) -> IDModGenService:
    """
    Builds the service the command line runs

    Parameters
    ----------
    args: :class:`argparse.Namespace`
        The parsed arguments, from :func:`makeArgParser`

    logger: :class:`Logger`
        Where the service reports what it does

    Raises
    ------
    :class:`Error`
        If the arguments are not valid

    Returns
    -------
    :class:`IDModGenService`
        The service
    """

    loader = ModLoaders.GIMI if (args.loader.upper() == ModLoaders.GIMI.value) else ModLoaders.WWMI
    if (loader == ModLoaders.GIMI):
        textureSources = dict(GIMITextureSource.parse(value) for value in (args.textureFrom or []))
        generator = GIMIIdentityModGenerator(includeFix = not args.noFix, faceRegister = args.faceRegister, textureSources = textureSources, logger = logger)
    else:
        generator = WWMIIdentityModGenerator(author = args.author, includeTextures = not args.noTextures, useVgMap = not args.rawBones, logger = logger)

    localFolders = {}
    for value in (args.localData or []):
        repo, separator, folder = value.partition("=")
        if (not separator or repo not in ModDownloadRepos.__members__):
            raise Error(f"--localData is REPO=FOLDER with REPO one of {', '.join(ModDownloadRepos.__members__)}, not {value!r}")
        localFolders[ModDownloadRepos[repo]] = folder

    if (args.all and not args.download):
        raise Error("--all is for --download")

    names = None
    assetsFolders = None
    if (args.download):
        names = ModDownloader.getCharacters(loader) if (args.all) else args.sources
    else:
        assetsFolders = args.sources

    return IDModGenService(loader, assetsFolders = assetsFolders, names = names, outputFolder = args.out, version = args.version,
                           downloader = ModDownloader(localFolders = localFolders, proxy = args.proxy, logger = logger), downloadFolder = args.downloadFolder,
                           generator = generator, modName = args.name, assetPrefix = getattr(args, "assetPrefix", None), handleExceptions = True, logger = logger)


def main(argv: Optional[List[str]] = None) -> int:
    """
    Runs the command line: ``python -m AGIDMGen <gimi|wwmi> SOURCE ... [--out FOLDER] [options]``

    Parameters
    ----------
    argv: Optional[List[:class:`str`]]
        The arguments, without the program name. If this value is ``None``, the arguments of the running program are used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Returns
    -------
    :class:`int`
        The exit code: 0 when every mod was generated, 1 when one could not be (or the arguments are not valid), 2 when a WWMI mod's shape keys do not match its ``Metadata.json``
    """

    args = makeArgParser().parse_args(argv)
    logger = Logger(logTxt = args.log is not None, verbose = not args.quiet)

    try:
        service = makeService(args, logger)
    except Error as e:
        logger.error(str(e))
        return 1

    service.generate()
    if (args.log is not None):
        os.makedirs(args.log, exist_ok = True)
        with open(os.path.join(args.log, LogFileName), "w", encoding = FileEncodings.UTF8.value) as f:
            f.write(logger.loggedTxt)

    stats = service.stats
    if (not stats.noErrors or not stats.generated):
        return 1
    if (any(getattr(mod, "checksumMatches", None) is False or getattr(mod, "dispatchYMatches", None) is False for mod in stats.generated.values())):
        return 2
    return 0
##### EndScript
