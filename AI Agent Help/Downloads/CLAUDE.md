# Downloads

How the library generates an identity mod with no asset repo cloned: from a character's **download
folder**, fetched at run time from AGRemap's repository or this one. This covers the layout of
`Data/Mod Downloads`, the tools that fill it and list it, and the rules for changing it. See
[Identity Mods](../IdentityMods/CLAUDE.md) for what the files become, and [Testing](../Testing/CLAUDE.md)
for `downloadsCheck.py`.

## THE DESIGN, AND WHO DECIDED WHAT (2026-10-05)

The maintainer's decisions, asked one by one on 2026-10-05:

- **What is stored.** `Data/Mod Downloads` holds **download folders in AGRemap's layout**, and identity
  mods are assembled from them. Raw asset folders are not stored.
- **No file is kept twice.** At run time each file comes from AGRemap's GitHub `master` if AGRemap
  keeps it, else from this repo's GitHub `main` (`ModDownloadRepos`, searched in that order). That
  saves space and avoids repeating downloads in both projects.
- **Local copies.** Callers and tests can point the downloader at local copies of either repo's
  `Data/Mod Downloads` (`ModDownloader(localFolders = ...)`, CLI `--localData AGRemap=...`).
- **Which version.** The newest version by default; a caller can ask for one. The rule is AGRemap's own
  for its asset data (`VersionSet::findClosest`): the newest version not newer than the one asked for,
  else the oldest. `VersionTools.getClosest` implements it, and `VersionTools.parse` treats `4_0`,
  `4.0` and `4` as the same version.
- **How files are fetched.** Through `FixRaidenBoss2.FileDownload`, AGRemap's own downloader, with
  `FixRaidenBoss2>=5.0.0` as a dependency. It retries transient failures with back-off and follows
  GitHub's redirects.
  - **It is imported only when a file actually has to be downloaded.** Loading it costs 30-60 s on this
    machine (its DLLs). A generation that copies every file from local folders never loads it.
- **Version labels for folders built from today's assets** (the maintainer's, 2026-10-05):
  - GI: `6_8`, for GI-Model-Importer-Assets at `2039d16` (2026-08-03);
  - WuWa: `2_7`, for WWMI-Assets at `eff456b` (2025-10-10).

  When an asset repo moves on, the new folders get the version it is at.
- **Skin names.** Use AGRemap's name where AGRemap has the skin (`SanhuaSkin1` -> `SanhuaExorcist`),
  else the asset repo's.

## The layout

`Data/Mod Downloads/<GI|WuWa>/<Name>/<X_Y>/`, as AGRemap's. The file kinds are listed in
[`Data/Mod Downloads/README.md`](../../Data/Mod%20Downloads/README.md). One file is this repo's addition:
**`<prefix>Hash.json`**, the asset folder's `hash.json`. AGRemap's GI folders carry no hashes, and the
GIMI `.ini` is written from them. WuWa needs no addition, because `<prefix>Metadata.json` has everything.

A version folder here holds **only what AGRemap's folder of the same version lacks**:

- for a GI character whose AGRemap folder is today's model, just `<prefix>Hash.json`;
- for a character AGRemap does not have, or whose newest AGRemap folder differs from today's assets,
  a whole folder under the asset repo's version.

## The tools (`Tools/Downloads/`)

| Tool | Does |
| --- | --- |
| `populateDownloads.py <gi\|wuwa> <assets> <AGRemap Data/Mod Downloads> --version X_Y [--only ...] [--dryRun]` | builds every asset folder's download folder, compares it with AGRemap's newest, and writes only the difference into `Data/Mod Downloads` |
| `exportAGRemapDownloads.py <AGRemap repo> <out> [--ref origin/master]` | exports AGRemap's `Data/Mod Downloads` exactly as `origin/master` has it (`git archive`), without touching the checkout's branch or files. **Every tool below takes this export, not the checkout** |
| `buildDownloadManifest.py <AGRemap Data/Mod Downloads> [--commit SHA]` | writes `AGIDMGen/api/src/py/AGIDMGen/data/ModDownloadData.py`: every version folder with its file prefix and the repo of each file, and `ModDownloadAGRemapCommit`, the AGRemap commit the export was made from (read from the export's `AGRemapCommit.txt`; it refuses a folder that names none, unless `--commit`) |
| `wwmiLiveHashes.py <version folder> <FrameAnalysis folder> --out <json> [--note ...]` | measures a WuWa character's `<Name>LiveHashes.json` off a frame dump (see "LIVE TEXTURE HASHES") |
| `staleManifest.py [--ref master] [--since SHA]` | names every character folder AGRemap changed on GitHub since `ModDownloadAGRemapCommit`, by file blob hash, so a file replaced under the same name counts. Exits 1 when one is stale. `modsCheck.py` runs it first (see below) |
| `downloadTools.py` | what the two share: `Aliases.json`, version folders, prefix detection |

**Rerun `buildDownloadManifest.py` after `populateDownloads.py`, and whenever AGRemap's `master` gains a
download folder.** The manifest is a generated file (it says so in its header); never edit it by hand.

**BUILD THE MANIFEST FROM AGREMAP'S `master`, NEVER FROM ITS CHECKOUT (2026-10-05).** The library downloads
AGRemap's files from its GitHub `master`, so the manifest must list exactly what `master` serves. A folder
that exists only on a local branch makes the library ask for files that 404, and one only on `master` is
missed. The procedure:

```bash
git -C "E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss" fetch origin master
py -3 Tools/Downloads/exportAGRemapDownloads.py "E:/Computer/Games/Genshin/Repos/Repos/Fix-Raiden-Boss" <scratch>/agmaster
py -3 Tools/Downloads/buildDownloadManifest.py "<scratch>/agmaster/Data/Mod Downloads"
```

The fetch only moves `origin/master`. The export never switches the checkout's branch: other agents share
that checkout, and it was on `add-citlali` on 2026-10-05.

**THE MANIFEST RECORDS ITS AGREMAP COMMIT, AND `staleManifest.py` CHECKS IT (the maintainer's request, 2026-10-23).**
The export writes `AGRemapCommit.txt` beside its `Data/`, and the manifest keeps it as `ModDownloadAGRemapCommit` (not
exported from the package). `staleManifest.py` diffs AGRemap's `Data/Mod Downloads` at that commit against `master`, with
five GitHub API calls (a `GITHUB_TOKEN` raises the 60-an-hour limit, and CI passes one). It sorts the changes into:
- **STALE**: any version folder, listed in the manifest or new. A new folder with no `Hash.json` / `Metadata.json`
  (eg. `GI/Tartaglia/4_0`) is reported stale too, although the rebuild will skip it. A rebuild clears it, because the
  manifest's commit becomes `master`.
- **unused**: everything else, such as a README or a `<Name>LiveHashes.json`.

It was proved against the real failure: with Lynae's old `Mods/` and the manifest pointed at `5422f264`, `modsCheck.py`
printed `wuwa:Lynae ... -- STALE MANIFEST` and named the fix.

**Rebuilt against `master` `5422f264` on 2026-10-05.** The checkout's `Data/Mod Downloads` had no local-only
files. `master` had two WuWa characters the checkout lacked, **Lynae and LynaePeppermint** (3_7, 8 weights a
vertex, blend remaps), and is otherwise identical. So the manifest gained exactly those two: 144 GI and 54
WuWa characters (55 versions), and nothing else changed. Lynae was then generated entirely from AGRemap's
GitHub (47 files, three blend remaps, checksum OK). LynaePeppermint was generated from the export
(checksum OK).

**Rebuilt against `master` `eedaf348` on 2026-10-23**, after CI's `wuwa:Lynae` failed (see [Testing](../Testing/CLAUDE.md)'s
`modsCheck.py`). `master` had changed Lynae's and LynaePeppermint's foils (full mip chains) and added their lighting ramps
and LynaePeppermint's jacket noise texture. It had also added Changli 3_7 and a `ChangliNymph` 3_7 folder.
`Tartaglia/4_0` stays skipped, since no file in it names the prefix. Still 144 GI and 54 WuWa characters (57 versions).
Lynae, LynaePeppermint, Changli and ChangliNymph were regenerated: Changli and ChangliNymph now come from 3_7.

**A FOLDER ALREADY KEPT HERE UNDER ANOTHER NAME (2026-10-23).** AGRemap's new `WuWa/ChangliNymph` is the skin this repo
kept as `WuWa/ChangliSkin1/2_7` (WWMI-Assets' name). With both in the manifest, one mod has two download folders, and
`ModNameDataTest.test_everyFolderNamedOnce` fails. The fix was to rename this repo's folder to AGRemap's name
(`git mv`; the files inside keep their `ChangliSkin1` prefix, which the manifest records per version). Then 2_7 (here)
and 3_7 (AGRemap) are two versions of one character, the newest wins, and Changli is laid out the same way.
`ModNameData` points `ChangliNymph` at the folder `ChangliNymph` and keeps `ChangliSkin1` as an alias, as `JinhsiBlossom`
keeps `JinhsiSkin1`. Expect the same for `CarlottaSkin1*` and `JinshiSkin1` if AGRemap adds them.

**A new folder is only live once it is on GitHub.** This repo's on `main`, AGRemap's on `master`.
Committing and merging them is the maintainer's call, as it is in AGRemap (its Overview: "commit them,
stop, and tell the maintainer").

## WHAT IS IN `Data/Mod Downloads` (populated 2026-10-05)

| Game | from AGRemap, nothing stored here | `Hash.json` only, beside AGRemap's folder | whole folder: AGRemap has none | whole folder: newer than AGRemap's newest | could not be built |
| --- | --- | --- | --- | --- | --- |
| GI (`6_8`) | - | 20 | 87 | 17 (AmberCN, Arlecchino, AyakaSpringbloom, Fischl, GanyuTwilight, JeanCN, KaeyaSailwind, Kirara, Lisa, MonaCN, Nilou, RaidenShogun, Rosaria, RosariaCN, ShenheFrostFlower, Xingqiu, XingqiuBamboo) | 9 (stale asset file names) |
| WuWa (`2_7`) | Sanhua, SanhuaExorcist (AGRemap's `2_5` is byte-identical to today's assets) | - | 48 | 0 | 0 |

Totals:

- **The manifest lists 124 GI and 52 WuWa characters** (53 WuWa versions: ChisaParfait has `3_5` and `3_7`).
- **On disk, 1.32 GB of GI (2,021 files) and 2.49 GB of WuWa (1,399 files)**, about 3.8 GB. The largest
  file is 5.6 MB, and the largest character folder is 80 MB (CartethyiaFleurdelys).
- **The binaries are in Git LFS (the maintainer's decision, 2026-10-05)**. See "GIT LFS" below.
  AGRemap stores its 853 MB as plain blobs.

## GIT LFS (2026-10-05)

`.gitattributes` tracks `Data/Mod Downloads/**/*.dds`, `*.buf` and `*.ib` in Git LFS: about 3.8 GB in
3,200 files. The patterns were written by `git lfs track` (the space is `[[:space:]]`). The 241 `.json`
files (1.1 MB) and `README.md` / `Aliases.json` stay ordinary git, so hash files and manifests diff and
review as text. `git lfs install --local` installed this repo's hooks; the LFS filters were already in the
user's global git config.

- **Proved on 2026-10-05, without committing.** `git check-attr filter` gives `lfs` for a `.buf`, `.ib` and
  `.dds` under `Data/Mod Downloads`, and nothing for its `.json` or a `.buf` elsewhere. Staging a buffer into
  a THROWAWAY index (`GIT_INDEX_FILE=...`) stored an LFS pointer (`oid sha256:...`, `size 51744`), while a
  `Hash.json` stayed an ordinary blob. The real index was untouched.
- **The silent failure LFS adds: a pointer in place of the file.** A clone made without git-lfs has ~130-byte
  pointer files in its working tree, and so does `--localData` pointed at it. An address that bypasses LFS
  (`raw.githubusercontent.com`) serves the pointer too. `ModDownloader` refuses any fetched file that is a
  pointer (`isLfsPointer`), with `DownloadFailed`, and any download that left no file.
- **The library's addresses are `github.com/<owner>/<repo>/raw/<branch>/...`.** GitHub redirects these to
  LFS storage for an LFS file, and FixRaidenBoss2's `FileDownload` follows redirects. **Proved on
  2026-10-05, after the first push** (`c1abc53`; 2,651 LFS objects, 3.2 GB):
  `GIMIIdentityModGenerator().generateFromRepo("Aino", ...)` fetched all 37 of Aino's files from this repo's
  GitHub in 26 s. Every LFS binary was byte-identical to the working tree, and `AinoHash.json` differed
  only in line endings.
- **Quotas.** LFS storage, and the bandwidth of every user's download, count against the repo owner's GitHub
  LFS quota, not ordinary repository limits. Check the plan before pushing all 3.8 GB.
- **AGRemap's own folders are not in LFS.** Its files keep coming from its ordinary blobs.

**Line endings.** `.gitattributes` marks `*.buf`, `*.ib` and `*.dds` binary, because both repos'
checkouts here run `core.autocrlf=true`. GitHub serves the `.json` files with LF where the checkout has
CRLF; this was seen on `SanhuaMetadata.json` and is harmless to `json.load`. So **never compare a JSON
downloaded from GitHub with a local checkout's byte for byte.**

**The network path was proved end to end on 2026-10-05.** `WWMIIdentityModGenerator().generateFromRepo("Sanhua", ...)`
was run with no local folders. All 31 files came from AGRemap's GitHub through `FixRaidenBoss2.FileDownload`;
the buffers and textures were identical to the checkout's, the checksum OK. It took 1.5 minutes,
including FixRaidenBoss2's import. No GI character can be fetched fully from GitHub until this repo's
`Data` is pushed, because every GI folder needs this repo's `Hash.json`.

## `Mods/`: EVERY CHARACTER'S IDENTITY MOD, READY-MADE (2026-10-06)

The maintainer created `Mods/` "for storing compiled mods in case users don't want to run the library".

- **How it is made.** `Tools/populateMods.py <AGRemap master export's Data/Mod Downloads>` runs
  `IDModGenService` over every character in the manifest. It reads AGRemap's files from the export and this
  repo's from `Data/`, so nothing is downloaded, and writes `Mods/<GI|WuWa>/<Name>/` and the index
  `Mods/README.md` (aliases, game version and source per mod). Folders are named by mod name (see "MOD NAMES AND
  ALIASES"). Use `--only gi|wuwa` and `--names ...` to redo part of it.
- **When to rerun it.** After any change to a generator, `Data/` or the manifest.
- **The 2026-10-06 run:** 144 GI and 54 WuWa mods, 0 failures, 4,182 files, 4.61 GB.
- **Git LFS.** `Mods/**/*.dds`, `*.buf` and `*.ib` are tracked in Git LFS, and `Mods/**/*.ini` is `-text`. The
  generators write `.ini` files with CRLF on purpose, as AGRemap's prototypes did, and `-text` keeps those bytes
  from `core.autocrlf`.
- **It costs little in LFS.** A mod's buffers and textures are byte-for-byte its download folder's, and LFS
  stores identical content once. Of the 4.61 GB, only 0.71 GB (696 distinct files) is content `Data/` does not
  already hold: what came from AGRemap's own folders.
- **What a mod contains.**
  - Each is what `python -m AGIDMGen <Name>` would write.
  - Skins with texture donors bind them.
  - WuWa mods name their textures `<prefix>Texture<hash>.dds` (see "THE WWMI PORT" in Identity Mods).

## MOD NAMES AND ALIASES: `ModNames`, AS AGREMAP NAMES ITS MOD TYPES (the maintainer's request, 2026-10-12)

The maintainer asked for "many alias names just like AGRemap", looked up with Aho-Corasick as AGRemap does, and for
the mods to be NAMED as AGRemap names its mod types. So a mod's name is no longer its download folder's name.

- **Three names per character.** `ModName.name` (what the mod, its `Mods/` folder, its `.ini` sections and its files
  are called, eg. `Raiden`), `ModName.folder` (the download folder, eg. `RaidenShogun`, which stays AGRemap's or the
  asset repo's name: never rename a download folder for this) and `ModName.aliases`.
- **The table is `AGIDMGen/data/ModNameData.py`, kept BY HAND** (not generated), `{game: {name: (folder, [aliases])}}`,
  as AGRemap keeps its aliases in `GIBuilder` / `WWMIBuilder`. It holds only this library's own aliases: at lookup,
  `ModNames` adds AGRemap's aliases from `FixRaidenBoss2.ModTypes` LIVE (matched by name and `gameTypeId`; the
  maintainer chose live over a copy) and the folder's name. A manifest folder missing from the table is named by
  its folder, so a new download folder works before anyone names it.
- **The naming convention.** AGRemap's mod type name where it has one (`Raiden`, `AyakaSpringBloom`, `Yaoyao`).
  Otherwise its style: the name players use, PascalCase (`HuTao`, `YunJin`, `Gaming`), a Japanese character's
  given name (`Kazuha`, `Ayato`, `Itto`, `Sara`, `Shinobu`, `Kokomi`; `Yae` is the one family name, as players say
  it), and a skin as the character then one word of the skin (`SanhuaExorcist`, `ChisaParfait`; ours:
  `ChangliNymph` for Laurel Nymph, `CarlottaSummer<Part>` for Splashing Summer, `JinhsiBlossom` for Peach Blossom).
  WuWa uses the in-game spelling `Jinhsi`, as AGRemap's `JinhsiBodyguard` alias does; WWMI-Assets says `Jinshi`.
  WWMI-Assets' part folders keep their part suffix (`CalcharoBody`), and `ZaniArchive` is Zani's whole model, so `Zani`.
  The WuWa skin names came from third-party guides (2026-10-12), not an official list: the maintainer is to review them.
- **Lookup is AGRemap's**: an `AhoCorasickSingleton(AhoCorasickBuilder())` per game, keyed by
  `ModNames.normalize(name)` (lowercase, and also without spaces, `_` and `-`, which AGRemap does not strip), and
  `getMaximal`: the LONGEST name or alias found INSIDE the text wins, as AGRemap's `ModTypeIdTools::findByName`.
  So `ModNames.search("RaidenShogunMod")` is Raiden. Names are filed before aliases, so an alias can never take a mod's
  name. The automaton is rebuilt whenever the manifest's folders or the table change (a key per lookup), so tests that
  `mock.patch.dict` either need no reset; a change to AGRemap's mod types needs `ModNames.clear()`.
- **Who uses the name.** `ModDownloader.getCharacters` returns mod names and `getName` returns the FOLDER for any name or
  alias; `generateFromRepo(..., modName = None)` now writes the mod under its mod's name (it was the download prefix);
  `IDModGenService` labels, files and dedupes downloaded characters by mod name (`ei` and `Raiden` make one `Raiden`).
- **Checks.** `test_ModNames.py`'s `ModNameDataTest` fails on an alias filed for two mods, on a folder named twice, and
  on a mod whose name or folder is one of AGRemap's names or aliases but is not named as AGRemap names it (both were
  shown to fail on a bad table first). `downloadsCheck.py` generates the download side with `modName = download.prefix`,
  so it still compares file by file with the asset side.
- **The 2026-10-12 rename** moved 16 mods (10 GI, 6 WuWa). Each, generated under its OLD name, was byte-identical to the
  committed `Mods/` first, so the regenerated mods differ only by name. `populateMods.py` now deletes a `Mods/` folder
  that is no mod's name, and `Mods/README.md` lists every mod's aliases.
- **Case-only renames on Windows (`AyakaSpringbloom` -> `AyakaSpringBloom`, `GaMing` -> `Gaming`).** The filesystem
  ignores case and so does git here (`core.ignorecase`): commit them with `git rm -r --cached Mods/GI/<old>` then
  `git add Mods/GI/<new>`, or the index keeps the old spelling.

## LIVE TEXTURE HASHES: `<Name>LiveHashes.json` (the maintainer's choice, 2026-11-14)

**A WuWa identity mod's texture overrides never fired in game, and nothing showed it.** WuWa streams its textures,
and 3DMigoto rehashes a texture as its mips load, so the hash an asset repo files a texture under (WWMI-Assets'
`t=<hash>`) is not the hash the game binds. An override on the asset hash silently does nothing, and the game draws
its own texture, which looks identical. Found on Zani at WuWa 3.8: her 18 textures painted flat purple stayed
unpainted; none of the 18 hashes was bound on any of her draws in a frame dump, while her mesh matched exactly. It
was **not** a 3.8 change: Chisa, whose folder AGRemap built from a dump (so from live hashes), still matched 27 of 28.
AGRemap had found the same on Sanhua at 3.7 (its Creating Remaps guide, "THE MOD LOOKS WRONG ON ITS OWN CHARACTER").

The maintainer chose AGRemap's fix, live-hash twins, over a dump-built download folder:

- **The table** is AGRemap's `<Name>LiveHashes.json`, in the CHARACTER folder beside the version folders: `{"_": note,
  "<asset hash>": "<live hash>"}`. AGRemap has Sanhua, SanhuaExorcist, Changli, ChangliNymph (and on `master`, Jinhsi
  and JinhsiBlossom); this repo has 38, starting with `WuWa/ZaniArchive/ZaniArchiveLiveHashes.json` (see "THE IN-GAME
  SWEEP" below).
- **The manifest** lists them in `ModDownloadLiveHashes` ({game: {folder: repo}}, AGRemap's first), written by
  `buildDownloadManifest.py`. `ModDownload.liveHashes` / `liveHashesFile` carry it, and `ModDownloader` fetches it from
  `<game>/<name>/<file>` (not the version folder), refusing an LFS pointer or a missing file like any other.
- **The `.ini`**: `WWMIIniBuilder` writes `[TextureOverrideTexture<n>Live]` after `[TextureOverrideTexture<n>]`, the same
  body on the live hash (AGRemap's `wwmiTextureFix.py --live` twin, in its naming). Only textures the mod carries, and
  whose live hash differs, get one. `generateFromRepo` reads the table (`WWMIIdentityModGenerator.readLiveHashes`);
  `generate` / `generateFromDownload` take `liveHashes=` for a caller who has one.
- **A table that is in the manifest but not yet on GitHub breaks generating that character from GitHub**
  (`DownloadFailed`): commit and push a new table together with the manifest, or test with `--localData`.

**Measuring a table: `Tools/Downloads/wwmiLiveHashes.py <version folder> <FrameAnalysis folder> --out <json> --note
...`.** Take the dump from the character menu, with the game's LOD bias at its maximum (`ImageDetail` 2 in
`<game>/Client/Saved/LocalStorage/LocalStorage.db`; read a COPY of it), and with no mod of the character loaded. It
pairs each asset texture with a texture bound on the character's draws (vb0 = `Metadata.json`'s `vb0_hash`) by pixel
correlation at 64 x 64, and leaves out anything unclear. **Zani (2026-11-14): 15 of 18 paired at 1.000, margins over
0.33**, off `FrameAnalysis-ZaniClean38-2026-11-14-022854` (a copy of her draws is not kept in the repo). Left out:

- `18a76e47` and `612a235b`: the game's copies are the same images with GREEN INVERTED (R, B, A correlate at 1.0, G at
  -1.0; same BC7 format and size). Binding the asset file there would flip the lighting, so they get no twin and the
  game keeps drawing its own. The tool names this case;
- `83141b71`: bound on no draw of that frame.

`8383cbbf -> a506a70d` is in AGRemap's Sanhua and Jinhsi tables too, measured independently: a texture the
characters share. **Proved in game (2026-11-14):** Zani's identity mod regenerated with the twins and its textures
painted purple turned her whole body purple; with the real textures she matched the no-mod screenshot.

**The manifest stayed on AGRemap's `eedaf348` for this change** (rebuilt from an export at that commit: only the new
table changed). `master` had moved on (Jinhsi / JinhsiBlossom 3_7 and their tables, Aether folders, Changli's), which
is a separate refresh (`staleManifest.py`).

**THE IN-GAME SWEEP (2026-11-14, WuWa 3.8).** Every WuWa mod reachable from the menus was purple-tested in game:
- **Reachable:** owned characters and skins are on the Resonators grid and its outfit screen (a locked skin's card still
  renders the model). Unowned characters are under **Gallery -> Crossing Stars**, which draws the real model's vb0, so
  the purple test and dumps work there.
- **Results:** 51 of the 54 pass with real textures matching a no-mod screenshot (46 at first, plus the five rebuilt
  below). Chisa, ChisaParfait, Lynae and
  LynaePeppermint needed no table (dump-built folders). The 4 AGRemap tables passed as they were. Every other passing
  mod needed a table: this repo now keeps 38.
- **Five are DEAD, not fixable by a table:** Yangyang (vb0 `bb5dfeaf`), RoverFemale (`3533a957`), Aalto (`93bbbdc0`),
  Yinlin (`42702199`) and Jiyan (`31b50c1d`) are drawn nowhere. The game draws new meshes for them: Rover's is
  `b7b6abd9` (41,562 vertices; the 2_7 folder has 31,790), and Aalto's is `21506004` (35,638 vs 35,634). They need new
  download folders built from the current meshes. Neither AGRemap's `master` nor WWMI-Assets (last commit 2025-10-10)
  has one.

  **They were rebuilt as `<Folder>/3_8`, here, from character-menu dumps** (see "DUMP-BUILT `3_8` FOLDERS" below).
  Each one turns fully purple and matches the no-mod shot.
- **Three are untestable from menus:** CarlottaHairCrystal (its vb0 `873457db` is not drawn in any menu tried),
  CartethyiaFleurdelys (a battle form, not an outfit) and RoverMale (the account's Rover is female).
- **AugustaHelm is unsure:** her gold sun-mask stayed unpainted. It is most likely a weapon or effect mesh, but that was
  not proved.

**Near-ties in `wwmiLiveHashes.py` were resolved by hand, and the tool should learn the rule.** A download folder often
files one image twice (a 4 MB copy and a 1 MB or 512 KB one), and the game binds it twice (full size, and a mip lower on
another draw). The tool drops both as a near-tie (margin under 0.1), and those were the textures that left coats and
dresses unpainted (Phoebe, Camellya, Shorekeeper). Each one was paired one to one with an untaken candidate scoring at
least 0.95, same file size first, then by score. Every table's note names its dump, the reason for each texture left
out, and the pairs resolved this way. Flat single-colour textures (Encore's `0585af30`) were paired by hand too.

**DUMP-BUILT `3_8` FOLDERS (2026-11-14): Yangyang, RoverFemale, Aalto, Yinlin, Jiyan.** These were built with AGRemap's
pipeline, run from its checkout without changing it (its `Data/Mod Downloads/WuWa/README.md` has the recipe):
1. `wwmiExtractDump.py --only <vb0>` extracts the dump;
2. `wwmiDownloadFolder.py` writes the folder, with `--minTextureKB 0` so the small lookup textures are kept;
3. `Tools/Misc/Diagnostics/wwmiCheckDownload.py` checks it against the dump's own bytes.

The folders keep their `2_7` prefix, and `2_7` stays beside them; the newest version wins. They carry the hashes the game
binds today, so they need no `LiveHashes.json`.

- **Proof of the pipeline at 3.8.** Chisa re-extracted from a fresh dump reproduced all 12 buffers, `Metadata.json` and 22
  textures of AGRemap's `Chisa/2_8`. The only difference is that it lacks the 6 textures AGRemap added later from a
  `dds` dump.
- **Proof of each folder.** `wwmiCheckDownload.py` reports 5 buffers byte-identical to bound slots, 4 derived and 0
  unexplained.
- **Dump with GameView's `dump --options "dump_rt dump_tex dump_cb dump_vb dump_ib buf txt dds"`**, which restores
  `d3dx.ini` itself.
  - `dds` keeps textures from being written as `.jpg`.
  - **`dump_rt` is required.** Without it, the shape-key compute outputs (`cs-u0` / `u1`) are not dumped, and the
    extractor fails with `KeyError <shape key hash>`.
  - Each dump is about 14 GB.

| folder | vb0 (2_7 -> 3_8) | ib | components, vertices | skeleton slots | weights |
| --- | --- | --- | --- | --- | --- |
| Yangyang | `bb5dfeaf` -> `4684b2e8` | `800ac114` | 8, 30,032 | 184 | 4 |
| RoverFemale | `3533a957` -> `b7b6abd9` | `f06093fa` | 7, 41,562 | 194 | 8 |
| Aalto | `93bbbdc0` -> `21506004` | `9d2b7daa` | 6, 35,638 | 167 | 4 |
| Yinlin | `42702199` -> `0b8b7323` | `2b9922b3` | 7, 48,136 | 203 | 4 |
| Jiyan | `31b50c1d` -> `9e6ec5e2` | `82a7b68b` | 7, 30,761 | 186 | 4 |

All five bind skeleton `cb4` `f02baf77`, have no blend remap, and are drawn with an `R16_UINT` index buffer.

**AGRemap's extractor fails on Yangyang and RoverFemale at 3.8, so report it to AGRemap.** Its error is `dispatch params
mismatch for SHAPEKEY_CS_1`.
- **The cause:** three compute dispatches write the same shape-key output. Their data buffers are byte-identical, but each
  has a different `cb0` and Y count. Yangyang's Y counts are 1159 / 372 / 939, and RoverFemale's 1725 / 555 / 1299.
- **The workaround:** a wrapper that imports `wwmiExtractDump` unchanged and hides the third dispatch (call 000005, a
  different shader). Hiding 000004 instead gave byte-identical output.
- **Why the result is trusted:** the builder's own check agrees (`dispatch_y 1159 vs 1159 (OK)`, `1725 vs 1725`),
  both checksums are OK, and both faces render correctly in game.
- **The wrapper was not kept**: it lived in a session's scratch folder. Aalto, Yinlin and Jiyan have only two such
  dispatches, and the unmodified extractor worked on them.

**RoverFemale is the Original Outfit.** The Resonators grid shows the Rover's worn outfit, so select the Original Outfit
card to see the mod.

**NEW CHARACTERS AND OUTFITS SINCE WWMI-ASSETS (2026-11-14, WuWa 3.8): 21 dump-built `3_8` folders.** Built with the same
recipe, prefix = folder name (no `2_7`), and named in `ModNameData.py` as the game shows them in PascalCase:
- **Where they were found:**
  - unowned characters: Gallery -> Crossing Stars (58 entries);
  - unowned outfits: the in-game Store's outfit preview (view only);
  - locked outfit cards on an owned character's outfit screen still render the model.
- **The 21:** Lily, Suoming, Jingran, Qingxiao, Suisui, YangyangXuanling, Lucilla, Lucy, Rebecca, Denia, Hiyuki, Sigrika,
  LuukHerssen, Aemeath, Mornye, Qiuyuan, Buling, HiyukiLuneNoire, ZaniDowntownRepose, MornyePlushDream and
  RoverFemalePerpetualSpark (a separate playable model).
  - All bind skeleton `f02baf77` with 8 weights a vertex. Most need a blend remap (merged skeletons of 260-501 slots).
  - `wwmiCheckDownload.py` gave 0 unexplained on each, and each turned purple in game and matched its no-mod shot.
  - 12 needed the third-dispatch workaround above (call 000005).
- **Screen-sized textures were removed by hand** from Mornye, MornyePlushDream, Aemeath and LuukHerssen (`2c25c841`,
  `7a11ab4c`, `a1332656`, and Mornye's 512x288 `0eca3068`, with their `TextureUsage.json` entries). They are 1708x964 frame
  snapshots: `7a11ab4c` and `a1332656` were the dump's own render-target outputs. Mornye's stockings stay grey in the
  purple test, likely shaded from one of these.
- **Not built:**
  - **Hsin:** her merged skeleton has 553 slots, past WWMI's 512-bone limit.
  - **Rebecca's jacket:** it is a second object (vb0 `99ec9b61`, 16,813 vertices), so the `Rebecca` mod paints all but
    the jacket. Building it needs a part split like Calcharo's, named by the maintainer.
- **Partial in the purple test:** Sigrika's emissive parts and RoverFemalePerpetualSpark's crown (an accessory) stay
  unpainted.

**`Jinshi` / `JinshiSkin1` here vs AGRemap's `Jinhsi` / `JinhsiBlossom`.** This repo's tables are for its own 2_7
folders. AGRemap's `master` keeps 3_7 folders and tables under the game's spelling. On the manifest refresh, expect the
`ChangliNymph` case below ("A FOLDER ALREADY KEPT HERE UNDER ANOTHER NAME"), with one table per folder.

## HASH FILES DERIVED FROM AGREMAP'S OWN DATA: `Tools/Downloads/hashFromAGRemap.py` (2026-10-05)

Some AGRemap GI folders have no asset folder to take a `hash.json` from:

- 12 skins AGRemap built from frame dumps: BennettAdventure, CharlotteHurlock, CherryHuTao,
  CitlaliWhisperofStars, JeanSea, KiraraBoots, LumineHeaven, NeuvilletteMelusent, NilouBreeze,
  XianglingCheer, YaoyaoBamboo and YelanTranquil;
- 8 characters whose asset folder cannot be built: BarbaraSummertime, DilucFlamme, FischlHighness,
  KeqingOpulent, KleeBlossomingStarlight, Lumine, NingguangOrchid and Yaoyao.

These get a `<prefix>Hash.json` derived from AGRemap's hash and index tables (`FixRaidenBoss2.ModData.Hashes` /
`.Indices`) and from the download folder's own file names. The tool's header says where each field comes
from. Run it with AGRemap's `api/src/py` on `PYTHONPATH`, or with FixRaidenBoss2 installed:

```bash
py -3 Tools/Downloads/hashFromAGRemap.py "<AGRemap>/Data/Mod Downloads" --check
py -3 Tools/Downloads/hashFromAGRemap.py "<AGRemap>/Data/Mod Downloads"
```

Then rerun `buildDownloadManifest.py`. **The manifest lists 144 GI characters after it (2026-10-05).**

**The rules, each learned from the data:**

- **Hashes: the newest row the folder's model was current for.** That is the newest row of all for a
  character's newest folder, else the newest row older than the next folder's version. The game rehashes
  models it does not change: Amber's `4_0` buffers are byte-identical to today's assets, but her hashes
  are not 4.0's. With each folder's own version, 18 of 20 `--check` comparisons failed.
- **Only a character's NEWEST folder by default.** Nothing in the data says when an older folder's model
  stopped being current, so `--olderVersions` is needed for those.
- **Object first indices: AGRemap's index rows where it has them; otherwise each object starts where the
  one before ends**, using the earlier `.ib` files' index counts in the order Head, Body, Dress, Extra,
  then A, B, C. AGRemap keeps no index rows for multi-component skins (`IndexData.cpp` explains why), but
  its parser configs' comments record their slot indices. The derivation reproduces every one:
  - YelanTranquil Body 0 / 53631 / 67374;
  - BennettAdventure Body 0 / 44334;
  - CitlaliWhisperofStars Body 0 / 60888 / 111096 / 122916;
  - CharlotteHurlock Body 0 / 53529 / 99756 / 103914 / 104172;
  - NeuvilletteMelusent main 0 / 46620 / 71025;
  - YaoyaoBamboo main 0 / 43092;
  - LumineHeaven main 0 / 57141.

  Where both sources exist they must agree, or the folder is refused.
- **AGRemap's mod names.** A skin's main component is filed as `<Skin>Main` (NeuvilletteMelusentMain),
  a character's as `<prefix>` or its folder name (Raiden). The lookup ignores case (AyakaSpringBloom).
- **Alias folders are skipped.** `Raiden` is another name of `RaidenShogun` (`Aliases.json`).

**How it was proved (2026-10-05):**

- **`--check`.** The tool derived the hash file of the 20 AGRemap folders that already have one from the
  asset repo, and compared what the generator reads. **19 agree in every hash, object and first index.**
  The 20th is a data disagreement, not a derivation fault; see "KAEYA'S FACE HASH" below.
- **Real mods.** Every derived hash of the 12 skins was searched for in the 386 `.ini` files of
  `E:\Computer\Games\Wuthering Waves Mods\Importer\GIMI\Mods`:
  - CherryHuTao, JeanSea, KiraraBoots, NilouBreeze and XianglingCheer: 5 of 5 found;
  - CitlaliWhisperofStars, LumineHeaven and YaoyaoBamboo: 15 of 15;
  - BennettAdventure 11 of 15, CharlotteHurlock 12 of 20, YelanTranquil 11 of 15, NeuvilletteMelusent 8 of 20.

  The partial counts are components the mods there do not override; no found hash contradicts a derived one.
- **All 20 generate** from their download folders (`downloadsCheck.py --only ...`).

**Still not generatable (2026-10-05):**

- `AyakaSpringbloom/5_4` and `Nilou/5_4` hold textures only.
- Older AGRemap folders of characters that have a newer folder are skipped by default
  (`--olderVersions`).

**TEXTURE DONORS ARE RECORDED TOO (2026-10-05).** An object with no textures of its own draws in the game
with another object's, its **texture donor**. AGRemap records the donors in each skin's
`GIMIComponentParserConfig`. Slots there read `{name, index, diffuseReg, lightMapReg, normalMapReg,
noTextures, textureDonor, donorNormalMap}`, and a donor is `"Body;A"`, or `";Head"` for the main component.

- **Where they are kept.** `hashFromAGRemap.py` reads them out of
  `IniParseData/<Name>/<Name>Parser.cpp`, as no Python accessor exists, and stores them in the hash file
  as each entry's `texture_sources` (this repo's addition to the format):
  `{"<object>": {"component": ..., "object": ..., "layout": "normalMap" | "plain"}}`. The layout is `plain`
  when the borrowing slot reads no normal map.
- **How they are used.** `GIMIIdentityModGenerator` binds a recorded donor's textures to an object that
  has none of its own, unless the caller passes `textureSources` for that component, which wins.
- **Seven skins have donors:** BennettAdventure, CharlotteHurlock, CitlaliWhisperofStars, LumineHeaven,
  NeuvilletteMelusent, YaoyaoBamboo and YelanTranquil. YelanTranquil's come out as Bang <- Body A
  (normal map) and Eye <- Body A (plain), exactly the `--textureFrom` her prototype documents.
  - **Donors are per object, not per component.** CharlotteHurlock's Body C borrows Body B, and Body D
    borrows Body A.
- **The slot indices are checked.** Every slot index in a config must equal the derived first index, or
  the folder is refused. All seven configs agreed (2026-10-05).
- **Objects with no donor stay textureless**, as AGRemap leaves them: CharlotteHurlock's Body E and
  Camera A.
- **Re-deriving.** `--overwrite --only <Name> ...` re-derives a hash file this tool wrote; an asset repo's
  hash file is never replaced.

## KAEYA'S FACE HASH: AGREMAP'S IS LIKELY STALE (looked into 2026-10-06)

The sources disagree on Kaeya's face diffuse:

- **AGRemap** (master, `api/src/cpp/core/src/data/HashData.cpp`): `6d5856da`. It was entered at 4.0 and never
  updated, although the same data moves Kaeya's `draw_vb` at 4.1 and his `ib` to `2b3f575a` at 4.3.
- **The GI asset repo**: `4e6a8e9d`, since its "Characters re-dump" (`4fb2b1f`, 2024-12-14). That dump is after
  4.3, since its IB is `2b3f575a`, and it replaced the face texture file as well as the hash.

**The evidence points to `4e6a8e9d`.** The re-dumped `KaeyaFaceHeadDiffuse.dds` is byte-identical (same sha1) to
`KaeyaSailwindFaceHeadDiffuse.dds`, and `4e6a8e9d` is also Sailwind's face hash in both sources. 3DMigoto
derives a texture's hash from its contents, so since the re-dump base Kaeya and Sailwind most likely share one
face texture. The texture before the re-dump was different.

- **No independent mod settles it.** In the maintainer's GIMI `Mods`, the only `.ini` with `6d5856da` is a
  KaeyaSailwind mod remapped by AGRemap, which only repeats AGRemap's data. No `.ini` uses `4e6a8e9d`.
- **This repo already uses `4e6a8e9d`.** Kaeya's `Hash.json` in `Data/Mod Downloads` is the asset repo's, and so
  is `Mods/GI/Kaeya`.
- **Not verified in game.** To settle it, hunt base Kaeya's face texture with GIMI. If it reports `4e6a8e9d`,
  AGRemap's `HashData.cpp` needs the update. That is AGRemap's change to make, not this repo's.
