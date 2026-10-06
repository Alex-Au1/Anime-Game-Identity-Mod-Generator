# Overview

What this project is, how the repo is laid out, and the operating norms that don't fit neatly under
Setup/Testing/Documentation/Architecture. Read this one first if you're new to the repo; it's the map
the other [AI Agent Help](../README.md) files assume you have. See [Setup](../Setup/CLAUDE.md) to get
running, [Testing](../Testing/CLAUDE.md) to verify, and [Identity Mods](../IdentityMods/CLAUDE.md) for
what the library actually generates.

## What this project is

AGIDMGen generates **identity mods**: a character's own model, unchanged, written out as a mod. In
[Anime Game Remap (AGRemap)](https://github.com/nhok0169/Anime-Game-Remap) they are step 4 of the
maintainer's thirteen-step `char <-> skin` remap pipeline ("identity mods of both"), the baseline every
later step is checked against. AGRemap built them with prototype scripts under its `Tools/`; this repo
turns that into a library of its own. [Identity Mods](../IdentityMods/CLAUDE.md) has the detail.

| | |
| --- | --- |
| Language | Python only (see "Python first" below) |
| Python | 3.9 or newer |
| Mod loaders | GIMI (Genshin Impact), WWMI (Wuthering Waves) |
| Package on PyPI | `AGIDMGen` (not published yet, 2026-10-05) |
| Default branch | `main` (AGRemap's is `master`; do not carry that over) |
| Remote | `https://github.com/Alex-Au1/Anime-Game-Identity-Mod-Generator` |

## AGRemap is the reference for every convention (2026-10-05)

The maintainer's instruction when this repo was created: **follow AGRemap's conventions**. AGRemap's
checkout is on this machine at `E:\Computer\Games\Genshin\Repos\Repos\Fix-Raiden-Boss`. Its guides:

| For | Read in AGRemap |
| --- | --- |
| habits that pay on any task (92 of them) | `AI Agent Help/Overview/CLAUDE.md`, "Working a feature or bug request here" |
| Python style, docstrings, one class per file | `AI Agent Help/Architecture/CLAUDE.md` and any file under `Anime Game Remap (for all users)/api/src/py/FixRaidenBoss2/` |
| unit test layout | `Testing/Unit Tester/` and `AI Agent Help/Testing/CLAUDE.md` |
| Sphinx docs | `Docs/src/conf.py` and `AI Agent Help/Documentation/CLAUDE.md` |
| how identity mods are made and used today | `Tools/Misc/Prototypes/identityMod.py`, `wwmiIdentityMod.py`, and `AI Agent Help/CreatingRemaps/CLAUDE.md` |

What was adapted rather than copied is listed where it applies (the unit tester is self-contained
rather than built on `AGRemapUtils`, the package sits under `src/py`, the branch is `main`). If this
repo's guides and AGRemap's disagree, this repo's win **for this repo**; if this repo's are silent,
AGRemap's apply. Write down any convention you adopt from there.

## Python first (2026-10-05)

The library is pure Python. A C++ / Cython layer is added **only** when some part is measured too
slow, or is plainly better done in C++ — the maintainer decides, from a measurement. Until then, a
dependency on a compiled package is a cost too: AGRemap's own GIMI generator reads dump text through
the compiled `FixRaidenBoss2.VbFile` / `IbFile`, which needs its `.pyd` and its DLLs (libz3, libcurl,
utf8proc). See [Architecture](../Architecture/CLAUDE.md).

## Repo layout

```
CLAUDE.md                     the agent entry point: topic table and dated callouts
README.md                     the GitHub front page
LICENSE                       Apache 2.0 (the repo); the package itself is MIT, as in AGRemap
.readthedocs.yaml             Read the Docs build (no install; conf.py puts the source on sys.path)
AI Agent Help/                these guides, one folder per topic, plus the Council roster (README.md)
AGIDMGen/                     the package's distribution folder (pyproject.toml, README.md, LICENSE)
  src/py/AGIDMGen/            the package source
    __init__.py               re-exports every public name flat, with an explicit __all__
    constants/                enums and constants
    exceptions/               Error and its subclasses
    model/                    the data an identity mod is built from / made of
    tools/                    helpers that are not model types
Testing/Unit Tester/          unittest suite (main.py, UnitTester/Tests, UnitTester/src)
Testing/Integration Tester/   acceptance checks against data outside the repo (wwmiCheck.py)
Tools/                        repo tools: auditApiDocs.py; Downloads/ (populateDownloads.py, buildDownloadManifest.py)
Data/Mod Downloads/           download folders, laid out as AGRemap's, holding only what AGRemap lacks (see Downloads)
Docs/                         Sphinx site (src/conf.py, src/index.rst, src/api.rst, src/_static/images)
Mods/                         pre-generated (compiled) identity mods, for users who don't want to run the library
```

`AGIDMGen/` at the root has no `__init__.py` on purpose — it is the distribution folder, like AGRemap's
`api/`. That makes it importable as an empty *namespace package* from the repo root; see
[Setup](../Setup/CLAUDE.md)'s trap.

## Operating norms

- **Don't push or open a PR unless asked.** If asked, branch off `main` and target `main`. Branch names
  are kebab-case (`add-wwmi-generator`).
- **Commit subjects are `Scope: lowercase imperative -- detail`**, AGRemap's style, e.g.
  `GIMI: write the face diffuse on ps-t1 for 6.x skins -- 6.x moved it off ps-t0`. Bodies end with
  the `Co-Authored-By:` line.
- **Several agents may share this checkout.** Never revert (`git checkout --`, `git restore`) a file
  you did not create.
- **This machine's agent sandbox cannot verify PyPI's TLS certificate (2026-10-05)**: `pip install`
  from PyPI and Sphinx's intersphinx fetches both fail with `CERTIFICATE_VERIFY_FAILED`. Do not
  disable verification to get around it; work offline (see [Setup](../Setup/CLAUDE.md)) or ask the
  maintainer.
- **Mark what you generate.** A file or folder a script wrote says so (a header line or a README), so
  the next agent does not hand-edit it.

## Working a feature or bug request here

AGRemap's list of habits (its Overview, "Working a feature or bug request here") applies here in
full. The ones that matter most for a generator library:

1. **Assume failure is silent.** A generator that "ran" may have written the wrong bytes. Check the
   artifact — the files it wrote — not the exit code.
2. **Prove a refactor by byte-identical output.** Generate the same character's identity mod before and
   after, and compare every file byte for byte. A single-component character's output must stay
   byte-identical to the old naming (AGRemap's `identityMod.py` keeps exactly this check).
3. **Never validate in a circle.** A test whose expected value comes from the code under test (or from
   the text that code parsed) proves nothing. Compare against the game's own buffers.
4. **Run a new check against a broken build first.** A check that has never failed is not known to work.
   (The unit tester was checked this way on 2026-10-05: one wrong expectation made it fail.)
5. **Find the existing code before writing new.** The thing you are about to write may already exist
   in AGRemap's prototypes, tools or library — port it, and say where it came from in the commit.
6. **A one-off diagnostic becomes a tool.** If you wrote a script to check something, it goes in the
   repo for the next agent.
7. **Docstrings are published.** Write them for a new user, in the present tense: no dates, no history,
   no links into `AI Agent Help/`. History goes here.

## Add yourself to The Council

When your session made a real contribution, add a badge to the roster in
[`AI Agent Help/README.md`](../README.md) — a work-specific name (`The <Role>`), an emoji pair and a
colour, in the same Shields.io static-badge format as the existing ones — or bump an existing badge's
count if your work fits its name. Then **recompute the total as the sum of every badge's count** and
write it into BOTH `Docs/src/_static/images/TheCouncilofClaudeAgentsBadgeWithCount.svg` and
`TheCouncilofClaudeAgentsBadgeMiniWithCount.svg`: in each, the `<text>` element that shows the number
AND the root `aria-label`. (Total on 2026-10-05: 1.)
