"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
import math
from typing import Any

TARGETS = ("BMXHT", "BMXWAIST", "BMXARMC", "BMXTHICR")
COMMENTS = ("BMIHT", "BMIWAIST", "BMIARMC", "BMITHICR")


def need(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def eligible_profile(seqn: int, panels: list[dict[str, Any]]) -> dict[str, Any]:
    need(len(panels) == 5 and {p["panel"] for p in panels} == {1, 2, 3, 4, 5}, "FIVE_PANEL_LINKAGE")
    first = panels[0]["fields"]
    need(
        all((p["fields"] == first for p in panels)), "INCONSISTENT_REPEATED_OBSERVATIONS_OR_CAUSES"
    )

    def observed(name: str) -> float:
        item = first[name]
        need(
            item["state"] == 0 and item["value"] is not None and math.isfinite(item["value"]),
            "MISSING_OR_INVALID_" + name,
        )
        return float(item["value"])

    gender, age = (observed("RIAGENDR"), observed("RIDAGEYR"))
    need(gender in (1, 2) and 20 <= age <= 69, "AGE_OR_SOURCE_CATEGORY")
    need(observed("BMDSTATS") in (1, 2, 3), "BMX_STATUS_CONFLICT")
    targets = [observed(name) for name in TARGETS]
    need(all((v > 0 for v in targets)), "NONPOSITIVE_OBSERVED_TARGET")
    for name in COMMENTS:
        comment = first[name]
        if comment["state"] == 0:
            need(name == "BMIHT" and comment["value"] == 3, "UNSUPPORTED_OR_CANNOT_OBTAIN_COMMENT")
        else:
            need(1 <= comment["state"] <= 28, "INVALID_COMMENT_STATE")
    return dict(
        private_family_key=["2005-2006", seqn, "primary"],
        seqn=seqn,
        source_gender_code=int(gender),
        source_gender_label={1: "Male", 2: "Female"}[int(gender)],
        targets_cm=targets,
        targets_m=[v / 100 for v in targets],
        source_fields=first,
        panels_verified=[1, 2, 3, 4, 5],
        eligibility_basis="Accepted PRIMARY training membership, retained pregnancy/status/quarantine decisions",
        comment_note="Missing comments are preserved, not interpreted as zero or proof of an uncomplicated exam",
    )


def choose(eligible: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for category in (1, 2):
        group = [p for p in eligible if p["source_gender_code"] == category]
        need(len(group) >= 5, "INSUFFICIENT_ELIGIBLE_TRAINING_FAMILIES")
        group.sort(
            key=lambda p: (
                hashlib.sha256(
                    f"FIT09|20261014|2005-2006|{category}|{p['seqn']}".encode()
                ).digest(),
                tuple(p["private_family_key"]),
            )
        )
        selected.extend(group[:5])
    need(len({tuple(p["private_family_key"]) for p in selected}) == 10, "DUPLICATE_SELECTED_FAMILY")
    return [{**p, "display_id": f"FIT09-{i:03d}"} for i, p in enumerate(selected, 1)]
