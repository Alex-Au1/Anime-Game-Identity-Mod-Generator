##### Credits

# ===== Anime Game Identity Mod Generator (AGIDMGen) =====
# Authors: Albert Gold#2696
#
# A sub-project of Anime Game Remap (AG Remap)
# if you used it to make your mods pls give credit for "Albert Gold#2696"

##### EndCredits


##### ExtImports
from typing import Dict, Tuple
##### EndExtImports


##### Script
#: The prefix of the full name of a DXGI format
DXGIFormatPrefix = "DXGI_FORMAT_"

# The DXGI formats a buffer element may be declared with, and how each one is decoded: the numpy dtype
#   of one channel and the number of channels.
#
# note: this is a dict and not an Enum on purpose -- several formats decode the same way
#   (R8G8B8A8_UINT and R8G8B8A8_UNORM), and an Enum would make those aliases of one member

#: The DXGI formats a buffer element can be decoded from (without the ``DXGI_FORMAT_`` prefix), each with the numpy dtype of one channel and the number of channels
DXGIFormats: Dict[str, Tuple[str, int]] = {
    "R32G32B32A32_FLOAT": ("<f4", 4), "R32G32B32_FLOAT": ("<f4", 3), "R32G32_FLOAT": ("<f4", 2), "R32_FLOAT": ("<f4", 1),
    "R16G16B16A16_FLOAT": ("<f2", 4), "R16G16B16_FLOAT": ("<f2", 3), "R16G16_FLOAT": ("<f2", 2), "R16_FLOAT": ("<f2", 1),
    "R8G8B8A8_UINT": ("u1", 4), "R8G8B8A8_UNORM": ("u1", 4), "R8G8B8A8_SNORM": ("i1", 4), "R8G8B8_SNORM": ("i1", 3), "R8_SNORM": ("i1", 1), "R8_UINT": ("u1", 1), "R8_UNORM": ("u1", 1),
    "R16G16B16A16_UINT": ("<u2", 4), "R16G16B16A16_UNORM": ("<u2", 4), "R16G16_UNORM": ("<u2", 2), "R16_UINT": ("<u2", 1),
    "R32G32B32A32_UINT": ("<u4", 4), "R32_UINT": ("<u4", 1),
}
##### EndScript
