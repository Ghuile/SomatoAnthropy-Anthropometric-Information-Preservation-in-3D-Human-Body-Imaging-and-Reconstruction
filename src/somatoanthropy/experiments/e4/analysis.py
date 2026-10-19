"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from somatoanthropy.data.phase01_nomo import atomic_bytes, atomic_json
from somatoanthropy.experiments.e4.core import (
    SITES,
    bootstrap,
    compatible,
    describe,
    effect,
    measurement,
    paired_values,
    seed_for,
    unique_people,
)


def write_csv(path: Path, rows: list[dict]) -> None:
    columns = list(dict.fromkeys((k for row in rows for k in row)))
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(
        (
            {
                k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v
                for k, v in r.items()
            }
            for r in rows
        )
    )
    atomic_bytes(path, stream.getvalue().encode("utf-8"))


def comparison_rows(snapshot: dict) -> tuple[list, list, list]:
    paired, values, contrasts = ([], [], [])
    for p in snapshot["pairs"]:
        for site in SITES:
            for branch in ("a", "b"):
                for state, sites in p[branch]["sites"].items():
                    q = sites[site]
                    values.append(
                        dict(
                            cohort=p["cohort"],
                            subject_uid=p["subject_uid"],
                            branch=branch,
                            collection=p[branch]["collection"],
                            body_uid=p[branch]["body_uid"],
                            state=state,
                            site=site,
                            value=measurement(q),
                            strict_value=measurement(q, strict=True),
                            geometry_quality=q.get("geometry_quality"),
                            quality_state=q.get("quality_state", q.get("historical_quality_state")),
                            reason=q.get("reason"),
                            fallback_applied=q.get("fallback_applied", False),
                            protocol=q.get("protocol"),
                            pose=q.get("pose"),
                            quantity=q.get("quantity"),
                            unit="engineering_cm",
                            details_path=q.get("details_path"),
                            definition=q.get("definition"),
                        )
                    )
            for state in ("fitted", "canonical"):
                for rule in ("proxy_inclusive", "ambiguity_excluded"):
                    strict = rule == "ambiguity_excluded"
                    qs = [
                        p[k]["sites"][s][site]
                        for k, s in (("a", "source"), ("b", "source"), ("a", state), ("b", state))
                    ]
                    nums = [measurement(q, strict=strict) for q in qs]
                    source_pose = "RELEASED_SOURCE_AND_SAVED_FITTED_MHR"
                    target_pose = (
                        source_pose
                        if state == "fitted"
                        else "T90_REFERENCE_ARTICULATION_TRANSFER_CANDIDATE"
                    )
                    available = (
                        all((v is not None for v in nums))
                        and compatible(qs[:2], source_pose)
                        and compatible(qs[2:], target_pose)
                    )
                    row = dict(
                        cohort=p["cohort"],
                        subject_uid=p["subject_uid"],
                        site=site,
                        state=state,
                        rule=rule,
                        available=available,
                        scope="released/fitted engineering"
                        if state == "fitted"
                        else "released-to-T90 exploratory; pose confounded",
                        sa=nums[0],
                        sb=nums[1],
                        ma=nums[2],
                        mb=nums[3],
                        unavailable_reason=" | ".join(
                            sorted(
                                {q.get("reason", "missing") for q, v in zip(qs, nums) if v is None}
                            )
                        ),
                    )
                    if available:
                        row.update(paired_values(*nums))
                    paired.append(row)
            a, b = (p["a"]["sites"], p["b"]["sites"])
            for name, left, right in (
                ("SMPL_SOURCE_TO_MHR", a["source"][site], a["fitted"][site]),
                ("CAESAR_SOURCE_TO_MHR", b["source"][site], b["fitted"][site]),
                ("SOURCE_A_MINUS_B", b["source"][site], a["source"][site]),
                ("FITTED_MHR_A_MINUS_B", b["fitted"][site], a["fitted"][site]),
                ("T90_MHR_A_MINUS_B", b["canonical"][site], a["canonical"][site]),
            ):
                x, y = (measurement(left), measurement(right))
                pose = (
                    "T90_REFERENCE_ARTICULATION_TRANSFER_CANDIDATE"
                    if name == "T90_MHR_A_MINUS_B"
                    else "RELEASED_SOURCE_AND_SAVED_FITTED_MHR"
                )
                good = x is not None and y is not None and compatible([left, right], pose)
                contrasts.append(
                    dict(
                        cohort=p["cohort"],
                        subject_uid=p["subject_uid"],
                        site=site,
                        contrast=name,
                        available=good,
                        value=y - x if good else None,
                    )
                )
            base = paired[-4]
            contrasts.append(
                dict(
                    cohort=p["cohort"],
                    subject_uid=p["subject_uid"],
                    site=site,
                    contrast="CHANGE_IN_ABSOLUTE_CROSS_PATH_DISAGREEMENT",
                    available=base["available"],
                    value=base.get("delta_absolute"),
                )
            )
    return (paired, values, contrasts)


def summarise(snapshot: dict, private: Path, public: Path, *, seed: int, replicates: int) -> dict:
    paired, values, contrasts = comparison_rows(snapshot)
    stats, draws = ([], {})
    groups = defaultdict(list)
    for r in paired:
        groups[r["cohort"], r["state"], r["rule"], r["site"]].append(r)
    for (cohort, state, rule, site), rows in sorted(groups.items()):
        good = unique_people([r for r in rows if r["available"]])
        for metric in (
            "source_signed",
            "source_absolute",
            "mhr_signed",
            "mhr_absolute",
            "delta_signed",
            "delta_absolute",
            "path_a",
            "path_b",
        ):
            x = [r[metric] for r in good]
            boot = bootstrap(
                x, seed=seed_for(seed, cohort, state, rule, site, metric), replicates=replicates
            )
            key = "/".join((cohort, state, rule, site, metric))
            draws[key] = boot.pop("draws")
            stats.append(
                dict(
                    cohort=cohort,
                    state=state,
                    rule=rule,
                    site=site,
                    metric=metric,
                    denominator=len(rows),
                    **describe(x),
                    **boot,
                    **effect(x),
                    unit="engineering_cm",
                    inferential_scope="case_only"
                    if site == "chest" and len(x) < 2
                    else "conditional_convenience_cohort",
                    primary_family=site in SITES[:4]
                    and state == "fitted"
                    and (rule == "proxy_inclusive"),
                )
            )
    contrast_stats = []
    groups = defaultdict(list)
    for r in contrasts:
        groups[r["cohort"], r["contrast"], r["site"]].append(r)
    for (cohort, contrast, site), rows in sorted(groups.items()):
        good = unique_people([r for r in rows if r["available"]])
        x = [r["value"] for r in good]
        boot = bootstrap(x, seed=seed_for(seed, cohort, contrast, site), replicates=replicates)
        draws["contrast/" + "/".join((cohort, contrast, site))] = boot.pop("draws")
        contrast_stats.append(
            dict(
                cohort=cohort,
                contrast=contrast,
                site=site,
                denominator=len(rows),
                **describe(x),
                **boot,
            )
        )
    groups = defaultdict(list)
    for r in values:
        groups[r["cohort"], r["collection"], r["branch"], r["state"], r["site"]].append(r)
    missing = []
    for (cohort, collection, branch, state, site), rows in sorted(groups.items()):
        missing.append(
            dict(
                cohort=cohort,
                collection=collection,
                branch=branch,
                state=state,
                site=site,
                denominator=len(rows),
                available=sum((r["value"] is not None for r in rows)),
                ambiguity_excluded_available=sum((r["strict_value"] is not None for r in rows)),
                reasons=dict(Counter((r["reason"] for r in rows if r["value"] is None))),
                validity_states=dict(
                    Counter(
                        (str(r["geometry_quality"]) + "/" + str(r["quality_state"]) for r in rows)
                    )
                ),
                pose_states=dict(Counter((r["pose"] for r in rows))),
            )
        )
    e0_check = []
    for previous in snapshot["readiness"]["common_subset"]:
        matches = {
            r["metric"]: r
            for r in stats
            if r["cohort"] == "primary"
            and r["state"] == "fitted"
            and (r["rule"] == "proxy_inclusive")
            and (r["site"] == previous["site"])
        }
        now = matches["delta_absolute"]
        delta = None if now["mean"] is None else now["mean"] - previous["mean_change_cm"]
        check = dict(
            site=previous["site"],
            e0_n=previous["paired_count"],
            e4_n=now["n"],
            mean_difference_from_e0=delta,
            matched=now["n"] == previous["paired_count"] and abs(delta or 0) < 1e-09,
        )
        e0_check.append(check)
        if not check["matched"]:
            raise ValueError("E0_READINESS_DISAGREEMENT_REQUIRES_INVESTIGATION: " + str(check))
    inventory = []
    for cohort, n, intersection in (
        ("primary", snapshot["primary_n"], snapshot["source_intersection_primary"]),
        (
            "complementary",
            snapshot["complementary_n"],
            snapshot["source_intersection_complementary"],
        ),
    ):
        ps = [p for p in snapshot["pairs"] if p["cohort"] == cohort]
        inventory.append(
            dict(
                cohort=cohort,
                source_intersection=intersection,
                paired_candidates=n,
                four_geometries=n,
                fitted_and_canonical_meshes_per_person=4,
                source_meshes_per_person=2,
                repeated_candidates_are_people=False,
                full_t90_transfer_pairs=sum(
                    (
                        p["a"]["t90_transfer_verified"] and p["b"]["t90_transfer_verified"]
                        for p in ps
                    )
                ),
                pinned_articulation_pairs=sum(
                    (
                        p["a"]["transfer_checks"]["pinned_articulation"]
                        and p["b"]["transfer_checks"]["pinned_articulation"]
                        for p in ps
                    )
                ),
            )
        )
    result = dict(
        inventory=inventory,
        statistics=stats,
        contrast_statistics=contrast_stats,
        missingness=missing,
        e0_verification=e0_check,
        overlap_n=snapshot["overlap_n"],
        unique_people=snapshot["unique_people"],
        bootstrap=dict(
            seed=seed,
            replicates=replicates,
            method="participant-paired percentile",
            primary_family="four sites; Bonferroni 98.75% mean intervals; exploratory intervals unadjusted",
            selection_inference="conditional on engineering-exposed convenience cohort; not population probability sample",
        ),
    )
    for name, rows in (
        ("paired-records", paired),
        ("measurement-records", values),
        ("six-contrasts", contrasts),
    ):
        atomic_json(private / (name + ".json"), rows)
        write_csv(private / (name + ".csv"), rows)
    atomic_json(private / "bootstrap-draws.json", draws)
    atomic_json(private / "analysis.json", result)
    atomic_json(public / "summary.json", result)
    for name, rows in (
        ("E4-T1-inventory", inventory),
        (
            "E4-T3-disagreement",
            [
                r
                for r in stats
                if r["state"] == "fitted"
                and r["rule"] == "proxy_inclusive"
                and (r["cohort"] == "primary")
                and (
                    r["metric"]
                    in ("source_signed", "source_absolute", "mhr_signed", "mhr_absolute")
                )
            ],
        ),
        (
            "E4-T4-change",
            [
                r
                for r in stats
                if r["state"] == "fitted"
                and r["rule"] == "proxy_inclusive"
                and (r["cohort"] == "primary")
                and r["metric"].startswith("delta_")
            ],
        ),
        ("E4-T5-complementary", [r for r in contrast_stats if r["cohort"] == "complementary"]),
        ("E4-T6-validity", missing),
        ("sensitivity-statistics", stats),
        ("six-contrast-statistics", contrast_stats),
    ):
        write_csv(public / (name + ".csv"), rows)
    return result


def geometry_analysis(
    geometry: list, paired: list, public: Path, private: Path, seed: int, replicates: int
) -> dict:
    groups = defaultdict(list)
    per_subject = {}
    for r in geometry:
        for contrast in r["results"]:
            groups[r["cohort"], contrast["contrast"]].append(contrast["metric"])
        per_subject[r["cohort"], r["subject_uid"]] = {
            r["contrast"]: r["metric"] for r in r["results"]
        }
    summary = []
    for (cohort, contrast), rows in sorted(groups.items()):
        for metric in ("symmetric_mean", "median", "p95", "rms"):
            x = [r[metric] for r in rows]
            summary.append(
                dict(
                    cohort=cohort,
                    contrast=contrast,
                    metric=metric,
                    **describe(x),
                    unit="engineering_metres",
                    samples_per_direction=sorted({r["samples_per_direction"] for r in rows}),
                    lod=sorted({r.get("lod", 0) for r in rows}),
                )
            )
    associations = []
    for cohort in ("primary", "complementary"):
        for site in SITES[:5]:
            rows = [
                r
                for r in paired
                if r["cohort"] == cohort
                and r["site"] == site
                and (r["state"] == "fitted")
                and (r["rule"] == "proxy_inclusive")
                and r["available"]
            ]
            for predictor in (
                "fit_surface_mean",
                "source_cross_path",
                "canonical_cross_path",
                "body_size",
                "source_disagreement",
            ):
                x, y, uids = ([], [], [])
                for r in unique_people(rows):
                    g = per_subject[r["cohort"], r["subject_uid"]]
                    if predictor == "fit_surface_mean":
                        v = (
                            g["source_to_mhr_a"]["symmetric_mean"]
                            + g["source_to_mhr_b"]["symmetric_mean"]
                        ) / 2
                    elif predictor in ("source_cross_path", "canonical_cross_path"):
                        v = g[predictor]["symmetric_mean"]
                    elif predictor == "body_size":
                        v = (r["sa"] + r["sb"]) / 2
                    else:
                        v = r["source_absolute"]
                    x.append(v)
                    y.append(r["delta_absolute"])
                    uids.append(r["subject_uid"])
                rho = None
                ci = None
                if len(x) >= 4 and np.ptp(x) > 0 and (np.ptp(y) > 0):
                    rho = float(spearmanr(x, y).statistic)
                    rng = np.random.default_rng(seed_for(seed, cohort, site, predictor))
                    a, b = (np.asarray(x), np.asarray(y))
                    draws = []
                    for ids in rng.integers(0, len(x), size=(replicates, len(x))):
                        if np.ptp(a[ids]) > 0 and np.ptp(b[ids]) > 0:
                            draws.append(float(spearmanr(a[ids], b[ids]).statistic))
                    ci = np.quantile(draws, [0.025, 0.975]).tolist() if draws else None
                associations.append(
                    dict(
                        cohort=cohort,
                        site=site,
                        predictor=predictor,
                        outcome="delta_absolute",
                        n=len(x),
                        rho=rho,
                        ci95=ci,
                        interpretation="exploratory unadjusted association; no causal attribution",
                    )
                )
    result = dict(summary=summary, associations=associations)
    write_csv(public / "E4-T2-geometry.csv", summary)
    write_csv(public / "geometry-associations.csv", associations)
    atomic_json(private / "geometry-analysis.json", result)
    return result
