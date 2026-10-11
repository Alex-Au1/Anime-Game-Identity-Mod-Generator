##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits

##### ExtImports
import sys
from typing import List, Optional
##### EndExtImports

##### LocalImports
from .apiRefs.ApiRefBuilder import ApiRefBuilder
from .apiRefs.BaseApiRef import BaseApiRef
from .controller.CommandBuilder import CommandBuilder
##### EndLocalImports


##### Script
def main(argv: Optional[List[str]] = None, apiRef: Optional[BaseApiRef] = None) -> int:
    """
    Runs the script

    :raw-html:`<br />`

    The script does not make the identity mods itself: it makes the API available and then hands the
    command line straight to the API's own ``main``. With no arguments (eg. the script double-clicked), the
    API asks which game and which characters to make the mods of

    Parameters
    ----------
    argv: Optional[List[:class:`str`]]
        The arguments, without the program name. If this value is ``None``, the arguments of the running program are used :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    apiRef: Optional[:class:`BaseApiRef`]
        How to reach the API :raw-html:`<br />` :raw-html:`<br />`

        When this is ``None``, whichever reference this script was compiled for is used. Running
        this out of the repo rather than from a compiled script is the case that passes one in,
        since the compiled-in values do not exist yet :raw-html:`<br />` :raw-html:`<br />`

        **Default**: ``None``

    Returns
    -------
    :class:`int`
        The exit code, as the API's ``main`` returns it
    """

    if (argv is None):
        argv = sys.argv[1:]

    if (apiRef is None):
        apiRef = ApiRefBuilder.build()

    command = CommandBuilder(apiRef.getOptions())

    # this script's own options have to be read before the API is fetched, since one of them decides
    #   whether the API gets downloaded at all. Everything else is the API's
    args, remainingArgs = command.preParse(argv)

    # the API is not fetched just to print its help: when it is not there, the help page only has
    #   this script's own options, and says how to see the rest
    if (args.help and not apiRef.canShowFullHelp(args)):
        command.printHelp(note = apiRef.getHelpNote())
        return 0

    apiMain = apiRef.loadMain(args)
    if (not args.help):
        return apiMain(remainingArgs)

    # the API's help page ends the program, so this script's own options are printed after it
    try:
        apiMain(remainingArgs)
    except SystemExit:
        pass

    command.printOwnOptions()
    return 0


# Main Driver Code
if __name__ == "__main__":
    sys.exit(main())
##### EndScript