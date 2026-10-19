"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import Any

import numpy as np

from somatoanthropy.geometry.anthropometry.adaptive_waist import select_adaptive
from somatoanthropy.geometry.anthropometry.mhr_site_revision2 import standing_normal
from somatoanthropy.geometry.anthropometry.mhr_sites import (
    anchor_position,
    surface_anchor,
    torso_section,
    validate_atlas,
)
from somatoanthropy.geometry.anthropometry.posterior_hip_fallback import apply_region_policy
from somatoanthropy.geometry.anthropometry.three_landmark_hip import measure_three_landmark_hip
from somatoanthropy.geometry.anthropometry.waist_above_abdomen import apply_fallback
from somatoanthropy.geometry.fit03_anthropometry.core import MeshMetrology


def measure_approved_sites(
    mesh: dict[str, np.ndarray], masks: dict[str, np.ndarray], atlas: dict[str, Any]
) -> dict[str, Any]:
    """Recompute the approved engineering rule on an already generated T90 mesh.

    No pose generation, fitting, source measurements or body-composition labels.
    Original flags are retained. Clinical values remain unset.
    """
    v, f = (mesh["vertices"], mesh["faces"])
    validate_atlas(atlas, v, f)
    ri = mesh["joint_names"].tolist().index("root")
    if standing_normal(mesh["skeleton"][ri]) is None:
        raise ValueError("ROOT_NOT_UPRIGHT")
    origin = mesh["skeleton"][ri, :3].astype(float) * 0.01
    origin[1] += float(mesh["floor_translation_m"])
    normal = np.array([0.0, 1.0, 0.0])
    engine = MeshMetrology(dict(vertices=v, faces=f, length_units="m"))
    attachments = {name: anchor_position(v, f, a) for name, a in atlas["anchors"].items()}

    def section(point: np.ndarray) -> dict[str, Any]:
        seed = origin + normal * float((point - origin) @ normal)
        return torso_section(v, f, point, normal, seed, masks["torso"], engine)

    def at(y: float) -> dict[str, Any]:
        return section(np.array([origin[0], y, origin[2]]))

    chest_point = (
        attachments["left_anterior_chest_feature"] + attachments["right_anterior_chest_feature"]
    ) / 2
    chest = section(chest_point)
    navel = attachments["umbilicus_model_surface"]
    abdomen = section(navel)
    lo, hi = (float(navel[1]), float(chest_point[1]))
    if hi <= lo:
        raise ValueError("INVALID_ABDOMEN_CHEST_INTERVAL")
    count = int(np.ceil((hi - lo) / 0.005)) + 1
    if not 3 <= count <= 160:
        raise ValueError("WAIST_SCAN_RESOURCE_BOUND")
    profile = []
    for y in np.linspace(lo, hi, count):
        q = at(float(y))
        profile.append(
            dict(
                world_y_m=float(y),
                normalized_height=float((y - lo) / (hi - lo)),
                quality_state=q["quality_state"],
                raw_contour_cm=q.get("raw_contour_cm"),
                reason=q["reason"],
            )
        )
    cut = at(lo + 0.5 * (hi - lo))
    profile = [p for p in profile if abs(p["normalized_height"] - 0.5) > 1e-12]
    profile.append(
        dict(
            world_y_m=lo + 0.5 * (hi - lo),
            normalized_height=0.5,
            quality_state=cut["quality_state"],
            raw_contour_cm=cut.get("raw_contour_cm"),
            reason=cut["reason"],
        )
    )
    profile.sort(key=lambda p: p["normalized_height"])
    selection = select_adaptive(profile, 0.5, 0.01)
    waist = dict(
        quality_state=selection["quality_state"], reason=selection["reason"], value_cm=None
    )
    if "selected_normalized_height" in selection:
        waist = at(lo + selection["selected_normalized_height"] * (hi - lo))
        if waist["quality_state"] == "PROXY_VALID":
            waist.update(quality_state=selection["quality_state"], reason=selection["reason"])
    waist.update(
        search_profile=profile,
        selection=selection,
        search_interval_world_y_m=[lo, lo + 0.5 * (hi - lo)],
        site_definition="Adaptive waist in lower 50% of navel-to-chest distance",
        scientific_margins_approved=False,
    )
    waist = apply_fallback(waist, lo, hi, at, 0.005)
    crotch_anchor = surface_anchor(v, f, masks["pelvis"], origin, 1, False)
    crotch = anchor_position(v, f, crotch_anchor)
    upper = attachments["upper_pelvis_surface"]
    hip = measure_three_landmark_hip(
        mesh,
        dict(trunk_frame=dict(origin_m=origin.tolist())),
        masks,
        dict(
            search_interval_world_y_m=[float(crotch[1]), float(upper[1])],
            crotch_surface_anchor=crotch_anchor,
            crotch_point_m=crotch.tolist(),
            upper_gluteal_point_m=upper.tolist(),
            boundary_qualification="Upper pelvis atlas and pelvic underside ray are engineering landmarks, not participant annotations",
        ),
    )
    hip = apply_region_policy(hip)
    return dict(chest=chest, waist=waist, abdomen=abdomen, hip=hip)


def require_t90_parameters(
    controls: dict[str, np.ndarray], reference: dict[str, np.ndarray]
) -> None:
    """Require the exact approved native articulation before current metrology.

    Identity, morphology and expression may differ between people. The first
    130 authored articulation controls must match the approved reference exactly.
    No automatic pose adjustment or fitting is performed by this guard.
    """
    for key, shape in (
        ("identity_coeffs", (1, 45)),
        ("lbs_model_params", (1, 204)),
        ("face_expr_coeffs", (1, 72)),
    ):
        if (
            key not in controls
            or controls[key].shape != shape
            or (not np.isfinite(controls[key]).all())
        ):
            raise ValueError("INVALID_NATIVE_T90_CONTROLS:" + key)
    expected = np.asarray(reference["lbs_model_params"])
    if expected.shape != (1, 204) or not np.isfinite(expected).all():
        raise ValueError("INVALID_T90_REFERENCE")
    if not np.array_equal(controls["lbs_model_params"][:, :130], expected[:, :130]):
        raise ValueError("APPROVED_T90_ARTICULATION_REQUIRED")
