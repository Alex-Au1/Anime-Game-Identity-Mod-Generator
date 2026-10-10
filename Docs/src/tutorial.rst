.. role:: raw-html(raw)
    :format: html

Tutorial
=========

.. important::
    When installing `Python`_, tick the box **"Add python.exe to PATH"** at the bottom of the installer's first screen.

:raw-html:`<br />`

Supported Games
---------------

.. list-table::
   :widths: 30 30 40
   :header-rows: 1

   * - Game
     - Mod Loader
     - The word to type
   * - GI
     - GIMI
     - ``gimi``
   * - WuWa
     - WWMI
     - ``wwmi``

:raw-html:`<br />`

**Choose your pick of which way to run the generator:**


  a. :ref:`Choice A: Quickstart! 🟢             (for beginners)<tutorial:Choice A: Quickstart 🟢>`
  b. :ref:`Choice B: CMD WITHOUT a Script 🟡    (recommended if you run by CMD)<tutorial:Choice B: Run on CMD Without a Script 🟡>`
  c. :ref:`Choice C: From an Asset Folder 🟡    (if you already have GI-Model-Importer-Assets or WWMI-Assets)<tutorial:Choice C: From an Asset Folder 🟡>`
  d. :doc:`Choice D: API 🟠                     (for expert coders)<apiSetup>`


:raw-html:`<br />`
:raw-html:`<br />`

Choice A: Quickstart 🟢
------------------------

STEP 1
~~~~~~

Right-click `AGIDMGen.py`_, choose **"Save link as..."**, and save the script into GIMI's or WWMI's ``Mods`` folder.

STEP 2
~~~~~~

Open `CMD`_ in that ``Mods`` folder and type ``python AGIDMGen.py``, the game's word, the character's name, then ``--download``.

*eg. for Yelan in GI:*

.. code-block:: bash

    python AGIDMGen.py gimi Yelan --download

then enter

*eg. for Sanhua in WuWa:*

.. code-block:: bash

    python AGIDMGen.py wwmi Sanhua --download

A new folder with the character's name (eg. ``Yelan``) appears beside the script, holding the mod.

.. tip::
    - Copy the character's name as it is written in the `Mods list`_. The new folder is named exactly as you typed it.
    - Want several characters? Put a space between their names: ``python AGIDMGen.py gimi Yelan YelanTranquil --download``
    - Want every character? Use ``--all`` instead of a name: ``python AGIDMGen.py gimi --download --all``

.. note::
    The first run installs what the script needs (numpy, and `AG Remap's API`_), so it takes a little longer. Later
    runs skip that.

STEP 3
~~~~~~

Open the game and enjoy it!

:raw-html:`<br />`

----

:raw-html:`<br />`

Choice B: Run on CMD Without a Script 🟡
-----------------------------------------

STEP 1
~~~~~~

Install the generator onto your computer by opening `CMD`_ and type:

.. code-block:: bash

    python -m pip install -U AGIDMGen

then enter

*( you can now run the program anywhere without copying a script! )*

STEP 2
~~~~~~

Open `CMD`_ in GIMI's or WWMI's ``Mods`` folder and type:

.. code-block:: bash

    python -m AGIDMGen gimi Yelan --download

then enter

STEP 3
~~~~~~

Open the game and enjoy it!

:raw-html:`<br />`

----

:raw-html:`<br />`

Choice C: From an Asset Folder 🟡
----------------------------------

For people who already have a copy of `GI-Model-Importer-Assets`_ or `WWMI-Assets`_ on their computer.

STEP 1
~~~~~~

Get the script, as in :ref:`Choice A's STEP 1 <tutorial:Choice A: Quickstart 🟢>`

STEP 2
~~~~~~

Open `CMD`_ in GIMI's or WWMI's ``Mods`` folder and type the game's word, then the **full** path to the character's
folder inside ``PlayerCharacterData``:

.. code-block:: bash

    python AGIDMGen.py gimi "C:\path\to\GI-Model-Importer-Assets\PlayerCharacterData\Yelan"

then enter

*( if you installed the generator as in Choice B, type* ``python -m AGIDMGen`` *instead of* ``python AGIDMGen.py`` *)*

STEP 3
~~~~~~

Open the game and enjoy it!

:raw-html:`<br />`

.. note::
    See :doc:`commandOpts` for every option the generator takes.


.. _CMD: https://www.google.com/search?q=how+to+open+cmd+in+a+folder&oq=how+to+open+cmd
.. _Python: https://www.python.org/downloads/
.. _Mods list: https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/blob/main/Mods/README.md
.. _AGIDMGen.py: https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator/raw/main/AGIDMGen/script%20build/src/AGIDMGen/AGIDMGen.py
.. _AG Remap's API: https://pypi.org/project/FixRaidenBoss2/
.. _GI-Model-Importer-Assets: https://github.com/SilentNightSound/GI-Model-Importer-Assets
.. _WWMI-Assets: https://github.com/SpectrumQT/WWMI-Assets
