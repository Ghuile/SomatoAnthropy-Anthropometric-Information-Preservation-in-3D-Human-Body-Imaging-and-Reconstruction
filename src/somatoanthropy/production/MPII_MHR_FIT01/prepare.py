"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
from typing import Any


def select(candidates, excluded, seed):
    rows = sorted(
        (r for r in candidates if r["source_id"] not in excluded),
        key=lambda r: (r["height_extent_m"], r["source_id"]),
    )
    if len({r["source_id"] for r in rows}) != len(rows) or len(rows) < 100:
        raise ValueError("Duplicate or insufficient eligible source groups")
    buckets: list[list[dict[str, Any]]] = [[] for _ in range(10)]
    for index, row in enumerate(rows):
        buckets[min(9, index * 10 // len(rows))].append(row)
    for bucket in buckets:
        bucket.sort(key=lambda r: hashlib.sha256(f"{seed}|{r['source_id']}".encode()).hexdigest())
    return [dict(buckets[j][i], height_extent_decile=j) for i in range(10) for j in range(10)]
