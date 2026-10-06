import os
import json
import struct
from typing import Dict, Any, List, Optional


# A hand-made WWMI asset folder, small enough that every expected value in the tests can be worked out
#   by hand. Each vertex is laid out as WWMI-Assets' .fmt files lay it out (54 bytes):
#
#   0  POSITION      R32G32B32_FLOAT      12 B
#   12 TANGENT       R8G8B8A8_SNORM        4 B
#   16 NORMAL        R8G8B8A8_SNORM        4 B   (the 4th byte is the bitangent sign)
#   20 BLENDINDICES  R8G8B8A8_UINT         4 B
#   24 BLENDWEIGHT   R8G8B8A8_UNORM        4 B
#   28 COLOR         R8G8B8A8_UNORM        4 B
#   32 TEXCOORD      R16G16_FLOAT          4 B
#   36 COLOR1        R16G16_UNORM          4 B
#   40 TEXCOORD1     R16G16_FLOAT          4 B
#   44 TEXCOORD2     R16G16_FLOAT          4 B
#   48 SHAPEKEY<k>   R16G16B16_FLOAT       6 B   (only when the component has a shape key)

Elements = [("POSITION", 0, "R32G32B32_FLOAT", 0), ("TANGENT", 0, "R8G8B8A8_SNORM", 12), ("NORMAL", 0, "R8G8B8A8_SNORM", 16),
            ("BLENDINDICES", 0, "R8G8B8A8_UINT", 20), ("BLENDWEIGHT", 0, "R8G8B8A8_UNORM", 24), ("COLOR", 0, "R8G8B8A8_UNORM", 28),
            ("TEXCOORD", 0, "R16G16_FLOAT", 32), ("COLOR", 1, "R16G16_UNORM", 36), ("TEXCOORD", 1, "R16G16_FLOAT", 40), ("TEXCOORD", 2, "R16G16_FLOAT", 44)]

# the layout of WWMI Tools' export, as WWMI-Assets' Metadata.json gives it
ExportFormat = {
    "Index": {"semantics": [{"name": "INDEX", "index": 0, "format": "R32_UINT", "stride": 12}]},
    "Position": {"semantics": [{"name": "POSITION", "index": 0, "format": "R32G32B32_FLOAT", "stride": 12}]},
    "Blend": {"semantics": [{"name": "BLENDINDICES", "index": 0, "format": "R8_UINT", "stride": 4}, {"name": "BLENDWEIGHT", "index": 0, "format": "R8_UINT", "stride": 4}]},
    "Vector": {"semantics": [{"name": "TANGENT", "index": 0, "format": "R8G8B8A8_SNORM", "stride": 4}, {"name": "NORMAL", "index": 0, "format": "R8G8B8_SNORM", "stride": 3},
                             {"name": "BITANGENTSIGN", "index": 0, "format": "R8_SNORM", "stride": 1}]},
    "Color": {"semantics": [{"name": "COLOR", "index": 0, "format": "R8G8B8A8_UNORM", "stride": 4}]},
    "TexCoord": {"semantics": [{"name": "TEXCOORD", "index": 0, "format": "R16G16_FLOAT", "stride": 4}, {"name": "COLOR", "index": 1, "format": "R16G16_UNORM", "stride": 4},
                               {"name": "TEXCOORD", "index": 1, "format": "R16G16_FLOAT", "stride": 4}, {"name": "TEXCOORD", "index": 2, "format": "R16G16_FLOAT", "stride": 4}]},
    "ShapeKeyOffset": {"semantics": [{"name": "SHAPEKEY", "index": 0, "format": "R32G32B32A32_UINT", "stride": 16}]},
    "ShapeKeyVertexId": {"semantics": [{"name": "SHAPEKEY", "index": 1, "format": "R32_UINT", "stride": 4}]},
    "ShapeKeyVertexOffset": {"semantics": [{"name": "SHAPEKEY", "index": 2, "format": "R16_FLOAT", "stride": 2}]},
}


class FixtureVertex():
    def __init__(self, position = (0.0, 0.0, 0.0), tangent = (1, 2, 3, 4), normal = (5, 6, 7, -1), bones = (0, 0, 0, 0), weights = (255, 0, 0, 0),
                 color = (10, 20, 30, 40), uv = (0, 0), shapeKey: Optional[tuple] = None):
        self.position = position
        self.tangent = tangent
        self.normal = normal
        self.bones = bones
        self.weights = weights
        self.color = color
        self.uv = uv
        self.shapeKey = shapeKey


class FixtureComponent():
    def __init__(self, vertices: List[FixtureVertex], indices: List[int], vgMap: Dict[str, int], vgOffset: int, shapeKey: Optional[int] = None, ibFormat: str = "R16_UINT"):
        self.vertices = vertices
        self.indices = indices
        self.vgMap = vgMap
        self.vgOffset = vgOffset
        self.shapeKey = shapeKey
        self.ibFormat = ibFormat

    def elements(self):
        result = list(Elements)
        if (self.shapeKey is not None):
            result.append(("SHAPEKEY", self.shapeKey, "R16G16B16_FLOAT", 48))
        return result

    def stride(self) -> int:
        return 54 if (self.shapeKey is not None) else 48

    def fmtTxt(self) -> str:
        lines = [f"stride: {self.stride()}", "topology: trianglelist", f"format: DXGI_FORMAT_{self.ibFormat}"]
        for i, (name, index, fmt, offset) in enumerate(self.elements()):
            lines += [f"element[{i}]:", f"  SemanticName: {name}", f"  SemanticIndex: {index}", f"  Format: {fmt}", "  InputSlot: 0",
                      f"  AlignedByteOffset: {offset}", "  InputSlotClass: per-vertex", "  InstanceDataStepRate: 0"]
        return "\n".join(lines) + "\n"

    def vbBytes(self) -> bytes:
        data = b""
        for v in self.vertices:
            row = struct.pack("<3f", *v.position) + struct.pack("<4b", *v.tangent) + struct.pack("<4b", *v.normal) + bytes(v.bones) + bytes(v.weights)
            row += bytes(v.color) + struct.pack("<2e", *v.uv) + struct.pack("<2H", 7, 8) + struct.pack("<2e", 0.5, 0.25) + struct.pack("<2e", 1.0, 2.0)
            if (self.shapeKey is not None):
                row += struct.pack("<3e", *(v.shapeKey or (0.0, 0.0, 0.0)))
            data += row
        return data

    def ibBytes(self) -> bytes:
        return struct.pack(f"<{len(self.indices)}{'H' if self.ibFormat == 'R16_UINT' else 'I'}", *self.indices)


def writeAssets(folder: str, components: List[FixtureComponent], metadataEdits: Optional[Dict[str, Any]] = None, textures: Optional[List[str]] = None) -> Dict[str, Any]:
    os.makedirs(folder, exist_ok = True)
    entries = []
    vertexOffset = 0
    indexOffset = 0

    for i, component in enumerate(components):
        with open(os.path.join(folder, f"Component {i}.fmt"), "w", encoding = "utf-8") as f:
            f.write(component.fmtTxt())
        with open(os.path.join(folder, f"Component {i}.vb"), "wb") as f:
            f.write(component.vbBytes())
        with open(os.path.join(folder, f"Component {i}.ib"), "wb") as f:
            f.write(component.ibBytes())

        entries.append({"vertex_offset": vertexOffset, "vertex_count": len(component.vertices), "index_offset": indexOffset, "index_count": len(component.indices),
                        "vg_offset": component.vgOffset, "vg_count": len(component.vgMap), "vg_map": component.vgMap})
        vertexOffset += len(component.vertices)
        indexOffset += len(component.indices)

    metadata = {"vb0_hash": "aaaa0000", "cb4_hash": "bbbb1111", "vertex_count": vertexOffset, "index_count": indexOffset, "components": entries,
                "shapekeys": {"offsets_hash": "cccc2222", "scale_hash": "dddd3333", "vertex_count": 0, "dispatch_y": 0, "checksum": 0},
                "export_format": ExportFormat}
    if (metadataEdits is not None):
        metadata.update(metadataEdits)

    with open(os.path.join(folder, "Metadata.json"), "w", encoding = "utf-8") as f:
        json.dump(metadata, f)

    for fileName in (textures or []):
        with open(os.path.join(folder, fileName), "wb") as f:
            f.write(fileName.encode("utf-8"))

    return metadata


def twoComponents() -> List[FixtureComponent]:
    """
    Component 0: 3 vertices, one triangle, local bones 0 / 1 -> merged 0 / 1
    Component 1: 4 vertices, two triangles, local bones 0 / 1 -> merged 0 (shared with component 0) / 3,
                 shape key 5 moving its vertices 1 and 3
    """

    c0 = FixtureComponent([FixtureVertex(position = (0.0, 0.0, 0.0), bones = (0, 1, 0, 0), weights = (200, 55, 0, 0)),
                           FixtureVertex(position = (1.0, 0.0, 0.0), bones = (1, 0, 0, 0)),
                           FixtureVertex(position = (0.0, 1.0, 0.0), normal = (5, 6, 7, 1))],
                          [0, 1, 2], {"0": 0, "1": 1}, vgOffset = 0)
    c1 = FixtureComponent([FixtureVertex(position = (2.0, 0.0, 0.0), bones = (1, 0, 0, 0)),
                           FixtureVertex(position = (3.0, 0.0, 0.0), shapeKey = (0.5, 0.0, -0.25)),
                           FixtureVertex(position = (2.0, 1.0, 0.0)),
                           FixtureVertex(position = (3.0, 1.0, 0.0), shapeKey = (0.0, 1.0, 0.0))],
                          [0, 1, 2, 2, 1, 3], {"0": 0, "1": 3}, vgOffset = 2, shapeKey = 5)
    return [c0, c1]
