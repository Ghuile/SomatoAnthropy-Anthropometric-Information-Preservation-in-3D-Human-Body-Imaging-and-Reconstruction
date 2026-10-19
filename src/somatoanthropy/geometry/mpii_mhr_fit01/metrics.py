"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import Any

import numpy as np


def mesh(vertices: Any, faces: Any) -> tuple[Any, Any]:
    v, f = (np.asarray(vertices, dtype=np.float64), np.asarray(faces))
    if v.ndim != 2 or v.shape[1] != 3 or (not np.isfinite(v).all()) or (len(v) < 3):
        raise ValueError("Finite Nx3 vertices required")
    if (
        f.ndim != 2
        or f.shape[1] != 3
        or (not len(f))
        or (f.dtype.kind not in "iu")
        or (f.min() < 0)
        or (f.max() >= len(v))
    ):
        raise ValueError("Valid independent indexed triangle topology required")
    return (v, f.astype(np.int64))


def samples(vertices: Any, faces: Any, count: int, seed: int) -> tuple[Any, Any, Any]:
    v, f = mesh(vertices, faces)
    triangles = v[f]
    areas = (
        np.linalg.norm(
            np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]), axis=1
        )
        * 0.5
    )
    if not np.isfinite(areas).all() or areas.sum() <= 0:
        raise ValueError("Nonempty finite positive surface area required")
    rng = np.random.default_rng(seed)
    ids = rng.choice(len(f), size=count, p=areas / areas.sum())
    uv = rng.random((count, 2))
    root = np.sqrt(uv[:, 0])
    bary = np.column_stack((1 - root, root * (1 - uv[:, 1]), root * uv[:, 1]))
    return ((triangles[ids] * bary[..., None]).sum(axis=1), ids, bary)


def distances(points: Any, vertices: Any, faces: Any, chunk: int = 128) -> Any:
    from scipy.spatial import cKDTree
    from trimesh.triangles import closest_point

    v, f = mesh(vertices, faces)
    p = np.asarray(points, dtype=np.float64)
    if p.ndim != 2 or p.shape[1] != 3 or (not len(p)) or (not np.isfinite(p).all()):
        raise ValueError("Nonempty finite query points required")
    triangles = v[f]
    centers = triangles.mean(axis=1)
    radii = np.linalg.norm(triangles - centers[:, None], axis=2).max(axis=1)
    tree = cKDTree(centers)
    upper = cKDTree(v).query(p)[0]
    result = np.empty(len(p))
    for start in range(0, len(p), chunk):
        queries = p[start : start + chunk]
        limits = upper[start : start + chunk]
        candidates = tree.query_ball_point(queries, limits + float(radii.max()) + 1e-12)
        for local, (point, bound, ids) in enumerate(zip(queries, limits, candidates, strict=True)):
            ids = np.asarray(ids, dtype=np.int64)
            good = np.linalg.norm(centers[ids] - point, axis=1) <= bound + radii[ids] + 1e-12
            ids = ids[good]
            if not len(ids):
                raise ValueError("Conservative surface candidates unexpectedly empty")
            projected = closest_point(triangles[ids], np.broadcast_to(point, (len(ids), 3)))
            result[start + local] = np.linalg.norm(projected - point, axis=1).min()
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite point-to-triangle distance")
    return result


def compare(
    source: Any, source_faces: Any, target: Any, target_faces: Any, *, count: int, seed: int
) -> dict[str, Any]:
    a, _, _ = samples(source, source_faces, count, seed)
    b, _, _ = samples(target, target_faces, count, seed + 1)
    forward = distances(a, target, target_faces)
    backward = distances(b, source, source_faces)
    combined = np.concatenate((forward, backward))
    return {
        "units": "metres",
        "method": "area-uniform samples to exact opposite indexed triangle surface",
        "source_to_mhr_mean": float(forward.mean()),
        "mhr_to_source_mean": float(backward.mean()),
        "symmetric_mean": float(combined.mean()),
        "median": float(np.median(combined)),
        "rms": float(np.sqrt(np.mean(combined**2))),
        "p95": float(np.percentile(combined, 95)),
        "maximum_sampled_distance": float(combined.max()),
        "samples_per_direction": count,
        "seeds": [seed, seed + 1],
        "directional_weights": [0.5, 0.5],
        "coverage": {
            "threshold_metres": 0.02,
            "source_to_mhr_fraction": float(np.mean(forward <= 0.02)),
            "mhr_to_source_fraction": float(np.mean(backward <= 0.02)),
        },
        "mask": "all faces, including known MHR facial defects",
        "chunk": 128,
        "regional_errors": {"status": "UNAVAILABLE_NO_VALIDATED_COMMON_ANATOMICAL_REGIONS"},
        "maximum_is_sample_dependent": True,
    }
