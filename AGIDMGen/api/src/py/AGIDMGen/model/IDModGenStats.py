##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Any, Dict
##### EndExtImports


##### Script
class IDModGenStats():
    """
    Class for what a run of :class:`IDModGenService` did: the mods it generated, and the characters it
    could not generate with the exception that stopped each

    Attributes
    ----------
    generated: Dict[:class:`str`, Any]
        The mods generated (:class:`GIMIIdentityMod` or :class:`WWMIIdentityMod`), by the character's name

    skipped: Dict[:class:`str`, :class:`BaseException`]
        The exception that stopped each character that could not be generated, by the character's name (or asset folder)
    """

    def __init__(self):
        self.generated: Dict[str, Any] = {}
        self.skipped: Dict[str, BaseException] = {}

    @property
    def noErrors(self) -> bool:
        """
        Whether every character was generated

        :getter: Retrieves whether no character was skipped
        :type: :class:`bool`
        """

        return not self.skipped

    def addGenerated(self, name: str, mod: Any):
        """
        Records a generated mod

        Parameters
        ----------
        name: :class:`str`
            The character's name

        mod: Any
            The mod generated
        """

        self.generated[name] = mod

    def addSkipped(self, name: str, error: BaseException):
        """
        Records a character that could not be generated

        Parameters
        ----------
        name: :class:`str`
            The character's name (or asset folder)

        error: :class:`BaseException`
            The exception that stopped it
        """

        self.skipped[name] = error

    def clear(self):
        """
        Forgets everything recorded
        """

        self.generated.clear()
        self.skipped.clear()
##### EndScript
