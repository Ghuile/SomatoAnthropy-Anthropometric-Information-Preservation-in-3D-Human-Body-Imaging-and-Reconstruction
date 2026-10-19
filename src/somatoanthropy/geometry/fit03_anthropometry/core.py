"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import math
from typing import Any, cast

import numpy as np

from somatoanthropy.geometry.anthropometry.model import Plane, SectionConfig
from somatoanthropy.geometry.anthropometry.section import mesh_section

VERSION = "fit03-indexed-digital-metrology-v1"


def project(points: np.ndarray, normal: np.ndarray) -> np.ndarray:
    basis = np.eye(3)[int(np.argmin(np.abs(normal)))]
    u = np.cross(normal, basis)
    u /= np.linalg.norm(u)
    w = np.cross(normal, u)
    return cast(np.ndarray, points @ np.stack((u, w), axis=1))


def simple_polygon(points: np.ndarray, tolerance: float = 1e-10) -> bool:
    """Vectorized closed-set segment test; adjacent indexed edges excluded."""
    n = len(points)
    if n < 3 or n > 4000:
        return False
    a = points
    b = np.roll(points, -1, axis=0)
    if np.any(np.linalg.norm(b - a, axis=1) <= tolerance):
        return False
    for i in range(n):
        ids = np.arange(i + 2, n)
        if i == 0:
            ids = ids[ids != n - 1]
        if not len(ids):
            continue
        c, d = (a[ids], b[ids])
        overlap_box = np.all(
            np.maximum(np.minimum(a[i], b[i]), np.minimum(c, d))
            <= np.minimum(np.maximum(a[i], b[i]), np.maximum(c, d)) + tolerance,
            axis=1,
        )
        if not overlap_box.any():
            continue
        c, d = (c[overlap_box], d[overlap_box])

        def cross(x: Any, y: Any) -> Any:
            return x[..., 0] * y[..., 1] - x[..., 1] * y[..., 0]

        ab = b[i] - a[i]
        cd = d - c
        x = cross(ab, c - a[i])
        y = cross(ab, d - a[i])
        z = cross(cd, a[i] - c)
        w = cross(cd, b[i] - c)
        e = tolerance * np.linalg.norm(ab)
        g = tolerance * np.linalg.norm(cd, axis=1)
        if np.any(
            ((x <= e) & (y >= -e) | (y <= e) & (x >= -e))
            & ((z <= g) & (w >= -g) | (w <= g) & (z >= -g))
        ):
            return False
    return True


def contains(points: np.ndarray, seed: np.ndarray, tolerance: float = 1e-10) -> bool:
    a, b = (points, np.roll(points, -1, axis=0))
    delta = b - a
    cross = delta[:, 0] * (seed[1] - a[:, 1]) - delta[:, 1] * (seed[0] - a[:, 0])
    on = (np.abs(cross) <= tolerance * np.linalg.norm(delta, axis=1)) & np.all(
        (seed >= np.minimum(a, b) - tolerance) & (seed <= np.maximum(a, b) + tolerance), axis=1
    )
    if on.any():
        return False
    sides = (a[:, 1] > seed[1]) != (b[:, 1] > seed[1])
    x = np.zeros(len(a))
    x[sides] = (b[sides, 0] - a[sides, 0]) * (seed[1] - a[sides, 1]) / (
        b[sides, 1] - a[sides, 1]
    ) + a[sides, 0]
    return bool(np.count_nonzero(sides & (seed[0] < x)) % 2)


def hull_points(points: np.ndarray) -> np.ndarray:
    ordered = sorted(set(map(tuple, points)))

    def half(items: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
        result: list[tuple[Any, ...]] = []
        for point in items:
            while len(result) >= 2:
                a, b = (np.asarray(result[-2]), np.asarray(result[-1]))
                c = np.asarray(point)
                cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
                if cross > 0:
                    break
                result.pop()
            result.append(point)
        return result

    return np.asarray(half(ordered)[:-1] + half(ordered[::-1])[:-1])


def perimeter(points: np.ndarray) -> float:
    return math.fsum(
        (
            float(np.linalg.norm(b - a))
            for a, b in zip(points, np.roll(points, -1, axis=0), strict=True)
        )
    )


class MeshMetrology:
    def __init__(self, mesh: dict[str, Any], *, tolerance_m: float = 1e-10) -> None:
        if mesh.get("length_units") != "m":
            raise ValueError("Metre inputs required; explicit conversion precedes measurement")
        self.vertices = np.asarray(mesh["vertices"], dtype=np.float64)
        self.faces = np.asarray(mesh["faces"])
        if (
            self.vertices.ndim != 2
            or self.vertices.shape[1] != 3
            or (not np.isfinite(self.vertices).all())
        ):
            raise ValueError("Finite Nx3 geometry required")
        if (
            self.faces.ndim != 2
            or self.faces.shape[1] != 3
            or self.faces.dtype.kind not in "iu"
            or (not len(self.faces))
        ):
            raise ValueError("Indexed triangular geometry required")
        if (self.faces < 0).any() or (self.faces >= len(self.vertices)).any():
            raise ValueError("Invalid face indices")
        self.triangles = self.vertices[self.faces]
        self.tolerance = float(tolerance_m)
        self.config = SectionConfig(tolerance_m=self.tolerance)

    def vertical_extent_cm(self) -> float:
        return float(np.ptp(self.vertices[:, 1]) * 100)

    def section(self, point: Any, normal: Any, seed: Any) -> dict[str, Any]:
        if seed is None:
            return {"status": "NOT_EVALUABLE", "reason": "MISSING_REQUIRED_SECTION_SEED"}
        try:
            plane = Plane(tuple(point), tuple(normal))
            n = np.asarray(plane.normal)
            p = np.asarray(plane.point)
            seed = np.asarray(seed, dtype=float)
            if seed.shape != (3,) or not np.isfinite(seed).all():
                raise ValueError("Invalid seed")
            distances = (self.triangles - p) @ n
            candidate = np.flatnonzero(
                (distances.min(1) <= self.tolerance) & (distances.max(1) >= -self.tolerance)
            )
            if not len(candidate):
                return {"status": "NOT_EVALUABLE", "reason": "NO_INTERSECTION"}
            ids, inverse = np.unique(self.faces[candidate], return_inverse=True)
            compact_faces = inverse.reshape(-1, 3)
            section = mesh_section(
                {"vertices": self.vertices[ids], "faces": compact_faces, "length_units": "m"},
                plane,
                config=self.config,
            )
            diagnostic = section.diagnostics
            if any(
                (
                    diagnostic[k]
                    for k in (
                        "open_polyline_count",
                        "branched_node_ids",
                        "local_degenerate_face_ids",
                        "local_duplicate_face_ids",
                        "coplanar_nonmanifold_edge_count",
                    )
                )
            ):
                return {
                    "status": "NOT_EVALUABLE",
                    "reason": "INVALID_OR_OPEN_LOCAL_SECTION",
                    "diagnostics": diagnostic,
                }
            candidates = []
            for path in section.polylines:
                if not path.closed:
                    continue
                pts = np.asarray(path.points[:-1])
                xy = project(pts - p, n)
                if not simple_polygon(xy, self.tolerance):
                    return {"status": "NOT_EVALUABLE", "reason": "NON_SIMPLE_SECTION_LOOP"}
                if contains(xy, project((seed - p)[None], n)[0], self.tolerance):
                    candidates.append((path, pts, xy))
            if len(candidates) != 1:
                return {
                    "status": "NOT_EVALUABLE",
                    "reason": "AMBIGUOUS_OR_UNIDENTIFIED_LOOP",
                    "closed_loop_count": diagnostic["closed_loop_count"],
                }
            path, pts, xy = candidates[0]
            selected_nodes = set(path.node_ids)
            face_ids = []
            for i, face in enumerate(compact_faces):
                a, b, c = map(int, face)
                possible = {
                    (a, a),
                    (b, b),
                    (c, c),
                    tuple(sorted((a, b))),
                    tuple(sorted((b, c))),
                    tuple(sorted((c, a))),
                }
                nodes = possible & selected_nodes
                if len(nodes) >= 2:
                    face_ids.append(int(candidate[i]))
            return {
                "status": "MEASURED",
                "units": "cm",
                "contour_cm": perimeter(pts) * 100,
                "tape_cm": perimeter(hull_points(xy)) * 100,
                "points_m": pts.tolist(),
                "plane_point_m": list(plane.point),
                "plane_normal": list(plane.normal),
                "seed_m": seed.tolist(),
                "selected_face_ids": face_ids,
                "closed_loop_count": diagnostic["closed_loop_count"],
                "method": VERSION,
                "clinical_validity": "NOT_ESTABLISHED",
                "coplanar_faces": len(diagnostic["coplanar_face_ids"]),
            }
        except (ValueError, IndexError, ArithmeticError) as exc:
            return {"status": "NOT_EVALUABLE", "reason": str(exc)}
