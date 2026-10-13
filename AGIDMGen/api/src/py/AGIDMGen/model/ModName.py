##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import List, Optional
##### EndExtImports


##### LocalImports
from ..constants.ModLoaders import ModLoaders
##### EndLocalImports


##### Script
class ModName():
    """
    Class for the names of one character's identity mod: the name the mod is written with, the other names it
    can be asked for by, and the download folder it is generated from

    :raw-html:`<br />`

    .. container:: operations

        **Supported Operations:**

        .. describe:: str(x)

            Retrieves :attr:`name`

    Parameters
    ----------
    loader: :class:`ModLoaders`
        The mod loader the character's mods are for

    name: :class:`str`
        The name of the mod, as Anime Game Remap names its mod types (eg. ``Raiden``, or ``AyakaSpringBloom`` for a skin)

    folder: :class:`str`
        The name of the character's download folder (eg. ``RaidenShogun``)

    aliases: Optional[List[:class:`str`]]
        The other names of the mod (eg. ``RaidenEi``). If this value is ``None``, the mod has no other names :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    base: Optional[:class:`str`]
        When the mod is one part of a character's model (eg. ``CarlottaBody``), the character's base name, which :attr:`name` starts with (eg. ``Carlotta``). If this value is ``None``, the mod is a whole character :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Attributes
    ----------
    loader: :class:`ModLoaders`
        The mod loader the character's mods are for

    name: :class:`str`
        The name of the mod

    folder: :class:`str`
        The name of the character's download folder

    aliases: List[:class:`str`]
        The other names of the mod

    base: Optional[:class:`str`]
        When the mod is one part of a character's model, the character's base name, or ``None``
    """

    def __init__(self, loader: ModLoaders, name: str, folder: str, aliases: Optional[List[str]] = None, base: Optional[str] = None):
        if (base is not None and (not name.startswith(base) or name == base)):
            raise ValueError(f"the part {name} does not start with its base name, {base}")

        self.loader = loader
        self.name = name
        self.folder = folder
        self.aliases = [] if (aliases is None) else list(aliases)
        self.base = base

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"ModName({self.loader.value}, {self.name!r}, folder = {self.folder!r})"

    @property
    def names(self) -> List[str]:
        """
        Every name the mod can be asked for by: :attr:`name`, then :attr:`aliases`

        :getter: Retrieves the names
        :type: List[:class:`str`]
        """

        return [self.name] + self.aliases

    @property
    def part(self) -> Optional[str]:
        """
        When the mod is one part of a character's model, which part: :attr:`name` after :attr:`base` (eg. ``Body`` for ``CarlottaBody``)

        :getter: Retrieves the part, or ``None`` if the mod is a whole character
        :type: Optional[:class:`str`]
        """

        return None if (self.base is None) else self.name[len(self.base):]
##### EndScript
