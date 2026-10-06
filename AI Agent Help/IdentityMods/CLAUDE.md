# Identity Mods

What an identity mod is, what AGRemap uses it for, and the two generators in AGRemap that this library
is ported from: their inputs, algorithms and output layouts, and the lessons recorded about them. See
[Testing](../Testing/CLAUDE.md) for how a generated mod is proved right, and
[Architecture](../Architecture/CLAUDE.md) for how a port is laid out in the package.

Paths in this file without a repo prefix are in **AGRemap's** checkout
(`E:\Computer\Games\Genshin\Repos\Repos\Fix-Raiden-Boss`). Line numbers were taken on 2026-10-05 and will
drift; search for the quoted name if one does not match.

## What an identity mod is

> the game's own model, spelled out as a GIMI mod from the character's asset folder ... every object
> the character has, drawn exactly as the game draws it

(`Tools/Misc/Prototypes/identityMod.py`, module docstring.) AGRemap's remap pipeline puts it at
**step 4**: "each one's own model written out as a mod, every object, vertex group, texture and material
band of the real model in one folder" (`AI Agent Help/CreatingRemaps/CLAUDE.md`, the pipeline table).

What AGRemap uses it for:

- **Every bone and every material band in one mod.** A downloaded mod covers only part of the model; the
  identity mod is where a skin's true light-map band legend is read.
- **Ground truth for a character's register layout** ("read the layout off it; do not infer it").
- **The input of diagnostics**: bone centroids (`wwmiBoneTally.py`, `vgSymmetry.py --identity`) and
  synthetic test mods built by copying a pristine identity mod and stripping or merging parts
  (`chisaParfaitSynth.py`, `neuvilletteMelusentSynth.py`, `lumineHeavenSynth.py`, `yaoyaoBambooSynth.py`).
- **Telling a pipeline defect from a mod's own defect**: run the identity mod through the fix first.
- **Download folders**: AGRemap's committed `Data/Mod Downloads/<Game>/<Name>/<ver>` buffers are the
  identity mod's buffers, byte for byte.

## THE GENERATORS TO PORT (2026-10-05)

| Loader | AGRemap source | Size | Depends on | Ported |
| --- | --- | --- | --- | --- |
| GIMI (Genshin) | `Tools/Misc/Prototypes/identityMod.py` | 343 lines | `FixRaidenBoss2.VbFile` / `IbFile` (**compiled**, pybind11), numpy | **yes, 2026-10-05**, with the dump readers rewritten in Python (see "THE GIMI PORT") |
| WWMI (WuWa) | `Tools/Misc/Prototypes/wwmiIdentityMod.py` | 571 lines | numpy only | **yes, 2026-10-05** (see "THE WWMI PORT") |

## THE GIMI PORT, AND THE DUMP READERS REWRITTEN IN PYTHON (2026-10-05)

The maintainer chose to rewrite AGRemap's compiled dump readers in Python rather than depend on
`FixRaidenBoss2` for them. `identityMod.py` maps onto the library as:

| Prototype | Library |
| --- | --- |
| `FRB.VbFile(b"", []).readDumpStr` | `VbDumpFile.read` / `fromTxt` (elements: `DumpElement`, channels: `DumpDataType`) |
| `FRB.IbFile(b"").readDumpStr` | `IbDumpFile.read` / `fromTxt` |
| `bufsFromDump` | `GIMIIdentityModGenerator.buildBuffers` |
| `parseTextureFrom` | `GIMITextureSource.parse` |
| `NormalMapLayout`, `PlainLayout`, `ORFix`, `NNFix` | `GIMITextureLayouts` (`registers`, `fixCommand`) |
| `BufOf`, `FixedStrides`, `BufOrder` | `GIMISemanticBuffers`, `GIMIFixedStrides`, `GIMIBuffers` |
| `main` | `GIMIIdentityModGenerator.generate` (returns a `GIMIIdentityMod`), and `python -m AGIDMGen gimi` |
| the `.ini` text | `GIMIIniBuilder.build` |

**What "the same bytes as `readDumpStr`" took.** These are read off the C++
(`api/src/cpp/core/src/model/files/{VbFile,IbFile,BufFile}.cpp`, `model/buffers/Buf{Float,Int,Unorm}.cpp`),
not guessed:

- **Number parsing.** Every value is parsed as C++ `std::from_chars` does:
  - the longest valid prefix is the value (`"12abc"` is 12, `"1.9"` read as an int is 1);
  - text with no valid prefix is **0**, as is `"+1"` (no leading `+`), hex, and a value out of range;
  - an unsigned `"-1"` is 0.

  Python's `int()` / `float()` accept `+`, `_` and non-ASCII digits, so `DumpValueTools` matches the
  grammar with regexes instead.
- **Vertex dumps.** A vertex is a blank-line-separated block. A line's values are everything after
  its **last** `:`, split on `,`. The values fill the flattened channels in order: missing ones are 0
  and extras are ignored. A dump with no blank lines is ONE vertex.
- **Index dumps.** A line with a `:` anywhere is header. Every other line is one triangle: three
  indices, space-separated, zero-filled. Indices are always 32-bit, because `IbFile(b"")` defaults
  to 4 bytes whatever the header's `format:` says.
- **Encoding.**
  - A float32 is rounded to nearest.
  - A float16 is **truncated**, AGRemap's default `BufFloat16::Rounding` (numpy's `astype(float16)`
    rounds, which would differ).
  - A UNORM is `trunc(value * max)`, not rounded.
  - An integer keeps its low bytes.
- **Formats.** The C++ reads only `FLOAT` (2 or 4 bytes), `SINT`, `UINT` and `UNORM`. Any other
  format, such as a `SNORM` or a channel narrower than a byte, fails the whole header, and the
  generator raises.

**What the GIMI port does differently, on purpose.** Each change below has a unit test:

- Missing files and bad metadata raise `BadAssetData`. The prototype crashed with a raw
  `FileNotFoundError` / `KeyError`.
- It checks everything before writing anything.
- A `--textureFrom` that names a lender component or object the character lacks raises. The prototype
  crashed on an unknown component and silently bound nothing for an unknown object.
- The `.ini`'s last comment says `built by AGIDMGen`.
- There is no path translation for WSL.

**It is about 4 times faster than the prototype (2026-10-05):** Yelan takes 10 s instead of 40 s, most
of the prototype's time being AGRemap's DLLs loading. Nothing has needed a C++ layer yet.

## THE WWMI PORT (2026-10-05)

`wwmiIdentityMod.py` maps onto the library as:

| Prototype | Library |
| --- | --- |
| `readFmt` | `FmtFile.read` / `FmtFile.fromTxt` |
| `formatOf`, `Formats` | `FormatTools.decode`, `DXGIFormats` |
| `Component` | `WWMIComponent` (`getElementBytes`, `getShapeKeys`) |
| `buildIndex`, `buildVertexBuffer`, `buildBlend`, `buildBlendRemaps`, `buildShapeKeys` | the same names on `WWMIIdentityModGenerator` |
| `iniText`, `blendRemapIni` | `WWMIIniBuilder.build` |
| `main` | `WWMIIdentityModGenerator.generate` (returns a `WWMIIdentityMod`), and `python -m AGIDMGen wwmi` |
| the printed report | `WWMIIdentityMod.getSummary()` |
| `BufferFiles`, `ShapeKeySlots`, `BlendRemapSize` | `WWMIBuffers`, `WWMIShapeKeySlots`, `WWMIBlendRemapSize` |

**What the port does differently, on purpose:**

- **Errors.** It raises `BadAssetData` / `UnknownDXGIFormat`, where the prototype used
  `SystemExit(message)`; the message is the same.
- **Validation before writing.** It checks everything before writing anything. The prototype could
  leave a half-written mod, for example when the Blend buffer's `vg_map` check failed after
  `Index.buf` was already written.
- **Missing metadata keys.** A missing `vb0_hash`, `cb4_hash`, `vertex_offset` or `index_offset` is a
  `BadAssetData`; the prototype hit a `KeyError`.
- **`mod.ini` credits.** Its two lines that name the generator say AGIDMGen.
- **No path translation.** It does not translate `E:\` paths to `/mnt/e/` (`winToPosix`); callers pass
  paths for the OS they run on.
- **Characters with no shape keys.** The summary handles them; the prototype's report crashed on
  `keys[0]` after writing the mod.
- **Exit code.** The command line exits with **2** when the shape keys' checksum or `dispatch_y` does not
  match `Metadata.json`. The prototype printed `MISMATCH` and exited 0.

**What it keeps exactly**, because AGRemap's tools and download folders depend on it:

- every buffer byte;
- the WWMI BETA-2 / WWMI Tools 1.3.4 `.ini` template, with its known differences from current real
  mods (see the lessons below);
- CRLF line endings;
- the default author `Anime Game Remap`.

How it was proved is in [Testing](../Testing/CLAUDE.md)'s "THE WWMI ACCEPTANCE CHECKS".

**The asset folder must carry `export_format` in its `Metadata.json`.** Older WWMI-Assets checkouts do
not have it (this machine's did not until the maintainer pulled it on 2026-10-05). The generator then refuses with *"Metadata.json's
export_format has no 'Position' buffer"*, as the prototype did. Deriving a default layout instead would
be a guess about the asset folder (Architecture: "Do not assume a mod's or an asset folder's structure"),
so it is the maintainer's call. Note that only the Blend stride varies between characters (8 or 16
bytes).

Related tools that reuse them, which the library should make unnecessary or thin:

- `Tools/Misc/Prototypes/giDownloadFolder.py`: the GIMI conversion without the `.ini`; it imports
  `bufsFromDump`, `ibFromDump` and `winToPosix` from `identityMod.py`.
- `Tools/Misc/Prototypes/wwmiDownloadFolder.py`: runs `wwmiIdentityMod.py` as a subprocess and renames
  its output.
- `Tools/Misc/Prototypes/wwmiExtractDump.py`: turns a frame dump into a WWMI asset folder for characters
  WWMI-Assets lacks, by running WWMI Tools' own extractor with `bpy` stubbed out.
- `Tools/Misc/Diagnostics/identityVsDump.py`: the GIMI acceptance test (see [Testing](../Testing/CLAUDE.md)).
- `Tools/DumpToModConverter/GI/GIDumpToModConverter.ipynb`: the older notebook on the same dump-reader path.

No SRMI (Star Rail) or ZZMI (Zenless) identity generator exists in AGRemap (2026-10-05).

### GIMI: `identityMod.py`

**Command line**:

```
python identityMod.py <assets> <mod> [--name N] [--assetPrefix P] [--noFix]
    [--faceRegister ps-t0|ps-t1] [--textureFrom COMP=COMP:OBJ[:normalMap|plain]]...
```

**Input** is a `GI-Model-Importer-Assets/PlayerCharacterData/<Name>` folder:

- `hash.json`: one entry per component, with `component_name`, `position_vb`, `blend_vb`,
  `texcoord_vb`, `draw_vb`, `ib`, `object_classifications`, `object_indexes`, `texture_hashes`.
- The dump text files `<prefix><Comp><Obj>-vb0=<hash>.txt` and `-ib=<hash>.txt`.
- The `.dds` textures.

No RemapDraft and no AGRemap hash data are involved.

**Algorithm**:

1. **Pick the components.** A component is a `hash.json` entry with both `position_vb` and `blend_vb`.
   Unskinned entries are reported and skipped.
2. **`bufsFromDump` (around line 125).** Reads the first object's vb0 dump with
   `FRB.VbFile(b"", []).readDumpStr()` and routes each element to a buffer:
   - POSITION / NORMAL / TANGENT go to **Position** (stride 40);
   - BLENDWEIGHT(S) / BLENDINDICES go to **Blend** (stride 32);
   - COLOR / TEXCOORD* go to **Texcoord** (stride 12 or 20, measured).

   It writes each buffer as `<name><comp><Part>.buf`.
3. **`ibFromDump` (around line 155).** Reads the indices with `FRB.IbFile.readDumpStr` and writes
   `<name><comp><obj>.ib` as R32_UINT. It checks that no index is past the vertex count.
4. **Copy the textures.** Each listed `.dds` is copied as `<name><comp><obj><Kind>.dds`. The face diffuse
   becomes `<name>Face<obj>Diffuse.dds`.
5. **Write `<name>.ini`** with **CRLF** line endings:
   - Per component: `TextureOverride<name><comp>{Position,Blend,Texcoord,VertexLimitRaise,IB}`. Blend
     gets `handling = skip` and `draw = <vc>,0`; IB gets `drawindexed = auto`.
   - Per object: a section with `match_first_index` and `ib`, and its texture registers in one of two
     layouts:
     - `NormalMapLayout`: `ps-t0` NormalMap, `ps-t1` Diffuse, `ps-t2` LightMap, then
       `run = CommandList\global\ORFix\ORFix`;
     - `PlainLayout`: `ps-t0` Diffuse, `ps-t1` LightMap, then `run = CommandList\global\ORFix\NNFix`.
     - The layout is picked by whether the object HAS a normal map (`identityMod.py` around line 294).
       Nothing in `hash.json` says which shader an object draws with; the prototype's header explains
       how it was read off a frame dump.
     - An object that binds no textures gets no `run` line (deliberate: ORFix / NNFix re-slot whatever
       is bound).
   - An optional `TextureOverride<name>FaceHeadDiffuse` on `--faceRegister`.
   - The Resource sections last.

**Output** (flat, one folder): `<N>.ini`, `<N><C>Position.buf`, `<N><C>Blend.buf`, `<N><C>Texcoord.buf`,
`<N><C><Obj>.ib`, `<N><C><Obj><Kind>.dds`, `<N>FaceHeadDiffuse.dds`. `<C>` is empty for a
single-component character, and that output **must stay byte-identical** to the old naming
(checked by the prototype itself).

**Options that exist for one character each, so a port must keep them general:**

- `--textureFrom`: a component that borrows another's textures (YelanTranquil's Bang / Eye).
- `--faceRegister ps-t1`: GI 6.x skins moved the face diffuse to `ps-t1`.
- `--assetPrefix`: CitlaliWhisperofStars' files are named `Citlali_WhisperOfStars...`.

### WWMI: `wwmiIdentityMod.py`

**Command line**:

```
python wwmiIdentityMod.py <assets> <mod> [--name] [--author "Anime Game Remap"] [--noTextures] [--rawBones]
```

**Input** is a `WWMI-Assets/PlayerCharacterData/<Name>` folder:

- `Metadata.json`:
  - `components[]`, each with `vertex_offset`, `index_offset`, `vertex_count`, `index_count`,
    `vg_offset`, `vg_count`, `vg_map`;
  - `export_format`, `vb0_hash`, `cb4_hash`;
  - `shapekeys{offsets_hash, scale_hash, checksum, dispatch_y}`.
- One `Component N.fmt` / `.vb` / `.ib` triple per component.
- The textures, named `Components-... t=<hash>.dds`.

**Algorithm**:

1. **Read the components.** Parse each `.fmt`, reshape its `.vb` into rows, and check that the offsets
   are contiguous and the counts match `Metadata.json`.
2. **Build the index buffer.** Add each component's `vertex_offset` to its local indices and
   concatenate.
3. **Copy the per-vertex data.** Position, Vector, Color and TexCoord are byte-copied, using the
   semantics in `export_format`. BITANGENTSIGN is synthesised from NORMAL's 4th byte.
4. **`buildBlend`.**
   - Bone ids go through each component's `vg_map`, or `vg_offset + local` with `--rawBones`.
   - Ids are truncated to uint8.
   - There are 4 or 8 weights per vertex.
5. **`buildBlendRemaps`.** Past 256 bones (the limit is 512), writes `BlendRemapVertexVG`,
   `BlendRemapForward` and `BlendRemapReverse` (512 uint16 per remap). This follows WWMI Tools 1.7.3's
   `build_blend_remap`.
6. **`buildShapeKeys`.** Writes sparse shape keys:
   - `ShapeKeyOffset` (128 uint32);
   - `ShapeKeyVertexId`;
   - `ShapeKeyVertexOffset` (six float16 per entry).
7. **Copy the textures** into `Textures/`.
8. **Write `mod.ini`.** It is the WWMI BETA-2 template copied from WWMI Tools 1.3.4's output:
   - the constants, `[Present]`, RegisterMod and MergeSkeleton;
   - `TextureOverrideComponent<i>`, matched on `vb0_hash`, `match_first_index` and `match_index_count`;
   - `TextureOverrideTexture<n>` with `this =`;
   - the shape-key and resource sections.
9. **Self-check.** The four shape-key offsets must sum to Metadata's `checksum`, and `dispatch_y` must
   match.

**Output**:

- `mod.ini`;
- `Meshes/{Index,Position,Blend,Vector,Color,TexCoord,ShapeKeyOffset,ShapeKeyVertexId,ShapeKeyVertexOffset}.buf`;
- `Meshes/BlendRemap*.buf`, only when the character needs a blend remap;
- `Textures/Components-... t=<hash>.dds`.

### What differs between the loaders

| | GIMI | WWMI |
| --- | --- | --- |
| buffers | separate per component | one merged mesh, drawn per component's index range |
| skeleton | per component | merged, de-duplicated through `vg_map`; blend remap past 256 bones |
| weights per vertex | 4 | 4 or 8 |
| textures | bound to `ps-t*` registers per object, layout by shader family (ORFix / NNFix) | overridden by hash (`this =`), no register lines |
| shape keys | none | sparse shape-key buffers |

## LESSONS AGREMAP RECORDED ABOUT IDENTITY MODS

These are AGRemap's, dated as recorded there (in `AI Agent Help/CreatingRemaps`, `VGRemaps` and `Overview`).

- **THE IDENTITY MOD IS THE EASY CASE IN FOUR SEPARATE WAYS (2026-09-15).** It uses
  `drawindexed = auto`, every vertex group and band, 32-bit indices, and one variant with today's
  hashes.
- **It is "a sample of none" (2026-10-02).** It is generated by the same repo that reads it, so it
  agrees with that code's assumptions by construction. An option whose only test was the identity mod
  is untested (2026-09-20).
- **It downloads nothing**, so it never exercises a fix's download path.
- **The acceptance test is a byte comparison against the game's own buffers, not a clean run.**
  Comparing against the dump text the writer itself parsed validates in a circle.
- **The WWMI template is not what current real mods look like.** It writes
  `vs-cb4 = ResourceMergedSkeleton`, where real mods write `= ref ...`. It maintains `$state_id`, which
  current real mods never assign; they keep `$merge_status_id`.
  - Keep the generator's output as it is unless the maintainer decides otherwise, since AGRemap's
    tools read it.
  - Never use it as evidence of what real mods contain.
- **WWMI Tools' version matters.** 1.3.3 hard-codes four ids per vertex and is wrong for an
  8-weight character; follow 1.7.3.
- **NEVER DUMP A CHARACTER WITH A MOD OF THAT CHARACTER INSTALLED (2026-09-20).** With the identity mod
  active, the dump's `cb4_hash` came back empty, and the extractor reported a 929-slot skeleton instead
  of 264.
- **Dumped textures are partly streamed.** Set the LOD bias to maximum and dump from the character menu
  (`Data/Mod Downloads/WuWa/README.md`).
- **A skin's band legend is the mod author's, not the skin's.** Yelan's 255 = fur was read off her
  identity mod.
- **Run a fix on a scratch copy, never on the pristine identity mod (2026-09-25).** An AGRemap undo
  (`RemapIniRemover`) matched "Remap" as a substring of `ResourceBlendRemap*` and deleted the identity
  mod's own blend-remap buffers.

## Where the test material is

- **No generated identity mods are committed anywhere.** They live on the maintainer's machine
  (`Mods/Yelan4`, `Mods/YelanTranquilIdentity`, `WWMI/SanhuaIdentity`, `ChisaParfaitIdentity`,
  `CharlotteIdentity`, ...).
- **WWMI-Assets is at `E:\Computer\Games\Wuthering Waves Mods\Repos\WWMI-Assets`**. The maintainer pulled it
  on 2026-10-05; it is now at commit `eff456b` (2025-10-10).
  - It has 50 characters under `PlayerCharacterData`, all with `export_format`.
  - 8 of them have eight bone weights a vertex.
  - Skins are named `<Char>SkinN`; `SanhuaSkin1` is AGRemap's `SanhuaExorcist`.
  - Changli, Roccia and Shorekeeper exercise the blend remap.

  Before the pull it was at `6581f79` (2025-01-13, 31 characters, no `export_format`). `E:\Computer\Games\Wuthering Waves Mods\Repos\Camellya` is a loose
  Camellya asset folder.
- **GI-Model-Importer-Assets is at `E:\Computer\Games\Genshin\Repos\Repos\GI-Model-Importer-Assets`
  (2026-10-05).** It is at commit `2039d16` (2026-08-03), with 134 folders under `PlayerCharacterData`.
  `GI-Model-Importer-Assets-Fork` beside it is from 2024-12-22. Some of its folders cannot be built
  from as they are:
  - **The dump files do not match `hash.json`** for BarbaraSummertime, DilucFlamme, FischlHighness,
    KeqingOpulent, KleeBlossomingStarlight, NingguangOrchid, TravelerBoy, TravelerGirl and YaoYao.
    `hash.json` names an `ib` hash that no dump file carries (BarbaraSummertime: `9cc5a563` in
    `hash.json`, `a411cfbc` on the files).
  - **RosariaCN's files are named `Rosaria...`**, so it needs `--assetPrefix Rosaria --name RosariaCN`.
  - **ShenheMod has no `hash.json`.**

  Both the prototype and the port refuse these folders.
- **The only component with an object that has no textures of its own is Flins' Lantern, object B**
  (2026-10-05). It is the one place to exercise `--textureFrom` on real data.
- The characters exercised so far:
  - GIMI: Yelan, YelanTranquil, Bennett, Charlotte, Citlali, Neuvillette, Lumine, Yaoyao (download
    checks: Diluc, Amber, Klee, Ganyu, Yelan, YelanTranquil).
  - WWMI: Sanhua, SanhuaExorcist, Chisa, ChisaParfait (420 bones); blend remap checked on Augusta, Iuno,
    Galbrena, Changli.
