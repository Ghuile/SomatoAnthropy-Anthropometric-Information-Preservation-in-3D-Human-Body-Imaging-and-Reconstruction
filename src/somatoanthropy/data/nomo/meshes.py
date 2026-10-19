"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

import hashlib
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

@dataclass(frozen=True)
class NomoMesh:
    vertices: NDArray[np.float64]
    faces: NDArray[np.int64]
    normals: NDArray[np.float64]
    normal_indices: NDArray[np.int64]
    units: None = None
    orientation: None = None

    @property
    def topology_sha256(self) -> str:
        return hashlib.sha256(np.asarray(self.faces.shape, dtype='<i8').tobytes() + self.faces.astype('<i8').tobytes()).hexdigest()

def read_mesh(raw: bytes) -> NomoMesh:
    vertices: list[list[float]] = []
    normals: list[list[float]] = []
    faces = []
    normal_indices = []
    for line in raw.decode('ascii').splitlines():
        fields = line.split()
        if not fields or fields[0].startswith('#'):
            continue
        if fields[0] in ('v', 'vn') and len(fields) == 4:
            (vertices if fields[0] == 'v' else normals).append([float(v) for v in fields[1:]])
        elif fields[0] == 'f' and len(fields) == 4:
            parts = [v.split('//') for v in fields[1:]]
            if not (all((len(v) == 1 for v in parts)) or all((len(v) == 2 for v in parts))):
                raise ValueError('Unsupported OBJ face syntax')
            faces.append([int(v[0]) - 1 for v in parts])
            if len(parts[0]) == 2:
                normal_indices.append([int(v[1]) - 1 for v in parts])
        else:
            raise ValueError('Unsupported OBJ record; explicit review required')
    v = np.asarray(vertices, dtype=np.float64).reshape(-1, 3)
    f = np.asarray(faces, dtype=np.int64).reshape(-1, 3)
    n = np.asarray(normals, dtype=np.float64).reshape(-1, 3)
    ni = np.asarray(normal_indices, dtype=np.int64).reshape(-1, 3)
    if not len(v) or not len(f) or (not np.isfinite(v).all()) or (not np.isfinite(n).all()):
        raise ValueError('Empty/nonfinite geometry')
    if f.min() < 0 or f.max() >= len(v):
        raise ValueError('Invalid face index')
    if len(ni) and (len(ni) != len(f) or ni.min() < 0 or ni.max() >= len(n)):
        raise ValueError('Invalid/mixed normal indices')
    return NomoMesh(np.frombuffer(v.tobytes(), dtype=v.dtype).reshape(v.shape), np.frombuffer(f.tobytes(), dtype=f.dtype).reshape(f.shape), np.frombuffer(n.tobytes(), dtype=n.dtype).reshape(n.shape), np.frombuffer(ni.tobytes(), dtype=ni.dtype).reshape(ni.shape))
