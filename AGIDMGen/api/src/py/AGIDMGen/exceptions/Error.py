##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### Script
class Error(Exception):
    """
    The base exception used by this module

    Parameters
    ----------
    message: :class:`str`
        the error message to print out
    """

    def __init__(self, message: str):
        super().__init__(f"ERROR: {message}")
##### EndScript
