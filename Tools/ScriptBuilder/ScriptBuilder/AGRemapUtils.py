import os
import sys

from .constants.Paths import UtilitiesSrcEnvVar


# What the builder uses from AGRemapUtils: the pip-installed package if there is one, otherwise AG Remap's
#   own source, at the folder the AGREMAP_UTILS_SRC environment variable names
try:
    from AGRemapUtils.Utils.scriptBuilder.ScriptBuilder import ScriptBuilder
    from AGRemapUtils.Utils.python.PyFile import PyFile
    from AGRemapUtils.Utils.python.FromImport import FromImport
    from AGRemapUtils.Utils.path.PyPathTools import PyPathTools
    from AGRemapUtils.Utils.softwareStats.BuildMetadata import BuildMetadata
    from AGRemapUtils.Utils.constants.BoilerPlate import ScriptChangeDir, ScriptPostamble
    from AGRemapUtils.Utils.constants.StrReplacements import VersionReplace, RanDateTimeReplace, RanHashReplace, BuiltDateTimeReplace, BuildHashReplace
except ImportError:
    utilitiesSrc = os.environ.get(UtilitiesSrcEnvVar)
    if (not utilitiesSrc):
        raise ImportError(f"AGRemapUtils is not installed: 'pip install AGRemapUtils', or set {UtilitiesSrcEnvVar} to '<AG Remap>/Tools/Utilities/src/AGRemapUtils'") from None

    sys.path.insert(1, utilitiesSrc)
    from Utils.scriptBuilder.ScriptBuilder import ScriptBuilder
    from Utils.python.PyFile import PyFile
    from Utils.python.FromImport import FromImport
    from Utils.path.PyPathTools import PyPathTools
    from Utils.softwareStats.BuildMetadata import BuildMetadata
    from Utils.constants.BoilerPlate import ScriptChangeDir, ScriptPostamble
    from Utils.constants.StrReplacements import VersionReplace, RanDateTimeReplace, RanHashReplace, BuiltDateTimeReplace, BuildHashReplace
