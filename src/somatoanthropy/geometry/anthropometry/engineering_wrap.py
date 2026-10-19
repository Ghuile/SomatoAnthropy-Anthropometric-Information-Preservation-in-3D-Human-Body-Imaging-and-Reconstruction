"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import copy

import numpy as np
import trimesh
from scipy.spatial import ConvexHull

from somatoanthropy.geometry.fit03_anthropometry.core import contains, perimeter, simple_polygon

ARITHMETIC_M = 1e-08


def overlap(a, b):
    """Closed planar ring intersections or containment, including touching."""
    if contains(a, b[0]) or contains(b, a[0]):
        return True
    aa, bb = (a[:, None], b[None, :])
    ad = (np.roll(a, -1, axis=0) - a)[:, None]
    bd = (np.roll(b, -1, axis=0) - b)[None, :]

    def cross(x, y):
        return x[..., 0] * y[..., 1] - x[..., 1] * y[..., 0]

    den = cross(ad, bd)
    valid = np.abs(den) > 1e-15
    t = np.divide(cross(bb - aa, bd), den, out=np.zeros_like(den), where=valid)
    u = np.divide(cross(bb - aa, ad), den, out=np.zeros_like(den), where=valid)
    return bool(np.any(valid & (t >= -1e-10) & (t <= 1 + 1e-10) & (u >= -1e-10) & (u <= 1 + 1e-10)))


class RingEngine:
    """Select a full connected trunk ring, keeping separate limbs separate."""

    def __init__(self, vertices, faces, seed_xz, *, reject_contact=True):
        self.vertices = np.asarray(vertices, dtype=float)
        self.faces = np.asarray(faces, dtype=np.int64)
        self.seed = np.asarray(seed_xz, dtype=float)
        self.mesh = trimesh.Trimesh(self.vertices, self.faces, process=False)
        self.cache = {}
        self.reject_contact = reject_contact

    def section(self, y, *, check_overlap=None):
        if check_overlap is None:
            check_overlap = self.reject_contact
        key = (float(y), check_overlap)
        if key in self.cache:
            return copy.deepcopy(self.cache[key])
        path = self.mesh.section(plane_normal=[0, 1, 0], plane_origin=[0, y, 0])
        rings = []
        if path is not None:
            for p in path.discrete:
                if len(p) >= 4 and np.linalg.norm(p[0] - p[-1]) <= ARITHMETIC_M:
                    p = np.asarray(p[:-1], dtype=float)
                    if simple_polygon(p[:, [0, 2]]):
                        rings.append(p)
        eligible = [p for p in rings if contains(p[:, [0, 2]], self.seed)]
        if len(eligible) != 1:
            return dict(
                geometry_quality="INVALID",
                reason="NO_UNIQUE_CLOSED_TARGET_RING",
                value_cm=None,
                points_m=[],
            )
        raw = eligible[0]
        contacting = any(
            (overlap(raw[:, [0, 2]], other[:, [0, 2]]) for other in rings if other is not raw)
        )
        if check_overlap and contacting:
            return dict(
                geometry_quality="INVALID",
                reason="TARGET_RING_TOUCHES_OTHER_COMPONENT",
                value_cm=None,
                points_m=[],
            )
        projected = raw[:, [0, 2]]
        hull = projected[ConvexHull(projected).vertices]
        tape = np.column_stack((hull[:, 0], np.full(len(hull), y), hull[:, 1]))
        result = dict(
            geometry_quality="VALID",
            quality_state="PROXY_VALID",
            reason="CLOSED_TARGET_RING_WITH_SEPARATE_CONTACTING_COMPONENT"
            if contacting
            else "FULL_CLOSED_TARGET_RING",
            raw_contour_cm=float(perimeter(raw) * 100),
            tape_envelope_cm=float(perimeter(tape) * 100),
            points_m=raw.tolist(),
            tape_points_m=tape.tolist(),
            raw_points_m=raw.tolist(),
            plane_origin_m=[float(self.seed[0]), float(y), float(self.seed[1])],
            plane_normal=[0.0, 1.0, 0.0],
            surface_contour_closed=True,
            closed_loop_count=len(rings),
            limb_overlap=contacting,
            value_cm=None,
            maximum_plane_residual_m=float(np.max(np.abs(raw[:, 1] - y))),
            scientific_margins_approved=False,
        )
        self.cache[key] = result
        return copy.deepcopy(result)
