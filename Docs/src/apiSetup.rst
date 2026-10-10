.. role:: raw-html(raw)
    :format: html

API Setup
=========

Installing
----------

The library is published on `Pypi`_ as ``AGIDMGen``. To install the library, run the following command in the terminal:

:raw-html:`<br />`

.. parsed-literal::

    python3 -m pip install -U "AGIDMGen"

On Windows, use ``py -3`` in place of ``python3``:

.. parsed-literal::

    py -3 -m pip install -U "AGIDMGen"

:raw-html:`<br />`

.. note::
    The library is pure Python. It installs ``numpy`` and AG Remap's API, ``FixRaidenBoss2``, for you.

:raw-html:`<br />`
:raw-html:`<br />`

Importing
---------

.. code-block:: python

    import AGIDMGen as IDMG
    import FixRaidenBoss2 as FRB          # AG Remap's API: its logger works for both libraries

    service = IDMG.IDModGenService(IDMG.ModLoaders.GIMI, names = ["Yelan"], outputFolder = "Mods", logger = FRB.Logger())
    service.generate()

:raw-html:`<br />`

.. note::
    The logger is AG Remap's own (``FixRaidenBoss2.BaseLogger`` / ``Logger``), so one logger serves both libraries.

:raw-html:`<br />`
:raw-html:`<br />`

How To Use
----------
- For some simple examples of using the API, visit :doc:`API Examples <apiExamples>`
- For a full reference of the API, visit :doc:`API Reference <api>`

.. _Pypi: https://pypi.org/project/AGIDMGen/
