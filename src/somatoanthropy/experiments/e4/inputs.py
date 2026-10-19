"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import Any


def index_unique(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> dict:
    result = {}
    for row in rows:
        key = tuple((row[k] for k in keys))
        if key in result:
            raise ValueError("DUPLICATE_LINK: " + str(key))
        result[key] = row
    return result


def linked_pair(a: dict, b: dict, cohort: str) -> dict:
    if a["subject_uid"] != b["subject_uid"] or a["source_id"] != b["source_id"]:
        raise ValueError("CROSS_PARTICIPANT_LINK")
    expected = "SMPL-NICP" if cohort == "primary" else "SMPL-LBFGSB"
    if a["collection"] != expected or b["collection"] != "CAESAR-NICP":
        raise ValueError("COHORT_REPRESENTATION_MISMATCH")
    if a["body_uid"] == b["body_uid"]:
        raise ValueError("INDEPENDENT_NATIVE_CANDIDATES_REQUIRED")
    return dict(cohort=cohort, subject_uid=a["subject_uid"], a=a, b=b)
