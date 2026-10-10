##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits

##### LocalImports

# --- Constants --------
from .constants.DumpDataKinds import DumpDataKinds
from .constants.DXGIFormats import DXGIFormats, DXGIFormatPrefix
from .constants.FileEncodings import FileEncodings, IniFileEncoding, ReadEncodings
from .constants.GIMIBuffers import GIMIBuffers, GIMISemanticBuffers, GIMIFixedStrides, GIMIHashFileSuffix
from .constants.GIMITextureLayouts import GIMITextureLayouts
from .constants.ModDownloadRepos import ModDownloadRepos, ModDownloadGameFolders
from .constants.ModLoaders import ModLoaders

# --- Data --------
from .data.ModDownloadData import ModDownloadData, ModDownloadAliases
from .constants.WWMIBuffers import WWMIBuffers, WWMIBlendRemapBuffers, WWMIShapeKeySlots, WWMIBlendRemapSize, WWMIBlendIndexLimit, WWMIDownloadNames, WWMIDownloadTextureSuffix

# --- Exceptions --------
from .exceptions.Error import Error
from .exceptions.BadAssetData import BadAssetData
from .exceptions.DownloadFailed import DownloadFailed
from .exceptions.UnknownDXGIFormat import UnknownDXGIFormat

# --- Model --------
from .model.IDModGenStats import IDModGenStats
from .model.ModDownload import ModDownload
from .model.files.DumpDataType import DumpDataType
from .model.files.DumpElement import DumpElement
from .model.files.FmtFile import FmtFile
from .model.files.IbDumpFile import IbDumpFile
from .model.files.VbDumpFile import VbDumpFile
from .model.gimi.GIMIComponent import GIMIComponent
from .model.gimi.GIMIIdentityMod import GIMIIdentityMod
from .model.gimi.GIMITextureSource import GIMITextureSource
from .model.wwmi.WWMIBlendRemap import WWMIBlendRemap
from .model.wwmi.WWMIComponent import WWMIComponent
from .model.wwmi.WWMIDrawRange import WWMIDrawRange
from .model.wwmi.WWMIMesh import WWMIMesh
from .model.wwmi.WWMIIdentityMod import WWMIIdentityMod
from .model.wwmi.WWMIShapeKeys import WWMIShapeKeys

# --- Tools --------
from .tools.DumpValueTools import DumpValueTools
from .tools.FormatTools import FormatTools
from .tools.ModDownloader import ModDownloader
from .tools.VersionTools import VersionTools
from .tools.gimi.GIMIDownloadFolderBuilder import GIMIDownloadFolderBuilder
from .tools.gimi.GIMIIniBuilder import GIMIIniBuilder
from .tools.gimi.GIMIIdentityModGenerator import GIMIIdentityModGenerator
from .tools.wwmi.WWMIDownloadFolderBuilder import WWMIDownloadFolderBuilder
from .tools.wwmi.WWMIIniBuilder import WWMIIniBuilder
from .tools.wwmi.WWMIIdentityModGenerator import WWMIIdentityModGenerator, WWMITexturePattern

# --- Service --------
from .IDModGenService import IDModGenService

##### EndLocalImports


__all__ = ["IDModGenService", "IDModGenStats",
           "DumpDataKinds", "GIMIBuffers", "GIMISemanticBuffers", "GIMIFixedStrides", "GIMITextureLayouts",
           "DumpDataType", "DumpElement", "IbDumpFile", "VbDumpFile", "GIMIComponent", "GIMIIdentityMod", "GIMITextureSource",
           "DumpValueTools", "GIMIIniBuilder", "GIMIIdentityModGenerator", "GIMIDownloadFolderBuilder", "WWMIDownloadFolderBuilder",
           "ModDownloadRepos", "ModDownloadGameFolders", "ModDownloadData", "ModDownloadAliases", "DownloadFailed", "ModDownload", "ModDownloader", "VersionTools",
           "GIMIHashFileSuffix", "WWMIDownloadNames", "WWMIDownloadTextureSuffix", "WWMIDrawRange", "WWMIMesh",
           "DXGIFormats", "DXGIFormatPrefix", "FileEncodings", "IniFileEncoding", "ReadEncodings", "ModLoaders",
           "WWMIBuffers", "WWMIBlendRemapBuffers", "WWMIShapeKeySlots", "WWMIBlendRemapSize", "WWMIBlendIndexLimit",
           "Error", "BadAssetData", "UnknownDXGIFormat",
           "FmtFile", "WWMIBlendRemap", "WWMIComponent", "WWMIIdentityMod", "WWMIShapeKeys",
           "FormatTools", "WWMIIniBuilder", "WWMIIdentityModGenerator", "WWMITexturePattern"]
