"""Researcher examples and distance-based clipping constrain the new rule."""

import numpy as np

from somatoanthropy.geometry.anthropometry.adaptive_waist import select_adaptive


def profile(values, heights=None):
    x = np.linspace(0, 1, len(values)) if heights is None else heights
    return [
        {
            "normalized_height": float(t),
            "raw_contour_cm": float(v),
            "quality_state": "PROXY_VALID",
        }
        for t, v in zip(x, values, strict=True)
    ]


def test_researcher_trough_example_returns_58_after_distance_cutoff():
    q = select_adaptive(profile([60, 61, 62, 59, 58, 58, 62, 63]))
    assert q["selected_raw_contour_cm"] == 58
    assert q["branch"] == "TROUGH_DOMINANT_MINIMUM"


def test_researcher_peak_example_returns_69_after_distance_cutoff():
    q = select_adaptive(profile([60, 65, 69, 68, 64, 66]))
    assert q["selected_raw_contour_cm"] == 69
    assert q["branch"] == "PEAK_DOMINANT_MAXIMUM"


def test_near_flat_uses_one_percent_of_median_and_returns_largest():
    q = select_adaptive(profile([60, 60.2, 60.1, 60.3, 60.1, 60.2]))
    assert q["branch"] == "NEAR_FLAT_MAXIMUM"
    assert q["selected_raw_contour_cm"] == 60.3
    assert q["retained_range_cm"] <= q["near_flat_limit_cm"]


def test_upper_twenty_percent_by_distance_cannot_select_chest_spike():
    q = select_adaptive(profile([60, 65, 69, 68, 64, 200], [0, 0.2, 0.4, 0.6, 0.8, 1.0]))
    assert q["selected_raw_contour_cm"] == 69
    assert 0 < q["selected_normalized_height"] <= 0.8
    assert q["retained_max_cm"] == 69


def test_monotonic_or_failed_profile_stays_ambiguous_and_does_not_select_abdomen():
    q = select_adaptive(profile([80, 75, 70, 65, 60]))
    assert q["quality_state"] == "SITE_AMBIGUOUS"
    assert 0 < q["selected_normalized_height"] <= 0.8
    p = profile([60, 65, 69, 68, 64, 66])
    p[2]["quality_state"] = "LIMB_CONTAMINATION"
    assert select_adaptive(p)["quality_state"] == "SITE_AMBIGUOUS"
