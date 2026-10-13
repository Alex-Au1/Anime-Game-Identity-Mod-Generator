#
# ===== Script =====
#
# Runs the script's source straight out of the repo, against the library's source in AGIDMGen/api:
#
#   py -3 Tools/Script/main.py Albedo
#
# The ScriptBuilder (Tools/ScriptBuilder) compiles this source into 'AGIDMGen/script build/src/AGIDMGen/AGIDMGen.py'.
#

import os
import sys

ScriptToolPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, ScriptToolPath)

from Script.apiRefs.PathApiRef import PathApiRef
from Script.main import main


# where the API's package sits, relative to this tool
APIPath = os.path.join(ScriptToolPath, "..", "..", "AGIDMGen", "api", "src", "py")


if __name__ == "__main__":
    # a compiled script reads the API's location out of the values the ScriptBuilder filled in.
    #   Running from source there is nothing filled in yet, so the path is handed over directly.
    sys.exit(main(apiRef = PathApiRef("AGIDMGen", apiPath = os.path.abspath(APIPath))))
