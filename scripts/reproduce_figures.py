"""Level 2: aggregate versions of Figures 1–6, with no individual geometry."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from somatoanthropy.aggregate import check_anchors, check_paper_tables, one, read

BLUE, ORANGE, GREEN = "#245675", "#B95729", "#32755D"
ROOT = Path(__file__).resolve().parents[1]


def style(ax, xlabel):
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", alpha=0.17)
    ax.set_axisbelow(True)


def forest(ax, rows, labels, *, key="mean", ci="mean_ci95", scale=1, color=BLUE):
    x = np.array([r[key] for r in rows]) * scale
    bounds = np.array([r[ci] for r in rows]) * scale
    ax.errorbar(
        x,
        np.arange(len(x)),
        xerr=np.array([x - bounds[:, 0], bounds[:, 1] - x]),
        fmt="o",
        color=color,
        capsize=3,
        markersize=5,
    )
    ax.set_yticks(np.arange(len(x)), labels)
    ax.invert_yaxis()


def boxes(ax, items):
    ax.axis("off")
    for i, (title, detail) in enumerate(items):
        y = 0.88 - i * 0.25
        ax.text(
            0.5,
            y,
            title + "\n" + detail,
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.7", fc="#EDF3F5", ec=BLUE, lw=1),
        )
        if i < len(items) - 1:
            ax.annotate(
                "",
                xy=(0.5, y - 0.17),
                xytext=(0.5, y - 0.075),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="->", color=BLUE),
            )


def figures():
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), layout="constrained")
    boxes(
        axes[0],
        [
            ("Linked source representations", "150 NOMO people · two NICP pathways"),
            ("Native reconstruction and T90", "45 identity · 204 rig · 72 expression controls"),
            ("Separate evaluations", "Fidelity · metrology · cross-path agreement"),
            ("Equation response", "q(H, W) = −20 H/W · arbitrary absolute zero"),
        ],
    )
    boxes(
        axes[1],
        [
            ("Control intervention", "4 development + 12 evaluation people"),
            ("Disjoint internal evaluation", "Same 4 development + 12 separate people"),
            ("Repeated observations", "10 D-FAUST people × 6 observations"),
            ("Participant-level inference", "Linked bodies and pairs stay in one cluster"),
        ],
    )
    yield (
        "Figure1",
        fig,
        ["paper_tables"],
        "Study architecture; no additional population is introduced downstream.",
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), layout="constrained")
    boxes(
        axes[0],
        [
            ("Source-specific processing", "Recorded axes, units and transforms"),
            ("Native MHR fitting", "Saved source pose and permitted controls"),
            ("Own-pose and canonical bodies", "Exact saved T90 articulation transfer"),
        ],
    )
    paths = ["SMPL-LBFGSB", "SMPL-NICP", "CAESAR-NICP"]
    rows = [
        one(ROOT, "E1-T3-global", dataset="NOMO", pathway=p, lod=0, metric="symmetric_mean")
        for p in paths
    ]
    forest(axes[1], rows, paths, scale=100)
    style(axes[1], "Mean symmetric surface error (engineering cm)")
    axes[1].set_xlim(0, 0.6)
    axes[1].set_title("Matched ten-person E1 panel\nOriginal 95% participant-bootstrap CIs")
    yield (
        "Figure2",
        fig,
        ["E1-T3-global"],
        "Aggregate replacement for the historical body-render panels. Historical pathways differ in source, solver and fitting history; no isolated topology effect.",
    )

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), layout="constrained")
    labels, b, c, effects = [], [], [], []
    for exp, cohort in [(1, "First"), (2, "Disjoint")]:
        for path in ["SMPL-NICP", "CAESAR-NICP"]:
            labels.append(cohort + " / " + path.split("-")[0])
            name, key = ("E2-1-T4-height", "arm") if exp == 1 else ("E2-2-T7-height", "condition")
            b.append(
                one(
                    ROOT,
                    name,
                    collection=path,
                    state="canonical",
                    **{key: "locked" if exp == 1 else "B"},
                )["sd_ratio"]
            )
            c.append(
                one(
                    ROOT,
                    name,
                    collection=path,
                    state="canonical",
                    **{key: "released" if exp == 1 else "C"},
                )["sd_ratio"]
            )
            effects.append(
                one(
                    ROOT,
                    f"E2-{exp}-paired-effects",
                    collection=path,
                    metric="geometry_mean_cm" if exp == 1 else "surface_mean_cm",
                    **(dict(state="fitted") if exp == 1 else dict(contrast="C-B")),
                )
            )
    y = np.arange(4)
    axes[0].hlines(y, b, c, color="#b4bfc5", lw=2)
    axes[0].plot(b, y, "o", label="B locked", color=BLUE)
    axes[0].plot(c, y, "o", label="C released", color=ORANGE)
    axes[0].set_yticks(y, labels)
    axes[0].set_ylim(4.0, -0.3)
    axes[0].legend(frameon=False, loc="lower left", ncols=2)
    style(axes[0], "Canonical/source extent SD ratio")
    forest(axes[1], effects, labels, ci="ci95")
    style(axes[1], "C−B surface error (engineering cm)")
    cross = [
        one(
            ROOT,
            "E2-1-paired-effects",
            collection="PAIRED_PATHWAYS",
            metric="cross_path_vertex_rms_cm",
        ),
        one(
            ROOT,
            "E2-2-paired-effects",
            collection="PAIRED_PATHWAYS",
            metric="cross_path_rms",
            contrast="C-B",
        ),
    ]
    forest(axes[2], cross, ["First", "Disjoint"], ci="ci95", color=ORANGE)
    style(axes[2], "C−B cross-path RMS (engineering cm)")
    fig.suptitle(
        "Extent and fidelity improve while cross-path disagreement increases · 12 people per evaluation"
    )
    yield (
        "Figure3",
        fig,
        ["E2-1-T4-height", "E2-2-T7-height", "E2-1-paired-effects", "E2-2-paired-effects"],
        "Separate first and disjoint evaluations; original exploratory 95% intervals. Point SD ratios are descriptive.",
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), layout="constrained")
    sites = ["height", "waist", "abdomen", "hip", "chest", "neck"]
    for ax, metric, title in zip(
        axes, ["sd", "range"], ["Within-person SD", "Within-person range"], strict=True
    ):
        rows = [one(ROOT, "E3-T3-repeatability", site=s, metric=metric) for s in sites]
        forest(ax, rows, sites, key="median", ci="median_ci95")
        style(ax, "Cohort median (engineering cm)")
        ax.set_title(title)
    fig.suptitle("Common raw-contour method · 10 people, six observations each")
    yield (
        "Figure4",
        fig,
        ["E3-T3-repeatability"],
        "Aggregate companion to the repeated-observation plot: median person summaries and original 95% intervals. Individual pseudonymous points are omitted. Historical strict measurements use a different definition and eligibility.",
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout="constrained")
    waist = []
    labels = []
    for path, state in [
        ("SMPL-NICP", "canonical"),
        ("SMPL-NICP", "fitted"),
        ("CAESAR-NICP", "canonical"),
        ("CAESAR-NICP", "fitted"),
    ]:
        waist.append(
            one(ROOT, "W-T4-dataset-agreement", pathway=path, state=state, mode="end_to_end")
        )
        labels.append(path.split("-")[0] + " " + state)
    for mode, label in [
        ("end_to_end", "Pooled canonical / B1"),
        ("umbilicus_offset_raw", "Pooled canonical / offset"),
    ]:
        waist.append(one(ROOT, "W-T5-full-NOMO", mode=mode))
        labels.append(label)
    forest(axes[0], waist, labels, key="mean_advantage", ci="CI95")
    axes[0].axvline(0, color="#999999", lw=0.8)
    style(axes[0], "P advantage (engineering cm)")
    axes[0].set_title("Dependent source-waist agreement")
    rows = [
        one(ROOT, "E5S1-T3-three-way-formula-agreement", first="P", second="B1", policy=p)
        for p in ["actual", "sourceH", "bodyH"]
    ]
    forest(
        axes[1],
        rows,
        ["Actual height", "Source height controlled", "Body height controlled"],
        color=ORANGE,
    )
    axes[1].axvline(0, color="#999999", lw=0.8)
    style(axes[1], "P advantage in equation response (pp)")
    axes[1].set_title("149 participant means over 596 states")
    yield (
        "Figure5",
        fig,
        ["W-T4-dataset-agreement", "W-T5-full-NOMO", "E5S1-T3-three-way-formula-agreement"],
        "Positive favours P. Each pathway/state row uses 149 observations; each pooled waist row uses 149 people/298 observations. Controlled-height intervals cross zero. The original E5 interval is retained separately in E5-T6S-primary-person-mean.",
    )

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), layout="constrained")
    groups = ["full_source_matched", "strict_source_matched"]
    available = {r["comparison_group"] for r in read(ROOT, "S2-T10-policy-tradeoffs")}
    if groups[1] not in available:
        groups[1] = next(g for g in available if g != groups[0])
    for ax, group in zip(axes, groups, strict=True):
        rows = [r for r in read(ROOT, "S2-T10-policy-tradeoffs") if r["comparison_group"] == group]
        for r in sorted(rows, key=lambda r: r["non_dominated"]):
            method = r["policy_id"].split("/")[0]
            color = {"P": BLUE, "B1": ORANGE, "B3_offset": GREEN}.get(method, "#777777")
            ax.scatter(
                r["cross_path_mae_pp"],
                r["reference_mae_pp"],
                s=45,
                facecolors=color if r["non_dominated"] else "white",
                edgecolors=color,
            )
            if r["non_dominated"]:
                ax.annotate(
                    r["policy_id"].replace("B3_offset", "Offset"),
                    (r["cross_path_mae_pp"], r["reference_mae_pp"]),
                    xytext=(5, 6),
                    textcoords="offset points",
                    fontsize=8,
                )
        ax.set_xmargin(0.25)
        ax.set_ymargin(0.2)
        style(ax, "Canonical cross-path MAE (pp)")
        ax.set_ylabel("Dependent-source MAE (pp)")
        ax.set_title(
            f"{'Full source matched' if group == groups[0] else 'Strict shared source height'} · {rows[0]['people']} people"
        )
    fig.suptitle("Descriptive three-objective membership · filled points are nondominated")
    yield (
        "Figure6",
        fig,
        ["S2-T10-policy-tradeoffs"],
        "Companion projection of all nine saved policies per comparison group. Membership retains the full three-objective result, including absolute log(canonical/source SD ratio). The current manuscript displays six of these policies per panel; use reproduce_manuscript_figures.py for that exact display. No statistical dominance or physiological validity is asserted; objectives within each group use the same people.",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reproduced/figures"))
    args = parser.parse_args()
    check_anchors(ROOT)
    check_paper_tables(ROOT)
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {"font.family": "DejaVu Sans", "font.size": 9, "svg.hashsalt": "somatoanthropy-0.1.0"}
    )
    inventory = []
    for name, fig, inputs, caption in figures():
        outputs = {}
        for ext in ["png", "svg"]:
            p = args.output / (name + "." + ext)
            metadata = (
                {"Software": "SomatoAnthropy"}
                if ext == "png"
                else {"Date": None, "Creator": "SomatoAnthropy"}
            )
            fig.savefig(p, dpi=180, metadata=metadata)
            if ext == "svg":
                p.write_text(p.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
            outputs[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
        inventory.append(
            dict(
                figure=name,
                caption=caption,
                input_tables=inputs,
                outputs=outputs,
                bootstrap_recomputed=False,
                individual_geometry=False,
            )
        )
        plt.close(fig)
    (args.output / "captions_and_provenance.json").write_text(
        json.dumps(inventory, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print("Six aggregate figures generated; original estimates and intervals retained.")


if __name__ == "__main__":
    main()
