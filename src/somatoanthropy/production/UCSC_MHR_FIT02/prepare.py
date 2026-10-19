"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib

from somatoanthropy.production.UCSC_MHR_FIT02.core import source_key


def select(rows, excluded, seed, maximum=50):
    if not 0 <= maximum <= 50:
        raise ValueError("Maximum additional population is 50")
    candidates = [r for r in rows if source_key(r) not in excluded]
    if len({r["source_id"].casefold() for r in candidates}) != len(candidates):
        raise ValueError("Ambiguous repeated publisher identity across groups")
    if len({source_key(r) for r in candidates}) != len(candidates):
        raise ValueError("Duplicate source identities")
    buckets = []
    for group in ("male", "female"):
        ordered = sorted(
            (r for r in candidates if r["source_sex_group"] == group),
            key=lambda r: (r["raw_height_proxy"], source_key(r)),
        )
        for decile in range(10):
            bucket = [
                r for i, r in enumerate(ordered) if min(9, i * 10 // max(1, len(ordered))) == decile
            ]
            bucket.sort(
                key=lambda r: hashlib.sha256(f"{seed}|{source_key(r)}".encode()).hexdigest()
            )
            buckets.append([dict(r, source_height_decile=decile) for r in bucket])
    result = []
    buckets = [buckets[i] for decile in range(10) for i in (decile, decile + 10)]
    while len(result) < min(maximum, len(candidates)):
        for bucket in buckets:
            if bucket and len(result) < maximum:
                result.append(bucket.pop(0))
    return result
