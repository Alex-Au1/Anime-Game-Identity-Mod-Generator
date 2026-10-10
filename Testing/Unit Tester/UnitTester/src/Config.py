from .AGRemapUtils import SysEnum
from .constants.ConfigKeys import ConfigKeys
from .constants.Paths import SrcPath


# The library is only tested as an API. Its single-file script build is the same code flattened, checked by
#   'Tools/ScriptBuilder/main.py --check' and by comparing the mods it writes (see the Testing guide)
SysPaths = {SysEnum.API: SrcPath}

# Initial configurations for the tester
Configs = {ConfigKeys.System: SysEnum.API,
           ConfigKeys.SysPath: SysPaths[SysEnum.API]}
