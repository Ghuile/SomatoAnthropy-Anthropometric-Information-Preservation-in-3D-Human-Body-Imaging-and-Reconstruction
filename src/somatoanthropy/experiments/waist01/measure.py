"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from somatoanthropy.data.nomo_completion import skeleton_points
from somatoanthropy.data.nomo_contact_sections import IndexedSections
from somatoanthropy.experiments.e2.measure import section
from somatoanthropy.experiments.reconciliation.storage import sha
from somatoanthropy.experiments.waist01.core import UPSTREAM, canonical
from somatoanthropy.experiments.waist01.inputs import compact
from somatoanthropy.geometry.anthropometry.adaptive_waist import select_adaptive
from somatoanthropy.geometry.anthropometry.approved_t90 import measure_approved_sites
from somatoanthropy.geometry.anthropometry.mhr_sites import anchor_position, validate_atlas


def mesh(c, r, masks):
    a = c.arrays(r["mesh"])
    if r.get("mesh_adapter") == "HIT_NATIVE_CM":
        a["vertices"] = np.asarray(a["vertices"], float) * 0.01
        a["skeleton"] = a["skeleton"].reshape(-1, 8)
        a["joint_names"] = masks["joint_names"]
        floor = -float(a["vertices"][:, 1].min())
        a["vertices"][:, 1] += floor
        a["floor_translation_m"] = np.array(floor)
    return a


def saved_waist(c, r, a, masks, atlas):
    old = dict(r["old_waist"])
    if r["dataset"] == "NOMO" and r["pathway"] == "SMPL-LBFGSB" and (r["state"] == "fitted"):
        from somatoanthropy.data.nomo_released_metrology import measure as released

        v, f = (a["vertices"], a["faces"])
        anchors = {name: anchor_position(v, f, q) for name, q in atlas["anchors"].items()}
        q = released(v, f, skeleton_points(a)["root"], anchors, masks["pelvis"])[0]["waist"]
        return (
            q,
            dict(
                mode="Unchanged released-pose selector on saved LBFGSB fitted mesh; historical measurement unavailable",
                selection_reproduced=True,
                historical_measurement_unavailable=True,
            ),
        )
    if r["dataset"] == "HIT":
        q = measure_approved_sites(a, masks, atlas)["waist"]
        return (
            q,
            dict(
                mode="Existing approved function on historical saved neutral pose",
                selection_reproduced=True,
            ),
        )
    p = old.get("details_path")
    if p:
        d = c.read(p)
    else:
        folder = Path(r["mesh"]).parent
        p = folder / "measurement_details.json"
        if not p.exists():
            p = folder / "measurement-details.json"
        d = c.read(p)
    q = d["waist"]
    profile = q.get("search_profile")
    if profile:
        selected = select_adaptive(profile, 0.5, 0.01)
        if selected != q.get("selection"):
            raise ValueError("HISTORICAL_SELECTOR_REPLAY_MISMATCH:" + r["record_id"])
        replay = dict(
            mode="Actual unchanged select_adaptive on saved original search profile; saved original plane and circumference",
            selection_reproduced=True,
        )
    else:
        replay = dict(
            mode="Original saved selector record and plane; complete search profile unavailable",
            selection_reproduced=False,
        )
    q = dict(q, **old)
    return (q, replay)


def valid_value(q, functional):
    x = q.get(functional)
    if x is None or not np.isfinite(x) or x <= 0:
        return None
    if q.get("geometry_quality") not in (None, "VALID"):
        return None
    return float(x)


def one(c, r, api, atlas, masks):
    body_type, convert, measure, slice_upstream = api
    a = mesh(c, r, masks)
    v, f = (a["vertices"], a["faces"])
    validate_atlas(atlas, v, f)
    joints = skeleton_points(a)
    anchors = {k: anchor_position(v, f, q) for k, q in atlas["anchors"].items()}
    q, replay = saved_waist(c, r, a, masks, atlas)
    floor = float(v[:, 1].min())
    transformed = convert(v * 100)
    adapter_residual = float(np.max(np.abs(transformed - canonical(v))))
    m = trimesh.Trimesh(transformed, f, process=False)
    official = measure(
        body_type(m, source="EXP-WAIST-01 saved LOD0 mesh adapter"), only=["waist_cm"]
    )
    if "body_fat_pct" in official:
        raise ValueError("UNREQUESTED_BODY_COMPOSITION")
    z = float(official["_waist_z"])
    value, points = slice_upstream(m, z, return_contour=True)
    if not np.isclose(value * 100, official["waist_cm"], atol=1e-09, rtol=0):
        raise ValueError("PUBLIC_API_WAIST_MISMATCH")
    points_original = (
        np.column_stack((points[:, 0], points[:, 2] + floor, -points[:, 1]))
        if points is not None
        else np.empty((0, 3))
    )
    engine = IndexedSections(v, f)
    p = q.get("plane_origin_m", q.get("plane_point_m"))
    if p is None:
        p = [0, float(q["fallback_height_m"]), 0] if "fallback_height_m" in q else None
    levels = dict(
        B1=floor + z,
        B2=floor + 0.63 * float(transformed[:, 2].max()),
        B3=float(anchors["umbilicus_model_surface"][1]),
        B3_offset=float(anchors["umbilicus_model_surface"][1] + 0.005),
    )
    if p is not None:
        levels["P"] = float(p[1])
    sections = {
        name: section(
            engine,
            [joints["root"][0], y, joints["root"][2]],
            [0, 1, 0],
            joints["root"],
            masks["torso"],
        )
        for name, y in levels.items()
    }
    ours = valid_value(q, "raw_contour_cm")
    audited = valid_value(sections.get("P", {}), "raw_contour_cm")
    fallback = bool(q.get("fallback_applied", False))
    fallback_residual = (
        levels.get("P", 0) - levels["B3_offset"] if fallback and "P" in levels else None
    )
    fallback_trigger = q.get(
        "original_selection_reason", q.get("selection", {}).get("reason", q.get("reason"))
    )
    base = {
        k: r.get(k)
        for k in (
            "record_id",
            "dataset",
            "subject_uid",
            "body_uid",
            "fit_uid",
            "observation_uid",
            "pathway",
            "state",
            "challenge_group",
            "source_axial_ratio",
            "source_top_tail",
            "source_extent",
            "source_sha256",
            "source_path",
            "source_id",
            "reference_tier",
            "reference_definition",
            "reference_dependent",
        )
    }
    return dict(
        base,
        mesh_path=r["mesh"],
        mesh_sha256=sha(r["mesh"]),
        parameter_path=r["parameter_path"],
        parameter_sha256=sha(r["parameter_path"]) if r["parameter_path"] else None,
        geometry=dict(
            vertices=len(v),
            faces=len(f),
            lod=0,
            frame="saved Y-up engineering metres; upstream proper rotation (x,-z,y), float32 and floor alignment",
            floor_y=floor,
            height_engineering_cm=float(np.ptp(v[:, 1]) * 100),
            official_height_cm=float(transformed[:, 2].max() * 100),
            adapter_max_residual_m=adapter_residual,
        ),
        reference=r["reference"],
        reference_protocol_compatible=False,
        P=compact(q),
        P_raw_cm=ours,
        P_audit_raw_cm=audited,
        P_audit_difference_cm=audited - ours if audited is not None and ours is not None else None,
        selector_replay=replay,
        fallback=fallback,
        fallback_trigger=fallback_trigger,
        fallback_offset_residual_m=fallback_residual,
        original_quality=q.get("quality_state"),
        anatomical_site="UNQUALIFIED_ENGINEERING_PROXY",
        human_review="NOT_REVIEWED",
        official=dict(
            api="clad_body.measure.measure(MhrBody, only=['waist_cm'])",
            commit=UPSTREAM,
            waist_cm=float(official["waist_cm"]),
            _waist_z=z,
            _waist_pct=float(official["_waist_pct"]),
            valid=bool(official["waist_cm"] > 0),
            points_m=points_original.tolist(),
        ),
        levels_world_y_m=levels,
        levels_floor_y_m={k: y - floor for k, y in levels.items()},
        levels_root_y_m={k: y - float(joints["root"][1]) for k, y in levels.items()},
        delta_y_m=levels["P"] - levels["B1"] if "P" in levels else None,
        delta_y_over_height=(levels["P"] - levels["B1"]) / np.ptp(v[:, 1])
        if "P" in levels
        else None,
        umbilicus_m=anchors["umbilicus_model_surface"].tolist(),
        root_m=joints["root"].tolist(),
        sections=sections,
        independent_physical_accuracy=False,
        scientific_margins_approved=False,
    )
