"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
from typing import Any

TASK = "PHASE01-HIT-FIT05"


def choose(rows, excluded, maximum=50, seed=20261017):
    if not 0 <= maximum <= 50:
        raise ValueError("At most 50 additional distinct people")
    ids = [str(r["subject_id"]) for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate source participant; resolve repeated observations")
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row["source_split"] != "train" or row["subject_id"] in excluded:
            continue
        if not row["path"].startswith(row["hit_gender_label"] + "/train/"):
            raise ValueError("Source split/path mismatch")
        groups.setdefault(row["hit_gender_label"], []).append(row)

    def rank(r):
        return hashlib.sha256(f"{TASK}/{seed}/{r['subject_id']}".encode()).hexdigest()

    for group in groups:
        groups[group] = sorted(groups[group], key=rank)
    result: list[dict[str, Any]] = []
    while len(result) < maximum and any(groups.values()):
        for group in sorted(groups):
            if groups[group] and len(result) < maximum:
                result.append(groups[group].pop(0))
    return result
