import os
import json
from typing import Dict, Any, List, Optional


# A hand-made GIMI asset folder, laid out as GI-Model-Importer-Assets' are: hash.json, the text dumps of
#   each object's vertex and index buffers (<prefix><component><object>-vb0=<hash>.txt / -ib=<hash>.txt)
#   and the textures (<prefix><component><object><kind>.dds). Each vertex is laid out as the game's
#   (92 bytes):
#
#   0  POSITION      R32G32B32_FLOAT       12 B  \
#   12 NORMAL        R32G32B32_FLOAT       12 B   > Position.buf, 40 B
#   24 TANGENT       R32G32B32A32_FLOAT    16 B  /
#   40 BLENDWEIGHT   R32G32B32A32_FLOAT    16 B  \  Blend.buf, 32 B
#   56 BLENDINDICES  R32G32B32A32_SINT     16 B  /
#   72 COLOR         R8G8B8A8_UNORM         4 B  \
#   76 TEXCOORD      R32G32_FLOAT           8 B   > Texcoord.buf, 20 B (12 without TEXCOORD1)
#   84 TEXCOORD1     R32G32_FLOAT           8 B  /

GameElements = [("POSITION", 0, "R32G32B32_FLOAT"), ("NORMAL", 0, "R32G32B32_FLOAT"), ("TANGENT", 0, "R32G32B32A32_FLOAT"),
                ("BLENDWEIGHT", 0, "R32G32B32A32_FLOAT"), ("BLENDINDICES", 0, "R32G32B32A32_SINT"), ("COLOR", 0, "R8G8B8A8_UNORM"),
                ("TEXCOORD", 0, "R32G32_FLOAT"), ("TEXCOORD", 1, "R32G32_FLOAT")]
ElementValueCounts = {"R32G32B32_FLOAT": 3, "R32G32B32A32_FLOAT": 4, "R32G32B32A32_SINT": 4, "R8G8B8A8_UNORM": 4, "R32G32_FLOAT": 2}
ElementSizes = {"R32G32B32_FLOAT": 12, "R32G32B32A32_FLOAT": 16, "R32G32B32A32_SINT": 16, "R8G8B8A8_UNORM": 4, "R32G32_FLOAT": 8}


def vbDumpTxt(vertexCount: int, elements = None) -> str:
    """A vertex buffer dump whose vertex i has every value of every element equal to i (COLOR: 1, so it is 255)"""
    elements = GameElements if (elements is None) else elements
    lines = [f"stride: {sum(ElementSizes[f] for _, _, f in elements)}", "first vertex: 0", f"vertex count: {vertexCount}", "topology: trianglelist"]
    offset = 0
    for i, (name, index, fmt) in enumerate(elements):
        lines += [f"element[{i}]:", f"  SemanticName: {name}", f"  SemanticIndex: {index}", f"  Format: {fmt}", "  InputSlot: 0",
                  f"  AlignedByteOffset: {offset}", "  InputSlotClass: per-vertex", "  InstanceDataStepRate: 0"]
        offset += ElementSizes[fmt]
    lines += ["", "vertex-data:", ""]

    for v in range(vertexCount):
        offset = 0
        for name, index, fmt in elements:
            value = 1 if (fmt == "R8G8B8A8_UNORM") else v
            semantic = name + (str(index) if index else "")
            lines.append(f"vb0[{v}]+{offset:03d} {semantic}: " + ", ".join([str(value)] * ElementValueCounts[fmt]))
            offset += ElementSizes[fmt]
        if (v + 1 < vertexCount):
            lines.append("")
    return "\r\n".join(lines) + "\r\n"


def ibDumpTxt(firstIndex: int, indices: List[int]) -> str:
    lines = ["byte offset: 0", f"first index: {firstIndex}", f"index count: {len(indices)}", "topology: trianglelist", "format: DXGI_FORMAT_R16_UINT", ""]
    lines += [" ".join(str(i) for i in indices[t:t + 3]) for t in range(0, len(indices), 3)]
    return "\r\n".join(lines) + "\r\n"


class FixtureObject():
    def __init__(self, name: str, firstIndex: int, indices: List[int], textures: Optional[List[str]] = None):
        self.name = name
        self.firstIndex = firstIndex
        self.indices = indices
        self.textures = [] if (textures is None) else textures


class FixtureComponent():
    def __init__(self, name: str, vertexCount: int, objects: List[FixtureObject], hashPrefix: str, skinned: bool = True, elements = None):
        self.name = name
        self.vertexCount = vertexCount
        self.objects = objects
        self.hashPrefix = hashPrefix
        self.skinned = skinned
        self.elements = elements

    def entry(self) -> Dict[str, Any]:
        h = self.hashPrefix
        result = {"component_name": self.name, "root_vs": "0", "draw_vb": f"{h}d0000", "position_vb": f"{h}p0000",
                  "texcoord_vb": f"{h}t0000", "ib": f"{h}i0000", "object_indexes": [o.firstIndex for o in self.objects],
                  "object_classifications": [o.name for o in self.objects],
                  "texture_hashes": [[[kind, ".dds", f"{h}{kind[:3].lower()}{i}"] for kind in o.textures] for i, o in enumerate(self.objects)]}
        if (self.skinned):
            result["blend_vb"] = f"{h}b0000"
        return result


def writeAssets(folder: str, prefix: str, components: List[FixtureComponent], face: bool = True) -> List[Dict[str, Any]]:
    os.makedirs(folder, exist_ok = True)
    entries = []
    for component in components:
        entry = component.entry()
        entries.append(entry)
        for obj in component.objects:
            base = os.path.join(folder, f"{prefix}{component.name}{obj.name}")
            with open(f"{base}-vb0={entry['position_vb']}.txt", "w", encoding = "utf-8", newline = "") as f:
                f.write(vbDumpTxt(component.vertexCount, component.elements))
            with open(f"{base}-ib={entry['ib']}.txt", "w", encoding = "utf-8", newline = "") as f:
                f.write(ibDumpTxt(obj.firstIndex, obj.indices))
            for kind in obj.textures:
                with open(f"{base}{kind}.dds", "wb") as f:
                    f.write(f"{component.name}{obj.name}{kind}".encode("utf-8"))

    if (face):
        entries.append({"component_name": "Face", "object_classifications": ["Head"], "texture_hashes": [[["Diffuse", ".dds", "facef00d"]]]})
        with open(os.path.join(folder, f"{prefix}FaceHeadDiffuse.dds"), "wb") as f:
            f.write(b"face")

    with open(os.path.join(folder, "hash.json"), "w", encoding = "utf-8") as f:
        json.dump(entries, f)
    return entries


def oneComponent() -> List[FixtureComponent]:
    """An older character: one unnamed component of 4 vertices, objects Head (one triangle) and Body (two)"""
    return [FixtureComponent("", 4, [FixtureObject("Head", 0, [0, 1, 2], ["Diffuse", "LightMap"]),
                                     FixtureObject("Body", 3, [1, 2, 3, 3, 2, 0], ["NormalMap", "Diffuse", "LightMap"])], "aa")]


def twoComponents() -> List[FixtureComponent]:
    """A newer character: a Body of 3 vertices with textures, a Bang of 3 vertices with none and no TEXCOORD1,
    and an unskinned Mouth"""
    noUV1 = [e for e in GameElements if e != ("TEXCOORD", 1, "R32G32_FLOAT")]
    return [FixtureComponent("Body", 3, [FixtureObject("A", 0, [0, 1, 2], ["NormalMap", "Diffuse", "LightMap"])], "bb"),
            FixtureComponent("Bang", 3, [FixtureObject("A", 0, [2, 1, 0])], "cc", elements = noUV1),
            FixtureComponent("Mouth", 3, [FixtureObject("A", 0, [0, 1, 2])], "dd", skinned = False)]
