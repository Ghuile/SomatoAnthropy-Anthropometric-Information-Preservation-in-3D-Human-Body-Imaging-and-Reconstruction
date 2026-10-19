"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from typing import Any

import numpy as np


def transform(points: Any, matrix: Any) -> Any:
    m = np.asarray(matrix, dtype=float)
    if (
        m.shape != (4, 4)
        or not np.isfinite(m).all()
        or (not np.array_equal(m[3], [0, 0, 0, 1]))
        or (not np.allclose(m[:3, :3].T @ m[:3, :3], np.eye(3), atol=1e-12))
        or (not np.isclose(np.linalg.det(m[:3, :3]), 1.0, atol=1e-12))
    ):
        raise ValueError("Finite proper rigid transform required")
    return np.asarray(points, dtype=float) @ m[:3, :3].T + m[:3, 3]
