"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import Any

import numpy as np


def select_candidates(fits: list[dict[str, Any]]) -> dict[str, str]:
    eligible = [
        r
        for r in fits
        if r["subject_uid"]
        and r["native_parameter_valid"]
        and (r["historical_native_replay"] == "PASS")
        and (r["human_review"]["human_fitted"] == "ACCEPT")
        and (r.get("candidate_assessment", {}).get("technical_lod0") == "PASS")
        and (r["candidate_assessment"].get("invalid_sites") == 0)
        and (r["candidate_assessment"].get("severe_regional_defect") is False)
    ]
    for uid in {r["subject_uid"] for r in eligible}:
        signatures = {
            r["ranking_metrics"]["definition"] for r in eligible if r["subject_uid"] == uid
        }
        if len(signatures) != 1:
            raise ValueError("INCOMPATIBLE_CANDIDATE_METRICS")
    for r in eligible:
        if any(
            (
                not np.isfinite(r["ranking_metrics"][k]) or r["ranking_metrics"][k] < 0
                for k in ("normalized_symmetric_rms", "normalized_p95")
            )
        ):
            raise ValueError("INVALID_CANDIDATE_METRICS")
    selected: dict[str, str] = {}
    for r in sorted(
        eligible,
        key=lambda r: (
            r["candidate_assessment"]["ambiguous_sites"],
            r["candidate_assessment"]["fallback_sites"],
            r["ranking_metrics"]["normalized_symmetric_rms"],
            r["ranking_metrics"]["normalized_p95"],
            r["observation_uid"],
        ),
    ):
        selected.setdefault(r["subject_uid"], r["body_uid"])
    return selected
