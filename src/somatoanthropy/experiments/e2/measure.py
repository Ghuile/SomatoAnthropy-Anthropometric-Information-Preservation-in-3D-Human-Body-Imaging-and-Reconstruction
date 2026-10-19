"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import numpy as np

from somatoanthropy.data.nomo_contact_sections import IndexedSections
from somatoanthropy.experiments.e2.core import midpoint_plane
from somatoanthropy.geometry.anthropometry.mhr_sites import anchor_position, surface_anchor
from somatoanthropy.geometry.anthropometry.three_landmark_hip import locate_landmarks


def compact(q):
    """Retain quantitative evidence and geometry linkage without copying surfaces."""
    return {
        k: v
        for k, v in q.items()
        if k not in ("points_m", "raw_points_m", "tape_points_m", "selected_face_ids")
    }


def section(engine, point, normal, seed, allowed):
    normal = np.asarray(normal, float)
    normal /= np.linalg.norm(normal)
    p = np.asarray(point, float)
    seed = np.asarray(seed, float)
    seed = seed + (p - seed) @ normal * normal
    q = engine.section(p, normal, seed, allowed)
    q.update(plane_origin_m=p.tolist(), plane_normal=normal.tolist(), seed_m=seed.tolist())
    return q


def proxy_sites(v, f, anchors, joints, masks):
    engine = IndexedSections(v, f)
    seed = joints["root"]
    normal = np.array([0.0, 1.0, 0.0])
    chest = (anchors["left_anterior_chest_feature"] + anchors["right_anterior_chest_feature"]) / 2
    result = {}
    for site, point in (("abdomen", anchors["umbilicus_model_surface"]), ("chest", chest)):
        result[site] = section(engine, point, normal, seed, masks["torso"])
    try:
        p, n = midpoint_plane(
            anchors["lower_thorax_surface"],
            anchors["upper_pelvis_surface"],
            joints["c_spine3"] - joints["c_spine0"],
        )
        result["waist"] = section(engine, p, n, seed, masks["torso"])
    except ValueError as error:
        result["waist"] = dict(geometry_quality="INVALID", reason=str(error))
    try:
        crotch_a = surface_anchor(v, f, masks["pelvis"], seed, 1, False)
        crotch = anchor_position(v, f, crotch_a)
        lo, hi = (float(crotch[1]), float(anchors["upper_pelvis_surface"][1]))
        landmark = locate_landmarks(v, f, masks["pelvis"], lo, hi)["A"]
        result["hip"] = section(engine, landmark["point_m"], normal, seed, masks["pelvis"])
        result["hip"].update(landmark=landmark, search_interval_world_y_m=[lo, hi])
    except ValueError as error:
        result["hip"] = dict(geometry_quality="INVALID", reason=str(error))
    waist = result["waist"]
    if waist["geometry_quality"] == "VALID":
        p, n = (np.asarray(waist["plane_origin_m"]), np.asarray(waist["plane_normal"]))
        sensitivity = []
        for offset in (-0.005, 0.005):
            q = section(engine, p + offset * n, n, seed, masks["torso"])
            sensitivity.append(dict(offset_engineering_m=offset, **compact(q)))
        waist["plane_sensitivity"] = sensitivity
    return (result, engine)
