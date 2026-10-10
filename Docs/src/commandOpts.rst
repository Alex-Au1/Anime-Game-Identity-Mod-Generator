.. role:: raw-html(raw)
    :format: html

Command Options
===============


Options
-------
Add these after the character's name. The **Game** column says which game has the option.

.. list-table::
   :widths: 25 15 60
   :header-rows: 1

   * - Option
     - Game
     - Description
   * - -h, -\-help
     - All
     - show this help message and exit
   * - -\-download
     - All
     - the names typed are characters' names: download their files and make their mods from them
   * - -\-all
     - All
     - with ``--download``: make the mod of every character
   * - -\-out folder
     - All
     - the folder the mods are made in, as ``<folder>/<name>``. If this option is not specified, then the mods are made in the current folder.
   * - -\-version str
     - All
     - with ``--download``: the game version wanted, eg. ``4.0``. If this option is not specified, then the newest version is used.
   * - -\-name str
     - All
     - the character's name inside the mod (one character only)
   * - -\-log folder
     - All
     - also write everything printed into ``<folder>/IDModGenLog.txt``
   * - -\-quiet
     - All
     - print only errors
   * - -\-proxy str
     - All
     - with ``--download``: the link to the proxy server, for those whose internet access must go through a proxy
   * - -\-downloadFolder folder
     - All
     - with ``--download``: keep the downloaded files in ``<folder>/<name>``. If this option is not specified, then they are deleted afterwards.
   * - -\-localData REPO=folder
     - All
     - with ``--download``: copy the files of ``AGRemap`` or ``AGIDMGen`` from a copy of its ``Data/Mod Downloads`` folder on your computer, instead of downloading them (can be given more than once)
   * - -\-noFix
     - GI
     - leave the ``ORFix`` / ``NNFix`` lines out of the mod
   * - -\-faceRegister str
     - GI
     - the slot the face texture is bound to. If this option is not specified, then ``ps-t0`` is used (some 6.x skins need ``ps-t1``).
   * - -\-assetPrefix str
     - GI
     - what the asset folder's files start with, when that is not the folder's name (one asset folder only)
   * - -\-textureFrom B=C:O[:plain|normalMap]
     - GI
     - part ``B``, which has no textures of its own, uses object ``O`` of part ``C``'s textures, eg. ``Bang=Body:A`` (can be given more than once)
   * - -\-author str
     - WuWa
     - the mod author WWMI shows. If this option is not specified, then ``Anime Game Remap`` is used.
   * - -\-noTextures
     - WuWa
     - leave the textures out
   * - -\-rawBones
     - WuWa
     - write bone indices as ``vg_offset`` + local index, instead of through the ``vg_map``

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
