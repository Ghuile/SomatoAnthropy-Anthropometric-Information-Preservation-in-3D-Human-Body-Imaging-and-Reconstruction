"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import copy
from typing import Any

import numpy as np

from somatoanthropy.geometry.anthropometry.three_landmark_hip import ARITHMETIC_M, select_candidate
from somatoanthropy.geometry.fit03_anthropometry.core import hull_points


def apply_region_policy(saved: dict[str, Any]) -> dict[str, Any]:
    """A boundary-constrained lateral extremum is not an interior gluteal site.

    If either B or C is outside the strict existing gluteal height interval,
    drop the lateral pair from selection and use A. Original candidate geometry
    and diagnostics remain untouched; invalid A never supplies a number.
    """
    lo, hi = saved["search_interval_world_y_m"]
    landmarks, sections = (saved["landmarks"], saved["landmark_sections"])
    eligibility = {}
    for label, landmark in landmarks.items():
        y = float(landmark["point_m"][1])
        inside = bool(np.isfinite(y) and lo + ARITHMETIC_M < y < hi - ARITHMETIC_M)
        eligibility[label] = dict(
            in_gluteal_interior=inside,
            eligible_for_selection=inside,
            reason="INSIDE_GLUTEAL_REGION" if inside else "AT_OR_OUTSIDE_GLUTEAL_HEIGHT_BOUNDARY",
        )
    outside = [label for label in ("B", "C") if not eligibility[label]["in_gluteal_interior"]]
    posterior = bool(outside)
    excluded = ["B", "C"] if posterior else []
    for label in excluded:
        eligibility[label]["eligible_for_selection"] = False
        if label not in outside:
            eligibility[label]["reason"] = "LATERAL_PAIR_DROPPED_USE_A"
    included = {label: q for label, q in sections.items() if label not in excluded}
    winner, flags = select_candidate(included)
    for label in included:
        if not eligibility[label]["in_gluteal_interior"]:
            flags.append("REGION_BOUNDARY_EXTREMUM:" + label)
        if landmarks[label]["multiple_extremum_heights"]:
            flags.append("MULTIPLE_EXTREMUM_HEIGHTS:" + label)
    result = copy.deepcopy(sections[winner]) if winner is not None else {}
    if winner is not None:
        raw = np.asarray(result["points_m"])
        hull = hull_points(raw[:, [0, 2]])
        points = np.column_stack(
            (hull[:, 0], np.full(len(hull), result["plane_origin_m"][1]), hull[:, 1])
        )
        result.update(
            raw_points_m=raw.tolist(),
            points_m=points.tolist(),
            engineering_value_cm=result["tape_envelope_cm"],
        )
    reason = (
        ";".join(flags)
        if flags
        else "POSTERIOR_A_AFTER_OUTSIDE_LATERAL_PAIR_EXCLUSION"
        if posterior
        else "LARGEST_TAPE_AT_THREE_INTERIOR_GLUTEAL_EXTREMA"
    )
    result.update(
        quality_state="CONTOUR_INVALID"
        if winner is None
        else "SITE_AMBIGUOUS"
        if flags
        else "PROXY_VALID",
        reason=reason,
        selection_flags=flags,
        landmarks=copy.deepcopy(landmarks),
        landmark_sections=copy.deepcopy(sections),
        landmark_eligibility=eligibility,
        outside_lateral_landmarks=outside,
        excluded_landmarks=excluded,
        posterior_fallback_applied=posterior,
        selected_landmark=winner,
        selection_quantity="tape_envelope_cm",
        selection_method="POSTERIOR_A_WHEN_LATERAL_OUTSIDE_ELSE_THREE_POINT_TAPE_MAXIMUM",
        selected_equal_value_landmarks=[
            label
            for label, q in included.items()
            if winner is not None
            and q["quality_state"] == "PROXY_VALID"
            and (q.get("tape_envelope_cm") == sections[winner]["tape_envelope_cm"])
        ],
        prior_selection_diagnostics={
            key: copy.deepcopy(saved.get(key))
            for key in (
                "quality_state",
                "reason",
                "selection_flags",
                "selected_landmark",
                "selection_method",
            )
        },
        search_interval_world_y_m=[lo, hi],
        scientific_margins_approved=False,
        value_cm=None,
        anatomical_qualification="UNQUALIFIED",
        source_protocol_compatible=False,
        previous_surge_cutoff_used=False,
        site_definition="If B or C is at/outside existing gluteal height boundaries, exclude lateral pair and use horizontal outside-tape section at A; otherwise compare A/B/C outside-tape values; keep invalid A and remaining contour/tied-height issues flagged",
    )
    for key in (
        "crotch_point_m",
        "crotch_surface_anchor",
        "upper_gluteal_point_m",
        "boundary_qualification",
    ):
        if key in saved:
            result[key] = copy.deepcopy(saved[key])
    return result
