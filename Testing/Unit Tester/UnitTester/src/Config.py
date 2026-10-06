from .AGRemapUtils import SysEnum
from .constants.ConfigKeys import ConfigKeys
from .constants.Paths import SrcPath


# The library is only tested as an API: it has no single-file script build
SysPaths = {SysEnum.API: SrcPath}

# Initial configurations for the tester
Configs = {ConfigKeys.System: SysEnum.API,
           ConfigKeys.SysPath: SysPaths[SysEnum.API]}
