"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import numpy as np

from somatoanthropy.experiments.e2_1.analysis import (
    anthropometric_rows,
    paired_summary,
    ratio_effect,
)
from somatoanthropy.experiments.e4.core import describe, seed_for


def anthro(recs):
    return [
        v
        for r in recs
        if r["status"] == "EVALUATED"
        for v in anthropometric_rows(
            dict(
                subject_uid=r["subject_uid"],
                collection=r["collection"],
                partition=r["partition"],
                source_historical=r["source_historical"],
                source_proxy=r["source_proxy"],
                arms={r["condition"]: r},
            )
        )
    ]


def grouped_anthropometry(aa, seed):
    out = []
    groups = sorted(
        {
            (r["partition"], r["collection"], r["arm"], r["state"], r["site"], r["method"])
            for r in aa
        }
    )
    for key in groups:
        rr = [
            r
            for r in aa
            if (r["partition"], r["collection"], r["arm"], r["state"], r["site"], r["method"])
            == key
        ]
        vals = [r["error"] for r in rr if r["error"] is not None]
        out.append(
            dict(
                zip(("partition", "collection", "condition", "state", "site", "method"), key),
                **describe(vals),
                eligible=len(rr),
                missing=len(rr) - len(vals),
                invalid_source=sum((not r["source_valid"] for r in rr)),
                invalid_target=sum((not r["target_valid"] for r in rr)),
                source_fallback_count=sum((r["fallback_applied"] for r in rr)),
                median_absolute=float(np.median(np.abs(vals))) if vals else None,
                p95_absolute=float(np.quantile(np.abs(vals), 0.95)) if vals else None,
            )
        )
    return out


def paired_effects(recs, aa, config, partition):
    out = []
    conditions = sorted({r["condition"] for r in recs if r["condition"] != "historical"})
    comparisons = [
        (condition, "B")
        for condition in conditions
        if condition not in ("B",) and (not condition.startswith(("S1-", "I1-")))
    ]
    comparisons += (
        [("D", "C")]
        if partition == "heldout"
        else [("noG1", "C"), ("noG2", "C"), ("R025", "C"), ("R4", "C")]
    )
    if partition == "heldout":
        comparisons += [("S1-C", "S1-B"), ("S1-D", "S1-C"), ("S1-D", "S1-B")]
    else:
        comparisons += [("S1-C", "S1-B"), ("I1-C", "I1-B")]
    for c, b in comparisons:
        for collection in sorted({r["collection"] for r in recs}):
            bb = {
                r["subject_uid"]: r
                for r in recs
                if r["collection"] == collection
                and r["condition"] == b
                and (r["status"] == "EVALUATED")
            }
            cc = {
                r["subject_uid"]: r
                for r in recs
                if r["collection"] == collection
                and r["condition"] == c
                and (r["status"] == "EVALUATED")
            }
            people = sorted(set(bb) & set(cc))
            base = dict(partition=partition, collection=collection, contrast=c + "-" + b)
            pairs = [(bb[u], cc[u]) for u in people]
            for metric, fn in (
                ("surface_mean_cm", lambda r: r["geometry"]["mean"] * 100),
                ("surface_median_cm", lambda r: r["geometry"]["median"] * 100),
                ("surface_rms_cm", lambda r: r["geometry"]["rms"] * 100),
                ("surface_p95_cm", lambda r: r["geometry"]["p95"] * 100),
                (
                    "fitted_height_absolute_error_cm",
                    lambda r: abs(
                        r["fitted"]["height"]["vertical_extent_cm"] - r["source_height_cm"]
                    ),
                ),
                (
                    "canonical_height_absolute_error_cm",
                    lambda r: abs(
                        r["canonical"]["height"]["vertical_extent_cm"] - r["source_height_cm"]
                    ),
                ),
                ("any_bound_fraction", lambda r: float(bool(r["bound_hits"]))),
            ):
                out.append(
                    dict(
                        base,
                        metric=metric,
                        **paired_summary(
                            [fn(y) - fn(x) for x, y in pairs],
                            seed_for(config["seed"], partition, collection, c, b, metric),
                        ),
                    )
                )
            if len(pairs) >= 2:
                out.append(
                    dict(
                        base,
                        metric="canonical_sd_ratio",
                        **ratio_effect(
                            [x["source_height_cm"] for x, y in pairs],
                            [x["canonical"]["height"]["vertical_extent_cm"] for x, y in pairs],
                            [y["canonical"]["height"]["vertical_extent_cm"] for x, y in pairs],
                            seed_for(config["seed"], partition, collection, c, b),
                        ),
                    )
                )
            for region in (
                "torso",
                "pelvis",
                "upper_leg",
                "lower_leg",
                "arms",
                "head_neck",
                "feet",
                "hands",
            ):
                vals = [
                    (
                        y["geometry"]["regions"][region]["mean"]
                        - x["geometry"]["regions"][region]["mean"]
                    )
                    * 100
                    for x, y in pairs
                    if all((region in t["geometry"]["regions"] for t in (x, y)))
                ]
                out.append(
                    dict(
                        base,
                        metric="region_" + region + "_cm",
                        **paired_summary(
                            vals, seed_for(config["seed"], partition, collection, c, b, region)
                        ),
                    )
                )
            for site in ("waist", "abdomen", "hip", "neck", "chest"):
                for method in (
                    "fixed_historical_source_plane",
                    "E2_midpoint_proxy" if site == "waist" else "E2_surface_proxy",
                ):
                    eligible = [
                        r
                        for r in aa
                        if r["partition"] == partition
                        and r["collection"] == collection
                        and (r["site"] == site)
                        and (r["method"] == method)
                        and (r["state"] == "fitted")
                        and (r["error"] is not None)
                    ]
                    eb = {r["subject_uid"]: r["error"] for r in eligible if r["arm"] == b}
                    ec = {r["subject_uid"]: r["error"] for r in eligible if r["arm"] == c}
                    vals = [abs(ec[u]) - abs(eb[u]) for u in sorted(set(eb) & set(ec))]
                    out.append(
                        dict(
                            base,
                            metric="anthropometric_absolute_error_cm",
                            site=site,
                            method=method,
                            **paired_summary(
                                vals,
                                seed_for(config["seed"], partition, collection, c, b, site, method),
                            ),
                        )
                    )
    return out
