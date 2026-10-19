"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import Any

import numpy as np

VERSION = "MHR-UMBILICAL-ADAPTIVE-WAIST-v4"


def prominences(values: np.ndarray) -> list[dict[str, Any]]:
    """Interior plateau peaks, bounded by higher peaks or the retained interval ends."""
    peaks = []
    i = 1
    while i < len(values) - 1:
        stop = i
        while stop + 1 < len(values) and abs(values[stop + 1] - values[i]) <= 1e-08:
            stop += 1
        if (
            stop < len(values) - 1
            and values[i] > values[i - 1] + 1e-08
            and (values[stop] > values[stop + 1] + 1e-08)
        ):
            left, right = (i - 1, stop + 1)
            while left > 0 and values[left - 1] <= values[i] + 1e-08:
                left -= 1
            while right < len(values) - 1 and values[right + 1] <= values[i] + 1e-08:
                right += 1
            score = values[i] - max(values[left : i + 1].min(), values[stop : right + 1].min())
            peaks.append(
                {
                    "index": (i + stop) // 2,
                    "prominence_cm": float(score),
                    "plateau_indices": [i, stop],
                }
            )
        i = stop + 1
    return peaks


def select_adaptive(
    profile: list[dict[str, Any]], retained_fraction: float = 0.8, near_flat_fraction: float = 0.01
) -> dict[str, Any]:
    """Compare bracketed peak/trough prominence, then choose the requested extreme.

    Cutoff is a fraction of physical A-to-C distance. Real runs insert an exact
    measured cutoff section; interpolation here also supports invented examples.
    Circumference arithmetic ties use 1e-8 cm, not an anatomical tolerance.
    """
    result: dict[str, Any] = {
        "version": VERSION,
        "retained_fraction": retained_fraction,
        "near_flat_fraction": near_flat_fraction,
        "scientific_margins_approved": False,
    }
    x = np.array([r["normalized_height"] for r in profile], dtype=float)
    if (
        len(x) < 3
        or not np.isfinite(x).all()
        or (not (np.diff(x) > 0).all())
        or (x[0] != 0)
        or (x[-1] < retained_fraction)
    ):
        return dict(result, quality_state="NOT_EVALUABLE", reason="INVALID_PROFILE_COORDINATES")
    required = x <= retained_fraction + 1e-12
    next_index = min(int(np.searchsorted(x, retained_fraction)), len(x) - 1)
    required[next_index] = True
    if any(
        (
            r["quality_state"] != "PROXY_VALID" or r.get("raw_contour_cm") is None
            for i, r in enumerate(profile)
            if required[i]
        )
    ):
        return dict(result, quality_state="SITE_AMBIGUOUS", reason="INCOMPLETE_RETAINED_PROFILE")
    valid_indices = np.flatnonzero(required)
    source_y = np.array([profile[int(i)]["raw_contour_cm"] for i in valid_indices], dtype=float)
    source_x = x[valid_indices]
    keep = source_x < retained_fraction - 1e-12
    xx = np.r_[source_x[keep], retained_fraction]
    yy = np.r_[source_y[keep], np.interp(retained_fraction, source_x, source_y)]
    median = float(np.median(yy))
    limit = near_flat_fraction * median
    spread = float(np.ptp(yy))
    result.update(
        retained_range_cm=spread,
        retained_median_cm=median,
        near_flat_limit_cm=limit,
        retained_min_cm=float(yy.min()),
        retained_max_cm=float(yy.max()),
        retained_heights=xx.tolist(),
        retained_circumferences_cm=yy.tolist(),
    )
    peaks, troughs = (prominences(yy), prominences(-yy))
    peak_score = max((p["prominence_cm"] for p in peaks), default=0.0)
    trough_score = max((p["prominence_cm"] for p in troughs), default=0.0)
    result.update(
        peak_prominence_cm=peak_score,
        trough_prominence_cm=trough_score,
        peaks=peaks,
        troughs=troughs,
    )
    state, reason = ("PROXY_VALID", "RESEARCHER_ADAPTIVE_EXTREMUM")
    if spread <= limit + 1e-08:
        branch, mode = ("NEAR_FLAT_MAXIMUM", "max")
        reason = "RESEARCHER_NEAR_FLAT_MAXIMUM_RULE"
    elif max(peak_score, trough_score) <= 1e-08:
        branch, mode = (
            ("UNBRACKETED_INCREASE_MAXIMUM", "max")
            if yy[-1] >= yy[0]
            else ("UNBRACKETED_DECREASE_MINIMUM", "min")
        )
        state, reason = ("SITE_AMBIGUOUS", "NO_BRACKETED_TURNING_POINT")
    elif abs(peak_score - trough_score) <= 1e-08:
        return dict(
            result,
            branch="COMPETING_PEAK_AND_TROUGH",
            quality_state="SITE_AMBIGUOUS",
            reason="EQUAL_PEAK_TROUGH_PROMINENCE",
        )
    else:
        branch, mode = (
            ("TROUGH_DOMINANT_MINIMUM", "min")
            if trough_score > peak_score
            else ("PEAK_DOMINANT_MAXIMUM", "max")
        )
        if max(peak_score, trough_score) < limit:
            state, reason = ("SITE_AMBIGUOUS", "TURNING_POINT_SMALLER_THAN_NEAR_FLAT_RANGE")
    candidates = np.flatnonzero(xx > 1e-12)
    value = (min if mode == "min" else max)(yy[candidates])
    ties = [int(i) for i in candidates if abs(yy[i] - value) <= 1e-08]
    index = min(ties, key=lambda i: (abs(xx[i] - retained_fraction / 2), i))
    if branch != "NEAR_FLAT_MAXIMUM":
        if index in (int(candidates[0]), len(xx) - 1):
            state, reason = ("SITE_AMBIGUOUS", "SELECTED_EXTREMUM_AT_RETAINED_BOUNDARY")
        if len(ties) > 1 and max(ties) - min(ties) + 1 != len(ties):
            state, reason = ("SITE_AMBIGUOUS", "EXTREMUM_AT_MULTIPLE_SEPARATE_HEIGHTS")
    return dict(
        result,
        branch=branch,
        quality_state=state,
        reason=reason,
        selected_normalized_height=float(xx[index]),
        selected_raw_contour_cm=float(yy[index]),
        selection_mode=mode,
        tied_extremum_heights=[float(xx[i]) for i in ties],
    )
