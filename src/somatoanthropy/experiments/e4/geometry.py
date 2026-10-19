"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import numpy as np

from somatoanthropy.geometry.mpii_mhr_fit01.metrics import compare


def positive_mesh(v: np.ndarray, f: np.ndarray) -> tuple:
    tri = v[f]
    positive = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) > 0
    return (v, f[positive], int((~positive).sum()))


def surface(a: tuple, b: tuple, count: int, seed: int) -> dict:
    av, af, az = positive_mesh(*a)
    bv, bf, bz = positive_mesh(*b)
    result = compare(av, af, bv, bf, count=count, seed=seed)
    result.update(
        units="engineering_metres",
        source_zero_area_faces_masked=az,
        target_zero_area_faces_masked=bz,
        physical_calibration="UNCONFIRMED",
        source_extents=np.ptp(av, axis=0).tolist(),
        target_extents=np.ptp(bv, axis=0).tolist(),
        extent_delta=(np.ptp(bv, axis=0) - np.ptp(av, axis=0)).tolist(),
        relative_extent_delta=(np.ptp(bv, axis=0) / np.ptp(av, axis=0) - 1).tolist(),
        no_scale_fit=True,
    )
    return result


def source_centered_fitted(vertices: np.ndarray, source: np.ndarray) -> np.ndarray:
    """Apply the source's own fixed origin translation to its fitted derivative."""
    return vertices - (source.min(0) + source.max(0)) / 2
