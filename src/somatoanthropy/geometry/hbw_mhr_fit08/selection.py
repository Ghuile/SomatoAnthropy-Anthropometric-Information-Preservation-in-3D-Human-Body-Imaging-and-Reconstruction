"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import Any


def select(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(rows) != 10 or len({r["source_id"] for r in rows}) != 10:
        raise ValueError(f"Exactly ten distinct validation families required; got {len(rows)}")
    if any((r["split"] != "val" for r in rows)):
        raise ValueError("Test or relabelled split is excluded")
    ordered = sorted(rows, key=lambda r: (r["source_id"], r["npy"]))
    return [{**r, "id": f"FIT08-{i:03d}"} for i, r in enumerate(ordered, 1)]
