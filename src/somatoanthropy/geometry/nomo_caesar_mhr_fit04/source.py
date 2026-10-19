"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import Any

import numpy as np


def surface_mask(vertices: Any, faces: Any) -> Any:
    t = np.asarray(vertices)[np.asarray(faces)]
    return np.linalg.norm(np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), axis=1) > 2e-16
