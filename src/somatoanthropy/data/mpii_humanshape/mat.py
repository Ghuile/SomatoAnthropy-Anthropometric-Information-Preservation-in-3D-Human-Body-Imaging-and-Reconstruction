"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

import math
import struct
import zlib
from collections.abc import Iterator
from typing import Any

import numpy as np
from numpy.typing import NDArray

MAX_ELEMENT_BYTES = 1000000000


def _elements(data: memoryview, endian: str) -> Iterator[tuple[int, memoryview]]:
    offset = 0
    while offset < len(data):
        if len(data) - offset < 8:
            raise ValueError("Truncated MAT tag")
        small_type, small_size = struct.unpack_from(endian + "HH", data, offset)
        if struct.unpack_from(endian + "I", data, offset)[0] > 65535:
            if small_size > 4:
                raise ValueError("Invalid small MAT element")
            yield (small_type, data[offset + 4 : offset + 4 + small_size])
            offset += 8
            continue
        kind, size = struct.unpack_from(endian + "II", data, offset)
        end = offset + 8 + size
        if size > MAX_ELEMENT_BYTES or end > len(data):
            raise ValueError("Truncated or oversized MAT element")
        yield (kind, data[offset + 8 : end])
        offset = end if kind == 15 else end + -size % 8
        if offset > len(data):
            raise ValueError("Truncated MAT padding")


def read_numeric_mat(raw: bytes) -> dict[str, NDArray[Any]]:
    if len(raw) < 128 or not raw.startswith(b"MATLAB 5.0 MAT-file"):
        raise ValueError("Only Level-5 MAT files supported")
    if raw[126:128] not in (b"IM", b"MI"):
        raise ValueError("Invalid MAT endian indicator")
    endian = "<" if raw[126:128] == b"IM" else ">"
    if struct.unpack_from(endian + "H", raw, 124)[0] != 256:
        raise ValueError("Unsupported MAT version")
    if any(raw[116:124]):
        raise ValueError("MAT subsystem data unsupported")
    result = {}
    for kind, payload in _elements(memoryview(raw)[128:], endian):
        if kind == 15:
            inflater = zlib.decompressobj()
            expanded = inflater.decompress(payload, MAX_ELEMENT_BYTES + 1)
            if (
                len(expanded) > MAX_ELEMENT_BYTES
                or not inflater.eof
                or inflater.unused_data
                or inflater.unconsumed_tail
            ):
                raise ValueError("Invalid/oversized compressed MAT stream")
            inner = list(_elements(memoryview(expanded), endian))
            if len(inner) != 1 or inner[0][0] != 14:
                raise ValueError("Compressed MAT must contain one numeric matrix")
            payload = inner[0][1]
        elif kind != 14:
            raise ValueError("Unsupported MAT data element")
        parts = list(_elements(payload, endian))
        if len(parts) != 4:
            raise ValueError("Only simple real numeric MAT arrays supported")
        (flag_type, flags), (dim_type, dims), (name_type, name), (real_type, values) = parts
        if flag_type != 6 or len(flags) != 8:
            raise ValueError("Invalid MAT flags")
        flag = struct.unpack_from(endian + "I", flags)[0]
        if flag != 6 or real_type not in (9, 4):
            raise ValueError("Only real nonlogical double arrays supported")
        if dim_type != 5 or len(dims) < 8 or len(dims) % 4:
            raise ValueError("Invalid MAT dimensions")
        shape = struct.unpack(endian + "i" * (len(dims) // 4), dims)
        itemsize = 8 if real_type == 9 else 2
        if any((x < 0 for x in shape)) or math.prod(shape) * itemsize != len(values):
            raise ValueError("MAT shape/storage mismatch")
        if name_type != 1:
            raise ValueError("Invalid MAT variable name type")
        key = bytes(name).decode("ascii")
        if not key or key in result:
            raise ValueError("Missing/duplicate MAT variable")
        storage = "f8" if real_type == 9 else "u2"
        array = np.frombuffer(values, dtype=np.dtype(endian + storage)).reshape(shape, order="F")
        if real_type == 4:
            array = np.frombuffer(array.astype("<f8").tobytes(order="F"), dtype="<f8").reshape(
                shape, order="F"
            )
        if not np.isfinite(array).all():
            raise ValueError("Nonfinite source numeric array")
        result[key] = array
    if not result:
        raise ValueError("Empty MAT file")
    return result
