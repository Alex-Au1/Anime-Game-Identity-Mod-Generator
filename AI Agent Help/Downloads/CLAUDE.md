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
| `buildDownloadManifest.py <AGRemap Data/Mod Downloads>` | writes `AGIDMGen/src/py/AGIDMGen/data/ModDownloadData.py`: every version folder with its file prefix and the repo of each file |
| `downloadTools.py` | what the two share: `Aliases.json`, version folders, prefix detection |

**Rerun `buildDownloadManifest.py` after `populateDownloads.py`, and whenever AGRemap's `master` gains a
download folder.** The manifest is a generated file (it says so in its header); never edit it by hand.

**The manifest lists AGRemap's files from a LOCAL checkout.** That checkout must match what AGRemap's
GitHub `master` serves. A folder that exists only on a local branch makes the library ask GitHub for
files that 404. On 2026-10-05 the local AGRemap checkout was on branch `add-citlali`. Check
`git -C <AGRemap> status` and compare it with `master` before regenerating for a release.

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
  The 20th is a data disagreement, not a derivation fault: Kaeya's face diffuse is `6d5856da` in
  AGRemap's data, while the asset repo changed it in December 2024 (`4fb2b1f`) to `4e6a8e9d`, which is
  AGRemap's KaeyaSailwind face hash. **Which one the game binds is the maintainer's call** (an in-game
  check). Kaeya's `Hash.json` here is the asset repo's.
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
