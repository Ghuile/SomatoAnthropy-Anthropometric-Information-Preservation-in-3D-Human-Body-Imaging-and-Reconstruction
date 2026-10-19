"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import Any

import numpy as np


def standing_normal(root_state: Any) -> np.ndarray | None:
    """Root orientation, not a curved lumbar bone chord, tests standing up."""
    state = np.asarray(root_state, dtype=float)
    if state.ndim != 1 or len(state) < 7:
        return None
    q = state[3:7]
    if q.shape != (4,) or not np.isfinite(q).all() or np.linalg.norm(q) < 1e-12:
        return None
    x, y, z, w = q / np.linalg.norm(q)
    up = np.array([2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w)])
    if not np.allclose(up, [0, 1, 0], atol=1e-07, rtol=0):
        return None
    return np.array([0.0, 1.0, 0.0])
