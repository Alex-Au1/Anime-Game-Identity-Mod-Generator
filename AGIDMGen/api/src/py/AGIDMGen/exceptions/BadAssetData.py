##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### LocalImports
from .Error import Error
##### EndLocalImports


##### Script
class BadAssetData(Error):
    """
    Exception when a character's asset folder is missing a file, or holds data that does not agree with
    itself (eg. a buffer whose size does not match the vertex count its metadata declares)

    Parameters
    ----------
    message: :class:`str`
        What is missing or wrong in the asset folder
    """

    def __init__(self, message: str):
        super().__init__(message)
##### EndScript
