##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits

##### ExtImports
from enum import Enum
##### EndExtImports


##### Script
class ShortCommandOpts(Enum):
    """
    The short forms of the options this script adds on top of the API's own
    """

    DisableUpdate = "-dup"
    PreRelease = "-pre"
    Help = "-h"
##### EndScript