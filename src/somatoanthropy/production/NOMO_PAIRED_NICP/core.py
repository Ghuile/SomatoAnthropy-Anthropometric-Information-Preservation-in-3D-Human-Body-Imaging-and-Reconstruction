"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib

TASK = "NOMO-PAIRED-NICP150"


def select_additional(existing, available, count=40, seed=20261017):
    """Balance recorded source groups; choose deterministically without fit outcomes."""
    chosen = []
    counts = {g: sum((s.startswith(g + "_") for s in existing)) for g in ("male", "female")}
    pool = set(available) - set(existing)
    for _ in range(count):
        group = min(counts, key=lambda g: (counts[g], g))
        candidates = [s for s in pool if s.startswith(group + "_")]
        if not candidates:
            candidates = list(pool)
        if not candidates:
            raise ValueError("Insufficient additional paired identities")
        sid = min(
            candidates, key=lambda s: (hashlib.sha256(f"{TASK}/{seed}/{s}".encode()).hexdigest(), s)
        )
        chosen.append(sid)
        pool.remove(sid)
        counts[sid.split("_")[0]] += 1
    return chosen
