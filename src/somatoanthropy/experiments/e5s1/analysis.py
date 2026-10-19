"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np
from scipy.stats import spearmanr

from somatoanthropy.experiments.e5s1.core import (
    CELLS,
    METHODS,
    POLICIES,
    TOL,
    complete_people,
    coordinate,
    evaluate,
    preference,
    summary,
)
from somatoanthropy.experiments.e5s1.inputs import sha
from somatoanthropy.workflow import RecordStore as Context


def positive(*xs: Any) -> bool:
    return all((x is not None and np.isfinite(x) and (x > 0) for x in xs))


def cohort(c: Context) -> Any:
    wide = {r["record_id"]: r for r in c.src("E5", "catalogue.json")["records"]}
    pairs = {(r["record_id"], r["mode"]): r for r in c.src("WAIST-01", "paired.json")}
    old = {(r["record_id"], r["mode"]): r for r in c.src("E5", "source-agreement.json")}
    branches: dict[Any, Any] = {}
    for pair in c.src("E4", "cohorts.json")["pairs"]:
        for k in ("a", "b"):
            r = pair[k]
            key = (r["subject_uid"], r["collection"])
            if key in branches:
                assert branches[key] == r
            branches[key] = r
    assert len({uid for uid, path in branches if path == "SMPL-NICP"}) == 150
    original_long = c.src("WAIST-01", "e5-long.json")
    assert [
        r["original_waist_record"] for r in c.src("E1", "e5-method-records.json")
    ] == original_long
    measurements = c.src("WAIST-01", "measurements.json")
    sections = {}
    native = {}
    for r in measurements:
        if r["dataset"] != "NOMO" or r["pathway"] not in ("SMPL-NICP", "CAESAR-NICP"):
            continue
        sections[r["record_id"]] = {
            m: {
                k: v
                for k, v in r["sections"][m].items()
                if k in ("geometry_quality", "raw_contour_cm", "tape_envelope_cm")
            }
            for m in METHODS
        }
        for pathkey, hashkey in (
            ("mesh_path", "mesh_sha256"),
            ("parameter_path", "parameter_sha256"),
            ("source_path", "source_sha256"),
        ):
            if r.get(pathkey):
                p, h = (r[pathkey], r[hashkey])
                assert sha(p) == h
                native[p] = h
    del measurements
    c.save("original-asset-protection.json", native)
    records, missing = ([], [])
    for rid, r in sorted(wide.items()):
        if r["dataset"] != "NOMO" or r["source_representation"] not in ("SMPL-NICP", "CAESAR-NICP"):
            continue
        path, state, uid = (r["source_representation"], r["pose"], r["subject_uid"])
        b = branches[uid, path]
        assert (r["body_uid"], r["fit_uid"], r["source_sha256"]) == (
            b["body_uid"],
            b["fit_uid"],
            b["source_sha256"],
        )
        hq = b["sites"]["source"]["height"]
        hs = hq.get("engineering_value_cm") if hq.get("geometry_quality") == "VALID" else None
        base = dict(
            record_id=rid,
            subject_uid=uid,
            pathway=path,
            state=state,
            body_uid=r["body_uid"],
            fit_uid=r["fit_uid"],
            mesh_sha256=r["mesh_sha256"],
            parameter_sha256=r["parameter_sha256"],
            source_sha256=b["source_sha256"],
            Hs=hs,
            Hb=r["height_cm"],
            source_height_definition=hq,
            body_height_definition=r["height_definition"],
            source_to_working=b["source_to_working"],
            pose_comparability=b["pose_comparability"],
            t90_transfer_verified=b["t90_transfer_verified"],
            fallback=r["fallback"],
            source_reference_definition=r["source_reference_definition"],
            physical_calibration=r["physical_calibration"],
            units="engineering_cm",
        )
        modes = {}
        for mode, func in (
            ("end_to_end", "raw_contour_cm"),
            ("site_raw", "raw_contour_cm"),
            ("site_tape", "tape_envelope_cm"),
        ):
            p = pairs[rid, mode]
            assert (p["subject_uid"], p["body_uid"], p["pathway"], p["state"]) == (
                uid,
                r["body_uid"],
                path,
                state,
            )
            offset = sections[rid]["B3_offset"]
            wo = offset.get(func) if offset["geometry_quality"] == "VALID" else None
            vals = dict(P=p["ours_cm"], B1=p["comparator_cm"], B3_offset=wo)
            eligible = p["pair_eligible"] and positive(
                hs, r["height_cm"], p["reference_cm"], *vals.values()
            )
            modes[mode] = dict(
                Ws=p["reference_cm"],
                waists=vals,
                source_functional=func,
                reference_tier=p["reference_tier"],
                reference_dependent=p["reference_dependent"],
                functional_comparability=p["functional_comparability"],
                eligible=bool(eligible),
            )
            if eligible:
                assert p["reference_tier"] == "R3" and p["reference_dependent"]
                o = old[rid, mode]
                assert (hs, r["height_cm"], p["reference_cm"], vals["P"], vals["B1"]) == (
                    o["source_height_cm"],
                    o["height_cm"],
                    o["source_waist_cm"],
                    o["ours_waist_cm"],
                    o["comparator_waist_cm"],
                )
            else:
                missing.append(
                    dict(
                        subject_uid=uid,
                        record_id=rid,
                        pathway=path,
                        state=state,
                        mode=mode,
                        missing_source_height=not positive(hs),
                        missing_source_waist=not positive(p["reference_cm"]),
                        invalid_methods=[m for m, v in vals.items() if not positive(v)],
                        reason="FROZEN_REFERENCE_OR_METHOD_UNAVAILABLE",
                    )
                )
        records.append(dict(base, modes=modes))
    assert len(records) == 600
    complete = complete_people([r for r in records if r["modes"]["end_to_end"]["eligible"]])
    assert len(complete) == 149
    for r in records:
        r["primary_eligible"] = r["subject_uid"] in complete
    c.save("cohort.json", records)
    c.save("missing.json", missing)
    c.save("eligible-people.json", sorted(complete))
    rows = []
    for mode in ("end_to_end", "site_raw", "site_tape"):
        for path, state in sorted(CELLS):
            rr = [r for r in records if r["pathway"] == path and r["state"] == state]
            good = [r for r in rr if r["modes"][mode]["eligible"]]
            rows.append(
                dict(
                    mode=mode,
                    pathway=path,
                    state=state,
                    selected_people=150,
                    selected_observations=len(rr),
                    eligible_people=len(good),
                    eligible_observations=len(good),
                    missing_observations=len(rr) - len(good),
                    missing_source_waist=sum((not positive(r["modes"][mode]["Ws"]) for r in rr)),
                    invalid_height=sum((not positive(r["Hs"], r["Hb"]) for r in rr)),
                    invalid_method_measurements=sum(
                        (
                            sum((not positive(v) for v in r["modes"][mode]["waists"].values()))
                            for r in rr
                        )
                    ),
                    linked_exactly=True,
                    source_reference="Dependent R3; no qualified physical/clinical reference",
                )
            )
    c.table("E5S1-T2-primary-matched-cohort", rows)
    return records


def responses(c: Context) -> Any:
    out = []
    for r in c.load("cohort.json"):
        if not r["primary_eligible"]:
            continue
        for mode, q in r["modes"].items():
            if not q["eligible"]:
                continue
            for method, w in q["waists"].items():
                out.append(
                    dict(
                        subject_uid=r["subject_uid"],
                        record_id=r["record_id"],
                        body_uid=r["body_uid"],
                        pathway=r["pathway"],
                        state=r["state"],
                        mode=mode,
                        method=method,
                        Hs=r["Hs"],
                        Hb=r["Hb"],
                        Ws=q["Ws"],
                        Wm=w,
                        source_functional=q["source_functional"],
                        **evaluate(r["Hs"], q["Ws"], r["Hb"], w),
                    )
                )
    c.save("responses.json", out)
    return out


def strata(rows: list[dict[str, Any]]) -> Any:
    yield ("all", rows)
    for path in ("SMPL-NICP", "CAESAR-NICP"):
        yield (path, [r for r in rows if r["pathway"] == path])
    for state in ("fitted", "canonical"):
        yield (state, [r for r in rows if r["state"] == state])
    for path, state in sorted(CELLS):
        yield (
            path + "/" + state,
            [r for r in rows if r["pathway"] == path and r["state"] == state],
        )


def comparisons(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[Any, Any] = defaultdict(dict)
    for r in rows:
        groups[r["record_id"], r["mode"]][r["method"]] = r
    out = []
    for (rid, mode), rs in sorted(groups.items()):
        assert set(rs) == set(METHODS)
        for first, second in (("P", "B1"), ("P", "B3_offset"), ("B1", "B3_offset")):
            a, b = (rs[first], rs[second])
            q = {k: a[k] for k in ("subject_uid", "pathway", "state", "Hs", "Hb", "Ws")}
            q.update(
                record_id=rid,
                mode=mode,
                first=first,
                second=second,
                **{p: abs(b[p]) - abs(a[p]) for p in POLICIES},
            )
            q.update(
                shift=q["sourceH"] - q["actual"],
                height_error_cm=a["Hb"] - a["Hs"],
                cancellation_difference_pp=b["cancellation_pp"] - a["cancellation_pp"],
                absolute_height_contribution_difference_pp=abs(b["height_contribution_pp"])
                - abs(a["height_contribution_pp"]),
                waist_advantage_cm=abs(b["waist_error_cm"]) - abs(a["waist_error_cm"]),
                compensating_distance_advantage_cm=b["compensating_distance_cm"]
                - a["compensating_distance_cm"],
            )
            q["shift_identity_residual_pp"] = q["shift"] - (
                q["cancellation_difference_pp"] - q["absolute_height_contribution_difference_pp"]
            )
            assert abs(q["shift_identity_residual_pp"]) < TOL
            assert abs(q["bodyH"] - q["sourceH"] * a["Hb"] / a["Hs"]) < TOL
            out.append(q)
    return out


def compensation(c: Context) -> Any:
    rows = [r for r in c.load("responses.json") if r["mode"] == "end_to_end"]
    table = []
    for name, rr in strata(rows):
        for method in METHODS:
            rs = [r for r in rr if r["method"] == method]
            for field in (
                "waist_contribution_pp",
                "height_contribution_pp",
                "actual",
                "cancellation_pp",
                "waist_error_cm",
                "compensating_distance_cm",
            ):
                table.append(
                    dict(
                        stratum=name,
                        method=method,
                        metric=field,
                        **summary(rs, field),
                        opposing_observation_fraction=float(np.mean([r["opposing"] for r in rs])),
                    )
                )
    c.table("E5S1-T5-error-compensation", table)
    pairs = comparisons(rows)
    c.save("compensation-pairs.json", pairs)
    cases = []
    for name, rr in strata([r for r in pairs if r["first"] == "P" and r["second"] == "B1"]):
        for actual in ("P", "B1", "tie"):
            rs = [r for r in rr if preference(r["actual"]) == actual]
            cases.append(
                dict(
                    stratum=name,
                    actual_preference=actual,
                    observations=len(rs),
                    source_waist_prefers_P=sum(
                        (preference(r["waist_advantage_cm"]) == "P" for r in rs)
                    ),
                    source_waist_prefers_B1=sum(
                        (preference(r["waist_advantage_cm"]) == "B1" for r in rs)
                    ),
                    source_waist_ties=sum(
                        (preference(r["waist_advantage_cm"]) == "tie" for r in rs)
                    ),
                    farther_source_waist_better_actual_formula=sum(
                        (
                            preference(r["waist_advantage_cm"]) not in (actual, "tie")
                            and actual != "tie"
                            for r in rs
                        )
                    ),
                    winner_closer_compensating_waist=sum(
                        (
                            preference(r["compensating_distance_advantage_cm"]) == actual
                            and actual != "tie"
                            for r in rs
                        )
                    ),
                    winner_has_more_cancellation=sum(
                        (
                            r["cancellation_difference_pp"] < -TOL
                            if actual == "P"
                            else r["cancellation_difference_pp"] > TOL
                            if actual == "B1"
                            else False
                            for r in rs
                        )
                    ),
                )
            )
    c.table("E5S1-T7-compensating-waist", cases)
    return table


def participant_means(rows: list[dict[str, Any]], fields: list[str]) -> list[dict[str, Any]]:
    groups: dict[str, Any] = defaultdict(list)
    for r in rows:
        groups[r["subject_uid"]].append(r)
    return [
        dict(
            subject_uid=k,
            observations=len(v),
            **{f: float(np.mean([r[f] for r in v])) for f in fields},
        )
        for k, v in sorted(groups.items())
    ]


def reversals(c: Context) -> Any:
    pairs = comparisons(c.load("responses.json"))
    c.save("paired-advantages.json", pairs)
    rr = [
        r
        for r in pairs
        if r["mode"] == "end_to_end" and r["first"] == "P" and (r["second"] == "B1")
    ]
    transitions, persons, shifts, relationships = ([], [], [], [])
    for name, rs in strata(rr):
        pp = participant_means(
            rs,
            [
                *POLICIES,
                "shift",
                "height_error_cm",
                "cancellation_difference_pp",
                "absolute_height_contribution_difference_pp",
            ],
        )
        for r in pp:
            r.update(stratum=name, **{p + "_preference": preference(r[p]) for p in POLICIES})
        persons.extend(pp)
        shifts.append(dict(stratum=name, **summary(pp, "shift")))
        for unit, us in (("participant", pp), ("observation", rs)):
            for target in ("sourceH", "bodyH"):
                for a in ("P", "B1", "tie"):
                    for b in ("P", "B1", "tie"):
                        count = sum(
                            (
                                preference(r["actual"]) == a and preference(r[target]) == b
                                for r in us
                            )
                        )
                        transitions.append(
                            dict(
                                stratum=name,
                                unit=unit,
                                controlled=target,
                                actual_preference=a,
                                controlled_preference=b,
                                count=count,
                                denominator=len(us),
                                fraction=count / len(us),
                                descriptive_near_zero_threshold_pp=0.1,
                                actual_within_descriptive_threshold=sum(
                                    (abs(r["actual"]) <= 0.1 for r in us)
                                ),
                                controlled_within_descriptive_threshold=sum(
                                    (abs(r[target]) <= 0.1 for r in us)
                                ),
                            )
                        )
        for field in (
            "height_error_cm",
            "cancellation_difference_pp",
            "absolute_height_contribution_difference_pp",
        ):
            feature_values = np.array([r[field] for r in pp], dtype=float)
            shift_values = np.array([r["shift"] for r in pp], dtype=float)
            rho = (
                float(spearmanr(feature_values, shift_values).statistic)
                if np.std(feature_values) > 0 and np.std(shift_values) > 0
                else None
            )
            relationships.append(
                dict(
                    stratum=name,
                    unit="participant means",
                    x=field,
                    y="advantage shift",
                    people=len(pp),
                    spearman_rho=rho,
                    causal=False,
                )
            )
    c.save("participant-advantages.json", persons)
    c.table("E5S1-T6-ranking-reversals", transitions)
    c.table("advantage-shifts", shifts)
    c.table("shift-associations", relationships)
    return transitions


def comparison_stats(rows: list[dict[str, Any]], use_strata: bool = True) -> list[Any]:
    out = []
    for name, rr in strata(rows) if use_strata else [("all", rows)]:
        for first, second in (("P", "B1"), ("P", "B3_offset"), ("B1", "B3_offset")):
            rs = [r for r in rr if r["first"] == first and r["second"] == second]
            for policy in POLICIES:
                out.append(
                    dict(
                        stratum=name,
                        first=first,
                        second=second,
                        policy=policy,
                        positive_favours=first,
                        **summary(rs, policy),
                    )
                )
    return out


def contours(c: Context) -> Any:
    all_pairs = c.load("paired-advantages.json")
    out = []
    for mode in ("end_to_end", "site_raw", "site_tape"):
        rr = [r for r in all_pairs if r["mode"] == mode]
        uids = complete_people([r for r in rr if r["first"] == "P" and r["second"] == "B1"])
        rr = [r for r in rr if r["subject_uid"] in uids]
        for s in comparison_stats(rr):
            if s["policy"] == "sourceH":
                out.append(
                    dict(
                        mode=mode,
                        reference_functional="tape_envelope_cm"
                        if mode == "site_tape"
                        else "raw_contour_cm",
                        functional_mismatch=mode == "end_to_end",
                        **s,
                    )
                )
    c.table("E5S1-T8-contour-functional-controls", out)
    available = []
    for mode in ("end_to_end", "site_raw", "site_tape"):
        rr = [r for r in all_pairs if r["mode"] == mode]
        for first, second in (("P", "B1"), ("P", "B3_offset"), ("B1", "B3_offset")):
            rs = [r for r in rr if r["first"] == first and r["second"] == second]
            pp = participant_means(rs, ["sourceH"])
            s = summary(pp, "sourceH")
            s = {k.replace("observation_", "participant_mean_"): v for k, v in s.items()}
            s["observations"] = len(rs)
            available.append(
                dict(
                    mode=mode,
                    first=first,
                    second=second,
                    policy="sourceH",
                    weighting="all available body pairs averaged within participant; participant distributions",
                    min_observations_per_person=min((r["observations"] for r in pp)),
                    max_observations_per_person=max((r["observations"] for r in pp)),
                    **s,
                )
            )
    c.table("contour-all-available", available)
    cohort_rows = [r for r in c.load("cohort.json") if r["primary_eligible"]]
    pairwise = []
    for mode in ("end_to_end", "site_raw", "site_tape"):
        for first, second in (("P", "B1"), ("P", "B3_offset"), ("B1", "B3_offset")):
            rr = []
            for r in cohort_rows:
                q = r["modes"][mode]
                if not positive(r["Hs"], q["Ws"], q["waists"][first], q["waists"][second]):
                    continue
                a = evaluate(r["Hs"], q["Ws"], r["Hb"], q["waists"][first])["sourceH"]
                b = evaluate(r["Hs"], q["Ws"], r["Hb"], q["waists"][second])["sourceH"]
                rr.append(dict(subject_uid=r["subject_uid"], effect=abs(b) - abs(a)))
            pp = participant_means(rr, ["effect"])
            s = {
                k.replace("observation_", "participant_mean_"): v
                for k, v in summary(pp, "effect").items()
            }
            s["observations"] = len(rr)
            pairwise.append(
                dict(
                    mode=mode,
                    first=first,
                    second=second,
                    policy="sourceH",
                    positive_favours=first,
                    eligibility="pair-specific, does not require third method",
                    **s,
                )
            )
    c.table("contour-pairwise-all-available", pairwise)
    common_uids = set.intersection(
        *(
            complete_people(
                [
                    r
                    for r in all_pairs
                    if r["mode"] == m and r["first"] == "P" and (r["second"] == "B1")
                ]
            )
            for m in ("end_to_end", "site_raw", "site_tape")
        )
    )
    matched: list[Any] = []
    for mode in ("end_to_end", "site_raw", "site_tape"):
        rs = [r for r in all_pairs if r["mode"] == mode and r["subject_uid"] in common_uids]
        matched.extend(
            (dict(mode=mode, **s) for s in comparison_stats(rs, False) if s["policy"] == "sourceH")
        )
    c.table("contour-matched-cohort", matched)
    return out


def policy(c: Context) -> Any:
    cohort_rows = c.load("cohort.json")
    groups: dict[str, Any] = defaultdict(list)
    for r in cohort_rows:
        groups[r["subject_uid"]].append(r)
    eligibility, anchors = ([], {})
    for uid, rs in sorted(groups.items()):
        hs = [r["Hs"] for r in rs]
        source_defs = [r["source_height_definition"] for r in rs]
        reasons = []
        if len(rs) != 4 or {(r["pathway"], r["state"]) for r in rs} != CELLS:
            reasons.append("INCOMPLETE_LINKAGE")
        if not all((positive(h) for h in hs)):
            reasons.append("SOURCE_HEIGHT_MISSING")
        elif max(hs) - min(hs) > 1e-08:
            reasons.append("CROSS_PATH_SOURCE_HEIGHT_DISAGREEMENT")
        if not all(
            (
                q.get("quantity") == "vertical_extent_cm"
                and q.get("geometry_quality") == "VALID"
                and (q.get("reason") == "SAVED_SURFACE_Y_EXTENT")
                for q in source_defs
            )
        ):
            reasons.append("UNDOCUMENTED_SOURCE_HEIGHT_DEFINITION")
        if len({(q.get("protocol"), q.get("pose"), q.get("unit")) for q in source_defs}) != 1:
            reasons.append("SOURCE_PROTOCOL_OR_POSE_MISMATCH")
        if not all((r["t90_transfer_verified"] for r in rs)):
            reasons.append("SAVED_POSE_TRANSFER_UNVERIFIED")
        anchor = (
            next((r["Hs"] for r in rs if r["pathway"] == "SMPL-NICP" and r["state"] == "fitted"))
            if not reasons
            else None
        )
        anchors[uid] = anchor
        eligibility.append(
            dict(
                subject_uid=uid,
                engineering_identity_anchor_eligible=not reasons,
                complete_waist_endpoint=rs[0]["primary_eligible"],
                anchor_cm=anchor,
                source_height_range_cm=max(hs) - min(hs)
                if all((positive(h) for h in hs))
                else None,
                reasons=reasons,
                clinical_stature_qualified=False,
                cross_path_pose_equality_verified=False,
                compatibility_scope="Same documented source descriptor and verified own fitted/canonical linkage; cross-path anatomical pose equality unverified",
            )
        )
    c.save("identity-anchor-eligibility.json", eligibility)
    rr = [r for r in c.load("responses.json") if anchors[r["subject_uid"]] is not None]
    outputs = []
    for r in rr:
        anchor = anchors[r["subject_uid"]]
        assert anchor is not None
        outputs.append(
            dict(
                r,
                identity_anchor=anchor,
                actual_coordinate=coordinate(r["Hb"], r["Wm"]),
                anchored_coordinate=coordinate(anchor, r["Wm"]),
                original_source_coordinate=coordinate(r["Hs"], r["Ws"]),
                anchored_source_coordinate=coordinate(anchor, r["Ws"]),
                anchored_drift=response_at_anchor(anchor, r["Ws"], r["Wm"]),
            )
        )
    c.save("identity-anchor-responses.json", outputs)
    table = []
    for mode in ("end_to_end", "site_raw", "site_tape"):
        complete = complete_people([r for r in outputs if r["mode"] == mode and r["method"] == "P"])
        for method in METHODS:
            rs = [
                r
                for r in outputs
                if r["mode"] == mode and r["method"] == method and (r["subject_uid"] in complete)
            ]
            for pol, field in (
                ("A_reconstructed_extent", "actual"),
                ("B_source_identity_anchor", "anchored_drift"),
            ):
                coordinate_field = (
                    "actual_coordinate" if pol.startswith("A_") else "anchored_coordinate"
                )
                pp = participant_means(rs, [coordinate_field])
                byuid: dict[str, list[float]] = defaultdict(list)
                for r in rs:
                    byuid[r["subject_uid"]].append(r[coordinate_field])
                table.append(
                    dict(
                        mode=mode,
                        method=method,
                        policy=pol,
                        eligible_height_identities=sum(
                            (r["engineering_identity_anchor_eligible"] for r in eligibility)
                        ),
                        eligible_formula_identities=len(byuid),
                        selected_identities=150,
                        coordinate_sd_of_person_means_pp=float(
                            np.std([r[coordinate_field] for r in pp], ddof=1)
                        ),
                        mean_within_person_four_body_sd_pp=float(
                            np.mean([np.std(v, ddof=1) for v in byuid.values()])
                        ),
                        **summary(rs, field),
                        clinical_stature_qualified=False,
                    )
                )
    c.table("E5S1-T9-identity-anchored-height-policy", table)
    return table


def response_at_anchor(h: float, ws: float, wm: float) -> float:
    return float(evaluate(h, ws, h, wm)["sourceH"])


def statistics(c: Context) -> Any:
    pairs = [r for r in c.load("paired-advantages.json") if r["mode"] == "end_to_end"]
    stats = comparison_stats(pairs)
    c.table("E5S1-T3-three-way-formula-agreement", [r for r in stats if r["stratum"] == "all"])
    c.table("E5S1-T4-pathway-state-effects", [r for r in stats if r["stratum"] != "all"])
    methods = []
    responses_rows = [r for r in c.load("responses.json") if r["mode"] == "end_to_end"]
    for name, rr in strata(responses_rows):
        for method in METHODS:
            rs = [r for r in rr if r["method"] == method]
            for pol in POLICIES:
                methods.append(dict(stratum=name, method=method, policy=pol, **summary(rs, pol)))
    c.table("method-specific-drift", methods)
    heights = []
    for name, rr in strata([r for r in pairs if r["first"] == "P" and r["second"] == "B1"]):
        heights.append(dict(stratum=name, **summary(rr, "height_error_cm"), unit="engineering_cm"))
    c.table("height-error-distribution", heights)
    difference_rows = []
    primary = [r for r in pairs if r["first"] == "P" and r["second"] == "B1"]
    for factor, a, b in (("pathway", "SMPL-NICP", "CAESAR-NICP"), ("state", "canonical", "fitted")):
        for pol in POLICIES:
            aa = {
                r["subject_uid"]: r[pol]
                for r in participant_means([r for r in primary if r[factor] == a], [pol])
            }
            bb = {
                r["subject_uid"]: r[pol]
                for r in participant_means([r for r in primary if r[factor] == b], [pol])
            }
            rs = [dict(subject_uid=k, contrast=aa[k] - bb[k]) for k in sorted(aa)]
            difference_rows.append(
                dict(
                    factor=factor, contrast=f"{a} minus {b}", policy=pol, **summary(rs, "contrast")
                )
            )
    c.table("paired-pathway-state-contrasts", difference_rows)
    c.table(
        "paired-cancellation-differences",
        [
            dict(stratum=name, metric=field, **summary(rr, field))
            for name, rr in strata(primary)
            for field in (
                "cancellation_difference_pp",
                "absolute_height_contribution_difference_pp",
                "shift",
            )
        ],
    )
    compensation_descriptors = []
    for name, rr in strata([r for r in responses_rows if r["method"] == "P"]):
        ds = [
            dict(
                subject_uid=r["subject_uid"],
                delta_compensating_waist_cm=r["compensating_waist_cm"] - r["Ws"],
            )
            for r in rr
        ]
        compensation_descriptors.append(
            dict(stratum=name, **summary(ds, "delta_compensating_waist_cm"))
        )
    c.table("compensating-waist-offset-distribution", compensation_descriptors)
    anchored = {
        r["subject_uid"]
        for r in c.load("identity-anchor-eligibility.json")
        if r["engineering_identity_anchor_eligible"] and r["complete_waist_endpoint"]
    }
    p = [r for r in primary if r["subject_uid"] in anchored]
    pp = participant_means(p, [*POLICIES])
    byuid: dict[str, list[Any]] = defaultdict(list)
    for r in p:
        byuid[r["subject_uid"]].append(r)
    c.table(
        "identity-anchor-ranking-consistency",
        [
            dict(
                people=len(pp),
                body_observations=len(p),
                actual_prefers_P=sum((preference(r["actual"]) == "P" for r in pp)),
                anchored_prefers_P=sum((preference(r["sourceH"]) == "P" for r in pp)),
                actual_to_anchor_switches=sum(
                    (preference(r["actual"]) != preference(r["sourceH"]) for r in pp)
                ),
                actual_B1_to_anchor_P=sum(
                    (
                        preference(r["actual"]) == "B1" and preference(r["sourceH"]) == "P"
                        for r in pp
                    )
                ),
                actual_P_to_anchor_B1=sum(
                    (
                        preference(r["actual"]) == "P" and preference(r["sourceH"]) == "B1"
                        for r in pp
                    )
                ),
                identities_with_mixed_actual_body_preferences=sum(
                    (
                        len({preference(r["actual"]) for r in rs} - {"tie"}) > 1
                        for rs in byuid.values()
                    )
                ),
                identities_with_mixed_anchored_body_preferences=sum(
                    (
                        len({preference(r["sourceH"]) for r in rs} - {"tie"}) > 1
                        for rs in byuid.values()
                    )
                ),
                interpretation="Anchoring removes variability of the height input; remaining waist/site and pathway differences still change preferences",
            )
        ],
    )
    return stats
