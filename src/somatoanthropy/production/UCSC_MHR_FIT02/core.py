"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations


def source_key(row):
    group, name = (row["source_sex_group"], row["source_id"])
    if group not in {"male", "female"} or not name or "/" in name or ("\\" in name):
        raise ValueError("Exact UCSC source-labelled group and basename required")
    return group + "/" + name
