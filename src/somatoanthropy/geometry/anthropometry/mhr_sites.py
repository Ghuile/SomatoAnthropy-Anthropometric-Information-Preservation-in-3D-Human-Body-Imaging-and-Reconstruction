"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from enum import StrEnum
from typing import Any, cast

import numpy as np

from somatoanthropy.geometry.fit03_anthropometry.core import (
    MeshMetrology,
    contains,
    project,
    simple_polygon,
)

ATLAS_VERSION = "MHR-LOD0-SURFACE-ATLAS-CANDIDATE-v1"


class SiteState(StrEnum):
    ANATOMICAL_VALID = "ANATOMICAL_VALID"
    PROXY_VALID = "PROXY_VALID"
    SITE_AMBIGUOUS = "SITE_AMBIGUOUS"
    SITE_OUT_OF_REGION = "SITE_OUT_OF_REGION"
    CONTOUR_INVALID = "CONTOUR_INVALID"
    LIMB_CONTAMINATION = "LIMB_CONTAMINATION"
    POSE_INCOMPATIBLE = "POSE_INCOMPATIBLE"
    LANDMARK_UNAVAILABLE = "LANDMARK_UNAVAILABLE"
    SOURCE_PROTOCOL_UNKNOWN = "SOURCE_PROTOCOL_UNKNOWN"
    NOT_EVALUABLE = "NOT_EVALUABLE"


def topology_hash(faces: Any) -> str:
    return hashlib.sha256(np.asarray(faces, dtype="<i8").tobytes()).hexdigest()


def anchor_position(vertices: Any, faces: Any, anchor: dict[str, Any]) -> np.ndarray:
    f = np.asarray(faces)
    i = anchor["face_id"]
    w = np.asarray(anchor["barycentric"], dtype=float)
    if not isinstance(i, int) or not 0 <= i < len(f):
        raise ValueError("LANDMARK_FACE_UNAVAILABLE")
    if (
        w.shape != (3,)
        or not np.isfinite(w).all()
        or (w < 0).any()
        or (not np.isclose(w.sum(), 1, atol=1e-12, rtol=0))
    ):
        raise ValueError("INVALID_BARYCENTRIC_ANCHOR")
    return cast(np.ndarray, w @ np.asarray(vertices, dtype=float)[f[i]])


def validate_atlas(atlas: dict[str, Any], vertices: Any, faces: Any) -> None:
    v, f = (np.asarray(vertices), np.asarray(faces))
    if (
        atlas["version"] != ATLAS_VERSION
        or v.shape != (atlas["vertex_count"], 3)
        or f.shape != (atlas["face_count"], 3)
        or (topology_hash(f) != atlas["topology_sha256"])
    ):
        raise ValueError("ATLAS_TOPOLOGY_MISMATCH")
    if not np.isfinite(v).all() or f.dtype.kind not in "iu" or (f < 0).any() or (f >= len(v)).any():
        raise ValueError("INVALID_NATIVE_GEOMETRY")
    for a in atlas["anchors"].values():
        anchor_position(v, f, a)


def _failure(state: str, reason: str, **diagnostics: Any) -> dict[str, Any]:
    return {"quality_state": str(state), "reason": reason, "value_cm": None, **diagnostics}


def _limb_segments(
    vertices: np.ndarray, faces: np.ndarray, ids: np.ndarray, p: np.ndarray, n: np.ndarray
) -> Iterator[tuple[int, np.ndarray]]:
    for fid in ids:
        tri = vertices[faces[fid]]
        d = (tri - p) @ n
        pts = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            if abs(d[i]) < 1e-10:
                pts.append(tri[i])
            if d[i] * d[j] < 0:
                pts.append(tri[i] + d[i] / (d[i] - d[j]) * (tri[j] - tri[i]))
        if len(pts) >= 2:
            yield (int(fid), np.array(pts[:2]))


def _touches_polygon(poly: np.ndarray, segment: np.ndarray) -> bool:
    if any((contains(poly, q) for q in segment)):
        return True
    a, b = (poly, np.roll(poly, -1, axis=0))
    c, d = segment
    box = np.all(
        np.maximum(np.minimum(a, b), np.minimum(c, d))
        <= np.minimum(np.maximum(a, b), np.maximum(c, d)) + 1e-10,
        axis=1,
    )
    a, b = (a[box], b[box])
    if not len(a):
        return False

    def cross(x: Any, y: Any) -> Any:
        return x[..., 0] * y[..., 1] - x[..., 1] * y[..., 0]

    ab, cd = (b - a, d - c)
    x, y, z, w = (cross(ab, c - a), cross(ab, d - a), cross(cd, a - c), cross(cd, b - c))
    return bool(np.any((x * y <= 1e-20) & (z * w <= 1e-20)))


def torso_section(
    vertices: Any,
    faces: Any,
    point: Any,
    normal: Any,
    seed: Any,
    allowed_faces: Any,
    engine: MeshMetrology | None = None,
) -> dict[str, Any]:
    """Select one indexed torso loop; never merge it with limbs or bridge a gap."""
    v, f = (np.asarray(vertices, dtype=float), np.asarray(faces))
    mask = np.asarray(allowed_faces, dtype=bool)
    p, n, seed = (np.asarray(x, dtype=float) for x in (point, normal, seed))
    if (
        mask.shape != (len(f),)
        or n.shape != (3,)
        or (not np.isfinite(n).all())
        or (np.linalg.norm(n) < 1e-12)
    ):
        return _failure(SiteState.NOT_EVALUABLE, "INVALID_REGION_OR_PLANE")
    n = n / np.linalg.norm(n)
    if (
        p.shape != (3,)
        or seed.shape != (3,)
        or (not np.isfinite(p).all())
        or (abs((seed - p) @ n) > 1e-08)
    ):
        return _failure(SiteState.NOT_EVALUABLE, "INVALID_PLANE_SEED")
    engine = engine or MeshMetrology({"vertices": v, "faces": f, "length_units": "m"})
    q = engine.section(p, n, seed)
    if q["status"] != "MEASURED":
        return _failure(
            SiteState.SITE_AMBIGUOUS
            if "AMBIGUOUS" in q.get("reason", "")
            else SiteState.CONTOUR_INVALID,
            q.get("reason", "NO_CONTOUR"),
            diagnostics=q,
        )
    selected = np.asarray(q["selected_face_ids"], dtype=int)
    if not len(selected) or not mask[selected].all():
        return _failure(
            SiteState.LIMB_CONTAMINATION,
            "SELECTED_CONTOUR_LEAVES_TORSO_REGION",
            diagnostic_section=q,
        )
    pts = np.asarray(q["points_m"])
    poly = project(pts - p, n)
    if not simple_polygon(poly):
        return _failure(SiteState.CONTOUR_INVALID, "SELF_INTERSECTING_SECTION")
    distances = (v[f] - p) @ n
    excluded = np.flatnonzero(~mask & (distances.min(1) <= 1e-10) & (distances.max(1) >= -1e-10))
    for fid, segment in _limb_segments(v, f, excluded, p, n):
        if _touches_polygon(poly, project(segment - p, n)):
            return _failure(
                SiteState.LIMB_CONTAMINATION,
                "LIMB_INTERSECTION_TOUCHES_TORSO_CONTOUR",
                excluded_face_id=fid,
                diagnostic_section=q,
            )
    return {
        "quality_state": str(SiteState.PROXY_VALID),
        "reason": "INDEXED_TORSO_CONTOUR_ONLY",
        "value_cm": None,
        "raw_contour_cm": q["contour_cm"],
        "tape_envelope_cm": q["tape_cm"],
        "points_m": q["points_m"],
        "plane_origin_m": p.tolist(),
        "plane_normal": n.tolist(),
        "selected_face_ids": q["selected_face_ids"],
        "closed_loop_count": q["closed_loop_count"],
        "excluded_intersecting_face_count": len(excluded),
        "limb_overlap": False,
        "maximum_plane_residual_m": float(np.max(np.abs((pts - p) @ n))),
        "anatomical_qualification": "UNQUALIFIED",
        "source_protocol_compatible": False,
    }


def surface_anchor(
    vertices: Any, faces: Any, allowed: Any, point: Any, axis: int, positive: bool
) -> dict[str, Any]:
    """A documented rig-to-surface ray creates a *candidate*, never external anatomy."""
    v, f = (np.asarray(vertices), np.asarray(faces))
    ids = np.flatnonzero(allowed)
    tri = v[f[ids]]
    axes = [i for i in range(3) if i != axis]
    a, b, c = (tri[:, 0][:, axes], tri[:, 1][:, axes], tri[:, 2][:, axes])
    d, e = (b - a, c - a)
    t = np.asarray(point)[axes] - a
    det = d[:, 0] * e[:, 1] - d[:, 1] * e[:, 0]
    good = np.abs(det) > 1e-12
    u = np.divide(t[:, 0] * e[:, 1] - t[:, 1] * e[:, 0], det, out=np.zeros(len(det)), where=good)
    w = np.divide(d[:, 0] * t[:, 1] - d[:, 1] * t[:, 0], det, out=np.zeros(len(det)), where=good)
    good &= (u >= 0) & (w >= 0) & (u + w <= 1)
    eligible = np.flatnonzero(good)
    if not len(eligible):
        raise ValueError("RIG_SURFACE_RAY_HAS_NO_ELIGIBLE_TRIANGLE")
    weights = np.column_stack((1 - u - w, u, w))
    coords = np.einsum("ij,ijk->ik", weights, tri)
    k = eligible[
        np.argmax(coords[eligible, axis]) if positive else np.argmin(coords[eligible, axis])
    ]
    return {
        "face_id": int(ids[k]),
        "barycentric": weights[k].tolist(),
        "qualification": "CANDIDATE_NOT_ANATOMICAL",
        "confidence": None,
    }
