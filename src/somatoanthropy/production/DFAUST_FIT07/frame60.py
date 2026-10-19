"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from collections import Counter
from typing import Any

from somatoanthropy.production.DFAUST_FIT07 import core as c

FAMILIES = (
    ("arm_motion", ("jumping_jacks", "chicken_wings", "shake_arms")),
    ("lower_limb_motion", ("knees", "one_leg_loose", "running_on_spot")),
    ("hip_torso_motion", ("hips", "shake_hips")),
    ("challenging_dynamic_motion", ("one_leg_jump", "light_hopping_stiff", "light_hopping_loose")),
    ("upper_body_motion", ("punching", "shake_shoulders")),
)
BASELINE = ("shake_arms", "shake_shoulders", "punching", "hips")
POSE_FEATURES = (
    "near_neutral",
    "arm_elevation",
    "lower_limb_flexion",
    "torso_rotation",
    "self_contact",
    "challenging_dynamic_motion",
)


def motion(key: str) -> str:
    return key.split("_", 1)[1]


def family(label: str) -> str:
    return next((name for name, labels in FAMILIES if label in labels), "other_motion")


def select_panel(inventory: dict[str, Any], pilot: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the pilot exactly; add an early baseline candidate and new motions.

    All non-baseline additions use floor((T-1)/2). Motion labels express nominal
    conditions, never observed pose, contact or a claim of anatomical validity.
    """
    sequences = sorted(inventory["sequences"], key=lambda r: (r["subject_uid"], r["key"]))
    people = sorted({r["subject_uid"] for r in sequences})
    if len(people) != 10:
        raise ValueError("TEN_SOURCE_IDENTITIES_REQUIRED")
    lookup = {(r["partition"], r["key"]): r for r in sequences}
    if len(lookup) != len(sequences):
        raise ValueError("DUPLICATE_SEQUENCE")
    rows = []
    for person_index, uid in enumerate(people, 1):
        available = [r for r in sequences if r["subject_uid"] == uid]
        seeds = sorted(
            (r for r in pilot if r["subject_uid"] == uid), key=lambda r: (r["key"], r["frame"])
        )
        if len(seeds) > 6:
            raise ValueError("PILOT_OVERFLOW_NO_FITS_DROPPED")
        chosen: list[tuple[dict[str, Any], int, dict[str, Any] | None, str]] = []
        for seed in seeds:
            sequence = lookup[seed["partition"], seed["key"]]
            chosen.append((sequence, seed["frame"], seed, "preserved_pilot"))
        used = {r[0]["key"] for r in chosen}

        def add(labels: tuple[str, ...], baseline: bool = False) -> bool:
            for label in labels:
                sequence = next(
                    (r for r in available if motion(r["key"]) == label and r["key"] not in used),
                    None,
                )
                if sequence is not None:
                    index = 0 if baseline else (sequence["frames"] - 1) // 2
                    chosen.append(
                        (
                            sequence,
                            index,
                            None,
                            "early_baseline_candidate" if baseline else "distinct_motion_midpoint",
                        )
                    )
                    used.add(sequence["key"])
                    return True
            return False

        if len(chosen) < 6:
            add(BASELINE, baseline=True)
        represented = {family(motion(r["key"])) for r in seeds}
        for name, labels in FAMILIES:
            if len(chosen) < 6 and name not in represented:
                add(labels)
        for sequence in available:
            if len(chosen) < 6:
                add((motion(sequence["key"]),))
        if len(chosen) != 6:
            raise ValueError("INSUFFICIENT_DISTINCT_MOTIONS_NO_REPEATED_FRAME_PADDING")
        for slot, (sequence, index, prior_fit, reason) in enumerate(chosen, 1):
            row = dict(
                c.identifiers(sequence["container_sha256"], sequence["key"], index),
                selection_id=f"D{person_index:02d}-F{slot:02d}",
                subject_label=f"D{person_index:02d}",
                partition=sequence["partition"],
                key=sequence["key"],
                motion=motion(sequence["key"]),
                nominal_motion_family=family(motion(sequence["key"])),
                frame=index,
                frame_index_base=0,
                sequence_frames=sequence["frames"],
                temporal_position=index / max(1, sequence["frames"] - 1),
                timestamp_seconds=None,
                temporal_basis="frame/(sequence_frames-1); no acquisition timestamp inferred",
                container_sha256=sequence["container_sha256"],
                selection_reason=reason,
                reuse_existing_fit=prior_fit is not None,
                fit_uid=prior_fit["fit_uid"] if prior_fit else None,
                existing_fit_directory=prior_fit["existing_fit_directory"] if prior_fit else None,
                historical_id=prior_fit.get("historical_id") if prior_fit else None,
                source_frame_validation="PRIOR_VERIFIED_PILOT"
                if prior_fit
                else "METADATA_ONLY_FRAME_CHECK_PENDING",
                pose_features=dict.fromkeys(POSE_FEATURES),
                pose_feature_status="NOT_ASSESSED_FROM_GEOMETRY",
                intended_near_neutral=reason == "early_baseline_candidate",
                scientifically_qualified=False,
            )
            rows.append(row)
    validate_panel(rows, inventory, pilot)
    return rows


def validate_panel(
    rows: list[dict[str, Any]], inventory: dict[str, Any], pilot: list[dict[str, Any]]
) -> None:
    lookup = {(r["partition"], r["key"]): r for r in inventory["sequences"]}
    old = {(r["partition"], r["key"], r["frame"]): r for r in pilot}
    if len(rows) != 60 or len(old) != len(pilot):
        raise ValueError("SIXTY_UNIQUE_FRAMES_REQUIRED")
    if len({r["observation_uid"] for r in rows}) != 60:
        raise ValueError("DUPLICATE_OBSERVATION")
    counts = Counter((r["subject_uid"] for r in rows))
    if len(counts) != 10 or set(counts.values()) != {6}:
        raise ValueError("SIX_FRAMES_PER_PERSON_REQUIRED")
    reused = set()
    for row in rows:
        source = lookup[row["partition"], row["key"]]
        index = row["frame"]
        if type(index) is not int or not 0 <= index < source["frames"]:
            raise ValueError("FRAME_OUT_OF_RANGE")
        expected = c.identifiers(source["container_sha256"], source["key"], index)
        if any((row[k] != v for k, v in expected.items())):
            raise ValueError("SOURCE_IDENTITY_CHANGED")
        if (
            row["subject_uid"] != source["subject_uid"]
            or row["sequence_frames"] != source["frames"]
            or row["container_sha256"] != source["container_sha256"]
        ):
            raise ValueError("SOURCE_METADATA_CHANGED")
        if row["temporal_position"] != index / max(1, source["frames"] - 1):
            raise ValueError("TEMPORAL_LOCATION_CHANGED")
        key = (row["partition"], row["key"], index)
        if row["reuse_existing_fit"] != (key in old):
            raise ValueError("REUSE_STATUS_CHANGED")
        if key in old:
            if any((row[k] != old[key][k] for k in ("fit_uid", "existing_fit_directory"))):
                raise ValueError("EXISTING_FIT_CHANGED")
            reused.add(key)
        elif row["fit_uid"] is not None or row["existing_fit_directory"] is not None:
            raise ValueError("UNFITTED_ROW_HAS_FIT")
    if reused != set(old):
        raise ValueError("PILOT_FIT_OMITTED")
    for uid in counts:
        group = [r for r in rows if r["subject_uid"] == uid]
        additions = [r["key"] for r in group if not r["reuse_existing_fit"]]
        pilot_keys = {r["key"] for r in group if r["reuse_existing_fit"]}
        if len(additions) != len(set(additions)) or set(additions) & pilot_keys:
            raise ValueError("NEW_FRAMES_MUST_USE_DISTINCT_NEW_SEQUENCES")
