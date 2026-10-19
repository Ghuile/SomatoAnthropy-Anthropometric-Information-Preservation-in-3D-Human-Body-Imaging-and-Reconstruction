"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from somatoanthropy.data.mpii_humanshape.mat import read_numeric_mat


def points_array(raw: bytes) -> NDArray[Any]:
    variables = read_numeric_mat(raw)
    if set(variables) != {"points"}:
        raise ValueError("Expected only the source points array")
    points = variables["points"]
    if points.ndim != 2 or points.shape[1] != 3 or (not len(points)):
        raise ValueError("Expected nonempty N by 3 source points")
    return points


def _immutable(array: NDArray[Any]) -> NDArray[Any]:
    return np.frombuffer(array.tobytes(), dtype=array.dtype).reshape(array.shape)


def template_arrays(raw: bytes) -> tuple[NDArray[Any], NDArray[Any], NDArray[Any], NDArray[Any]]:
    lines = raw.decode("ascii").splitlines()
    header = lines[0].split() if lines else []
    if len(header) != 4:
        raise ValueError("Invalid model.dat header")
    n, f, j, smooth = (int(x) for x in header)
    if min(n, f, j, smooth) <= 0:
        raise ValueError("Empty model.dat structure")
    rows = [line.split() for line in lines[1:] if line.strip()]
    if len(rows) != n + f + j:
        raise ValueError("Unexpected model.dat row count")
    if (
        any((len(row) != 3 + smooth * 2 for row in rows[:n]))
        or any((len(row) != 3 for row in rows[n : n + f]))
        or any((len(row) != 8 for row in rows[n + f :]))
    ):
        raise ValueError("Unexpected model.dat row widths")
    vertices = np.array(rows[:n], dtype=np.float64)
    faces = np.array([[int(x) for x in row] for row in rows[n : n + f]], dtype=np.int64)
    joints = np.array(rows[n + f :], dtype=np.float64)
    if not np.isfinite(vertices).all() or not np.isfinite(joints).all():
        raise ValueError("Nonfinite model.dat data")
    if faces.min() < 0 or faces.max() >= n:
        raise ValueError("Out-of-range zero-based face index")
    return tuple((_immutable(x) for x in (vertices[:, :3], faces, vertices[:, 3:], joints)))
