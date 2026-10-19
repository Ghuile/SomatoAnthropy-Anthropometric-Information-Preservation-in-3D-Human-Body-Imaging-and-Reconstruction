"""Frozen aggregate selection and checks against manuscript display precision."""

from __future__ import annotations

import json
from pathlib import Path


def read(root: Path, name: str) -> list[dict]:
    return json.loads((root / "results/aggregate" / (name + ".json")).read_text("utf-8"))


def one(root: Path, name: str, **where) -> dict:
    rows = [r for r in read(root, name) if all(r.get(k) == v for k, v in where.items())]
    if len(rows) != 1:
        raise ValueError(f"EXPECTED_ONE_AGGREGATE:{name}:{where}:{len(rows)}")
    return rows[0]


def interval(row: dict, key="mean", ci="mean_ci95", decimals=4, signed=False) -> str:
    def number(x):
        return format(x, ("+" if signed else "") + f".{decimals}f").replace("-", "−")

    return f"{number(row[key])} [{number(row[ci][0])}, {number(row[ci][1])}]"


def check_anchors(root: Path) -> list[dict]:
    """Compare frozen estimates, intervals and denominators, without re-bootstrapping."""
    checked = []

    def check(label, actual, expected, tolerance=5e-5):
        if isinstance(expected, (list, tuple)):
            if len(actual) != len(expected):
                raise ValueError("ANCHOR_LENGTH:" + label)
            for i, (a, e) in enumerate(zip(actual, expected, strict=True)):
                check(f"{label}[{i}]", a, e, tolerance)
            return
        if abs(actual - expected) > tolerance:
            raise ValueError(f"ANCHOR_MISMATCH:{label}:{actual}:{expected}")
        checked.append(dict(anchor=label, actual=actual, expected=expected, tolerance=tolerance))

    for path, expected in [("SMPL-NICP", 0.17279079055512783), ("CAESAR-NICP", 0.1717733732937397)]:
        r = one(
            root,
            "height-variation-control-audit",
            population="pathway_all_available",
            collection=path,
        )
        check("E2 " + path, r["canonical_to_source_sd_ratio"], expected, 1e-14)
        check("E2 people " + path, r["people"], 150, 0)
    for path, first, held in [("SMPL-NICP", 0.5861, 0.5786), ("CAESAR-NICP", 0.5870, 0.5693)]:
        a = one(root, "E2-1-T4-height", collection=path, state="canonical", arm="released")
        b = one(root, "E2-2-T7-height", collection=path, state="canonical", condition="C")
        for label, r, expected in [("first", a, first), ("disjoint", b, held)]:
            check(label + path, r["sd_ratio"], expected)
            check(label + " n " + path, r["n"], 12, 0)
    for name, metric, mean, ci in [
        ("E2-1-paired-effects", "cross_path_vertex_rms_cm", 0.4756, [0.2823, 0.7211]),
        ("E2-2-paired-effects", "cross_path_rms", 0.4808, [0.3506, 0.6331]),
    ]:
        where = dict(collection="PAIRED_PATHWAYS", metric=metric)
        if name.startswith("E2-2"):
            where["contrast"] = "C-B"
        r = one(root, name, **where)
        check(name + " cross-path", r["mean"], mean)
        check(name + " interval", r["ci95"], ci)
    r = one(root, "E3-T2-geometry", region="global_surface", alignment="saved_floor_frame")
    check("E3 median person median", r["median"], 2.030738412367885, 1e-12)
    check("E3 interval", r["median_ci95"], [1.6813081046139722, 2.2345845435921285], 1e-12)
    check("E3 independent people", r["subjects"], 10, 0)
    for mode, mae, advantage, ci in [
        ("end_to_end", 3.543, 0.649, [0.365, 0.923]),
        ("umbilicus_offset_raw", 2.714, -0.179, [-0.377, -0.008]),
    ]:
        r = one(root, "W-T5-full-NOMO", mode=mode)
        check(mode + " P MAE", r["ours_MAE"], 2.893, 5e-4)
        check(mode + " comparator MAE", r["comparator_MAE"], mae, 5e-4)
        check(mode + " advantage", r["mean_advantage"], advantage, 5e-4)
        check(mode + " CI", r["CI95"], ci, 5e-4)
        check(mode + " n", [r["people"], r["body_pairs"]], [149, 298], 0)
    r = read(root, "E5-T6S-primary-person-mean")[0]
    check("E5 actual", r["mean"], -0.6519785407196393, 1e-14)
    check("E5 original CI", r["mean_ci95"], [-0.8720514366604958, -0.4400866515006125], 1e-14)
    for policy, mean in [
        ("actual", -0.6519785407196393),
        ("sourceH", 0.139748546),
        ("bodyH", 0.150170121),
    ]:
        r = one(root, "E5S1-T3-three-way-formula-agreement", first="P", second="B1", policy=policy)
        check("S1 " + policy, r["mean"], mean, 1e-8)
        check("S1 n " + policy, [r["people"], r["observations"]], [149, 596], 0)
    for method, cross, four, canonical, ratio in [
        ("P", 0.3093, 1.4408, 1.2734, 1.0380),
        ("B1", 0.2193, 1.5805, 1.5452, 0.8211),
        ("B3_offset", 0.2032, 1.1794, 1.1511, 0.9237),
    ]:
        r = one(root, "S2-T4-canonical-cross-path", method=method, height_policy="H2")
        check(method + " H2 cross", r["mean"], cross)
        check(method + " H2 cross n", [r["people"], r["body_observations"]], [150, 300], 0)
        for stratum, value, observations in [("all", four, 596), ("canonical", canonical, 298)]:
            r = one(
                root,
                "S2-T8-dependent-reference",
                method=method,
                height_policy="H2",
                stratum=stratum,
            )
            check(method + " H2 " + stratum, r["mean"], value)
            check(
                method + " H2 reference n " + stratum,
                [r["people"], r["body_observations"]],
                [149, observations],
                0,
            )
        r = one(root, "S2-T7-coordinate-diversity", method=method, height_policy="H2")
        check(method + " H2 SD ratio", r["sd_ratio"], ratio)
        check(method + " H2 SD n", r["people"], 149, 0)
    for r, n in zip(read(root, "S2-T3-height-eligibility"), [103, 104, 109, 138, 150], strict=True):
        check(r["policy"] + " eligibility", r["eligible_people"], n, 0)
    front = [
        r
        for r in read(root, "S2-T10-policy-tradeoffs")
        if r["comparison_group"] == "full_source_matched" and r["non_dominated"]
    ]
    if {r["policy_id"] for r in front} != {"B3_offset/H1", "B3_offset/H2", "P/H2"}:
        raise ValueError("CONDITIONAL_PARETO_FRONT_MISMATCH")
    for r in front:
        check("Pareto n " + r["policy_id"], r["people"], 149, 0)
    return checked


def check_paper_tables(root: Path) -> int:
    """Reconstruct numerical display cells directly from their detailed tables."""
    tables = {r["id"]: r for r in read(root, "paper_tables")}
    count = 0

    def compare(table, i, j, value):
        nonlocal count
        expected = tables[table]["rows"][i][j]
        if value != expected:
            raise ValueError(f"DISPLAY_MISMATCH:{table}:{i}:{j}:{value!r}!={expected!r}")
        count += 1

    for i, value in enumerate(["150", "149 complete", "60", "12", "12", "10", "103"]):
        compare("Table1", i, 1, value)
    for i, path in enumerate(["SMPL-NICP", "CAESAR-NICP"]):
        r = one(
            root, "E2-2-paired-effects", contrast="D-C", collection=path, metric="surface_mean_cm"
        )
        value = f"{r['mean']:.6f} [{r['ci95'][0]:.6f}, {r['ci95'][1]:.7f}]".replace("-", "−")
        compare("TableS1", i, 1, value)
        compare("TableS1", i, 2, f"{r['n']} people")
    r = one(
        root,
        "E2-2-paired-effects",
        contrast="D-C",
        collection="PAIRED_PATHWAYS",
        metric="cross_path_rms",
    )
    value = f"{r['mean']:+.5f} [{r['ci95'][0]:.6f}, {r['ci95'][1]:.5f}]".replace("-", "−")
    compare("TableS1", 2, 1, value)
    compare("TableS1", 2, 2, f"{r['n']} people")
    for i, condition in enumerate(["B", "C", "D"], start=3):
        r = one(root, "E2-2-T5-stability", partition="heldout", condition=condition)
        compare("TableS1", i, 1, interval(r, ci="ci95", decimals=5 if condition == "B" else 4))
        compare("TableS1", i, 2, f"{r['n']} people")
    # Table 2 has intentionally different historical precision in its four rows.
    for i, (exp, path) in enumerate([(e, p) for e in [1, 2] for p in ["SMPL-NICP", "CAESAR-NICP"]]):
        name = "E2-1-T4-height" if exp == 1 else "E2-2-T7-height"
        key = "arm" if exp == 1 else "condition"
        b = one(
            root, name, collection=path, state="canonical", **{key: "locked" if exp == 1 else "B"}
        )
        c = one(
            root, name, collection=path, state="canonical", **{key: "released" if exp == 1 else "C"}
        )
        compare("Table2", i, 1, f"{b['sd_ratio']:.4f}→{c['sd_ratio']:.4f}")
        compare("Table2", i, 2, f"{b['mae']:.3f}→{c['mae']:.3f}")
        extra = dict(state="canonical") if exp == 1 else dict(contrast="C-B")
        r = one(
            root,
            f"E2-{exp}-paired-effects",
            collection=path,
            metric="height_absolute_error_cm" if exp == 1 else "canonical_height_absolute_error_cm",
            **extra,
        )
        compare("Table2", i, 3, interval(r, ci="ci95", decimals=3 if exp == 1 else 4))
        extra = dict(state="fitted") if exp == 1 else dict(contrast="C-B")
        r = one(
            root,
            f"E2-{exp}-paired-effects",
            collection=path,
            metric="geometry_mean_cm" if exp == 1 else "surface_mean_cm",
            **extra,
        )
        text = f"{r['mean']:.4f} [{r['ci95'][0]:.4f}, {r['ci95'][1]:.5f}]".replace("-", "−")
        compare("Table2", i, 4, text)
    for i, site in enumerate(["height", "waist", "abdomen", "hip"]):
        for j, path in enumerate(["SMPL-NICP", "CAESAR-NICP"]):
            r = one(root, "E2-T3-preservation", collection=path, state="fitted", site=site)
            compare("Table3", i, 1 + 2 * j, str(r["n"]))
            compare("Table3", i, 2 + 2 * j, f"{r['mae']:.4f}")
    for i, mode in enumerate(["end_to_end", "umbilicus_offset_raw"]):
        r = one(root, "W-T5-full-NOMO", mode=mode)
        compare("Table4", i, 1, f"{r['comparator_MAE']:.3f}")
        compare("Table4", i, 2, f"{r['ours_MAE']:.3f}")
        text = f"{r['mean_advantage']:+.3f} [{r['CI95'][0]:.3f}, {r['CI95'][1]:.3f}]".replace(
            "-", "−"
        )
        compare("Table4", i, 3, text)
    for j, method in enumerate(["P", "B1", "B3_offset"], start=1):
        for i, (name, where, key, ci) in enumerate(
            [
                ("S2-T4-canonical-cross-path", {}, "mean", "mean_ci95"),
                ("S2-T8-dependent-reference", dict(stratum="all"), "mean", "mean_ci95"),
                ("S2-T8-dependent-reference", dict(stratum="canonical"), "mean", "mean_ci95"),
                ("S2-T7-coordinate-diversity", {}, "sd_ratio", "sd_ratio_ci95"),
            ]
        ):
            r = one(root, name, method=method, height_policy="H2", **where)
            compare("Table5", i, j, interval(r, key, ci))
    for i, site in enumerate(["height", "waist", "abdomen", "hip", "chest", "neck"]):
        sd = one(root, "E3-T3-repeatability", site=site, metric="sd")
        rng = one(root, "E3-T3-repeatability", site=site, metric="range")
        compare("TableS2", i, 1, f"{sd['median']:.3f}")
        compare("TableS2", i, 2, interval(rng, "median", "median_ci95", decimals=3))
    for i, r in enumerate(read(root, "S2-T3-height-eligibility")):
        compare("TableS3", i, 1, str(r["eligible_people"]))
    return count
