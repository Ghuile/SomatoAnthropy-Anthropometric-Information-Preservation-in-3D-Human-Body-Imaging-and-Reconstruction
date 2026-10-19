"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Any

import numpy as np

from somatoanthropy.experiments.e5.delivery import anon
from somatoanthropy.experiments.e5s2.core import (
    HEIGHTS,
    METHODS,
    MODES,
    PATHS,
    coordinate,
    indices,
    pareto,
    rank,
    repeated_person,
    stats,
    valid,
)
from somatoanthropy.workflow import RecordStore as Context


def groups(rows: Any, fields: Any) -> Any:
    result = defaultdict(list)
    for r in rows:
        result[tuple((r[k] for k in fields))].append(r)
    return sorted(result.items())


def cohort(c: Context) -> Any:
    heights = {r["subject_uid"]: r for r in c.load("height-qualification.json")}
    old = c.src("E5-S1", "cohort.json")
    catalogue = {r["record_id"]: r for r in c.src("E5", "catalogue.json")["records"]}
    measurements = {r["record_id"]: r for r in c.src("WAIST-01", "measurements.json")}
    base, rows, missing = ([], [], [])
    for r in old:
        h = heights[r["subject_uid"]]
        original = catalogue[r["record_id"]]
        assert r["Hb"] == original["height_cm"]
        base.append(
            dict(
                r,
                original_model_hashes=original["original_model_hashes"],
                sex_status="not assigned; source category retained only in frozen catalogue",
                age_status="unqualified",
                fitting_version=original["model_fitting_version"],
            )
        )
        for mode in MODES:
            waists = dict(r["modes"][mode]["waists"])
            if mode == "end_to_end":
                waists["B2"] = original["waists"].get("B2")
            else:
                section = measurements[r["record_id"]]["sections"]["B2"]
                waists["B2"] = (
                    section.get("raw_contour_cm" if mode == "site_raw" else "tape_envelope_cm")
                    if section["geometry_quality"] == "VALID"
                    else None
                )
            ws = r["modes"][mode]["Ws"]
            sourceq = coordinate(r["Hs"], ws) if valid(r["Hs"], ws) else None
            for method, w in waists.items():
                for hp in HEIGHTS:
                    height_value = (
                        r["Hb"]
                        if hp == "H1"
                        else r["Hs"]
                        if hp == "H2"
                        else h["strict_anchor_cm"]
                        if hp == "H3_strict"
                        else h["anchors"][hp]
                    )
                    if not valid(height_value, w):
                        missing.append(
                            dict(
                                subject_uid=r["subject_uid"],
                                record_id=r["record_id"],
                                mode=mode,
                                method=method,
                                height_policy=hp,
                                reason="HEIGHT_ANCHOR_INELIGIBLE"
                                if height_value is None
                                else "FROZEN_WAIST_UNAVAILABLE",
                            )
                        )
                        continue
                    rows.append(
                        dict(
                            subject_uid=r["subject_uid"],
                            record_id=r["record_id"],
                            pathway=r["pathway"],
                            state=r["state"],
                            mode=mode,
                            method=method,
                            height_policy=hp,
                            H=height_value,
                            W=w,
                            q=coordinate(height_value, w),
                            source_q=sourceq,
                            source_height=r["Hs"],
                            source_waist=ws,
                            source_reference_dependent=True,
                            source_reference_type="R3 MHR-mapped released-source waist proxy",
                            absolute_bf_estimate=False,
                            physical_stature_qualified=False,
                            source_height_physical=False,
                        )
                    )
    assert len(base) == 600 and len({r["subject_uid"] for r in base}) == 150
    c.save("cohort.json", base)
    c.save("responses.json", rows)
    c.save("missing.json", missing)
    coverage = []
    for mode in MODES:
        for method in METHODS:
            for hp in HEIGHTS:
                rr = [
                    r
                    for r in rows
                    if (r["mode"], r["method"], r["height_policy"]) == (mode, method, hp)
                ]
                complete = [rs for _, rs in groups(rr, ["subject_uid"]) if len(rs) == 4]
                reference = [rs for rs in complete if all((r["source_q"] is not None for r in rs))]
                coverage.append(
                    dict(
                        mode=mode,
                        method=method,
                        height_policy=hp,
                        selected_people=150,
                        selected_body_observations=600,
                        valid_body_observations=len(rr),
                        complete_four_body_people=len(complete),
                        complete_source_reference_people=len(reference),
                        invalid_or_ineligible_body_observations=600 - len(rr),
                        no_imputation=True,
                    )
                )
    c.table("S2-T9-coverage-failures", coverage)
    return dict(identities=150, bodies=600, responses=len(rows), missing_policy_inputs=len(missing))


def consistency(c: Context) -> Any:
    rows = c.load("responses.json")
    cross, fitted = ([], [])
    for (mode, method, hp, uid), rs in groups(
        rows, ["mode", "method", "height_policy", "subject_uid"]
    ):
        cells = {(r["pathway"], r["state"]): r for r in rs}
        if all(((p, "canonical") in cells for p in PATHS)):
            a, b = [cells[p, "canonical"] for p in PATHS]
            diff = a["q"] - b["q"]
            cross.append(
                dict(
                    mode=mode,
                    method=method,
                    height_policy=hp,
                    subject_uid=uid,
                    signed_pp=diff,
                    absolute_pp=abs(diff),
                    mean_q=(a["q"] + b["q"]) / 2,
                    smpl_q=a["q"],
                    caesar_q=b["q"],
                    source_mean_q=(a["source_q"] + b["source_q"]) / 2
                    if a["source_q"] is not None and b["source_q"] is not None
                    else None,
                )
            )
        for p in PATHS:
            if (p, "fitted") in cells and (p, "canonical") in cells:
                d = cells[p, "canonical"]["q"] - cells[p, "fitted"]["q"]
                fitted.append(
                    dict(
                        mode=mode,
                        method=method,
                        height_policy=hp,
                        subject_uid=uid,
                        pathway=p,
                        signed_pp=d,
                        absolute_pp=abs(d),
                    )
                )
    c.save("canonical-people.json", cross)
    c.save("fitted-canonical-people.json", fitted)
    table = []
    for (mode, m, hp), rr in groups(cross, ["mode", "method", "height_policy"]):
        s = stats([r["absolute_pp"] for r in rr])
        bias = stats([r["signed_pp"] for r in rr])
        table.append(
            dict(
                mode=mode,
                method=m,
                height_policy=hp,
                body_observations=2 * len(rr),
                **s,
                signed_bias_pp=bias["mean"],
                signed_bias_ci95=bias["mean_ci95"],
            )
        )
    c.table("S2-T4-canonical-cross-path", table)
    c.table(
        "S2-T5-fitted-canonical",
        [
            dict(
                mode=mode,
                method=m,
                height_policy=hp,
                pathway=p,
                body_observations=2 * len(rr),
                **stats([r["absolute_pp"] for r in rr]),
                signed_change_pp=float(np.mean([r["signed_pp"] for r in rr])),
            )
            for (mode, m, hp, p), rr in groups(
                fitted, ["mode", "method", "height_policy", "pathway"]
            )
        ],
    )
    examples = []
    for (mode, m, hp), rr in groups(cross, ["mode", "method", "height_policy"]):
        for r in sorted(rr, key=lambda x: (-x["absolute_pp"], x["subject_uid"]))[:3]:
            examples.append(
                dict(
                    participant=anon(r["subject_uid"]),
                    **{k: v for k, v in r.items() if k != "subject_uid"},
                )
            )
    c.table("canonical-large-disagreement-examples", examples)
    return dict(canonical_participant_endpoints=len(cross), fitted_canonical_endpoints=len(fitted))


def repeated(c: Context) -> Any:
    old = c.src("E5", "repeated-observations.json")
    people, pairs, observations = ([], [], [])
    for (uid, m), rs in groups(
        [r for r in old if r["method"] in METHODS], ["subject_uid", "method"]
    ):
        rs = sorted(rs, key=lambda r: r["observation_uid"])
        median_h = float(np.median([r["height_cm"] for r in rs]))
        for hp in ("H1", "observation_median_counterfactual"):
            vals = [
                dict(
                    r,
                    q=coordinate(r["height_cm"] if hp == "H1" else median_h, r["waist_cm"]),
                    height_policy=hp,
                )
                for r in rs
            ]
            observations.extend(vals)
            people.append(
                dict(subject_uid=uid, method=m, height_policy=hp, **repeated_person(vals))
            )
            for a, b in combinations(vals, 2):
                dq = b["q"] - a["q"]
                waist = coordinate(
                    a["height_cm"] if hp == "H1" else median_h, b["waist_cm"]
                ) - coordinate(a["height_cm"] if hp == "H1" else median_h, a["waist_cm"])
                height_part = dq - waist
                pairs.append(
                    dict(
                        subject_uid=uid,
                        method=m,
                        height_policy=hp,
                        observation_a=a["observation_uid"],
                        observation_b=b["observation_uid"],
                        signed_pp=dq,
                        absolute_pp=abs(dq),
                        waist_first_pp=waist,
                        height_second_pp=height_part,
                        cancellation_pp=abs(waist) + abs(height_part) - abs(dq),
                    )
                )
    c.save("repeated-people.json", people)
    c.save("repeated-pairs.json", pairs)
    c.save("repeated-observations.json", observations)
    summaries = []
    for (m, hp), rs in groups(people, ["method", "height_policy"]):
        for metric in ("sd_pp", "range_pp", "mad_pp", "mean_pairwise_absolute_pp"):
            summaries.append(
                dict(
                    method=m,
                    height_policy=hp,
                    metric=metric,
                    body_observations=60,
                    selected_people=10,
                    selected_observations=60,
                    valid_observations=60,
                    failure_rate=0.0,
                    source_height_anchor_available=False,
                    **stats([r[metric] for r in rs]),
                )
            )
    c.table("S2-T6-repeated-consistency", summaries)
    c.table(
        "repeated-participant-outcomes",
        [
            dict(
                participant=anon(r["subject_uid"]),
                **{k: v for k, v in r.items() if k != "subject_uid"},
            )
            for r in people
        ],
    )
    c.table("repeated-method-contrasts", contrasts(people, ["height_policy"], "sd_pp"))
    c.table(
        "repeated-contribution-summary",
        [
            dict(
                method=m,
                height_policy=hp,
                waist_first_mean_absolute_pp=float(np.mean([abs(r["waist_first_pp"]) for r in rs])),
                height_second_mean_absolute_pp=float(
                    np.mean([abs(r["height_second_pp"]) for r in rs])
                ),
                mean_cancellation_pp=float(np.mean([r["cancellation_pp"] for r in rs])),
                people=10,
                pairs=150,
                interpretation="15 dependent pairs/person; descriptive ordered decomposition; intervals use people only",
            )
            for (m, hp), rs in groups(pairs, ["method", "height_policy"])
        ],
    )
    return dict(people=10, observations=60, no_independent_height_anchor=True)


def diversity(c: Context) -> Any:
    table = []
    for (mode, m, hp), rr in groups(
        c.load("canonical-people.json"), ["mode", "method", "height_policy"]
    ):
        for subset in ("all_available", "source_matched"):
            rs = (
                rr
                if subset == "all_available"
                else [r for r in rr if r["source_mean_q"] is not None]
            )
            x = np.array([r["mean_q"] for r in rs])
            s = stats(x)
            source = (
                np.array([r["source_mean_q"] for r in rs]) if subset == "source_matched" else None
            )
            ratio = float(x.std(ddof=1) / source.std(ddof=1)) if source is not None else None
            ratio_ci = (
                np.quantile(
                    x[indices(len(x))].std(1, ddof=1) / source[indices(len(x))].std(1, ddof=1),
                    [0.025, 0.975],
                ).tolist()
                if source is not None
                else None
            )
            table.append(
                dict(
                    mode=mode,
                    method=m,
                    height_policy=hp,
                    cohort=subset,
                    body_observations=2 * len(rs),
                    **s,
                    iqr=float(np.quantile(x, 0.75) - np.quantile(x, 0.25)),
                    p5_p95_range=float(np.quantile(x, 0.95) - np.quantile(x, 0.05)),
                    cross_path_spearman=rank(
                        [r["smpl_q"] for r in rs], [r["caesar_q"] for r in rs]
                    ),
                    source_sd=float(source.std(ddof=1)) if source is not None else None,
                    sd_ratio=ratio,
                    sd_ratio_ci95=ratio_ci,
                    source_spearman=rank(x, source) if source is not None else None,
                    mean_cross_path_absolute_pp=float(np.mean([r["absolute_pp"] for r in rs])),
                )
            )
    c.table("S2-T7-coordinate-diversity", table)
    contrasts_out = []
    for (mode,), rr in groups(c.load("canonical-people.json"), ["mode"]):
        bypolicy = {}
        for (m, hp), rs in groups(rr, ["method", "height_policy"]):
            bypolicy[m, hp] = {r["subject_uid"]: r["mean_q"] for r in rs}
        for a, b in combinations(sorted(bypolicy), 2):
            if a[0] != b[0] and a[1] != b[1]:
                continue
            uids = sorted(bypolicy[a].keys() & bypolicy[b].keys())
            x, y = (np.array([bypolicy[k][u] for u in uids]) for k in (a, b))
            ix = indices(len(uids))
            contrasts_out.append(
                dict(
                    mode=mode,
                    first="/".join(a),
                    second="/".join(b),
                    people=len(uids),
                    sd_first_minus_second_pp=float(x.std(ddof=1) - y.std(ddof=1)),
                    sd_difference_ci95=np.quantile(
                        x[ix].std(1, ddof=1) - y[ix].std(1, ddof=1), [0.025, 0.975]
                    ).tolist(),
                    participant_rank_agreement=rank(x, y),
                )
            )
    c.table("diversity-paired-contrasts", contrasts_out)
    return dict(diversity_summaries=len(table), paired_sd_contrasts=len(contrasts_out))


def reference(c: Context) -> Any:
    people = []
    for (mode, m, hp, uid), rs in groups(
        c.load("responses.json"), ["mode", "method", "height_policy", "subject_uid"]
    ):
        if len(rs) != 4 or not all((r["source_q"] is not None for r in rs)):
            continue
        strata = {
            "all": rs,
            "canonical": [r for r in rs if r["state"] == "canonical"],
            "fitted": [r for r in rs if r["state"] == "fitted"],
        }
        strata.update({p: [r for r in rs if r["pathway"] == p] for p in PATHS})
        strata.update(
            {
                p + "/" + s: [r for r in rs if r["pathway"] == p and r["state"] == s]
                for p in PATHS
                for s in ("canonical", "fitted")
            }
        )
        for name, vals in strata.items():
            ds = [r["q"] - r["source_q"] for r in vals]
            people.append(
                dict(
                    mode=mode,
                    method=m,
                    height_policy=hp,
                    subject_uid=uid,
                    stratum=name,
                    absolute_pp=float(np.mean(np.abs(ds))),
                    signed_pp=float(np.mean(ds)),
                    body_observations=len(vals),
                    dependent_reference=True,
                )
            )
    c.save("reference-people.json", people)
    table = []
    for (mode, m, hp, s), rs in groups(people, ["mode", "method", "height_policy", "stratum"]):
        x = np.array([r["absolute_pp"] for r in rs])
        ix = indices(len(x))
        summary = (
            stats(x)
            if s in ("all", "canonical")
            else dict(
                people=len(x),
                mean=float(x.mean()),
                median=float(np.median(x)),
                mean_ci95=np.quantile(x[ix].mean(1), [0.025, 0.975]).tolist(),
            )
        )
        table.append(
            dict(
                mode=mode,
                method=m,
                height_policy=hp,
                stratum=s,
                body_observations=sum((r["body_observations"] for r in rs)),
                **summary,
                signed_bias_pp=float(np.mean([r["signed_pp"] for r in rs])),
                reference="Frozen dependent R3 MHR-mapped source proxy; may favour umbilicus methods",
                physiological_accuracy=False,
            )
        )
    c.table("S2-T8-dependent-reference", table)
    return dict(participant_stratum_endpoints=len(people), reference_summaries=len(table))


def contrasts(rows: Any, grouping: Any, field: str) -> Any:
    out = []
    for key, rr in groups(rows, grouping):
        policies: dict[str, dict[str, float]] = {}
        for r in rr:
            pol = r["method"] + "/" + r.get("height_policy", "")
            policies.setdefault(pol, {})[r["subject_uid"]] = r[field]
        for a, b in combinations(sorted(policies), 2):
            ma, ha = a.split("/")
            mb, hb = b.split("/")
            if ma != mb and ha != hb:
                continue
            ids = sorted(policies[a].keys() & policies[b].keys())
            diffs = np.array([policies[a][u] - policies[b][u] for u in ids])
            ix = indices(len(ids))
            out.append(
                dict(
                    zip(grouping, key),
                    first=a,
                    second=b,
                    people=len(ids),
                    mean=float(diffs.mean()),
                    median=float(np.median(diffs)),
                    mean_ci95=np.quantile(diffs[ix].mean(1), [0.025, 0.975]).tolist(),
                    direction="first-minus-second; negative favours first for disagreement",
                    interval="unadjusted exploratory paired-person bootstrap",
                )
            )
    return out


def compare(c: Context) -> Any:
    cc = contrasts(c.load("canonical-people.json"), ["mode"], "absolute_pp")
    fc = contrasts(c.load("fitted-canonical-people.json"), ["mode", "pathway"], "absolute_pp")
    ref = contrasts(c.load("reference-people.json"), ["mode", "stratum"], "absolute_pp")
    c.table("canonical-paired-policy-contrasts", cc)
    c.table("fitted-canonical-paired-policy-contrasts", fc)
    c.table("reference-paired-policy-contrasts", ref)
    return dict(canonical=len(cc), fitted_canonical=len(fc), reference=len(ref))


def select(c: Context) -> Any:
    cp = c.load("canonical-people.json")
    ref = c.load("reference-people.json")
    all_pareto = []
    for group, hps in (
        ("full_source_matched", ("H1", "H2", "H3_t0.25")),
        ("strict_common", ("H1", "H2", "H3_strict")),
    ):
        subset = [
            r
            for r in cp
            if r["mode"] == "end_to_end"
            and r["method"] in METHODS[:3]
            and (r["height_policy"] in hps)
            and (r["source_mean_q"] is not None)
        ]
        bypolicy = {k: rs for k, rs in groups(subset, ["method", "height_policy"])}
        ids = sorted(
            set.intersection(*[{r["subject_uid"] for r in rs} for rs in bypolicy.values()])
        )
        options = []
        for (m, hp), rr in bypolicy.items():
            rr = [r for r in rr if r["subject_uid"] in ids]
            errors = [
                r["absolute_pp"]
                for r in ref
                if r["subject_uid"] in ids
                and (r["mode"], r["method"], r["height_policy"], r["stratum"])
                == ("end_to_end", m, hp, "canonical")
            ]
            assert len(errors) == len(ids)
            sd = float(np.std([r["mean_q"] for r in rr], ddof=1))
            source_sd = float(np.std([r["source_mean_q"] for r in rr], ddof=1))
            options.append(
                dict(
                    policy_id=m + "/" + hp,
                    cohort=ids,
                    comparison_group=group,
                    people=len(ids),
                    cross_path_mae_pp=float(np.mean([r["absolute_pp"] for r in rr])),
                    reference_mae_pp=float(np.mean(errors)),
                    coordinate_sd_pp=sd,
                    source_sd_pp=source_sd,
                    sd_ratio=sd / source_sd,
                    sd_ratio_distance=abs(float(np.log(sd / source_sd))),
                    height_eligible_people=next(
                        (
                            r["complete_four_body_people"]
                            for r in c.src_table("S2-T9-coverage-failures")
                            if (r["mode"], r["method"], r["height_policy"]) == ("end_to_end", m, hp)
                        )
                    ),
                    interpretation="Point-estimate descriptive Pareto; no statistical dominance or physiological validity",
                )
            )
        all_pareto.extend(pareto(options))
    c.save("pareto-private.json", all_pareto)
    c.table(
        "S2-T10-policy-tradeoffs",
        [{k: v for k, v in r.items() if k != "cohort"} for r in all_pareto],
    )
    return dict(
        non_dominated=[
            r["comparison_group"] + ":" + r["policy_id"] for r in all_pareto if r["non_dominated"]
        ]
    )
