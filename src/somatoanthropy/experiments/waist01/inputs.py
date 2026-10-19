"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations


def compact(q):
    return {
        k: v
        for k, v in q.items()
        if k
        not in (
            "points_m",
            "raw_points_m",
            "tape_points_m",
            "selected_face_ids",
            "search_profile",
            "remeasurement",
        )
    }
