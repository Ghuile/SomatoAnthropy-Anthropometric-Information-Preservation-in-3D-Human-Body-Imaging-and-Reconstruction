"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any


def apply_fallback(
    candidate: dict[str, Any],
    abdomen_y: float,
    chest_y: float,
    section_at: Callable[[float], dict[str, Any]],
    offset_m: float,
) -> dict[str, Any]:
    result = copy.deepcopy(candidate)
    if candidate["quality_state"] == "PROXY_VALID":
        result.update(fallback_applied=False, selection_method="ADAPTIVE_LOWER_HALF")
        return result
    y = abdomen_y + offset_m
    if not abdomen_y < y < abdomen_y + 0.5 * (chest_y - abdomen_y):
        raise ValueError("FALLBACK_OUTSIDE_RETAINED_WAIST_INTERVAL")
    measured = section_at(y)
    result.update(measured)
    contour_valid = measured["quality_state"] == "PROXY_VALID"
    result.update(
        fallback_applied=True,
        fallback_offset_m=offset_m,
        fallback_height_m=y,
        selected_normalized_height=offset_m / (chest_y - abdomen_y),
        original_selection_quality_state=candidate["quality_state"],
        original_selection_reason=candidate["reason"],
        quality_state="SITE_AMBIGUOUS" if contour_valid else measured["quality_state"],
        reason="UNRESOLVED_WAIST_ABOVE_ABDOMEN_FALLBACK"
        if contour_valid
        else "ABOVE_ABDOMEN_FALLBACK_CONTOUR_INVALID",
        fallback_contour_valid=contour_valid,
        selection_method="ABDOMEN_PLUS_EXPLICIT_VERTICAL_OFFSET",
        engineering_value_cm=measured.get("raw_contour_cm"),
        scientific_margins_approved=False,
    )
    return result
