"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import Any

import numpy as np

from somatoanthropy.geometry.anthropometry.mhr_sites import torso_section
from somatoanthropy.geometry.fit03_anthropometry.core import MeshMetrology, hull_points, perimeter

ARITHMETIC_M = 1e-10


def locate_landmarks(
    vertices: np.ndarray, faces: np.ndarray, allowed: np.ndarray, lo: float, hi: float
) -> dict[str, Any]:
    """Exact linear extrema of pelvis triangles clipped to the horizontal slab.

    Include edge/plane intersections: restricting only original vertices would
    omit possible extrema at the region boundaries. Face IDs and barycentric
    coordinates retain the link to the original saved mesh.
    """
    if not np.isfinite([lo, hi]).all() or lo >= hi:
        raise ValueError("INVALID_GLUTEAL_REGION")
    ids = np.flatnonzero(allowed)
    tri = np.asarray(vertices, dtype=float)[faces[ids]]
    positions, barycentrics, face_ids = ([], [], [])
    for k in range(3):
        keep = (tri[:, k, 1] >= lo) & (tri[:, k, 1] <= hi)
        positions.append(tri[keep, k])
        barycentrics.append(np.tile(np.eye(3)[k], (int(keep.sum()), 1)))
        face_ids.append(ids[keep])
    for a, b in ((0, 1), (1, 2), (2, 0)):
        ya, yb = (tri[:, a, 1], tri[:, b, 1])
        for y in (lo, hi):
            keep = (np.minimum(ya, yb) < y) & (np.maximum(ya, yb) > y)
            t = (y - ya[keep]) / (yb[keep] - ya[keep])
            weights = np.zeros((len(t), 3))
            weights[:, a], weights[:, b] = (1 - t, t)
            xyz = np.einsum("ij,ijk->ik", weights, tri[keep])
            xyz[:, 1] = y
            positions.append(xyz)
            barycentrics.append(weights)
            face_ids.append(ids[keep])
    points, weights, source_faces = (
        np.concatenate(positions),
        np.concatenate(barycentrics),
        np.concatenate(face_ids),
    )
    if not len(points) or not np.isfinite(points).all():
        raise ValueError("EMPTY_OR_NONFINITE_GLUTEAL_REGION")
    result = {}
    for label, axis, sign, definition in (
        ("A", 2, -1, "posterior -Z"),
        ("B", 0, -1, "lateral -X"),
        ("C", 0, 1, "lateral +X"),
    ):
        scores = sign * points[:, axis]
        best = float(scores.max())
        exact = np.flatnonzero(scores == best)
        index = min(exact, key=lambda i: (int(source_faces[i]), *weights[i].tolist()))
        tied = np.flatnonzero(best - scores <= ARITHMETIC_M)
        height_span = float(np.ptp(points[tied, 1]))
        point = points[index]
        result[label] = dict(
            label=label,
            definition=definition,
            point_m=point.tolist(),
            face_id=int(source_faces[index]),
            barycentric=weights[index].tolist(),
            coordinate_axis=axis,
            coordinate_sign=sign,
            extremum_coordinate_m=float(point[axis]),
            tied_height_span_m=height_span,
            multiple_extremum_heights=height_span > ARITHMETIC_M,
            at_region_boundary=bool(min(abs(point[1] - lo), abs(point[1] - hi)) <= ARITHMETIC_M),
            qualification="ENGINEERING_SURFACE_EXTREMUM_NOT_ANNOTATED_ANATOMY",
        )
    return result


def select_candidate(candidates: dict[str, Any]) -> tuple[str | None, list[str]]:
    valid = [
        label
        for label, q in candidates.items()
        if q["quality_state"] == "PROXY_VALID" and q.get("tape_envelope_cm") is not None
    ]
    flags = ["UNMEASURABLE_LANDMARK_SECTION:" + label for label in candidates if label not in valid]
    if not valid:
        return (None, flags)
    return (max(valid, key=lambda label: candidates[label]["tape_envelope_cm"]), flags)


def measure_three_landmark_hip(
    mesh: dict[str, np.ndarray],
    baseline: dict[str, Any],
    masks: dict[str, np.ndarray],
    saved: dict[str, Any],
) -> dict[str, Any]:
    v, f = (mesh["vertices"], mesh["faces"])
    lo, hi = saved["search_interval_world_y_m"]
    landmarks = locate_landmarks(v, f, masks["pelvis"], lo, hi)
    origin = np.asarray(baseline["trunk_frame"]["origin_m"])
    normal = np.array([0.0, 1.0, 0.0])
    engine = MeshMetrology(dict(vertices=v, faces=f, length_units="m"))
    candidates = {}
    for label, landmark in landmarks.items():
        y = landmark["point_m"][1]
        point = np.array([origin[0], y, origin[2]])
        section = torso_section(v, f, point, normal, point, masks["pelvis"], engine)
        candidates[label] = section
    winner, flags = select_candidate(candidates)
    for label, landmark in landmarks.items():
        if landmark["at_region_boundary"]:
            flags.append("REGION_BOUNDARY_EXTREMUM:" + label)
        if landmark["multiple_extremum_heights"]:
            flags.append("MULTIPLE_EXTREMUM_HEIGHTS:" + label)
    result = dict(candidates[winner]) if winner is not None else {}
    if "points_m" in result:
        raw = np.asarray(result["points_m"])
        hull = hull_points(raw[:, [0, 2]])
        points = np.column_stack(
            (hull[:, 0], np.full(len(hull), result["plane_origin_m"][1]), hull[:, 1])
        )
        assert abs(perimeter(points) * 100 - result["tape_envelope_cm"]) < 1e-07
        result.update(
            raw_points_m=raw.tolist(),
            points_m=points.tolist(),
            engineering_value_cm=result["tape_envelope_cm"],
        )
    state = "CONTOUR_INVALID" if winner is None else "SITE_AMBIGUOUS" if flags else "PROXY_VALID"
    result.update(
        quality_state=state,
        reason=";".join(flags) if flags else "LARGEST_TAPE_AT_THREE_GLUTEAL_EXTREMA",
        selection_flags=flags,
        landmarks=landmarks,
        landmark_sections=candidates,
        selected_landmark=winner,
        selected_equal_value_landmarks=[
            label
            for label in candidates
            if winner is not None
            and candidates[label].get("tape_envelope_cm") == candidates[winner]["tape_envelope_cm"]
            and (candidates[label]["quality_state"] == "PROXY_VALID")
        ],
        selection_quantity="tape_envelope_cm",
        selection_method="MAXIMUM_OUTSIDE_TAPE_AT_POSTERIOR_AND_BILATERAL_EXTREMA",
        search_interval_world_y_m=[lo, hi],
        crotch_point_m=saved["crotch_point_m"],
        crotch_surface_anchor=saved["crotch_surface_anchor"],
        upper_gluteal_point_m=saved["upper_gluteal_point_m"],
        boundary_qualification=saved["boundary_qualification"],
        previous_surge_cutoff_used=False,
        scientific_margins_approved=False,
        value_cm=None,
        anatomical_qualification="UNQUALIFIED",
        site_definition="Compare horizontal outside-tape circumferences at posterior -Z, lateral -X and lateral +X extrema of masked gluteal surface, upper pelvis to crotch inclusive; choose largest measurable candidate, flag incomplete comparisons or boundary/tied-height extrema",
    )
    return result
