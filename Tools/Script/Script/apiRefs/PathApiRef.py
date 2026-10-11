##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits

##### ExtImports
import os
import sys
from typing import Any, Optional
##### EndExtImports

##### LocalImports
from ..constants.BuildData import ApiRelPath
from .BaseApiRef import BaseApiRef
##### EndLocalImports


##### Script
class PathApiRef(BaseApiRef):
    """
    This class inherits from :class:`BaseApiRef`

    :raw-html:`<br />`

    Reaches the API by a path on this machine, the way every tool in this repo reaches the others

    :raw-html:`<br />`

    .. note::
        The API's own dependencies (numpy, FixRaidenBoss2) must already be importable

    Parameters
    ----------
    package: :class:`str`
        The API, both as a module to import and as an installation name

    apiPath: Optional[:class:`str`]
        The folder holding the API's package :raw-html:`<br />` :raw-html:`<br />`

        When this is ``None``, the path is worked out from where this script sits, using the
        relative path the ScriptBuilder compiled in :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``
    """

    def __init__(self, package: str, apiPath: Optional[str] = None):
        super().__init__(package)
        self._apiPath = apiPath

    def getApiPath(self) -> str:
        """
        The folder holding the API's package

        Returns
        -------
        :class:`str`
            The folder
        """

        if (self._apiPath is not None):
            return self._apiPath

        scriptFolder = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(scriptFolder, *ApiRelPath.split("/")))

    def prepare(self, args: Any):
        apiPath = self.getApiPath()

        if (not os.path.isdir(apiPath)):
            raise FileNotFoundError(f"This is a 'dev' build of the script, which expects the API's source at: {apiPath}")

        # first, so the source wins over any installed release of the API
        sys.path.insert(0, apiPath)
##### EndScript