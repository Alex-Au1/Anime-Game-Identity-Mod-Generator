.. role:: raw-html(raw)
    :format: html

API Examples
============

Below are a few simple and common examples of using the API.

.. note::
    For more detailed information about the API, see :doc:`api`

:raw-html:`<br />`
:raw-html:`<br />`

Making Several Identity Mods
----------------------------

:class:`~AGIDMGen.IDModGenService` makes each mod into ``<outputFolder>/<name>``. A character that fails does not
stop the others: it is recorded in ``service.stats``, and nothing is printed unless you give it a logger.

:raw-html:`<br />`

From Download Folders
~~~~~~~~~~~~~~~~~~~~~

No asset repository needed: each character's files are downloaded for you. The characters can be of both games: each
one's game is found from its name (``Zani`` is WuWa's), and a name can be any of the character's aliases (see
:ref:`commandOpts:Mod Names`).

.. code-block:: python
    :linenos:

    import AGIDMGen as IDMG
    import FixRaidenBoss2 as FRB

    service = IDMG.IDModGenService(names = ["Yelan", "YelanTranquil", "Zani"], outputFolder = "Mods", logger = FRB.Logger())
    service.generate()

    print("Made:", sorted(service.stats.generated))

:raw-html:`<br />`

From Asset Folders
~~~~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:

    import AGIDMGen as IDMG

    service = IDMG.IDModGenService(assetsFolders = ["WWMI-Assets/PlayerCharacterData/Sanhua"], outputFolder = "Mods")
    service.generate()

:raw-html:`<br />`

Every Character
~~~~~~~~~~~~~~~

.. code-block:: python
    :linenos:

    import AGIDMGen as IDMG

    # every game's; for one game's only, IDMG.ModNames.getAll([IDMG.ModLoaders.GIMI])
    names = [modName.name for modName in IDMG.ModNames.getAll()]
    service = IDMG.IDModGenService(names = names, outputFolder = "Mods")
    service.generate()

:raw-html:`<br />`

As the Command Line Does
~~~~~~~~~~~~~~~~~~~~~~~~

:class:`IDModGenServiceCLI` wraps the service with what the command line adds: options given as strings, a log file,
tips at the end, and an exit code.

.. code-block:: python
    :linenos:

    import AGIDMGen as IDMG

    serviceCLI = IDMG.IDModGenServiceCLI(sources = ["Zani", "Ayaka"], games = ["GI", "WuWa"], outputFolder = "Mods", log = "Logs")
    serviceCLI.generate()
    print(serviceCLI.exitCode)      # 0 when every mod was made

:raw-html:`<br />`
:raw-html:`<br />`

Logging in a Server
-------------------

Give each request its own logger, and either read what it wrote afterwards or forward each line as it is written.

.. code-block:: python
    :linenos:

    import AGIDMGen as IDMG
    import FixRaidenBoss2 as FRB

    class ForwardingLogger(FRB.BaseLogger):
        def write(self, message: str):
            send_to_frontend(message)          # eg. a websocket, a queue, a database row

        def read(self, desc: str) -> str:
            return ""                          # nothing interactive on a server

    logger = FRB.Logger(logTxt = True, verbose = False)     # or: ForwardingLogger()
    service = IDMG.IDModGenService(names = ["Yelan"], outputFolder = folder, logger = logger)
    service.generate()
    transcript = logger.loggedTxt

:raw-html:`<br />`
:raw-html:`<br />`

Making One Identity Mod Directly
--------------------------------

The generators can also be used on their own. Unlike the service, they raise an error when they fail.

.. code-block:: python
    :linenos:

    import AGIDMGen as IDMG

    mod = IDMG.GIMIIdentityModGenerator().generate("GI-Model-Importer-Assets/PlayerCharacterData/Yelan", "Mods/Yelan")
    mod = IDMG.WWMIIdentityModGenerator().generateFromRepo("Sanhua", "Mods/Sanhua", version = "2.5")
    print("\n".join(mod.getSummary()))
