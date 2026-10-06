import os
import sys

from .constants.Paths import UtilitiesSrcEnvVar


# What the tester uses from AGRemapUtils: the pip-installed package if there is one, otherwise AG Remap's
#   own source, at the folder the AGREMAP_UTILS_SRC environment variable names
try:
    from AGRemapUtils.Utils.tests.BaseTestProgram import BaseTestProgram
    from AGRemapUtils.Utils.exceptions.TesterFailed import TesterFailed
    from AGRemapUtils.Utils.enums.SysEnum import SysEnum
    from AGRemapUtils.Utils.enums.StrEnum import StrEnum
except ImportError:
    utilitiesSrc = os.environ.get(UtilitiesSrcEnvVar)
    if (not utilitiesSrc):
        raise ImportError(f"AGRemapUtils is not installed: 'pip install AGRemapUtils', or set {UtilitiesSrcEnvVar} to '<AG Remap>/Tools/Utilities/src/AGRemapUtils'") from None

    sys.path.insert(1, utilitiesSrc)
    from Utils.tests.BaseTestProgram import BaseTestProgram
    from Utils.exceptions.TesterFailed import TesterFailed
    from Utils.enums.SysEnum import SysEnum
    from Utils.enums.StrEnum import StrEnum
