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
class DownloadFailed(Error):
    """
    Exception when a file of a download folder cannot be downloaded

    Parameters
    ----------
    url: :class:`str`
        The address of the file

    reason: :class:`str`
        Why the download failed

    Attributes
    ----------
    url: :class:`str`
        The address of the file
    """

    def __init__(self, url: str, reason: str):
        super().__init__(f"Could not download {url}: {reason}")
        self.url = url
##### EndScript
