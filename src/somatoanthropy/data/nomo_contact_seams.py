"""Frozen source-reference contour definitions; no delivery or participant IO."""

import numpy as np
import trimesh
from scipy.spatial import ConvexHull, cKDTree

from somatoanthropy.data.nomo_contact_sections import IndexedSections
from somatoanthropy.geometry.fit03_anthropometry.core import contains, project, simple_polygon


class SourceSeamSections(IndexedSections):
    """Use an actual closed geometric ring only after a complete region check.

    This is a source-template seam fallback. A valid indexed ring containing
    excluded arm faces cannot be replaced by another, more convenient contour.
    Coordinate coincidence never licenses a bridge or a fabricated cap.
    """

    def __init__(self, vertices, faces):
        super().__init__(vertices, faces)
        self.mesh = trimesh.Trimesh(self.v, self.f, process=False)

    def section(self, point, normal, seed, allowed=None):
        q = super().section(point, normal, seed, allowed)
        if (
            q["geometry_quality"] == "VALID"
            or q["reason"] == "INDEXED_TARGET_RING_INCLUDES_EXCLUDED_REGION"
        ):
            return q
        if allowed is None:
            return q
        point, normal, seed = map(lambda p: np.asarray(p, float), (point, normal, seed))
        normal /= np.linalg.norm(normal)
        path = self.mesh.section(plane_origin=point, plane_normal=normal)
        eligible = []
        if path is not None:
            for p in path.discrete:
                if len(p) < 4 or np.linalg.norm(p[0] - p[-1]) > 1e-08:
                    continue
                raw = np.asarray(p[:-1])
                xy = project(raw - point, normal)
                if simple_polygon(xy) and contains(xy, project((seed - point)[None], normal)[0]):
                    eligible.append(raw)
        if len(eligible) != 1:
            return q
        raw = eligible[0]
        segments, local = trimesh.intersections.mesh_plane(
            self.mesh, normal, point, return_faces=True
        )
        near = cKDTree(raw).query(segments.reshape(-1, 3))[0].reshape(-1, 2)
        supporting = self.ids[local[np.all(near <= 1e-07, axis=1)]]
        if not len(supporting) or np.any(~np.asarray(allowed, bool)[supporting]):
            return q
        endpoints = segments[np.all(near <= 1e-07, axis=1)].reshape(-1, 3)
        if np.max(cKDTree(endpoints).query(raw)[0]) > 1e-07:
            return q
        tape = raw[ConvexHull(project(raw - point, normal)).vertices]
        result = dict(
            geometry_quality="VALID",
            reason="CLOSED_SOURCE_TEMPLATE_SEAM_RING_WITH_COMPLETE_REGION_SUPPORT",
            points_m=raw.tolist(),
            raw_points_m=raw.tolist(),
            tape_points_m=tape.tolist(),
            raw_contour_cm=float(
                np.linalg.norm(np.roll(raw, -1, axis=0) - raw, axis=1).sum() * 100
            ),
            tape_envelope_cm=float(
                np.linalg.norm(np.roll(tape, -1, axis=0) - tape, axis=1).sum() * 100
            ),
            plane_origin_m=point.tolist(),
            plane_normal=normal.tolist(),
            selected_face_ids=supporting.tolist(),
            surface_contour_closed=True,
            region_check=dict(
                valid=True,
                supporting_face_count=len(supporting),
                outside_face_count=0,
                outside_face_ids=[],
            ),
            connectivity="SOURCE_TEMPLATE_SEAM_GEOMETRIC_CLOSURE_WITH_ALL_ORIGINAL_FACE_REGION_CHECK",
            indexed_failure_reason=q["reason"],
            fabricated_segments=0,
            scientific_margins_approved=False,
        )
        return result
