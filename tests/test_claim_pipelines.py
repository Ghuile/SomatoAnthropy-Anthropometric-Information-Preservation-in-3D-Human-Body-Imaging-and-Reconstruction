"""Invented record fixtures exercise aggregation without releasing input records."""

import json
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from somatoanthropy.claims import (
    MECHANISMS,
    PATHWAYS,
    cohort_counts,
    control_domains,
    fallback_counts,
    height_statistics,
    validate_record_linkage,
)
from somatoanthropy.native_probe import probe_controls

ROOT = Path(__file__).resolve().parents[1]


def test_cohort_counts_keep_selection_and_provider_category_separate():
    rows = [
        dict(source_id="female_fixture-a", selection="RETAINED"),
        dict(source_id="male_fixture-b", selection="ADDITIONAL"),
        dict(source_id="female_fixture-c", selection="REPLACEMENT"),
    ]
    result = cohort_counts({"participants": rows})
    assert result["people"] == 3
    assert result["female_source_category"] == 2
    assert result["male_source_category"] == 1
    assert [r["people"] for r in result["selection_counts"]] == [1, 1, 1]
    with pytest.raises(ValueError, match="DUPLICATE"):
        cohort_counts({"participants": rows + [rows[0]]})


def test_fallback_counts_preserve_overlapping_people_and_complete_pathways():
    rows = []
    for person, flags in [("fixture-a", [True, False]), ("fixture-b", [True, True])]:
        for path, flag in zip(["SMPL-NICP", "CAESAR-NICP"], flags, strict=True):
            rows.append(
                dict(
                    dataset="NOMO",
                    state="canonical",
                    mode="end_to_end",
                    pair_eligible=True,
                    pathway=path,
                    subject_uid=person,
                    fallback=flag,
                )
            )
    result = fallback_counts(rows)
    assert result["people"] == 2
    assert result["body_observations"] == 4
    assert result["fallback_observations"] == 3
    assert result["nonfallback_observations"] == 1
    assert result["fallback_people"] == 2
    assert result["nonfallback_people"] == 1
    assert result["both_strata_people"] == 1
    assert fallback_counts(rows[:-1])["people"] == 1
    with pytest.raises(ValueError, match="DUPLICATE"):
        fallback_counts(rows + [rows[0]])
    bad = deepcopy(rows)
    bad[0]["fallback"] = None
    with pytest.raises(ValueError, match="BOOLEAN"):
        fallback_counts(bad)


def test_height_statistics_use_source_target_ranks_without_exporting_cases():
    rows = [
        dict(
            partition="heldout",
            collection="SMPL-NICP",
            condition="B",
            state="canonical",
            case=f"fixture-{i}",
            source_extent_cm=x,
            native_extent_cm=5 - x,
        )
        for i, x in enumerate([1.0, 2.0, 3.0])
    ]
    result = height_statistics(rows)
    assert len(result) == 1
    assert result[0]["n"] == 3
    assert result[0]["spearman"] == pytest.approx(-1)
    assert "case" not in result[0] and "subject_uid" not in result[0]
    with pytest.raises(ValueError, match="DUPLICATE"):
        height_statistics(rows + [rows[0]])


def test_full_model_audit_distinguishes_zero_domain_from_zero_transform():
    rows = json.loads((ROOT / "configs/control_audit_204.json").read_text("utf-8"))
    result = control_domains(rows)
    assert result["audited_controls"] == 204
    assert result["released_controls"] == 9
    assert result["zero_domain_claims"] == [
        dict(index=147, name="scale_hip_height", minimum=0.0, maximum=0.0),
        dict(index=148, name="scale_hip_depth", minimum=0.0, maximum=0.0),
        dict(index=152, name="scale_ankle_height", minimum=-0.0, maximum=0.0),
    ]
    assert all(rows[i]["affected_joint_channels"] for i in [147, 148, 152])
    with pytest.raises(ValueError, match="204"):
        control_domains(rows[:9])


def test_native_probe_reads_columns_and_preserves_authored_limits():
    matrix = np.zeros((7, 2))
    matrix[1, 0] = 3.5
    matrix[6, 1] = -2
    character = SimpleNamespace(
        parameter_transform=SimpleNamespace(transform=SimpleNamespace(numpy=lambda: matrix)),
        skeleton=SimpleNamespace(joints=[SimpleNamespace(name="invented_joint")]),
        parameter_limits=["invented authored limit"],
    )
    probe = probe_controls(SimpleNamespace(character=character), ["invented-a", "invented-b"])
    assert probe["rows"][0]["affected_joint_channels"] == [
        dict(joint="invented_joint", channel="ty", coefficient=3.5)
    ]
    assert probe["rows"][1]["affected_joint_channels"] == [
        dict(joint="invented_joint", channel="scale", coefficient=-2.0)
    ]
    assert probe["limits"] == ["invented authored limit"]


def test_linkage_rejects_different_people_with_equal_denominators():
    heights, geometry = [], []
    for path in PATHWAYS:
        for partition, arms in [("heldout", ("B", "C")), ("development", MECHANISMS)]:
            for arm in arms:
                for person in ("invented-a", "invented-b"):
                    labels = dict(partition=partition, collection=path, condition=arm, case=person)
                    for state in ("fitted", "canonical"):
                        heights.append(dict(labels, state=state, source_extent_cm=150.0))
                    if partition == "development":
                        geometry.append(dict(labels, mean_cm=1.0))
    validate_record_linkage(heights, geometry)
    changed = deepcopy(heights)
    changed[0]["case"] = "invented-replacement"
    with pytest.raises(ValueError, match="PAIRED_HEIGHT_MEMBERSHIP"):
        validate_record_linkage(changed, geometry)
    changed = deepcopy(geometry)
    changed[0]["case"] = "invented-replacement"
    with pytest.raises(ValueError, match="PAIRED_GEOMETRY_MEMBERSHIP"):
        validate_record_linkage(heights, changed)
