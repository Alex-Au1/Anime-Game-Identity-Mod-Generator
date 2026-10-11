##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits

##### ExtImports
from typing import Any, Callable, Dict, Optional, Tuple
##### EndExtImports


##### Script
class CommandOption():
    """
    A single command line option, declared once and registered in more than one place

    :raw-html:`<br />`

    .. note::
        This script has to read some of its options *before* the API exists to parse them: whether to
        skip updating the API's package decides whether the package gets downloaded at all. So each option
        is registered into a throwaway parser that reads it early, and into the help page of this script's
        own options

    Parameters
    ----------
    args: Tuple[Any, ...]
        The positional arguments to hand to `argparse's add_argument`_

    kwargs: Optional[Dict[:class:`str`, Any]]
        The keyword arguments to hand to `argparse's add_argument`_
    """

    def __init__(self, args: Tuple[Any, ...], kwargs: Optional[Dict[str, Any]] = None):
        self.args = args
        self.kwargs = {} if (kwargs is None) else kwargs

    def add(self, addFunc: Callable[..., Any]):
        """
        Registers this option

        Parameters
        ----------
        addFunc: Callable[..., Any]
            The function that adds an option, taking the same arguments as
            `argparse's add_argument`_
        """

        addFunc(*self.args, **self.kwargs)
##### EndScript