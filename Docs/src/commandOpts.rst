.. role:: raw-html(raw)
    :format: html

Command Options
===============


Usage
-----
Type the characters' names, of either game, then any options:

.. code-block:: bash

    python -m AGIDMGen Zani Ayaka ei --out MyMods

Each character's game is found from its name (see :ref:`commandOpts:Mod Names`), so there is no game to type first. An
asset folder (a character's folder of `GI-Model-Importer-Assets <https://github.com/SilentNightSound/GI-Model-Importer-Assets>`_
or `WWMI-Assets <https://github.com/SpectrumQT/WWMI-Assets>`_) can be given instead of a name: its game is found from its
files (a ``hash.json`` or a ``Metadata.json``).

Every character named is downloaded: its files come from `Anime Game Remap <https://github.com/nhok0169/Anime-Game-Remap>`_'s
repository, and those it does not keep from this library's. A source is read as an asset folder instead when it is a path
(it has a ``/`` or ``\``), or a folder holding a game's asset files. A folder that is neither, and is named as a
character is (eg. an old ``Yelan`` mod folder where you run the command), does not stop that character being downloaded.

:raw-html:`<br />`

Options
-------
Add these after the characters' names. The **Game** column says which game's mods an option is for.

.. list-table::
   :widths: 25 15 60
   :header-rows: 1

   * - Option
     - Game
     - Description
   * - -h, -\-help
     - All
     - show this help message and exit
   * - -\-game GI,WuWa
     - All
     - look the names up only in these games, separated by commas, by `Anime Game Remap <https://github.com/nhok0169/Anime-Game-Remap>`_'s
       names for them (``GI``, ``Genshin``, ``WuWa``, ``WutheringWaves``) or their mod loaders' (``GIMI``, ``WWMI``). If this
       option is not specified, then every game is.
   * - -\-all
     - All
     - make the mod of every character (of the ``--game`` games, if given)
   * - -\-out folder
     - All
     - the folder the mods are made in, as ``<folder>/<name>``. If this option is not specified, then the mods are made in the current folder.
   * - -\-version str
     - All
     - for downloaded characters: the game version wanted, eg. ``4.0``, for every game. If this option is not specified, then the newest version is used.
   * - -\-nameReplace CHARACTER:NEWNAME,...
     - All
     - new names for some of the characters, written into their mods instead of their usual names: the mod's folder, and
       a GI mod's files and sections (a WuWa mod's name shows in WWMI). Give ``CHARACTER:NEWNAME`` pairs separated by
       commas, eg. ``--nameReplace "ei:Raiden1, Zani:Shorty"`` (spaces around them are fine), where ``CHARACTER`` is:

       - any name or alias of a character being made, as a whole (``ei``, not ``Heizo``, though ``Ei`` is in it)
       - a character's base name, for all of its parts being made: ``Carlotta:Shorty`` makes ``CarlottaBody`` and
         ``CarlottaHairCrystal`` into ``ShortyBody`` and ``ShortyHairCrystal`` (a skin is a character of its own:
         ``CarlottaSummer`` is hers)
       - or an asset folder's name

       ``NEWNAME`` is letters, digits, ``_`` and ``-``. If a character is given twice (eg. ``ei:A, Raiden:B``), the later
       new name wins. A pair for none of the characters being made, a pair that is not ``CHARACTER:NEWNAME``, or a new
       name another mod is already written into, is skipped, and the run says so.
   * - -\-log folder
     - All
     - also write everything printed into ``<folder>/IDModGenLog.txt``
   * - -\-quiet
     - All
     - print only errors
   * - -\-proxy str
     - All
     - for downloaded characters: the link to the proxy server, for those whose internet access must go through a proxy
   * - -\-downloadFolder folder
     - All
     - for downloaded characters: keep the downloaded files in ``<folder>/<name>``. If this option is not specified, then they are deleted afterwards.
   * - -\-localData REPO=folder
     - All
     - for downloaded characters: copy the files of ``AGRemap`` or ``AGIDMGen`` from a copy of its ``Data/Mod Downloads`` folder on your computer, instead of downloading them (can be given more than once)
   * - -\-noFix
     - GI
     - leave the ``ORFix`` / ``NNFix`` lines out of the mod
   * - -\-faceRegister str
     - GI
     - the slot the face texture is bound to. If this option is not specified, then ``ps-t1`` is used, where GI 6.0 and newer read it (``ps-t0`` is for older versions, and on 6.x it gives white cheeks).
   * - -\-assetPrefix str
     - GI
     - what the asset folder's files start with, when that is not the folder's name (one asset folder only)
   * - -\-textureFrom B=C:O[:plain|normalMap]
     - GI
     - part ``B``, which has no textures of its own, uses object ``O`` of part ``C``'s textures, eg. ``Bang=Body:A`` (can be given more than once)
   * - -\-author str
     - WuWa
     - the mod author WWMI shows. If this option is not specified, then ``AGIDMGen`` is used.
   * - -\-noTextures
     - WuWa
     - leave the textures out
   * - -\-rawBones
     - WuWa
     - write bone indices as ``vg_offset`` + local index, instead of through the ``vg_map``

:raw-html:`<br />`

Mod Names
---------
A mod is named as `Anime Game Remap <https://github.com/nhok0169/Anime-Game-Remap>`_ names its mod types: the name players
use, eg. ``Raiden`` or ``Kazuha``, and for a skin the character's name then the skin's, eg. ``AyakaSpringBloom``. A
character can be asked for by:

- its mod's name (``Raiden``)
- its download folder's name (``RaidenShogun``)
- any of its aliases (``Ei``, ``Shogun``), Anime Game Remap's included

The names are not case sensitive, and spaces, ``_`` and ``-`` are ignored, so ``raiden shogun`` is ``Raiden``. As in
Anime Game Remap, the longest name found in what you type is the one used (``LumineHeaven`` is ``LumineHeaven``, not
``Lumine``). The mod is always made under its mod's name: ``ei`` makes ``Raiden``.

Some WuWa characters' models come as several parts, each its own mod (``CarlottaBody``, ``CarlottaHairCrystal``, ...). Ask
for the character's base name to make all of its parts at once: ``Carlotta``, ``CarlottaSummer`` (her skin), ``Calcharo``,
``Lupa``, or ``Augusta`` (her mod and ``AugustaHelm``). A part's own name (``CarlottaBody``) makes only that part.

Below are the characters whose mods can be made, with their aliases and their download folders:

:raw-html:`<br />`

.. modnametable::

:raw-html:`<br />`

Exit Codes
----------

.. list-table::
   :widths: 15 85
   :header-rows: 1

   * - Code
     - Meaning
   * - 0
     - every mod was made
   * - 1
     - a mod could not be made, or the options are not valid
   * - 2
     - a WWMI mod's shape keys do not match its ``Metadata.json``
