"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

import numpy as np

from somatoanthropy.data.nomo_completion import skeleton_points
from somatoanthropy.data.nomo_contact_sections import neck_section
from somatoanthropy.experiments.e2.measure import proxy_sites
from somatoanthropy.experiments.e3.core import PROTOCOL, VERSION
from somatoanthropy.geometry.anthropometry.mhr_sites import anchor_position


def common(mesh, atlas, masks):
    v, f = (mesh["vertices"], mesh["faces"])
    joints = skeleton_points(mesh)
    anchors = {k: anchor_position(v, f, a) for k, a in atlas["anchors"].items()}
    sites, engine = proxy_sites(v, f, anchors, joints, masks)
    names = masks["joint_names"][masks["dominant_joint"]]
    allowed = np.char.startswith(names, "c_neck") | np.isin(names, ["c_head", "c_jaw", "c_spine3"])
    neck = neck_section(engine, joints, np.all(allowed[f], axis=1))
    sites["neck"] = neck
    sites["height"] = dict(
        geometry_quality="VALID",
        reason="GLOBAL_Y_EXTENT_NOT_STATURE",
        raw_contour_cm=float(np.ptp(v[:, 1]) * 100),
        tape_envelope_cm=float(np.ptp(v[:, 1]) * 100),
    )
    return (sites, engine, joints)


def fields(r, site, method, q, *, functional="raw_contour_cm", eligible=True):
    value = q.get(functional)
    good = (
        q.get("geometry_quality") == "VALID"
        and value is not None
        and np.isfinite(value)
        and (value > 0)
    )
    return dict(
        experiment_id="EXP-E3",
        dataset_id="DFAUST",
        subject_uid=r["subject_uid"],
        observation_uid=r["observation_uid"],
        fit_uid=r["fit_uid"],
        body_uid=r["body_uid"],
        selection_id=r["selection_id"],
        participant=r["subject_label"],
        sequence_uid=r["sequence_uid"],
        source_asset_hash=r["source_asset_hash"],
        native_parameter_hash=r["native_parameter_hash"],
        mhr_model_revision=r["mhr_model_revision"],
        canonical_pose_id=r["canonical_pose_id"],
        measurement_definition_id=site + "_" + functional,
        measurement_protocol_version=PROTOCOL
        if method.startswith(("B_", "C_"))
        else "NOMO-T90-APPROVED-v1+E3-indexed-audit",
        measurement_site_status=q.get("quality_state", "GEOMETRIC_PROXY_UNQUALIFIED"),
        coordinate_frame="saved canonical Y-up native-cm*0.01 plus floor translation; root-local plane coordinates separate",
        unit_convention="engineering_cm; source metre calibration conditional",
        comparison_type=method,
        result_value=float(value) if good and eligible else None,
        quality_state="GEOMETRIC_PROXY" if good and eligible else "UNAVAILABLE",
        geometry_quality=q.get("geometry_quality"),
        site=site,
        method=method,
        functional=functional,
        anatomy="UNQUALIFIED",
        analysis_version=VERSION,
        fallback=q.get("fallback_applied", False),
        historical_quality_state=q.get("historical_quality_state", q.get("quality_state")),
        reason=q.get("reason"),
        reference_excluded=not eligible and method.startswith("C_"),
    )
