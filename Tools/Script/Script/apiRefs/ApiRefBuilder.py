##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits

##### LocalImports
from ..constants.BuildData import ApiPackage, EnvName
from ..constants.BuildEnvs import BuildEnv
from .BaseApiRef import BaseApiRef
from .PackageApiRef import PackageApiRef
from .PathApiRef import PathApiRef
##### EndLocalImports


##### Script
class ApiRefBuilder():
    """
    Picks how this build of the script reaches the API
    """

    @classmethod
    def build(cls) -> BaseApiRef:
        """
        Retrieves the way this build of the script reaches the API

        Returns
        -------
        :class:`BaseApiRef`
            How to reach the API
        """

        if (BuildEnv.match(EnvName) == BuildEnv.Prod):
            return PackageApiRef(ApiPackage)

        return PathApiRef(ApiPackage)
##### EndScript