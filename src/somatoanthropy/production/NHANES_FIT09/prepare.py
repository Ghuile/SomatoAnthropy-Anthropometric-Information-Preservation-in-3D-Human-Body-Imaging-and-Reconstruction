"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np


def stratified_selection(
    population: list[dict[str, Any]], excluded: set[int], maximum: int, seed: str
) -> list[dict[str, Any]]:
    if not 0 <= maximum <= 50:
        raise ValueError("At most fifty additional participants")
    keys = [tuple(p["private_family_key"]) for p in population]
    if len(set(keys)) != len(keys):
        raise ValueError("Repeated source family; imputations are not individuals")
    groups = {
        g: sorted(
            [p for p in population if p["source_gender_code"] == g and p["seqn"] not in excluded],
            key=lambda p: p["seqn"],
        )
        for g in (1, 2)
    }
    total = min(maximum, sum((len(v) for v in groups.values())))
    allocation = {g: min(len(groups[g]), total // 2) for g in groups}
    while sum(allocation.values()) < total:
        available = [g for g in groups if allocation[g] < len(groups[g])]
        g = min(available, key=lambda g: (allocation[g], g))
        allocation[g] += 1
    chosen: list[dict[str, Any]] = []
    for g, rows in groups.items():
        if not allocation[g]:
            continue
        x = np.asarray([p["targets_cm"] for p in rows], dtype=float)
        if not np.isfinite(x).all() or x.shape[1] != 4 or (x <= 0).any():
            raise ValueError("Only four finite positive observed targets may select shape")
        median = np.median(x, axis=0)
        spread = np.percentile(x, 75, axis=0) - np.percentile(x, 25, axis=0)
        z = (x - median) / np.where(spread > 0, spread, 1.0)
        tie = [hashlib.sha256(f"{seed}|{g}|{p['seqn']}".encode()).digest() for p in rows]
        first = min(range(len(rows)), key=lambda i: (float(np.sum(z[i] ** 2)), tie[i]))
        selected = [first]
        distances = np.sum((z - z[first]) ** 2, axis=1)
        while len(selected) < allocation[g]:
            candidates = [i for i in range(len(rows)) if i not in selected]
            index = min(candidates, key=lambda i: (-float(distances[i]), tie[i]))
            selected.append(index)
            distances = np.minimum(distances, np.sum((z - z[index]) ** 2, axis=1))
        chosen.extend((rows[i] for i in selected))
    return chosen
