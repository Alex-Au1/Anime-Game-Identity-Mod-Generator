##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
import re
from typing import Iterable, Optional
from FixRaidenBoss2 import Version, VersionSet
##### EndExtImports


##### LocalImports
from ..exceptions.Error import Error
##### EndLocalImports


##### Script
# a game version: numbers separated by '.' (a version) or '_' (a version folder)
_GameVersionPattern = re.compile(r"[0-9]+(?:[._][0-9]+)*")


class VersionTools():
    """
    Tools for the game versions download folders are filed under (``4_0`` for version 4.0), on top of
    Anime Game Remap's ``FixRaidenBoss2.Version`` and ``FixRaidenBoss2.VersionSet``
    """

    @classmethod
    def parse(cls, version: str) -> Version:
        """
        Reads a game version written as a version folder (``4_0``) or as a version (``4.0``)

        .. note::
            Trailing zeros do not count, so ``4``, ``4.0`` and ``4_0_0`` are the same version.

        Parameters
        ----------
        version: :class:`str`
            The version

        Raises
        ------
        :class:`Error`
            If the text is not a version

        Returns
        -------
        ``FixRaidenBoss2.Version``
            The version
        """

        txt = version.strip()
        result = Version.parse(txt.replace("_", ".")) if (_GameVersionPattern.fullmatch(txt)) else None
        if (result is None):
            raise Error(f"'{version}' is not a game version (eg. 4.0 or 4_0)")
        return result

    @classmethod
    def getClosest(cls, versions: Iterable[str], version: Optional[str] = None) -> Optional[str]:
        """
        Chooses one of the available versions, the way Anime Game Remap chooses a version of its asset data
        (``FixRaidenBoss2.VersionSet.findClosest``):

        - no version asked for: the newest
        - otherwise: the newest one that is not newer than the version asked for
        - if every available version is newer than the one asked for: the oldest

        Parameters
        ----------
        versions: Iterable[:class:`str`]
            The available versions (eg. version folder names)

        version: Optional[:class:`str`]
            The version asked for. If this value is ``None``, the newest is chosen :raw-html:`<br />` :raw-html:`<br />`

            **Default**: ``None``

        Raises
        ------
        :class:`Error`
            If a version is not a game version

        Returns
        -------
        Optional[:class:`str`]
            The chosen version, as it was written in ``versions``, or ``None`` if there are no versions
        """

        written = {}
        versionSet = VersionSet()
        for available in versions:
            parsed = cls.parse(available)
            written[parsed.toString()] = available
            versionSet.add(parsed)

        if (not written):
            return None

        chosen = versionSet.findClosest(None if (version is None) else cls.parse(version))
        return written[chosen.toString()]
##### EndScript
