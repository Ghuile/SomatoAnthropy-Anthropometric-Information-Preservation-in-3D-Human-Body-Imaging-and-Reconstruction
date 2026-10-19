"""Five-millimetre fallback is explicit, measured, bounded and never a midpoint."""

import pytest

from somatoanthropy.geometry.anthropometry.waist_above_abdomen import apply_fallback


def at(y):
    return dict(
        quality_state="PROXY_VALID",
        reason="MEASURED",
        raw_contour_cm=80.0,
        plane_origin_m=[0.0, y, 0.0],
    )


def test_unresolved_waist_is_measured_exactly_five_mm_above_abdomen():
    candidate = dict(
        quality_state="SITE_AMBIGUOUS",
        reason="EQUAL_PEAK_TROUGH_PROMINENCE",
        search_interval_world_y_m=[1.0, 1.2],
        search_profile=[],
    )
    q = apply_fallback(candidate, 1.0, 1.4, at, 0.005)
    assert q["plane_origin_m"][1] == 1.0 + 0.005
    assert q["fallback_applied"] and q["engineering_value_cm"] == 80.0
    assert q["quality_state"] == "SITE_AMBIGUOUS"
    assert q["original_selection_reason"] == "EQUAL_PEAK_TROUGH_PROMINENCE"


def test_clear_waist_does_not_move_to_fallback():
    q = apply_fallback(dict(at(1.1), engineering_value_cm=80.0), 1.0, 1.4, at, 0.005)
    assert q["plane_origin_m"][1] == 1.1
    assert not q["fallback_applied"]


def test_invalid_fallback_contour_retains_failure():
    def invalid(y):
        return dict(quality_state="LIMB_CONTAMINATION", reason="FAILED")

    q = apply_fallback(
        dict(quality_state="SITE_AMBIGUOUS", reason="UNCLEAR"), 1.0, 1.4, invalid, 0.005
    )
    assert q["quality_state"] == "LIMB_CONTAMINATION"
    assert q["reason"] == "ABOVE_ABDOMEN_FALLBACK_CONTOUR_INVALID"


def test_fallback_must_be_strictly_inside_retained_half():
    with pytest.raises(ValueError):
        apply_fallback(
            dict(quality_state="SITE_AMBIGUOUS", reason="UNCLEAR"),
            1.0,
            1.004,
            at,
            0.005,
        )
