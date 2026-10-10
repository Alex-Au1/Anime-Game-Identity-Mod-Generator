# Testing

How to run and add unit tests, and how to prove a generated identity mod is right, which no unit test
alone can do. See [Setup](../Setup/CLAUDE.md) first if nothing runs, and
[Identity Mods](../IdentityMods/CLAUDE.md) for what a correct identity mod contains.

## Running the unit tests

From `Testing/Unit Tester`:

```bash
py -3 main.py
```

| Command | Runs |
| --- | --- |
| `py -3 main.py` | everything registered in `UnitTester/Tests/__init__.py` |
| `py -3 main.py ErrorTest` | one test class |
| `py -3 main.py ErrorTest.test_message_prefixedWithError` | one test |
| `py -3 main.py -k Import` | tests whose name contains `Import` |
| `-v` / `-q` / `-f` | verbose / quiet / stop at the first failure |

The results go to `unitTestResults.txt` beside `main.py` (gitignored) and are printed. `main.py` raises
`TesterFailed("unit")` on any failure or error, **and when no test ran at all** — a mistyped test name
otherwise reads as `OK`. It can be launched from any directory; paths come from
`UnitTester/src/constants/Paths.py`, not the working directory.

**It runs on AGRemapUtils' `BaseTestProgram`, as AGRemap's tester does (the maintainer's tip,
2026-10-05).** That also gives `-s api`; `-s script` is not available, because this library has no
script build.

- AGRemapUtils is imported from the pip-installed package.
- On a machine without it (this one, 2026-10-05: PyPI's TLS fails in the agent sandbox), set
  `AGREMAP_UTILS_SRC` to `E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Tools/Utilities/src/AGRemapUtils`.
  The tester then loads AGRemap's own source (`UnitTester/src/AGRemapUtils.py`).
- **Without either, it stops with an ImportError that says so.**

`UnitTestProgram.runTests` copies `-v` / `-f` onto the file runner: unittest applies them only to a runner
class, so AGRemap's tester ignores them.

## Adding a test

- One file per class under test: `UnitTester/Tests/test_<ClassName>.py`, holding
  `class <ClassName>Test(BaseUnitTest)`.
- **Register it** in `UnitTester/Tests/__init__.py` (`from .test_<ClassName> import <ClassName>Test`).
  An unregistered file is never run, and nothing tells you.
- Import the package through the base: `from .baseUnitTest import BaseUnitTest, IDMG`, then
  `IDMG.<Name>`. Only public names (`__all__`) should be needed; reaching into submodules means the
  name is either missing from `__init__.py` or should not be tested directly.
- Method names: `test_<condition>_<expectedResult>`, e.g. `test_noBlendBuffer_componentSkipped`.
- Group a class's tests by the method under test with banner comments
  (`# =============== build ======...`), and prefer a table of cases (`tests = [...]; for ... in tests:`).
- `BaseUnitTest` gives `self.patch()` / `self.patchObj()` (mocks cleaned up automatically) and
  `compareDict` / `compareList` with readable failure messages.
- **Run a new test against broken code once** and watch it fail before you trust it.
- **GIMI generator tests do the same** (`gimiAssetsFixture.py`): text dumps written in 3DMigoto's format
  (CRLF, as the asset repo's are), where vertex i holds the value i in every channel, so every expected
  buffer is a one-line `struct.pack`. The dump readers' tests (`test_DumpValueTools`, `test_DumpDataType`,
  `test_VbDumpFile`, `test_IbDumpFile`) pin AGRemap's C++ behaviour case by case: from_chars prefixes, a
  float16 that truncation and rounding disagree on, zero-filled short vertices. On 2026-10-05 ten
  deliberate breakages each failed the suite: float16 rounded, UNORM rounded, values after the first
  `:`, a whitespace line not ending a vertex, the index header read as data, no zero-fill, a leading `+`
  accepted, `plain` keeping the normal map, a `run =` line without textures, and no index range check.
- **The service, logger and command line** (`test_IDModGenService`, `test_BaseLogger`, `test_Main`) use
  `CaptureLogger` (in `test_BaseLogger.py`), a `BaseLogger` that keeps its lines, as a server's would. On
  2026-10-05 five deliberate breakages each failed the suite: a failing character stopping the run,
  `handleExceptions` ignored, ENJOY despite errors, a quiet logger hiding errors, and exit 0 on a failure.
- **WWMI generator tests build their asset folder by hand** (`wwmiAssetsFixture.py`): two components, 7
  vertices, one shape key, small enough that every expected byte is worked out in the test rather than
  taken from the code. `highBoneComponents()` in `test_WWMIIdentityModGenerator.py` builds a merged bone
  300 for the blend remap. On 2026-10-05, six deliberate breakages of the generator each failed the
  suite: index offset dropped, `vg_map` ignored, wrong bitangent byte, remap ignoring weights, shape-key
  offsets off by one, stale remap kept.

## PROVING AN IDENTITY MOD IS RIGHT (inherited from AGRemap, 2026-10-05)

The unit tests prove the pieces. They cannot prove the output, because an identity mod is "right" only
if it reproduces the game's own model. AGRemap's acceptance tests, which the ports here must keep
passing:

| Loader | Check | In AGRemap |
| --- | --- | --- |
| GIMI | byte-compare the mod's `Position` / `Blend` / `Texcoord` / `.ib` against the frame dump's `vb0` / `vb1` / `ib` `.buf` files; fail on any difference **or when nothing was compared** | `Tools/Misc/Diagnostics/identityVsDump.py <hash.json> <mod> <FrameAnalysis> [--name]` |
| GIMI | regenerate a committed download folder and compare it | `Tools/Misc/Prototypes/giDownloadFolder.py --check` (Diluc, Amber, Klee, Ganyu, Yelan, YelanTranquil) |
| WWMI | regenerate a committed download folder and compare it | `Tools/Misc/Prototypes/wwmiDownloadFolder.py --check` |
| WWMI | the four shape-key offsets sum to Metadata's `checksum`; `dispatch_y` matches | built into `wwmiIdentityMod.py`'s self-check |
| WWMI | blend remap past 256 bones | `Tools/Misc/Diagnostics/wwmiCheckBlendRemap.py` |

AGRemap's download folders (`Data/Mod Downloads/GI/<Name>/<ver>`, `Data/Mod Downloads/WuWa/<Name>/<ver>`)
are byte-for-byte the identity mods' buffers, so they are the nearest committed golden files.

Two rules from AGRemap's lessons:

- **Compare against the game's buffers, not the dump text the generator parsed.** Re-reading your own
  input agrees with you by construction.
- **"It loads in game" is not the test.** The identity mod is the easiest mod there is (see
  [Identity Mods](../IdentityMods/CLAUDE.md)'s lessons); a bug that only shows on real mods will not show
  on it.

## CI: `.github/workflows` (2026-10-06)

The layout follows AGRemap's. `tests.yml` ("Testers") is the entry point: a push to `main`, a pull request,
every 3 days, or a manual run. It calls `test-workflow.yml`, which runs both testers side by side:

| Job | Workflow | What it runs |
| --- | --- | --- |
| `Unit Tests (3.9)`, `Unit Tests (3.13)` | `unit-test-workflow.yml` | `pip install ./AGIDMGen/api` (proving the packaging and pulling numpy and FixRaidenBoss2 from PyPI), the tester's `requirements.txt` (AGRemapUtils), then `main.py`, then `Tools/ScriptBuilder/main.py --check` (the committed script build is what the source builds; added 2026-10-10) |
| `Integration Tests` | `integration-test-workflow.yml` | `modsCheck.py`: regenerates a sample of identity mods from GitHub and compares them with the committed `Mods/` |

- **Unlike AGRemap, it also runs on a push to `main`.** Nothing is compiled, so a run takes minutes.
- **The job names are what a branch protection rule matches**, as a chain such as
  `Tests / Unit Tests (3.9) / Run Unit Tester`. Renaming a job strands the rule, as AGRemap's CI guide warns;
  change them only together with the rule.
- **`main`'s branch protection requires two checks (set by the maintainer, 2026-10-06):**
  `Tests / Unit Tests (3.13) / Run Unit Tester` and `Tests / Integration Tests / Run Integration Tester`.
  `Unit Tests (3.9)` still runs, guarding `requires-python = ">=3.9"`, but does not block a merge.
- **No checkout fetches Git LFS.** `modsCheck.py` checks each generated binary against the sha256 and size its
  `Mods/` pointer records. So a run spends LFS bandwidth only on the sample character whose download folder
  is this repo's own (Razor, about 6 MB).
- **What CI cannot run:** `gimiCheck.py`, `wwmiCheck.py` and `downloadsCheck.py` need the asset repos and AGRemap's
  prototypes, which only this machine has. Run them by hand after a generator change.
- **Checked here before the first push (2026-10-06):** every workflow parses, every `uses:` target exists, and every
  input passed is declared (a PyYAML check). FixRaidenBoss2 5.0.0 on PyPI has manylinux x86_64 wheels for cp39 to
  cp315. AGRemapUtils 1.0.7's wheel contains `Utils/tests/BaseTestProgram.py` and the rest of what the tester
  imports. **The first run on GitHub (commit 252be50, 2026-10-06) passed every job.**
- **The script build's check runs on PyPI's AGRemapUtils 1.0.7 (2026-10-10).** It was published on 2026-10-05,
  after AGRemap's 2026-09-10 change that gave `ScriptBuilder` its `replacements`, and it requires `ordered-set`. Checked
  from PyPI's JSON, not yet by a run on GitHub.

## PUBLISHING TO PYPI: `python-publish.yml` (2026-10-10)

`python-publish.yml` ("Upload AGIDMGen Package") publishes the package, laid out like AGRemap's file of the same name.
It runs on a **published release or by hand**, and both do the same three steps:

| Job | What it does |
| --- | --- |
| `Tests` | `test-workflow.yml`, the same two testers `tests.yml` runs |
| `Build distribution` | `python -m build` in `AGIDMGen/api` (sdist + one `py3-none-any` wheel), `twine check --strict`, then installs the WHEEL in a clean venv and imports `AGIDMGen` from outside the repo |
| `Publish AGIDMGen Package to PyPI` | `pypa/gh-action-pypi-publish`, trusted publishing, environment `pypi` |

- **No compile step and no cibuildwheel**, unlike AGRemap's: the package is pure Python.
- **The version is `pyproject.toml`'s, not the release tag's.** Bump it, and rebuild the script build (it reads the
  version), before releasing; PyPI refuses a version it already has, and the run fails at the last step.
- **The upload is a plain job of `python-publish.yml`, never in a reusable workflow**: PyPI refuses a trusted-publishing
  token minted inside one (`invalid-publisher`; AGRemap's CI guide, 2026-09-18).
- **The maintainer's one-time setup on PyPI**: register a trusted publisher for `AGIDMGen` with owner `Alex-Au1`,
  repository `Anime-Game-Identity-Mod-Generator`, workflow `python-publish.yml`, environment `pypi`. While the project
  does not exist on PyPI yet, that is a *pending* publisher (PyPI -> Account -> Publishing). Without it the last job
  fails with `invalid-publisher`.
- **Checked here before the first run (2026-10-10):** every workflow parses, and an offline sdist of
  `AGIDMGen/api` (setuptools 68) holds all 11 package folders, `py.typed`, the README and the LICENSE. The wheel
  could not be built here (no `wheel` package, and PyPI is unreachable from the sandbox); the workflow's own
  install-and-import step is its check. **It has not run on GitHub yet.**

## PROVING THE SCRIPT BUILD (2026-10-10)

The single-file script (`AGIDMGen/script build/src/AGIDMGen/AGIDMGen.py`, see [Overview](../Overview/CLAUDE.md)) is the library
flattened into one file, so its acceptance test is **the same bytes as the library**: run it and `python -m AGIDMGen`
on the same characters and compare the mod folders, and compare both with `Mods/`. Pass `--out` as an absolute path:
the script changes into its own folder first. On 2026-10-10 Albedo, Aino, Aalto and Augusta (110 files) matched
`Mods/` byte for byte.

- **`--check` was proven against a broken build:** a line appended to the committed script makes it exit 1.
- **The name-clash guard was proven on a two-module fake package** that both define `Shared`.
- **The build is deterministic:** `--check` passes under several `PYTHONHASHSEED`s. Keep every collection of modules
  the builder visits ordered; a plain set's order changes from run to run, and with it the order of the script.

## `modsCheck.py`: THE COMMITTED MODS ARE THE GOLDEN OUTPUT (2026-10-06)

```bash
py -3 modsCheck.py                                      # the sample, from GitHub
py -3 modsCheck.py --all --localData AGRemap=<export> --localData AGIDMGen=<repo>/Data/Mod\ Downloads
```

The sample covers:

- Yelan: AGRemap's files plus this repo's `Hash.json`;
- YelanTranquil: several components, texture donors;
- Razor: every file from this repo, through LFS;
- Sanhua: AGRemap's files only;
- Lynae: 8 weights, three blend remaps.

`--all` regenerates every mod in `Mods/`.

**Its first run found a real bug (2026-10-06).** A GIMI mod made by `generateFromRepo` named its download folder in
the `.ini`'s last comment, and that folder was a TEMPORARY one (`tmp1ypq794d`). So the output was not
reproducible, and the 144 committed GI mods each carried a random name. `generateFromRepo` now passes
`sourceName = "GI/<Name>/<version>"`, and the GI mods were regenerated.

## THE DOWNLOAD FOLDERS' CHECK: `Testing/Integration Tester/downloadsCheck.py` (2026-10-05)

```bash
py -3 downloadsCheck.py gi "E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Data/Mod Downloads" --assets "E:/Computer/Games/Genshin/Repos/Repos/GI-Model-Importer-Assets/PlayerCharacterData"
py -3 downloadsCheck.py wuwa "E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Data/Mod Downloads" --assets "E:/Computer/Games/Wuthering Waves Mods/Repos/WWMI-Assets/PlayerCharacterData"
```

It generates every character in the manifest from its NEWEST download folder, read from local copies of
both repos, and compares the result with the same character generated from its asset folder:

- GI: every file must match, and the `.ini` apart from its last comment;
- WuWa: every `Meshes/` buffer must match, and the texture hashes must be the same.

**Result on 2026-10-05, after populating:**

- **GI: 123 of 124 characters are identical to their asset folder's mod.** RosariaCN is generated only,
  because its asset folder needs `--assetPrefix`.
- **WuWa: 50 of 52 are identical**, the textures compared by hash. Chisa and ChisaParfait are generated
  only; they have no asset folder (AGRemap built them from frame dumps).

The run caught a library bug: an alias whose target has no listed folder (`YaoYao` -> `Yaoyao`) crashed
`find` with a `KeyError`. It now raises `Error`.

**Run it after `populateDownloads.py` and `buildDownloadManifest.py`.** It proves both the data and
`generateFromDownload`. It never touches the network; `ModDownloader`'s network path is unit-tested with
`FixRaidenBoss2` mocked. A real download from AGRemap's GitHub through `FixRaidenBoss2.FileDownload` worked
from this machine on 2026-10-05 (`GI/Amber/4_0/AmberHead.ib`, identical to the local copy).

## THE GIMI ACCEPTANCE CHECKS: `Testing/Integration Tester/gimiCheck.py` (2026-10-05)

The same two modes as `wwmiCheck.py` below; `checkTools.py` holds what the two share. From
`Testing/Integration Tester`:

```bash
py -3 gimiCheck.py prototype "E:/Computer/Games/Genshin/Repos/Repos/GI-Model-Importer-Assets/PlayerCharacterData" "E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Tools/Misc/Prototypes/identityMod.py"
```

**`prototype`** runs AGRemap's `identityMod.py` and the library on every character, and compares every file.

- The prototype needs AGRemap's compiled `FixRaidenBoss2` (it loads it from AGRemap's checkout).
- `--extra=...` gives both programs the same options, e.g. `--extra="--noFix"`. Write `--extra=` with the
  `=` when the options themselves start with `--`, or argparse takes them for gimiCheck's own.
- `--only` limits the run to some characters.
- The run takes about 1.5 hours: the prototype spends about 40 s per character loading AGRemap's DLLs.

**Result on 2026-10-05:**

- **All 123 characters the asset repo can build from: identical, 2,227 files.** That includes the 31
  multi-component ones and Kinich / KukiShinobu / Ororon, which have unskinned components.
- **The other 10 are refused by both programs, for the same missing file.** The asset repo's file names
  disagree with its own `hash.json`; [Identity Mods](../IdentityMods/CLAUDE.md) lists them.
- **The options also agree:**
  - RosariaCN with `--assetPrefix Rosaria --name RosariaCN`;
  - Flins with `--textureFrom Lantern=Lantern:A:plain --faceRegister ps-t1`, and with
    `--textureFrom Lantern=Body:A`;
  - Flins and Kinich with `--noFix`.

Because the prototype parses the dumps with AGRemap's C++ readers, this is also the proof that the
Python readers produce the same bytes.

```bash
py -3 gimiCheck.py golden "E:/Computer/Games/Genshin/Repos/Repos/GI-Model-Importer-Assets/PlayerCharacterData" "E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Data/Mod Downloads/GI"
```

**`golden`** compares every `.buf` / `.ib` of AGRemap's committed GI download folders with what the library
generates from the current asset folder. It **exits 1 on this machine, and that is the data, not the
code (2026-10-05):**

- 216 buffers were compared.
- Eight characters' `4_0` folders differ from today's assets: AmberCN, Fischl, JeanCN, Kirara, Lisa,
  MonaCN, Rosaria and Xingqiu. The game changed their model after 4.0, and for every one of the eight
  the prototype and the library agree byte for byte.
- Eight more are not generated with default options:
  - seven have the stale dump file names above: BarbaraSummertime, DilucFlamme, FischlHighness,
    KeqingOpulent, KleeBlossomingStarlight, NingguangOrchid and Yaoyao (whose asset folder is `YaoYao`);
  - RosariaCN needs `--assetPrefix Rosaria`.
- Every other character matches.

Read its output per folder; a NEW mismatch on a character that matched before is the signal.

## THE WWMI ACCEPTANCE CHECKS: `Testing/Integration Tester/wwmiCheck.py` (2026-10-05)

The data these checks need is outside the repo, so they are a script rather than part of `main.py`.
**Run both after any change to the WWMI generator.** Each exits 1 on any difference, and also when
nothing was compared. From `Testing/Integration Tester`:

```bash
py -3 wwmiCheck.py golden "E:/Computer/Games/Wuthering Waves Mods/Repos/WWMI-Assets/PlayerCharacterData" "E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Data/Mod Downloads/WuWa"
```

**`golden`** generates every character that has both a WWMI-Assets folder and an AGRemap download
folder. It compares the buffers byte for byte with AGRemap's committed `<Name><Buffer>.buf`, which are
the game's data as AGRemap's pipeline proved it. This is the check that does not validate in a circle.
It uses the download folder's `<Name>Metadata.json`, because that one carries `export_format`.
On 2026-10-05 only Sanhua had both: **9 of 9 buffers identical**.

```bash
py -3 wwmiCheck.py prototype "E:/Computer/Games/Wuthering Waves Mods/Repos/WWMI-Assets/PlayerCharacterData" "E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Tools/Misc/Prototypes/wwmiIdentityMod.py" --exportFormatFrom "E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss/Data/Mod Downloads/WuWa/Sanhua/2_5/SanhuaMetadata.json"
```

**`prototype`** runs AGRemap's `wwmiIdentityMod.py` and this library on every character, and compares
**every file** they write.

- `mod.ini` may differ only in its two lines that name the generator.
- When both programs refuse a character, the refusal must carry the same message.
- `--only Name ...` limits the run to some characters.

`--exportFormatFrom <a Metadata.json>` gives an asset folder with no `export_format` (WWMI-Assets before late
2025) that one's. Both programs then read the same input, so they must still agree byte for byte.

**Results on 2026-10-05:**

| WWMI-Assets | Result |
| --- | --- |
| `eff456b`, 2025-10-10, 50 characters | **all 50 identical, 1,408 files**, with no `--exportFormatFrom` needed. That includes the 8-weight characters (Augusta, Iuno, ...) and the blend-remap ones (Changli, Roccia, Shorekeeper). After the `WWMIMesh` refactor, a sample of 7 was rerun: identical |
| `6581f79`, 2025-01-13, 31 characters | all 31 identical (830 files), with Sanhua's `export_format` given |

`golden` also passes on the newer checkout with `--alias SanhuaExorcist=SanhuaSkin1`: 18 of 18 buffers
match, for Sanhua and SanhuaExorcist. Every shape-key checksum and `dispatch_y` matched `Metadata.json`.
The run takes about 20 minutes, mostly spent copying textures; use `--only` while iterating.

AugustaHelm, CarlottaHairCrystal, CarlottaHairNormal, CarlottaSkin1HairNormal and LupaTail have **no shape keys**. The prototype writes their mod, then
crashes printing its report (`keys[0]`). The check recognises exactly that crash and compares the files
anyway. Any other prototype crash still counts as a difference.

Both checks were run against a deliberately broken generator (the bitangent sign read from the wrong
byte): `golden` reported 1 difference and exited 1.

**Before trusting a change to either check, break the generator and watch the check fail** (Overview habit 4).
