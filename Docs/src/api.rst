.. role:: raw-html(raw)
    :format: html

=============
API Reference
=============

Every class below is importable straight from the top-level package, e.g. ``AGIDMGen.IDModGenService``.

:raw-html:`<br />`

Where to start
**************

You rarely need more than a handful of the classes on this page. Depending on what you want to do:

- **Make the identity mods of several characters at once**, the way the command line does:
  :class:`IDModGenService`. It records what it made, and every error, in its :class:`IDModGenStats`.
- **Make one character's identity mod**: :class:`GIMIIdentityModGenerator` (GI) or
  :class:`WWMIIdentityModGenerator` (WuWa). Unlike the service, they raise an error when they fail.
- **Choose the game**: :class:`ModLoaders`.
- **Find the characters that can be made without an asset folder**: :class:`ModDownloader`.

:doc:`API Examples <apiExamples>` shows each of these end to end.

:raw-html:`<br />`
:raw-html:`<br />`

Service
*******

IDModGenService
===============

.. attributetable:: AGIDMGen.IDModGenService

.. autoclass:: AGIDMGen.IDModGenService
    :members:

:raw-html:`<br />`

Model
*****

DumpDataType
============

.. attributetable:: AGIDMGen.DumpDataType

.. autoclass:: AGIDMGen.DumpDataType
    :members:

:raw-html:`<br />`

DumpElement
===========

.. attributetable:: AGIDMGen.DumpElement

.. autoclass:: AGIDMGen.DumpElement
    :members:

:raw-html:`<br />`

FmtFile
=======

.. attributetable:: AGIDMGen.FmtFile

.. autoclass:: AGIDMGen.FmtFile
    :members:

:raw-html:`<br />`

GIMIComponent
=============

.. attributetable:: AGIDMGen.GIMIComponent

.. autoclass:: AGIDMGen.GIMIComponent
    :members:

:raw-html:`<br />`

GIMIIdentityMod
===============

.. attributetable:: AGIDMGen.GIMIIdentityMod

.. autoclass:: AGIDMGen.GIMIIdentityMod
    :members:

:raw-html:`<br />`

GIMITextureSource
=================

.. attributetable:: AGIDMGen.GIMITextureSource

.. autoclass:: AGIDMGen.GIMITextureSource
    :members:

:raw-html:`<br />`

IbDumpFile
==========

.. attributetable:: AGIDMGen.IbDumpFile

.. autoclass:: AGIDMGen.IbDumpFile
    :members:

:raw-html:`<br />`

IDModGenStats
=============

.. attributetable:: AGIDMGen.IDModGenStats

.. autoclass:: AGIDMGen.IDModGenStats
    :members:

:raw-html:`<br />`

ModDownload
===========

.. attributetable:: AGIDMGen.ModDownload

.. autoclass:: AGIDMGen.ModDownload
    :members:

:raw-html:`<br />`

VbDumpFile
==========

.. attributetable:: AGIDMGen.VbDumpFile

.. autoclass:: AGIDMGen.VbDumpFile
    :members:

:raw-html:`<br />`

WWMIBlendRemap
==============

.. attributetable:: AGIDMGen.WWMIBlendRemap

.. autoclass:: AGIDMGen.WWMIBlendRemap
    :members:

:raw-html:`<br />`

WWMIComponent
=============

.. attributetable:: AGIDMGen.WWMIComponent

.. autoclass:: AGIDMGen.WWMIComponent
    :members:

:raw-html:`<br />`

WWMIDrawRange
=============

.. attributetable:: AGIDMGen.WWMIDrawRange

.. autoclass:: AGIDMGen.WWMIDrawRange
    :members:

:raw-html:`<br />`

WWMIIdentityMod
===============

.. attributetable:: AGIDMGen.WWMIIdentityMod

.. autoclass:: AGIDMGen.WWMIIdentityMod
    :members:

:raw-html:`<br />`

WWMIMesh
========

.. attributetable:: AGIDMGen.WWMIMesh

.. autoclass:: AGIDMGen.WWMIMesh
    :members:

:raw-html:`<br />`

WWMIShapeKeys
=============

.. attributetable:: AGIDMGen.WWMIShapeKeys

.. autoclass:: AGIDMGen.WWMIShapeKeys
    :members:

:raw-html:`<br />`

Constants
*********

DumpDataKinds
=============

.. attributetable:: AGIDMGen.DumpDataKinds

.. autoclass:: AGIDMGen.DumpDataKinds
    :members:

:raw-html:`<br />`

DXGIFormatPrefix
================

.. autodata:: AGIDMGen.constants.DXGIFormats.DXGIFormatPrefix

:raw-html:`<br />`

DXGIFormats
===========

.. autodata:: AGIDMGen.constants.DXGIFormats.DXGIFormats

:raw-html:`<br />`

FileEncodings
=============

.. attributetable:: AGIDMGen.FileEncodings

.. autoclass:: AGIDMGen.FileEncodings
    :members:

:raw-html:`<br />`

GIMIBuffers
===========

.. attributetable:: AGIDMGen.GIMIBuffers

.. autoclass:: AGIDMGen.GIMIBuffers
    :members:

:raw-html:`<br />`

GIMIFixedStrides
================

.. autodata:: AGIDMGen.constants.GIMIBuffers.GIMIFixedStrides

:raw-html:`<br />`

GIMIHashFileSuffix
==================

.. autodata:: AGIDMGen.constants.GIMIBuffers.GIMIHashFileSuffix

:raw-html:`<br />`

GIMISemanticBuffers
===================

.. autodata:: AGIDMGen.constants.GIMIBuffers.GIMISemanticBuffers

:raw-html:`<br />`

GIMITextureLayouts
==================

.. attributetable:: AGIDMGen.GIMITextureLayouts

.. autoclass:: AGIDMGen.GIMITextureLayouts
    :members:

:raw-html:`<br />`

IniFileEncoding
===============

.. autodata:: AGIDMGen.constants.FileEncodings.IniFileEncoding

:raw-html:`<br />`

ModDownloadGameFolders
======================

.. autodata:: AGIDMGen.constants.ModDownloadRepos.ModDownloadGameFolders

:raw-html:`<br />`

ModDownloadRepos
================

.. attributetable:: AGIDMGen.ModDownloadRepos

.. autoclass:: AGIDMGen.ModDownloadRepos
    :members:

:raw-html:`<br />`

ModLoaders
==========

.. attributetable:: AGIDMGen.ModLoaders

.. autoclass:: AGIDMGen.ModLoaders
    :members:

:raw-html:`<br />`

ReadEncodings
=============

.. autodata:: AGIDMGen.constants.FileEncodings.ReadEncodings

:raw-html:`<br />`

WWMIBlendIndexLimit
===================

.. autodata:: AGIDMGen.constants.WWMIBuffers.WWMIBlendIndexLimit

:raw-html:`<br />`

WWMIBlendRemapBuffers
=====================

.. autodata:: AGIDMGen.constants.WWMIBuffers.WWMIBlendRemapBuffers

:raw-html:`<br />`

WWMIBlendRemapSize
==================

.. autodata:: AGIDMGen.constants.WWMIBuffers.WWMIBlendRemapSize

:raw-html:`<br />`

WWMIBuffers
===========

.. attributetable:: AGIDMGen.WWMIBuffers

.. autoclass:: AGIDMGen.WWMIBuffers
    :members:

:raw-html:`<br />`

WWMIDownloadNames
=================

.. autodata:: AGIDMGen.constants.WWMIBuffers.WWMIDownloadNames

:raw-html:`<br />`

WWMIDownloadTextureSuffix
=========================

.. autodata:: AGIDMGen.constants.WWMIBuffers.WWMIDownloadTextureSuffix

:raw-html:`<br />`

WWMIShapeKeySlots
=================

.. autodata:: AGIDMGen.constants.WWMIBuffers.WWMIShapeKeySlots

:raw-html:`<br />`

Data
****

ModDownloadAliases
==================

.. autodata:: AGIDMGen.data.ModDownloadData.ModDownloadAliases
    :no-value:

:raw-html:`<br />`

ModDownloadData
===============

.. autodata:: AGIDMGen.data.ModDownloadData.ModDownloadData
    :no-value:

:raw-html:`<br />`

Exceptions
**********

BadAssetData
============

.. attributetable:: AGIDMGen.BadAssetData

.. autoclass:: AGIDMGen.BadAssetData
    :members:

:raw-html:`<br />`

DownloadFailed
==============

.. attributetable:: AGIDMGen.DownloadFailed

.. autoclass:: AGIDMGen.DownloadFailed
    :members:

:raw-html:`<br />`

Error
=====

.. attributetable:: AGIDMGen.Error

.. autoclass:: AGIDMGen.Error
    :members:

:raw-html:`<br />`

UnknownDXGIFormat
=================

.. attributetable:: AGIDMGen.UnknownDXGIFormat

.. autoclass:: AGIDMGen.UnknownDXGIFormat
    :members:

:raw-html:`<br />`

Tools
*****

DumpValueTools
==============

.. attributetable:: AGIDMGen.DumpValueTools

.. autoclass:: AGIDMGen.DumpValueTools
    :members:

:raw-html:`<br />`

FormatTools
===========

.. attributetable:: AGIDMGen.FormatTools

.. autoclass:: AGIDMGen.FormatTools
    :members:

:raw-html:`<br />`

GIMIDownloadFolderBuilder
=========================

.. attributetable:: AGIDMGen.GIMIDownloadFolderBuilder

.. autoclass:: AGIDMGen.GIMIDownloadFolderBuilder
    :members:

:raw-html:`<br />`

GIMIIdentityModGenerator
========================

.. attributetable:: AGIDMGen.GIMIIdentityModGenerator

.. autoclass:: AGIDMGen.GIMIIdentityModGenerator
    :members:

:raw-html:`<br />`

GIMIIniBuilder
==============

.. attributetable:: AGIDMGen.GIMIIniBuilder

.. autoclass:: AGIDMGen.GIMIIniBuilder
    :members:

:raw-html:`<br />`

ModDownloader
=============

.. attributetable:: AGIDMGen.ModDownloader

.. autoclass:: AGIDMGen.ModDownloader
    :members:

:raw-html:`<br />`

VersionTools
============

.. attributetable:: AGIDMGen.VersionTools

.. autoclass:: AGIDMGen.VersionTools
    :members:

:raw-html:`<br />`

WWMIDownloadFolderBuilder
=========================

.. attributetable:: AGIDMGen.WWMIDownloadFolderBuilder

.. autoclass:: AGIDMGen.WWMIDownloadFolderBuilder
    :members:

:raw-html:`<br />`

WWMIIdentityModGenerator
========================

.. attributetable:: AGIDMGen.WWMIIdentityModGenerator

.. autoclass:: AGIDMGen.WWMIIdentityModGenerator
    :members:

:raw-html:`<br />`

WWMIIniBuilder
==============

.. attributetable:: AGIDMGen.WWMIIniBuilder

.. autoclass:: AGIDMGen.WWMIIniBuilder
    :members:

:raw-html:`<br />`

WWMITexturePattern
==================

.. autodata:: AGIDMGen.tools.wwmi.WWMIIdentityModGenerator.WWMITexturePattern

:raw-html:`<br />`
