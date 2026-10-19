"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import cast

import numpy as np

SOURCE_TO_NATIVE_AXES = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]])


def source_to_working(points: np.ndarray) -> np.ndarray:
    if points.shape != (6449, 3) or not np.isfinite(points).all():
        raise ValueError("MPII points require finite (6449, 3); no SMPL interpretation")
    return cast(np.ndarray, np.asarray(points, dtype=np.float64) @ SOURCE_TO_NATIVE_AXES.T * 0.001)
