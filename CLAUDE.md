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
| Testing | [`AI Agent Help/Testing/CLAUDE.md`](AI%20Agent%20Help/Testing/CLAUDE.md) | running or adding unit tests, or proving a generated identity mod is right (**a byte comparison against the game's own buffers, never a clean run**), or looking at one in game with AGRemap's GameView |
| Documentation | [`AI Agent Help/Documentation/CLAUDE.md`](AI%20Agent%20Help/Documentation/CLAUDE.md) | writing docstrings or building the Sphinx docs — the warning baseline, and why every public export needs a hand-written `api.rst` entry |
| Architecture | [`AI Agent Help/Architecture/CLAUDE.md`](AI%20Agent%20Help/Architecture/CLAUDE.md) | writing new library code — package layout, one class per file, the `##### Credits` / `##### Script` section markers, naming and docstring style (all inherited from AGRemap), and **when C++/Cython is allowed in (only once Python is measured too slow)** |
| Downloads | [`AI Agent Help/Downloads/CLAUDE.md`](AI%20Agent%20Help/Downloads/CLAUDE.md) | working on `Data/Mod Downloads`, `ModDownloader`, `generateFromRepo` / downloading by name, or the `Tools/Downloads` tools: **files come from AGRemap's GitHub first and this repo's second, so nothing is stored twice**; the generated manifest; the newest-version rule; what cannot be generated from downloads yet |
| Identity Mods | [`AI Agent Help/IdentityMods/CLAUDE.md`](AI%20Agent%20Help/IdentityMods/CLAUDE.md) | working on the generators themselves — what an identity mod is and what AGRemap uses it for, the **GIMI and WWMI generators in AGRemap that this library is ported from** (inputs, algorithm, output layout), and every lesson AGRemap's agents recorded about them |

**BEFORE A FEATURE OR BUG REQUEST, READ [Overview](AI%20Agent%20Help/Overview/CLAUDE.md)'s "Working a feature or bug
request here" (2026-10-10).** It has:

- the change checklist: which check to rerun, and which COMMITTED generated files (the manifest, `Mods/`) to
  regenerate, after each kind of change. **A command-line change has a row listing the SEVEN places users read about
  it** (docs pages, both READMEs, the script's README, the maintainer's launcher); **an `.ini` text change has a row
  too** (the parity checks' skip lists, and all of `Mods/`);
- **`Tools/modsDiff.py` proves a regeneration of `Mods/`**: snapshot before, compare after; it fails on any changed
  binary and lists each changed `.ini` line once with its count. Do not use `git diff Mods` for this (10+ minutes here);
- where the asset repos and AGRemap's data live on this machine;
- this machine's tooling quirks: pushing, a slow git after `Mods/` changes, no `gh` login, searches to keep
  out of `Mods/` and `Data/`, reading PyPI through Python when pip cannot, AGRemap's API vanishing mid-rebuild,
  **never a second checkout (`git worktree add` pulls 7+ GB of LFS) and how to commit to a branch from a temporary
  index instead**, Git Bash's CRLF traps, and previewing an image in the browser pane over local HTTP;
- the habits, among them: **the maintainer asks for UX in small steps, and 0.1.0 needs no compatibility shims**
  (habit 16), **ask before guessing names or data** (17), **match names exactly where a wrong match does harm** (18),
  **the checkout moves between your turns** (check `git status -sb`, `git log -5` and
  `HEAD` against `origin/main` before starting and before committing; re-read a file before editing it), how to
  commit to `main` from another branch, **a requested branch starts from `origin/main`, not from the checkout**, and
  **test the artifact a user actually runs** (the PyPI package, the script, `Mods/`), not only the source;
- **a report of how a mod LOOKS is checked in the game itself** (habits 20-21): read the frame dumps already on this
  machine, then drive the game with AGRemap's GameView. **Paint the texture flat purple to prove a binding is live**,
  because an identity mod binds the game's own texture and a dead binding looks the same as a working one. The recipe
  and its traps are in [Testing](AI%20Agent%20Help/Testing/CLAUDE.md)'s "LOOKING AT A GENERATED MOD IN GAME";
- **another agent may commit your uncommitted work for you** (habit 22): check `origin/main`'s last commits for your
  files before committing, and never start git commands into someone else's running `git checkout` / `git pull`.

Commit and push only when asked, and then straight to `main`, unless the maintainer asks for a branch.

**THE COUNCIL HERE IS "THE SUB-COUNCIL OF CLAUDE AGENTS" (the maintainer's naming, 2026-10-11)**, a branch of AGRemap's
Council of CLAUDE Agents, with its own art (a teal-and-silver crest differenced with a gold label, every image mirrored
in still water). "Add yourself to The Council" means its ritual: [Overview](AI%20Agent%20Help/Overview/CLAUDE.md)'s
"Add yourself to The Sub-Council", which sets the counter from the roster's sum and adds your colour to the member
gradients. The SVGs keep AGRemap's `TheCouncilofClaudeAgents*.svg` names because the PyPI README links them by URL.

**THIS IS A PYTHON LIBRARY, AND STAYS ONE UNTIL A MEASUREMENT SAYS OTHERWISE (2026-10-05).** The
maintainer's decision: no C++ / pybind11 / Cython layer until some part is *measured* too slow, or is
plainly better done in C++. When that happens it goes beside the Python source as `src/cpp` /
`src/cy`, the way AGRemap's API is laid out — that is why the package lives at
`AGIDMGen/api/src/py/AGIDMGen` and not `AGIDMGen/api/src/AGIDMGen`. Bring the measurement when you propose it.
See [Architecture](AI%20Agent%20Help/Architecture/CLAUDE.md).

**FOLLOW AGREMAP'S CONVENTIONS; ITS DOCS ARE ON THIS MACHINE (2026-10-05).** Code style, docstrings,
test layout, the agent docs' own format and the commit style are all AGRemap's. Its repo is at
`E:\Computer\Games\Genshin\Repos\Repos\Fix-Raiden-Boss`, with its agent docs under its own
`AI Agent Help/`. When this repo's guides do not cover something, look there before inventing a new
convention — and when you adopt one, write it down here. See [Overview](AI%20Agent%20Help/Overview/CLAUDE.md).

**`tools/` HOLDS ONLY HELPERS THAT KNOW NOTHING ABOUT MODDING, AS IN AGREMAP (the maintainer's rule, 2026-10-11).**
Generators, `.ini` builders, download-folder builders and `ModDownloader` are mod logic and live in `model/`
(`model/gimi/`, `model/wwmi/`); `tools/` keeps static helpers like `FormatTools` and `VersionTools`. `api.rst` files
each entry under the section of its folder. Moving a class is a refactor with its own checklist row in
[Overview](AI%20Agent%20Help/Overview/CLAUDE.md); see [Architecture](AI%20Agent%20Help/Architecture/CLAUDE.md).

**BOTH GENERATORS ARE PORTED (2026-10-05).**

- **WWMI.** `WWMIIdentityModGenerator` (`python -m AGIDMGen <WuWa names>`) is byte-identical to AGRemap's
  `wwmiIdentityMod.py` on all 50 WWMI-Assets characters (2025-10 checkout), and to AGRemap's committed
  Sanhua and SanhuaExorcist buffers.
- **GIMI.** `GIMIIdentityModGenerator` (`python -m AGIDMGen <GI names>`) is byte-identical to `identityMod.py`
  on all 123 GI-Model-Importer-Assets characters that can be built from.
- **The GIMI dump readers were rewritten in Python (`VbDumpFile` / `IbDumpFile`), by the maintainer's
  choice.** They reproduce AGRemap's C++ `readDumpStr` byte for byte, quirks included: `from_chars`
  parsing, truncated float16, truncated UNORM. **Do not "fix" one of those quirks**; doing so breaks
  parity with every mod AGRemap has built.
- **Rerun `Testing/Integration Tester/{gimi,wwmi}Check.py` after any change to a generator.**

See [Identity Mods](AI%20Agent%20Help/IdentityMods/CLAUDE.md) and [Testing](AI%20Agent%20Help/Testing/CLAUDE.md).

**GIMI MODS BIND THE FACE DIFFUSE ON `ps-t1` BY DEFAULT (the maintainer's choice, 2026-10-13).** GI 6.x reads it from
`ps-t1`; on `ps-t0` it lands in the face's light-map slot and its blush mask shows as white cheeks. Read off the game's
frame dumps (`Tools/faceDumpRegisters.py`) and proved in game. AGRemap's prototype still defaults to `ps-t0`, which
`gimiCheck.py` mirrors. See [Identity Mods](AI%20Agent%20Help/IdentityMods/CLAUDE.md)'s "WHITE CHEEKS".

**IDENTITY MODS CAN BE GENERATED WITH NO ASSET REPO, FROM DOWNLOAD FOLDERS (2026-10-05).**
`generateFromRepo` / `python -m AGIDMGen <Name> ...` fetches a character's newest
download folder: each file from AGRemap's GitHub if AGRemap keeps it, else from this repo's
`Data/Mod Downloads`, which holds only what AGRemap lacks. The fetching goes through AGRemap's
`FixRaidenBoss2.FileDownload`. **The library knows about a folder only through the generated
`AGIDMGen/data/ModDownloadData.py`**: rerun `Tools/Downloads/buildDownloadManifest.py` after any change to
either repo's download folders, **on an export of AGRemap's `master` (`exportAGRemapDownloads.py`), never
on AGRemap's checkout**, which may be on another branch. See [Downloads](AI%20Agent%20Help/Downloads/CLAUDE.md).

**MODS ARE NAMED AS AGREMAP NAMES ITS MOD TYPES, AND TAKE ALIASES THE WAY AGREMAP'S DO (the maintainer's request, 2026-10-12).**
`ModNames` finds a character by its mod's name (`Raiden`), its download folder's (`RaidenShogun`) or an alias (`Ei`), through
AGRemap's `AhoCorasickSingleton` (longest match wins, case ignored). AGRemap's own aliases are read live from
`FixRaidenBoss2.ModTypes`; this library's are in the hand-kept `AGIDMGen/data/ModNameData.py`. A mod, its `Mods/` folder and
its `.ini` are named by the mod's name, never the download folder's. See [Downloads](AI%20Agent%20Help/Downloads/CLAUDE.md)'s
"MOD NAMES AND ALIASES".

**ONE RUN, ANY GAMES: THE GAME IS FOUND FROM EACH CHARACTER (the maintainer's request, 2026-10-13).** `python -m AGIDMGen
Zani Ayaka` makes a WuWa and a GI mod; there is no game argument (`--game GI,WuWa` only narrows the name lookup), and no
`--download`: every name is downloaded. Both went 2026-10-13, with no compatibility for 0.1.0 (the maintainer: only a
publishing test, nobody uses it). `IDModGenService` takes no `ModLoaders`, and `IDModGenServiceCLI` is its
command line half, as AGRemap's `RemapServiceCLI` is `RemapService`'s. See [Architecture](AI%20Agent%20Help/Architecture/CLAUDE.md)'s
"THE SERVICE, THE LOGGER AND `Model`".

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

**CI RUNS BOTH TESTERS ON GITHUB ACTIONS (2026-10-06)**, laid out like AGRemap's (`tests.yml` -> `test-workflow.yml`
-> the unit and integration workflows):

- the unit tester on Python 3.9 and 3.13, after `pip install ./AGIDMGen/api`;
- `Testing/Integration Tester/modsCheck.py`, which regenerates a sample from GitHub and checks it against the
  committed `Mods/` through their LFS pointers' sha256, fetching no LFS.

**`python-publish.yml` publishes `AGIDMGen` to PyPI (2026-10-10; 0.1.0 is out, 2026-10-11)**, on a published release or
by hand: both testers first, then the sdist and wheel, then a trusted-publishing upload (already registered on PyPI).
The version is `pyproject.toml`'s, so bump it, and rebuild the script, before a release; PyPI refuses a version it has.
A release is the maintainer's call: never start one unasked. See [Testing](AI%20Agent%20Help/Testing/CLAUDE.md)'s
"PUBLISHING TO PYPI" and [Overview](AI%20Agent%20Help/Overview/CLAUDE.md)'s change checklist.

**Job names are branch-protection check names; do not rename them casually.** See [Testing](AI%20Agent%20Help/Testing/CLAUDE.md)'s "CI".

**`Mods/` HOLDS EVERY CHARACTER'S PRE-GENERATED IDENTITY MOD (2026-10-06)**, for users who do not want to run
the library. There are 144 GI and 54 WuWa mods, `Mods/<GI|WuWa>/<Name>/`, listed in `Mods/README.md`.

- **It is all generated** by `Tools/populateMods.py`, through `IDModGenService`, from each character's newest
  download folder. Rerun the tool; never edit `Mods/` by hand.
- **Regenerate it after any change to a generator, `Data/` or the manifest.**
- **Binaries are in Git LFS, and the `.ini` files are `-text`**, so their CRLF bytes reach users as generated.

See [Downloads](AI%20Agent%20Help/Downloads/CLAUDE.md)'s "`Mods/`".

**THE LIBRARY ALSO RUNS FROM ONE SCRIPT, `AGIDMGen/script build/src/AGIDMGen/AGIDMGen.py` (the maintainer's request,
2026-10-10)**, for users who cannot install a Python package. As in AGRemap, `Tools/ScriptBuilder/main.py` compiles the
script's own source, `Tools/Script`, and the script only REACHES the library, in one of two builds (`--env`):

- **`prod` is the committed build: it pip-installs `AGIDMGen` from PyPI** (with numpy and FixRaidenBoss2) and updates it
  on every run, unless `--disableUpdate`;
- **`dev` reaches `AGIDMGen/api/src/py` by a relative path**, for trying a library change through the script here.
- **Rebuild with `--env prod` after any change to `Tools/Script`**; CI's `main.py --env prod --check` fails on a stale or
  a `dev` script. A library change needs no rebuild, but reaches script users only once it is released to PyPI.
- **Its `.py` files are generated**: never edit them.

See [Overview](AI%20Agent%20Help/Overview/CLAUDE.md)'s "THE SCRIPT BUILD".

**AN IDENTITY MOD IS A SAMPLE OF NONE (inherited from AGRemap, 2026-10-02).** It is the easy case in
every way (every vertex group and band, 32-bit indices, `drawindexed = auto`, one variant with today's
hashes, nothing downloaded), and it is generated by the same code that reads it, so it agrees with
that code's assumptions *by construction*. "It loads in game" proves little; **the acceptance test is
a byte comparison of the generated buffers against the game's own frame-dump buffers** — never against
the dump *text* the generator itself parsed, which validates in a circle. See
[Testing](AI%20Agent%20Help/Testing/CLAUDE.md).
