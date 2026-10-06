# Mod Downloads

The **download folders** the library generates identity mods from, laid out exactly as
[Anime Game Remap](https://github.com/nhok0169/Anime-Game-Remap)'s own `Data/Mod Downloads`:

```
<Game>/<Name>/<X_Y>/      GI or WuWa / the character's folder / the game version, 4_0 for 4.0
```

**Nothing here repeats a file AG Remap has.** At run time the library takes each file from AG Remap's
GitHub `master` if AG Remap keeps it, and from this repository's `main` otherwise
(`AGIDMGen.ModDownloadRepos`), so a folder here holds only what AG Remap lacks:

| What is here | When |
| --- | --- |
| a whole folder, under the version the asset repo was at | AG Remap has no folder for the character, or its newest one differs from today's assets |
| only `<prefix>Hash.json`, in the SAME version folder as AG Remap's | AG Remap's newest folder is today's model byte for byte (GI only: AG Remap's GI folders carry no hashes) |
| nothing | AG Remap's newest folder is today's model, and the folder is complete (WuWa: `Metadata.json` has the hashes) |

## The files

**GI** (as AG Remap's `giDownloadFolder.py` writes them):

| file | what it is |
| --- | --- |
| `<P><C>Position.buf`, `Blend.buf`, `Texcoord.buf` | each skinned component's vertex buffer, split as GIMI lays it out (40 / 32 / 12 or 20 bytes a vertex) |
| `<P><C><Obj>.ib` | each object's indices, `R32_UINT` |
| `<P><C><Obj><Kind>.dds`, `<P>Face<Kind>.dds` | every texture `hash.json` lists |
| `<P>Hash.json` | **this repository's addition**: the asset folder's `hash.json`, which the `.ini` is written from |

**WuWa** (as AG Remap's `wwmiDownloadFolder.py` writes them):

| file | what it is |
| --- | --- |
| `<P>Index.buf`, `Position`, `Blend`, `Vector`, `Color`, `Texcoord`, `ShapeKeyOffset`, `ShapeKeyVertexId`, `ShapeKeyVertexOffset` | the identity mod's `Meshes/` buffers |
| `<P>BlendRemapVertexVG.buf`, `Forward`, `Reverse` | only for a merged skeleton past 256 bones |
| `<P>Texture<hash>.dds` | every texture of the asset folder |
| `<P>Metadata.json`, `<P>TextureUsage.json` | the asset folder's manifests |

`<P>` is the folder's file prefix, usually the character's folder name (AG Remap's `Raiden` folder uses
`RaidenShogun`), and `<C>` the component's name, empty for an older one-component character.

## Git LFS

The binaries here (`.buf`, `.ib`, `.dds`) are stored in [Git LFS](https://git-lfs.com); the `.json` files are not.
Install Git LFS before cloning (`git lfs install`), or run `git lfs pull` after, or the files are small pointer
files the library refuses.

## Changing what is here

**Never edit a folder by hand.** They are written by `Tools/Downloads/populateDownloads.py` from the asset
repos, and the library only knows about a folder once `Tools/Downloads/buildDownloadManifest.py` has listed it
in `AGIDMGen/src/py/AGIDMGen/data/ModDownloadData.py`. `Aliases.json` maps an asset repo's name to the
folder's (`KamisatoAyaka` -> `Ayaka`, `SanhuaSkin1` -> `SanhuaExorcist`). The library only finds these files
once they are on this repository's `main`, as AG Remap's must be on its `master`.
