# CLAUDE.md

**Anime Game Identity Mod Generator** (`AGIDMGen`) — a Python library that generates *identity mods*:
a character's own, unmodified model written out as a mod (every object, vertex group, texture and
material band of the real model in one folder), for 3DMigoto-based mod loaders (GIMI, WWMI). It is a
sub-project of [Anime Game Remap (AGRemap)](https://github.com/nhok0169/Anime-Game-Remap), whose tools
used to build identity mods themselves; this repo is the library, its docs site, and its test suite.

Detailed operating instructions — how to set up, test, document, and extend this project — live
under [`AI Agent Help/`](AI%20Agent%20Help/README.md), split by topic. **Read the file(s) below
relevant to your task before guessing at commands or conventions**; don't rediscover the
setup/test/doc pipelines from scratch when they're already written down.

| Topic | File | Read it when you're... |
| --- | --- | --- |
| Overview | [`AI Agent Help/Overview/CLAUDE.md`](AI%20Agent%20Help/Overview/CLAUDE.md) | new to the repo — project purpose, how it relates to AGRemap, full directory layout, branch/PR norms. **Also has "Working a feature or bug request here" — read that before starting any task** |
| Setup | [`AI Agent Help/Setup/CLAUDE.md`](AI%20Agent%20Help/Setup/CLAUDE.md) | bootstrapping from a fresh clone — which Python, why nothing needs installing to test or build the docs, and **the namespace-package trap that makes a wrong `sys.path` still "import" `AGIDMGen`** |
| Testing | [`AI Agent Help/Testing/CLAUDE.md`](AI%20Agent%20Help/Testing/CLAUDE.md) | running or adding unit tests, or proving a generated identity mod is right (**a byte comparison against the game's own buffers, never a clean run**) |
| Documentation | [`AI Agent Help/Documentation/CLAUDE.md`](AI%20Agent%20Help/Documentation/CLAUDE.md) | writing docstrings or building the Sphinx docs — the warning baseline, and why every public export needs a hand-written `api.rst` entry |
| Architecture | [`AI Agent Help/Architecture/CLAUDE.md`](AI%20Agent%20Help/Architecture/CLAUDE.md) | writing new library code — package layout, one class per file, the `##### Credits` / `##### Script` section markers, naming and docstring style (all inherited from AGRemap), and **when C++/Cython is allowed in (only once Python is measured too slow)** |
| Downloads | [`AI Agent Help/Downloads/CLAUDE.md`](AI%20Agent%20Help/Downloads/CLAUDE.md) | working on `Data/Mod Downloads`, `ModDownloader`, `generateFromRepo` / `--download`, or the `Tools/Downloads` tools: **files come from AGRemap's GitHub first and this repo's second, so nothing is stored twice**; the generated manifest; the newest-version rule; what cannot be generated from downloads yet |
| Identity Mods | [`AI Agent Help/IdentityMods/CLAUDE.md`](AI%20Agent%20Help/IdentityMods/CLAUDE.md) | working on the generators themselves — what an identity mod is and what AGRemap uses it for, the **GIMI and WWMI generators in AGRemap that this library is ported from** (inputs, algorithm, output layout), and every lesson AGRemap's agents recorded about them |

**THIS IS A PYTHON LIBRARY, AND STAYS ONE UNTIL A MEASUREMENT SAYS OTHERWISE (2026-10-05).** The
maintainer's decision: no C++ / pybind11 / Cython layer until some part is *measured* too slow, or is
plainly better done in C++. When that happens it goes beside the Python source as `src/cpp` /
`src/cy`, the way AGRemap's API is laid out — that is why the package lives at
`AGIDMGen/src/py/AGIDMGen` and not `AGIDMGen/src/AGIDMGen`. Bring the measurement when you propose it.
See [Architecture](AI%20Agent%20Help/Architecture/CLAUDE.md).

**FOLLOW AGREMAP'S CONVENTIONS; ITS DOCS ARE ON THIS MACHINE (2026-10-05).** Code style, docstrings,
test layout, the agent docs' own format and the commit style are all AGRemap's. Its repo is at
`E:\Computer\Games\Genshin\Repos\Repos\Fix-Raiden-Boss`, with its agent docs under its own
`AI Agent Help/`. When this repo's guides do not cover something, look there before inventing a new
convention — and when you adopt one, write it down here. See [Overview](AI%20Agent%20Help/Overview/CLAUDE.md).

**BOTH GENERATORS ARE PORTED (2026-10-05).**

- **WWMI.** `WWMIIdentityModGenerator` (`python -m AGIDMGen wwmi`) is byte-identical to AGRemap's
  `wwmiIdentityMod.py` on all 50 WWMI-Assets characters (2025-10 checkout), and to AGRemap's committed
  Sanhua and SanhuaExorcist buffers.
- **GIMI.** `GIMIIdentityModGenerator` (`python -m AGIDMGen gimi`) is byte-identical to `identityMod.py`
  on all 123 GI-Model-Importer-Assets characters that can be built from.
- **The GIMI dump readers were rewritten in Python (`VbDumpFile` / `IbDumpFile`), by the maintainer's
  choice.** They reproduce AGRemap's C++ `readDumpStr` byte for byte, quirks included: `from_chars`
  parsing, truncated float16, truncated UNORM. **Do not "fix" one of those quirks**; doing so breaks
  parity with every mod AGRemap has built.
- **Rerun `Testing/Integration Tester/{gimi,wwmi}Check.py` after any change to a generator.**

See [Identity Mods](AI%20Agent%20Help/IdentityMods/CLAUDE.md) and [Testing](AI%20Agent%20Help/Testing/CLAUDE.md).

**IDENTITY MODS CAN BE GENERATED WITH NO ASSET REPO, FROM DOWNLOAD FOLDERS (2026-10-05).**
`generateFromRepo` / `python -m AGIDMGen <gi|wuwa> <Name> <mod> --download` fetches a character's newest
download folder: each file from AGRemap's GitHub if AGRemap keeps it, else from this repo's
`Data/Mod Downloads`, which holds only what AGRemap lacks. The fetching goes through AGRemap's
`FixRaidenBoss2.FileDownload`. **The library knows about a folder only through the generated
`AGIDMGen/data/ModDownloadData.py`**: rerun `Tools/Downloads/buildDownloadManifest.py` after any change to
either repo's download folders. See [Downloads](AI%20Agent%20Help/Downloads/CLAUDE.md).

**`IDModGenService` IS THE LIBRARY'S ENTRY POINT, AND `BaseLogger` ITS VIEW (the maintainer's direction, 2026-10-05).**
They follow AGRemap's `RemapService` / logger for API users, and for a future Django backend that will use both
libraries:

- `generate()` returns nothing and fills `stats`;
- a failing character is recorded, never raised;
- nothing is printed without a logger;
- the logger IS AGRemap's (`FixRaidenBoss2.BaseLogger` / `Logger`), so one logger serves both libraries.

The command line is a thin view over the service. Reporting classes extend AGRemap's `Model` and report
through `self.print(...)`. See [Architecture](AI%20Agent%20Help/Architecture/CLAUDE.md)'s "THE SERVICE, THE LOGGER AND `Model`".

**USE AGREMAP'S API WHERE IT ALREADY DOES THE JOB (the maintainer's rule, 2026-10-05).** `FixRaidenBoss2` is a
dependency imported with the package (3.2 s cold, 0.3 s warm). The library takes AGRemap's logger, `Model`,
`Version` / `VersionSet` and `FileDownload`; the dump readers stay a Python rewrite by the maintainer's earlier
choice. **On this machine, put AGRemap's `api/src/py` on `PYTHONPATH` for everything** (see
[Setup](AI%20Agent%20Help/Setup/CLAUDE.md)). The table of what is and is not AGRemap's is in
[Architecture](AI%20Agent%20Help/Architecture/CLAUDE.md)'s "USE AGREMAP'S API WHERE IT ALREADY DOES THE JOB".

**THE TESTERS AND TOOLS USE AGREMAPUTILS (the maintainer's tip, 2026-10-05).** The unit tester runs on its
`BaseTestProgram`, as AGRemap's does. On a machine without `pip install AGRemapUtils`, set
`AGREMAP_UTILS_SRC` to `<AGRemap>/Tools/Utilities/src/AGRemapUtils`. See [Testing](AI%20Agent%20Help/Testing/CLAUDE.md).
Reach for its `CreditsUpdater`, `Heading` or `Pipeline` before writing a new tool helper.

**`Data/Mod Downloads`' BINARIES ARE IN GIT LFS (the maintainer's decision, 2026-10-05).** About 3.8 GB of
`.dds` / `.buf` / `.ib` are tracked by `.gitattributes`; the `.json` stay ordinary git. A clone without git-lfs
has pointer files, which `ModDownloader` refuses with `DownloadFailed`. Downloading LFS files through
`github.com/.../raw/main/...` works: Aino was generated entirely from GitHub after the first push
(2026-10-05). LFS storage and bandwidth count against the owner's quota. See [Downloads](AI%20Agent%20Help/Downloads/CLAUDE.md)'s "GIT LFS".

**`Mods/` HOLDS PRE-GENERATED IDENTITY MODS (2026-10-05)**, for users who do not want to run the
library. It is empty (2026-10-05). How and from what to fill it (asset repos or download folders, which
characters, which versions) is the maintainer's call; ask first.

**AN IDENTITY MOD IS A SAMPLE OF NONE (inherited from AGRemap, 2026-10-02).** It is the easy case in
every way (every vertex group and band, 32-bit indices, `drawindexed = auto`, one variant with today's
hashes, nothing downloaded), and it is generated by the same code that reads it, so it agrees with
that code's assumptions *by construction*. "It loads in game" proves little; **the acceptance test is
a byte comparison of the generated buffers against the game's own frame-dump buffers** — never against
the dump *text* the generator itself parsed, which validates in a circle. See
[Testing](AI%20Agent%20Help/Testing/CLAUDE.md).
