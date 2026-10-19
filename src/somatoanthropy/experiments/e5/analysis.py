"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import itertools
from collections import Counter, defaultdict
from typing import Any

import numpy as np
from scipy.stats import spearmanr

from somatoanthropy.experiments.e5.core import (
    REPLICATES,
    decompose,
    grouped,
    positive,
    response,
    seed_for,
    summarize,
)


def measurement(q: Any) -> Any:
    if q.get("geometry_quality") != "VALID":
        return None
    value = q.get("engineering_value_cm")
    return value if positive(value) else None


def reconstruction(c: Any) -> Any:
    direct = c.load_source("E2", "report03/direct-records.json")
    groups: dict[Any, Any] = defaultdict(dict)
    for r in direct:
        key = (r["subject_uid"], r["collection"], r["method"], r["state"])
        assert r["site"] not in groups[key]
        groups[key][r["site"]] = r
    cohort = c.load_source("E4", "cohorts.json")
    branches = {
        (p[k]["subject_uid"], p[k]["collection"]): p[k] for p in cohort["pairs"] for k in ("a", "b")
    }
    records = []
    misses = []
    triples = []
    for (uid, path), branch in sorted(branches.items()):
        for method in ("historical", "E2_proxy_raw", "E2_proxy_tape"):
            states = {}
            for state in ("fitted", "canonical"):
                q = groups[uid, path, method, state].get("waist", {})
                h = groups[uid, path, "historical", state]["height"]
                states[state] = (h.get("mhr"), q.get("mhr"))
                source = (h.get("source"), q.get("source"))
                if "source" in states and states["source"] != source:
                    raise ValueError("SOURCE_INPUT_CHANGED_BETWEEN_STATES")
                states["source"] = source
            vals = {}
            for a, b in [("source", "fitted"), ("fitted", "canonical"), ("source", "canonical")]:
                h0, w0 = states[a]
                h1, w1 = states[b]
                meta = dict(
                    component="E5-A",
                    dataset="NOMO",
                    subject_uid=uid,
                    pathway=path,
                    method=method,
                    transition=f"{a}_to_{b}",
                    state=b,
                    body_uid=branch["body_uid"],
                    fit_uid=branch["fit_uid"],
                    source_sha256=branch["source_sha256"],
                    source_reference_dependent=True,
                    classification="FORMULA_RESPONSE_ONLY",
                    physical_calibration="UNQUALIFIED",
                    site_protocol="E2 historical adaptive/fallback"
                    if method == "historical"
                    else "E2 mapped anatomical proxy; distinct from adaptive/fallback",
                    unit="engineering_cm",
                    h0=h0,
                    w0=w0,
                    h1=h1,
                    w1=w1,
                    canonicalisation="E4 exact saved transfer checks; LBFGSB expression differences retained in body-lineage.json",
                    fallback_source=groups[uid, path, method, "fitted"]
                    .get("waist", {})
                    .get("fallback_source"),
                    fallback_mhr=groups[uid, path, method, b if b != "source" else "fitted"]
                    .get("waist", {})
                    .get("fallback_mhr"),
                )
                if positive(h0, w0, h1, w1):
                    r = dict(meta, **decompose(h0, w0, h1, w1))
                    records.append(r)
                    vals[a, b] = r["drift_pp"]
                else:
                    misses.append(
                        dict(
                            meta,
                            reason="MISSING_OR_INVALID_COMPATIBLE_HEIGHT_WAIST",
                            missing_height=not positive(h0, h1),
                            missing_waist=not positive(w0, w1),
                        )
                    )
            if len(vals) == 3:
                residual = (
                    vals["source", "canonical"]
                    - vals["source", "fitted"]
                    - vals["fitted", "canonical"]
                )
                assert abs(residual) < 1e-10
                triples.append(
                    dict(
                        subject_uid=uid,
                        pathway=path,
                        method=method,
                        decomposition_residual_pp=residual,
                    )
                )
    c.save("reconstruction.json", records)
    c.save("reconstruction-missing.json", misses)
    c.save("three-state-decomposition.json", triples)
    summary = grouped(records, ["pathway", "method", "transition"])
    cross = []
    by: dict[Any, Any] = defaultdict(dict)
    for r in records:
        by[r["subject_uid"], r["method"], r["transition"]][r["pathway"]] = r
    for (uid, method, transition), paths in by.items():
        for a, b in [("SMPL-NICP", "CAESAR-NICP"), ("SMPL-NICP", "SMPL-LBFGSB")]:
            if a in paths and b in paths:
                cross.append(
                    dict(
                        subject_uid=uid,
                        method=method,
                        transition=transition,
                        pathway=a + "_to_" + b,
                        drift_pp=paths[b]["drift_pp"] - paths[a]["drift_pp"],
                        absolute_drift_change_pp=paths[b]["absolute_pp"] - paths[a]["absolute_pp"],
                    )
                )
    c.save("pathway-contrasts.json", cross)
    c.table("E5-T3-reconstruction-drift", summary)
    c.table("E5-T3S-pathway-contrasts", grouped(cross, ["pathway", "method", "transition"]))
    wide = c.load("catalogue.json")["records"]
    saved: dict[Any, Any] = defaultdict(dict)
    for r in wide:
        if r["dataset"] == "NOMO":
            saved[r["subject_uid"], r["source_representation"], r["body_uid"]][r["pose"]] = r
    supplemental = []
    for (uid, path, body), saved_states in sorted(saved.items()):
        if set(saved_states) != {"fitted", "canonical"}:
            continue
        saved_a, saved_b = (saved_states["fitted"], saved_states["canonical"])
        assert saved_a["fit_uid"] == saved_b["fit_uid"]
        h0, w0, h1, w1 = (
            saved_a["height_cm"],
            saved_a["waists"]["P"],
            saved_b["height_cm"],
            saved_b["waists"]["P"],
        )
        if positive(h0, w0, h1, w1):
            supplemental.append(
                dict(
                    subject_uid=uid,
                    pathway=path,
                    body_uid=body,
                    fit_uid=saved_a["fit_uid"],
                    fitted_mesh_sha256=saved_a["mesh_sha256"],
                    canonical_mesh_sha256=saved_b["mesh_sha256"],
                    method="WAIST_frozen_P",
                    transition="fitted_to_canonical",
                    classification="FORMULA_RESPONSE_ONLY",
                    h0=h0,
                    w0=w0,
                    h1=h1,
                    w1=w1,
                    **decompose(h0, w0, h1, w1),
                )
            )
    c.save("saved-MHR-state-sensitivity.json", supplemental)
    c.table(
        "E5-T3S-frozen-WAIST-fitted-canonical",
        grouped(supplemental, ["pathway", "method", "transition"]),
    )
    return records


def waist(c: Any) -> Any:
    wide = {r["record_id"]: r for r in c.load("catalogue.json")["records"]}
    pairs = c.load_source("WAIST-01", "paired.json")
    cohorts = c.load_source("E4", "cohorts.json")
    branches = {
        (p[k]["subject_uid"], p[k]["collection"]): p[k]
        for p in cohorts["pairs"]
        for k in ("a", "b")
    }
    rows = []
    agreement = []
    missing = []
    for p in pairs:
        r = wide[p["record_id"]]
        assert (p["subject_uid"], p["body_uid"], p["state"]) == (
            r["subject_uid"],
            r["body_uid"],
            r["pose"],
        )
        h = r["height_cm"]
        wp = p["ours_cm"]
        wc = p["comparator_cm"]
        meta = dict(
            component="E5-B",
            subject_uid=r["subject_uid"],
            dataset=r["dataset"],
            pathway=p["pathway"],
            state=p["state"],
            record_id=r["record_id"],
            body_uid=r["body_uid"],
            mesh_sha256=r["mesh_sha256"],
            mode=p["mode"],
            comparator=p["comparator"],
            fallback=p["fallback"],
            height_cm=h,
            ours_waist_cm=wp,
            comparator_waist_cm=wc,
            classification="FORMULA_RESPONSE_ONLY",
            unit="engineering_cm",
            functional_comparability=p["functional_comparability"],
        )
        if not p["pair_eligible"] or not positive(h, wp, wc):
            missing.append(dict(meta, reason="INVALID_OR_UNMATCHED_WAIST_PAIR"))
            continue
        rows.append(
            dict(meta, drift_pp=response(h, wc, h, wp), absolute_pp=abs(response(h, wc, h, wp)))
        )
        ref = p["reference_cm"]
        branch = branches.get((r["subject_uid"], p["pathway"]))
        hs = measurement(branch["sites"]["source"]["height"]) if branch else None
        if r["dataset"] == "NOMO" and p["reference_dependent"] and positive(hs, ref):
            assert hs is not None
            dp = response(hs, ref, h, wp)
            db = response(hs, ref, h, wc)
            agreement.append(
                dict(
                    meta,
                    source_height_cm=hs,
                    source_waist_cm=ref,
                    source_functional=p["source_functional"],
                    source_reference_definition=p["reference_definition"],
                    source_reference_dependent=True,
                    source_reference_tier=p["reference_tier"],
                    ours_drift_pp=dp,
                    comparator_drift_pp=db,
                    drift_pp=abs(db) - abs(dp),
                    height_controlled_advantage_pp=abs(response(h, ref, h, wc))
                    - abs(response(h, ref, h, wp)),
                    positive_favours="P",
                    ours_absolute_pp=abs(dp),
                    comparator_absolute_pp=abs(db),
                )
            )
    c.save("waist.json", rows)
    c.save("waist-missing.json", missing)
    c.save("source-agreement.json", agreement)
    c.table(
        "E5-T5-waist-method-sensitivity",
        grouped(rows, ["dataset", "pathway", "state", "mode", "comparator"]),
    )
    c.table(
        "E5-T5S-adaptive-fallback",
        grouped(rows, ["dataset", "pathway", "state", "mode", "fallback"]),
    )
    c.table(
        "E5-T6-source-formula-agreement",
        grouped(agreement, ["pathway", "state", "mode", "comparator"]),
    )
    c.table(
        "E5-T6S-source-waist-common-height",
        grouped(
            agreement, ["pathway", "state", "mode", "comparator"], "height_controlled_advantage_pp"
        ),
    )
    primary = [
        r
        for r in agreement
        if r["mode"] == "end_to_end" and r["pathway"] in ("SMPL-NICP", "CAESAR-NICP")
    ]
    counts = Counter((r["subject_uid"] for r in primary))
    primary = [r for r in primary if counts[r["subject_uid"]] == 4]
    c.table(
        "E5-T6S-primary-person-mean",
        [
            dict(
                estimand="mean of four NICP fitted/canonical observations per complete person",
                **summarize(primary),
            )
        ],
    )
    return rows


def repeated(c: Any) -> Any:
    wide = [r for r in c.load("catalogue.json")["records"] if r["dataset"] == "DFAUST"]
    records = []
    for r in wide:
        assert r["pose"] == "canonical"
        for method in ("P", "B1", "B3_offset", "B2"):
            w = r["waists"].get(method)
            h = r["height_cm"]
            if positive(h, w):
                records.append(
                    dict(
                        subject_uid=r["subject_uid"],
                        body_uid=r["body_uid"],
                        observation_uid=r["observation_uid"],
                        method=method,
                        height_cm=h,
                        waist_cm=w,
                        formula_response_coordinate_pp=-20 * h / w,
                        coordinate_definition="-20H/W; arbitrary zero, not an absolute BF estimate",
                    )
                )
    e3 = c.load_source("E3", "measure.json")["records"]
    heights = {
        r["body_uid"]: r["result_value"]
        for r in e3
        if r["site"] == "height" and r["method"] == "B_common_raw_contour_cm"
    }
    for r in e3:
        if r["site"] != "waist" or r["method"] not in (
            "B_common_raw_contour_cm",
            "B_common_tape_envelope_cm",
            "C_fixed_F01_raw_contour_cm",
            "C_fixed_F01_tape_envelope_cm",
        ):
            continue
        if r["selection_id"].endswith("-F01"):
            continue
        w = r["result_value"]
        h = heights[r["body_uid"]]
        if r["geometry_quality"] == "VALID" and positive(h, w):
            records.append(
                dict(
                    subject_uid=r["subject_uid"],
                    body_uid=r["body_uid"],
                    observation_uid=r["observation_uid"],
                    method=r["method"] + "_F01_excluded",
                    height_cm=h,
                    waist_cm=w,
                    formula_response_coordinate_pp=-20 * h / w,
                    coordinate_definition="-20H/W; arbitrary zero; E3 atlas engineering plane, not adaptive waist",
                    selection_id=r["selection_id"],
                )
            )
    people = []
    pairs = []
    groups = defaultdict(list)
    for r in records:
        groups[r["subject_uid"], r["method"]].append(r)
    for (uid, method), rs in sorted(groups.items()):
        x = np.array([r["formula_response_coordinate_pp"] for r in rs])
        diffs = [abs(a - b) for a, b in itertools.combinations(x, 2)]
        people.append(
            dict(
                subject_uid=uid,
                method=method,
                observations=len(rs),
                sd_pp=float(np.std(x, ddof=1)) if len(x) > 1 else None,
                range_pp=float(np.ptp(x)),
                median_absolute_deviation_pp=float(np.median(abs(x - np.median(x)))),
                mean_pairwise_absolute_pp=float(np.mean(diffs)) if diffs else None,
                maximal_disagreement_pp=max(diffs) if diffs else None,
                height_range_cm=float(np.ptp([r["height_cm"] for r in rs])),
                waist_range_cm=float(np.ptp([r["waist_cm"] for r in rs])),
                absolute_formula_mean=None,
                absolute_mean_reason="No documented sex/age in frozen adapter",
                classification="FORMULA_RESPONSE_ONLY",
            )
        )
        for a, b in itertools.combinations(rs, 2):
            pairs.append(
                dict(
                    subject_uid=uid,
                    method=method,
                    body0=a["body_uid"],
                    body1=b["body_uid"],
                    drift_pp=b["formula_response_coordinate_pp"]
                    - a["formula_response_coordinate_pp"],
                )
            )
    c.save("repeated-observations.json", records)
    c.save("repeated-people.json", people)
    c.save("repeated-pairs.json", pairs)
    public = [
        dict(
            {k: v for k, v in r.items() if k != "subject_uid"},
            participant="P-"
            + __import__("hashlib").sha256(r["subject_uid"].encode()).hexdigest()[:12],
        )
        for r in people
    ]
    c.table("E5-T7-repeated-observation-people", public)
    summary = []
    for method in sorted({r["method"] for r in people}):
        rs = [r for r in people if r["method"] == method]
        for metric in (
            "sd_pp",
            "range_pp",
            "median_absolute_deviation_pp",
            "mean_pairwise_absolute_pp",
            "height_range_cm",
            "waist_range_cm",
        ):
            summary.append(dict(method=method, metric=metric, **summarize(rs, metric)))
    c.table("E5-T7S-repeated-summary", summary)
    comparisons = []
    idx = {(r["subject_uid"], r["method"]): r for r in people}
    for uid in sorted({r["subject_uid"] for r in people}):
        for method in ("B1", "B3_offset", "B2"):
            if (uid, "P") in idx and (uid, method) in idx:
                comparisons.append(
                    dict(
                        subject_uid=uid,
                        comparison=method + "_minus_P",
                        drift_pp=idx[uid, method]["sd_pp"] - idx[uid, "P"]["sd_pp"],
                    )
                )
        for functional in ("raw_contour_cm", "tape_envelope_cm"):
            own_key = "B_common_" + functional + "_F01_excluded"
            fixed_key = "C_fixed_F01_" + functional + "_F01_excluded"
            if (uid, own_key) in idx and (uid, fixed_key) in idx:
                comparisons.append(
                    dict(
                        subject_uid=uid,
                        comparison="fixed_minus_own_" + functional,
                        drift_pp=idx[uid, fixed_key]["sd_pp"] - idx[uid, own_key]["sd_pp"],
                    )
                )
    c.save("repeated-method-comparisons.json", comparisons)
    c.table("E5-T7S-method-SD-comparisons", grouped(comparisons, ["comparison"]))


def decomposition(c: Any) -> Any:
    rows = c.load("reconstruction.json") + c.load("controls.json")
    summaries = []
    groups = defaultdict(list)
    for r in rows:
        key = tuple(
            (
                r.get(k)
                for k in (
                    "component",
                    "experiment",
                    "partition",
                    "pathway",
                    "method",
                    "transition",
                    "state",
                    "comparison",
                )
            )
        )
        groups[key].append(r)
        assert abs(r["drift_pp"] - r["phi_height_pp"] - r["phi_waist_pp"]) < 1e-10
    for key, rs in sorted(groups.items(), key=lambda x: str(x[0])):
        meta = dict(
            zip(
                (
                    "component",
                    "experiment",
                    "partition",
                    "pathway",
                    "method",
                    "transition",
                    "state",
                    "comparison",
                ),
                key,
            )
        )
        for metric in (
            "height_only_pp",
            "waist_only_pp",
            "interaction_pp",
            "phi_height_pp",
            "phi_waist_pp",
            "cancelled_magnitude_pp",
        ):
            summaries.append(
                dict(
                    meta,
                    metric=metric,
                    cancellation_fraction=float(np.mean([r["cancellation"] for r in rs])),
                    **summarize(rs, metric),
                )
            )
    c.table("E5-T4-height-waist-decomposition", summaries)
    c.save("decomposition.json", rows)


def associations(c: Any) -> Any:
    recon = c.load("reconstruction.json")
    links = c.load_source("E1", "e5-geometry-measurements.json")
    lookup = defaultdict(list)
    for r in links:
        if r["site"] == "height":
            lookup[r["subject_uid"], r["collection"], r["state"], r["method"]].append(r)
    pairs = []
    for r in recon:
        if (
            r["transition"] not in ("source_to_fitted", "source_to_canonical")
            or r["method"] != "historical"
        ):
            continue
        for link in lookup[r["subject_uid"], r["pathway"], r["state"], r["method"]]:
            assert (
                link["body_uid"] == r["body_uid"]
                and link["fit_uid"] == r["fit_uid"]
                and (link["source_sha256"] == r["source_sha256"])
            )
            pairs.append(
                dict(
                    subject_uid=r["subject_uid"],
                    pathway=r["pathway"],
                    state=r["state"],
                    level=link["level"],
                    region=link["region"],
                    geometry_unit=link["geometry_unit"],
                    global_error=link["global_error"],
                    regional_error=link["regional_error"],
                    drift_pp=r["drift_pp"],
                    absolute_pp=r["absolute_pp"],
                    absolute_height_delta=abs(r["delta_height_cm"]),
                    absolute_waist_delta=abs(r["delta_waist_cm"]),
                    body_uid=r["body_uid"],
                    fit_uid=r["fit_uid"],
                    source_sha256=r["source_sha256"],
                )
            )
    c.save("geometry-formula-links.json", pairs)
    stats = []
    for keys, rs in _association_groups(pairs):
        meta = dict(zip(("pathway", "state", "level", "region", "geometry_unit"), keys))
        for field in (
            "global_error",
            "regional_error",
            "absolute_height_delta",
            "absolute_waist_delta",
        ):
            xy = [r for r in rs if r.get(field) is not None and np.isfinite(r[field])]
            if len(xy) < 4:
                continue
            assert len({r["subject_uid"] for r in xy}) == len(xy)
            x = np.array([r[field] for r in xy])
            y = np.array([r["absolute_pp"] for r in xy])
            if np.ptp(x) == 0 or np.ptp(y) == 0:
                continue
            rho = float(spearmanr(x, y).statistic)
            rng = np.random.default_rng(seed_for(*keys, field))
            draws: list[float] = []
            for ix in rng.integers(0, len(x), size=(REPLICATES, len(x))):
                if np.ptp(x[ix]) and np.ptp(y[ix]):
                    draws.append(float(spearmanr(x[ix], y[ix]).statistic))
            stats.append(
                dict(
                    meta,
                    predictor=field,
                    people=len(xy),
                    rho=rho,
                    ci95=np.quantile(draws, [0.025, 0.975]).tolist(),
                    replicates=len(draws),
                    interpretation="Exploratory association, no predictive or physiological generalisation; direct-input correlations are deterministic formula relationships",
                )
            )
    c.table("E5-T9-geometry-formula-associations", stats)
    examples = []
    for pathway in ("SMPL-NICP", "CAESAR-NICP"):
        rs = [
            r
            for r in pairs
            if r["pathway"] == pathway
            and r["state"] == "canonical"
            and (r["level"] == "historical_E4")
            and (r["region"] == "global")
        ]
        gx = np.quantile([r["global_error"] for r in rs], [0.25, 0.75])
        fy = np.quantile([r["absolute_pp"] for r in rs], [0.25, 0.75])
        for rule, candidates in (
            (
                "global <= within-path Q25; absolute BF >= Q75",
                [r for r in rs if r["global_error"] <= gx[0] and r["absolute_pp"] >= fy[1]],
            ),
            (
                "global >= within-path Q75; absolute BF <= Q25",
                [r for r in rs if r["global_error"] >= gx[1] and r["absolute_pp"] <= fy[0]],
            ),
        ):
            for r in sorted(candidates, key=lambda r: r["absolute_pp"], reverse=True)[:4]:
                examples.append(dict(r, selection_rule=rule))
    c.save("geometry-counterexamples.json", examples)
    c.table(
        "E5-T9S-geometry-counterexamples",
        [
            dict(
                participant="P-"
                + __import__("hashlib").sha256(r["subject_uid"].encode()).hexdigest()[:12],
                **{
                    k: r[k]
                    for k in (
                        "pathway",
                        "global_error",
                        "geometry_unit",
                        "absolute_pp",
                        "selection_rule",
                    )
                },
            )
            for r in examples
        ],
    )
    decisions = c.load_source("E1", "decisions.json")
    audited = []
    for d in decisions:
        text = " ".join((str(d.get(k, "")) for k in ("problem", "implemented_treatment"))).lower()
        if any((k in text for k in ("skeletal", "nine", "locked", "control restriction"))):
            cls = "Matched saved-state consequence: E5-D"
        elif any((k in text for k in ("waist", "umbilic", "63%", "clad"))):
            cls = "Matched saved-method consequence: E5-B; dependent source reference"
        elif any((k in text for k in ("canonical", "t90", "pose"))):
            cls = "Matched representation change: E5-A/C; combined effects, no isolated cause"
        elif any(
            (k in text for k in ("height", "vertical", "head", "feet", "floor", "torso", "source"))
        ):
            cls = "Association or input-definition consequence only; isolated BF counterfactual unavailable"
        else:
            cls = "Implementation rationale only; isolated BF effect not evaluable"
        audited.append(
            dict(
                decision_id=d["decision_id"],
                problem=d["problem"],
                e1_evidence_class=d["evidence_class"],
                e5_evidence_class=cls,
                limitation=d["confounders_and_limitations"],
            )
        )
    assert len(audited) == 24
    c.table("E5-T12S-decision-audit", audited)


def _association_groups(rows: Any) -> Any:
    groups = defaultdict(list)
    for r in rows:
        groups[
            tuple((r[k] for k in ("pathway", "state", "level", "region", "geometry_unit")))
        ].append(r)
    return sorted(groups.items(), key=lambda x: str(x[0]))
