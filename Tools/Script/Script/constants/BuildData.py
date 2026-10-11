##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### Script
# note: every value below is filled in by the ScriptBuilder when this script is compiled. Running
#   this module straight out of the repo leaves the placeholders as they are, which is why
#   Tools/Script/main.py hands in its own API reference instead of relying on them.

# note: every placeholder below is a STRING on purpose, so this module is valid python before anything is
#   filled in

# EnvName: The environment this script was built for. See BuildEnv
EnvName = "{{Build Env}}"

# ApiRelPath: Where the API's source folder sits relative to this script
#
# note: separated by '/' rather than by os.sep, so that a script compiled on one OS still finds the
#   API on another. Only a 'dev' build uses this.
ApiRelPath = "{{API Rel Path}}"

# ApiPackage: The API, both as a module to import and as an installation name on pypi
ApiPackage = "{{API Package}}"
##### EndScript