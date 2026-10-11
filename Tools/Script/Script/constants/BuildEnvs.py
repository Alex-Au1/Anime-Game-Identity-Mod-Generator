##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits

##### ExtImports
from enum import Enum
from typing import Optional
##### EndExtImports


##### Script
class BuildEnv(Enum):
    """
    The environment a build of this script was made for
    """

    Dev = "dev"
    """
    Reaches the API by a path on this machine, the way the tools in this repo reach each other
    """

    Prod = "prod"
    """
    Downloads the API from `pypi`_ at runtime
    """

    @classmethod
    def match(cls, name: str) -> Optional["BuildEnv"]:
        """
        Retrieves the environment by name

        Parameters
        ----------
        name: :class:`str`
            The name of the environment

        Returns
        -------
        Optional[:class:`BuildEnv`]
            The found environment, or ``None``
        """

        name = name.lower().strip()
        for env in cls:
            if (env.value == name):
                return env

        return None
##### EndScript