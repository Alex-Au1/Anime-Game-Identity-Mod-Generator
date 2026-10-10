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
class ModLoaders(Enum):
    """
    The 3DMigoto mod loaders that an identity mod can be generated for

    Attributes
    ----------
    GIMI: :class:`str`
        The `GIMI <https://github.com/SilentNightSound/GI-Model-Importer>`_ mod loader for GI

    WWMI: :class:`str`
        The `WWMI <https://github.com/SpectrumQT/WWMI-Package>`_ mod loader for WuWa
    """

    GIMI = "GIMI"
    WWMI = "WWMI"
##### EndScript
