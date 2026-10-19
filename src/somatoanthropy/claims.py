"""Aggregate audit claims from frozen model metadata and separately licensed records.

The rank calculation delegates to the original experiment implementation. Record
identifiers are used only to validate linkage and count people; none is returned.
"""

import json
from collections import defaultdict
from pathlib import Path

from somatoanthropy.experiments.e2_1.core import variation
from somatoanthropy.experiments.e2_2.core import GROUPS
from somatoanthropy.experiments.e4.core import describe
from somatoanthropy.reconstruction import MHR_REVISION

PATHWAYS = ("SMPL-NICP", "CAESAR-NICP")
SELECTIONS = ("RETAINED", "REPLACEMENT", "ADDITIONAL")
MECHANISMS = ("B", "C", "G1", "G2", "G3", "G4", "noG1", "noG2", "R025", "R4")
CONDITIONS = set(MECHANISMS) | {"historical", "D", "S1-B", "S1-C", "S1-D", "I1-B", "I1-C"}


def cohort_counts(manifest):
    """Count the frozen selection stages and provider category labels only."""
    counts = {
        s: dict(selection=s, people=0, female_source_category=0, male_source_category=0)
        for s in SELECTIONS
    }
    seen = set()
    for row in manifest["participants"]:
        identity = row["source_id"]
        if identity in seen:
            raise ValueError("DUPLICATE_COHORT_IDENTITY")
        seen.add(identity)
        category = identity.partition("_")[0]
        if category not in {"female", "male"} or row["selection"] not in counts:
            raise ValueError("UNSUPPORTED_PROVIDER_CATEGORY_OR_SELECTION")
        group = counts[row["selection"]]
        group["people"] += 1
        group[category + "_source_category"] += 1
    return dict(
        people=len(seen),
        selection_counts=list(counts.values()),
        female_source_category=sum(r["female_source_category"] for r in counts.values()),
        male_source_category=sum(r["male_source_category"] for r in counts.values()),
    )


def fallback_counts(rows):
    """Canonical P-side flags on complete, eligible paired NICP pathways."""
    people = defaultdict(dict)
    for row in rows:
        if not (
            row["dataset"] == "NOMO"
            and row["state"] == "canonical"
            and row["mode"] == "end_to_end"
            and row["pair_eligible"] is True
            and row["pathway"] in PATHWAYS
        ):
            continue
        if not isinstance(row["fallback"], bool):
            raise ValueError("BOOLEAN_SAVED_FALLBACK_FLAG_REQUIRED")
        group = people[row["subject_uid"]]
        if row["pathway"] in group:
            raise ValueError("DUPLICATE_PERSON_PATHWAY_OBSERVATION")
        group[row["pathway"]] = row["fallback"]
    complete = [p for p in people.values() if set(p) == set(PATHWAYS)]
    flags = [flag for person in complete for flag in person.values()]
    fallback_people = sum(any(p.values()) for p in complete)
    nonfallback_people = sum(not all(p.values()) for p in complete)
    return dict(
        people=len(complete),
        body_observations=len(flags),
        fallback_observations=sum(flags),
        nonfallback_observations=len(flags) - sum(flags),
        fallback_people=fallback_people,
        nonfallback_people=nonfallback_people,
        both_strata_people=sum(any(p.values()) and not all(p.values()) for p in complete),
        incomplete_people_excluded=len(people) - len(complete),
    )


def control_domains(rows):
    """Read authored domains separately from transform-column coefficients."""
    if len(rows) != 204 or {r["index"] for r in rows} != set(range(204)):
        raise ValueError("FULL_204_CONTROL_AUDIT_REQUIRED")
    if any(r["revision"] != MHR_REVISION for r in rows):
        raise ValueError("PINNED_MODEL_REVISION_REQUIRED")
    index = {r["index"]: r for r in rows}
    for row in rows:
        bounds = row["bounds"]
        if bounds and bounds["minimum"] > bounds["maximum"]:
            raise ValueError("INVALID_AUTHORED_DOMAIN")
    targets = {147: "scale_hip_height", 148: "scale_hip_depth", 152: "scale_ankle_height"}
    claims = []
    for i, name in targets.items():
        row = index[i]
        bounds = row["bounds"]
        if (
            row["name"] != name
            or row["released"]
            or not bounds
            or bounds["minimum"] != 0
            or bounds["maximum"] != 0
        ):
            raise ValueError("CLAIMED_ZERO_DOMAIN_NOT_FIXED")
        claims.append(
            dict(index=i, name=name, minimum=bounds["minimum"], maximum=bounds["maximum"])
        )
    return dict(
        audited_controls=204,
        released_controls=sum(r["released"] for r in rows),
        zero_domain_count=sum(
            bool(r["bounds"]) and r["bounds"]["minimum"] == r["bounds"]["maximum"] == 0
            for r in rows
        ),
        zero_domain_claims=claims,
    )


def height_statistics(rows):
    """Replay original variation() on the saved individual-height table schema."""
    groups = defaultdict(list)
    seen = set()
    for row in rows:
        key = tuple(row[k] for k in ("partition", "collection", "condition", "state"))
        if (
            key[0] not in {"development", "heldout"}
            or key[1] not in PATHWAYS
            or key[2] not in CONDITIONS
            or key[3] not in {"fitted", "canonical"}
        ):
            raise ValueError("UNKNOWN_HEIGHT_STRATUM")
        person = (*key, row["case"])
        if person in seen:
            raise ValueError("DUPLICATE_HEIGHT_RECORD")
        seen.add(person)
        groups[key].append(row)
    result = []
    for key, group in sorted(groups.items()):
        if len(group) < 2:
            raise ValueError("AT_LEAST_TWO_PEOPLE_PER_HEIGHT_STRATUM")
        values = variation(
            [float(r["source_extent_cm"]) for r in group],
            [float(r["native_extent_cm"]) for r in group],
        )
        result.append(
            dict(zip(("partition", "collection", "condition", "state"), key, strict=True), **values)
        )
    return result


def geometry_statistics(rows):
    """Original descriptive mean of saved per-person surface means, in cm."""
    groups = defaultdict(list)
    seen = set()
    for row in rows:
        if row["partition"] != "development" or row["condition"] not in MECHANISMS:
            continue
        key = tuple(row[k] for k in ("partition", "collection", "condition"))
        if row["collection"] not in PATHWAYS:
            raise ValueError("UNKNOWN_GEOMETRY_PATHWAY")
        person = (*key, row["case"])
        if person in seen:
            raise ValueError("DUPLICATE_GEOMETRY_RECORD")
        seen.add(person)
        groups[key].append(float(row["mean_cm"]))
    return [
        dict(zip(("partition", "collection", "condition"), key, strict=True), **describe(values))
        for key, values in sorted(groups.items())
    ]


def validate_record_linkage(heights, geometry):
    """Require the same people and source extents across the contrasted arms."""
    height_groups = defaultdict(dict)
    for row in heights:
        key = tuple(row[k] for k in ("partition", "collection", "condition", "state"))
        person = row["case"]
        if person in height_groups[key]:
            raise ValueError("DUPLICATE_HEIGHT_RECORD")
        height_groups[key][person] = float(row["source_extent_cm"])
    geometry_groups = defaultdict(set)
    for row in geometry:
        key = tuple(row[k] for k in ("partition", "collection", "condition"))
        if row["case"] in geometry_groups[key]:
            raise ValueError("DUPLICATE_GEOMETRY_RECORD")
        geometry_groups[key].add(row["case"])
    for path in PATHWAYS:
        for partition, arms in [("heldout", ("B", "C")), ("development", MECHANISMS)]:
            baseline = height_groups[(partition, path, "B", "canonical")]
            if not baseline:
                raise ValueError("PAIRED_HEIGHT_BASELINE_REQUIRED")
            for arm in arms:
                for state in ("fitted", "canonical"):
                    if height_groups[(partition, path, arm, state)] != baseline:
                        raise ValueError("PAIRED_HEIGHT_MEMBERSHIP_OR_SOURCE_MISMATCH")
                if partition == "development" and geometry_groups[(partition, path, arm)] != set(
                    baseline
                ):
                    raise ValueError("PAIRED_GEOMETRY_MEMBERSHIP_MISMATCH")


def mechanism_summary(heights, geometry):
    def select(rows, **labels):
        found = [r for r in rows if all(r.get(k) == v for k, v in labels.items())]
        if len(found) != 1:
            raise ValueError("ONE_AGGREGATE_PER_MECHANISM_STRATUM_REQUIRED")
        return found[0]

    result = []
    for condition in MECHANISMS:
        for path in PATHWAYS:
            labels = dict(partition="development", collection=path, condition=condition)
            fitted = select(heights, **labels, state="fitted")
            canonical = select(heights, **labels, state="canonical")
            surface = select(geometry, **labels)
            if not fitted["n"] == canonical["n"] == surface["n"]:
                raise ValueError("MECHANISM_DENOMINATOR_MISMATCH")
            result.append(
                dict(
                    labels,
                    people=fitted["n"],
                    fitted_to_source_sd_ratio=fitted["sd_ratio"],
                    canonical_to_source_sd_ratio=canonical["sd_ratio"],
                    fitted_height_mae_cm=fitted["mae"],
                    surface_mean_cm=surface["mean"],
                )
            )
    return result


def assemble_claims(heights, geometry, cohort, fallback, controls):
    """The same output schema for frozen public aggregates and local-record replay."""
    ranks = []
    for path in PATHWAYS:
        for condition in ("B", "C"):
            selected = [
                r
                for r in heights
                if r["partition"] == "heldout"
                and r["collection"] == path
                and r["state"] == "canonical"
                and r["condition"] == condition
            ]
            if len(selected) != 1:
                raise ValueError("HELDOUT_CANONICAL_RANK_ROW_REQUIRED")
            r = selected[0]
            ranks.append(
                {
                    k: r[k]
                    for k in ("partition", "collection", "condition", "state", "n", "spearman")
                }
            )
    return dict(
        schema_version=1,
        spearman=ranks,
        canonical_P_fallback=fallback,
        cohort_build_and_provider_categories=cohort,
        mechanism_groups=GROUPS,
        development_mechanisms=mechanism_summary(heights, geometry),
        control_domains=controls,
    )


def frozen_claims(root: Path):
    """Reproduce the display claims from participant-free released summaries."""

    def read(name):
        return json.loads((root / name).read_text("utf-8"))

    prefix = "results/aggregate/"
    heights = read(prefix + "E2-2-height-all-arms.json")
    geometry = {}
    for name in ["E2-2-group-arms", "E2-2-regularization-arms"]:
        for row in read(prefix + name + ".json"):
            if row["metric"] != "mean_cm":
                continue
            key = tuple(row[k] for k in ("partition", "collection", "condition"))
            if key in geometry and (
                geometry[key]["mean"] != row["mean"] or geometry[key]["n"] != row["n"]
            ):
                raise ValueError("CONFLICTING_FROZEN_MECHANISM_MEANS")
            geometry[key] = row
    selection = read(prefix + "NOMO-cohort-selection.json")
    cohort = dict(
        people=sum(r["people"] for r in selection),
        selection_counts=selection,
        female_source_category=sum(r["female_source_category"] for r in selection),
        male_source_category=sum(r["male_source_category"] for r in selection),
    )
    strata = read(prefix + "canonical-fallback-strata.json")
    positive = next(r for r in strata if r["fallback"] is True)
    negative = next(r for r in strata if r["fallback"] is False)
    fallback = dict(
        people=positive["total_people"],
        body_observations=sum(r["observations"] for r in strata),
        fallback_observations=positive["observations"],
        nonfallback_observations=negative["observations"],
        fallback_people=positive["people"],
        nonfallback_people=negative["people"],
        both_strata_people=positive["people"] + negative["people"] - positive["total_people"],
        incomplete_people_excluded=0,
    )
    marginal = [r for r in read(prefix + "waist-fallback-counts.json") if r["state"] == "canonical"]
    if (
        sum(r["body_fallback_count"] for r in marginal) != positive["observations"]
        or sum(r["people"] for r in marginal) != fallback["body_observations"]
    ):
        raise ValueError("FALLBACK_STRATA_AND_PATHWAY_COUNTS_DISAGREE")
    return assemble_claims(
        heights,
        list(geometry.values()),
        cohort,
        fallback,
        control_domains(read("configs/control_audit_204.json")),
    )


def compare_claims(actual, expected, tolerance=1e-12):
    """Compare scalar summaries; tolerate only last-digit arithmetic differences."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            raise ValueError("CLAIM_SCHEMA_MISMATCH")
        for key in expected:
            compare_claims(actual[key], expected[key], tolerance)
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise ValueError("CLAIM_ROW_COUNT_MISMATCH")
        for a, e in zip(actual, expected, strict=True):
            compare_claims(a, e, tolerance)
    elif isinstance(expected, (float, int)) and not isinstance(expected, bool):
        import math

        if (
            not isinstance(actual, (float, int))
            or not math.isfinite(actual)
            or abs(actual - expected) > tolerance
        ):
            raise ValueError("CLAIM_VALUE_MISMATCH")
    elif actual != expected:
        raise ValueError("CLAIM_LABEL_MISMATCH")
