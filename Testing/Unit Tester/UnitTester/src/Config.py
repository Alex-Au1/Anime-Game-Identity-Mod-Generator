from .AGRemapUtils import SysEnum
from .constants.ConfigKeys import ConfigKeys
from .constants.Paths import SrcPath


# The library is only tested as an API. Its single-file script build only reaches the API (by a path, or from
#   PyPI), checked by 'Tools/ScriptBuilder/main.py --env prod --check' and by comparing the mods it writes (see the
#   Testing guide)
SysPaths = {SysEnum.API: SrcPath}

# Initial configurations for the tester
Configs = {ConfigKeys.System: SysEnum.API,
           ConfigKeys.SysPath: SysPaths[SysEnum.API]}
