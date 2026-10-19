import json
import struct
from pathlib import Path

import numpy as np


def read_glb(path):
    """Read a self-contained static triangle GLB; return data without transforming it."""
    raw = Path(path).read_bytes()
    magic, version, size = struct.unpack_from("<4sII", raw, 0)
    if magic != b"glTF" or version != 2 or size != len(raw):
        raise ValueError("Invalid GLB header")
    chunks = []
    offset = 12
    while offset < len(raw):
        length, kind = struct.unpack_from("<II", raw, offset)
        offset += 8
        if offset + length > len(raw):
            raise ValueError("Truncated GLB")
        chunks.append((kind, raw[offset : offset + length]))
        offset += length
    doc = json.loads(next(data for kind, data in chunks if kind == 0x4E4F534A))
    binary = next(data for kind, data in chunks if kind == 0x004E4942)
    if len(doc.get("buffers", [])) != 1 or "uri" in doc["buffers"][0]:
        raise ValueError("External buffers are not allowed")
    if doc.get("skins") or doc.get("animations") or doc.get("images"):
        raise ValueError("Unexpected rig, animation or texture")

    def accessor(index):
        acc = doc["accessors"][index]
        if "sparse" in acc:
            raise ValueError("Sparse accessor not supported")
        view = doc["bufferViews"][acc["bufferView"]]
        if view.get("buffer", 0) != 0:
            raise ValueError("Unexpected buffer")
        dtype = np.dtype({5126: "<f4", 5125: "<u4", 5123: "<u2", 5121: "u1"}[acc["componentType"]])
        width = {"SCALAR": 1, "VEC3": 3}[acc["type"]]
        count = int(acc["count"])
        stride = int(view.get("byteStride", dtype.itemsize * width))
        start = int(view.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
        if count < 1 or stride < dtype.itemsize * width:
            raise ValueError("Invalid accessor layout")
        if start + (count - 1) * stride + width * dtype.itemsize > len(binary):
            raise ValueError("Accessor outside buffer")
        return np.ndarray(
            (count, width),
            dtype=dtype,
            buffer=binary,
            offset=start,
            strides=(stride, dtype.itemsize),
        ).copy()

    if len(doc.get("meshes", [])) != 1:
        raise ValueError("Expected one mesh")
    primitives = doc["meshes"][0]["primitives"]
    if len(primitives) != 1 or primitives[0].get("mode", 4) != 4:
        raise ValueError("Expected triangles")
    primitive = primitives[0]
    vertices = accessor(primitive["attributes"]["POSITION"])
    indices = accessor(primitive["indices"]).reshape(-1)
    if len(indices) % 3:
        raise ValueError("Invalid triangle index count")
    faces = indices.reshape(-1, 3)
    if vertices.shape[1] != 3 or not np.isfinite(vertices).all():
        raise ValueError("Invalid vertex coordinates")
    if faces.max() >= len(vertices):
        raise ValueError("Face index outside vertex array")
    for node in doc.get("nodes", []):
        if any(k in node for k in ["matrix", "translation", "rotation", "scale"]):
            raise ValueError("Unexpected node transform")
    return vertices, faces, doc
