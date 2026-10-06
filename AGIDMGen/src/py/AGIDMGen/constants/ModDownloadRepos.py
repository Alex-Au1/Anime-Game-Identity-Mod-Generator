##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from enum import Enum
from typing import Dict
##### EndExtImports


##### LocalImports
from .ModLoaders import ModLoaders
##### EndLocalImports


##### Script
class ModDownloadRepos(Enum):
    """
    The repositories that hold characters' download folders, in the order they are searched: a file Anime
    Game Remap has is taken from Anime Game Remap, so it is never kept twice. Each value is the address of
    the repository's ``Data/Mod Downloads`` folder

    Attributes
    ----------
    AGRemap: :class:`str`
        `Anime Game Remap <https://github.com/nhok0169/Anime-Game-Remap>`_'s download folders

    AGIDMGen: :class:`str`
        This library's own download folders, for what Anime Game Remap does not have
    """

    AGRemap = "https://github.com/nhok0169/Anime-Game-Remap/raw/master/Data/Mod%20Downloads"
    AGIDMGen = "https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/raw/main/Data/Mod%20Downloads"


#: The folder of each mod loader's game in ``Data/Mod Downloads``
ModDownloadGameFolders: Dict[ModLoaders, str] = {ModLoaders.GIMI: "GI", ModLoaders.WWMI: "WuWa"}
##### EndScript
