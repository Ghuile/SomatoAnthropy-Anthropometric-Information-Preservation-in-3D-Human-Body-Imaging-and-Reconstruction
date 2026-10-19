"""Original manuscript drawing statements with portable SVG output and public inputs.

No statistics, confidence intervals or Pareto membership are estimated here.
The drawing statements retain the three source generators; see figure provenance.
"""

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
OUT = args.output
OUT.mkdir(parents=True, exist_ok=True)
for i in range(1, 7):
    if (OUT / f"Figure{i}.svg").exists():
        raise FileExistsError("Use a fresh output directory")
W = 13.86 * 72 / 2.54
C = {
    "ink": "#203744",
    "muted": "#536873",
    "grid": "#DFE7EB",
    "P": "#087F91",
    "B1": "#B95729",
    "B3_offset": "#6164A9",
    "B": "#245675",
    "C": "#B95729",
}


def load(name):
    return json.loads((ROOT / "results/aggregate" / (name + ".json")).read_text("utf-8"))


def one(rows, **criteria):
    found = [r for r in rows if all(r.get(k) == v for k, v in criteria.items())]
    if len(found) != 1:
        raise ValueError((criteria, len(found)))
    return found[0]


def num(x, d=2, sign=False):
    return (f"{x:+.{d}f}" if sign else f"{x:.{d}f}").replace("-", "−")


class Vector:
    def __init__(self, name, height):
        self.name = name
        self.h = height
        self.nodes = []
        self.rect(0, 0, W, height, "#FFFFFF")

    def line(self, x1, y1, x2, y2, color=C["ink"], width=0.7):
        self.nodes.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'
        )

    def rect(self, x, y, w, h, fill=None, stroke=None, width=0.8):
        self.nodes.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>'
        )

    def marker(self, x, y, color, shape="circle", filled=True, r=3.2):
        fill = color if filled else "#FFFFFF"
        if shape == "circle":
            self.nodes.append(
                f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="1"/>'
            )
        elif shape == "square":
            self.rect(x - r, y - r, 2 * r, 2 * r, fill, color, 1)
        else:
            pts = [(x, y - r * 1.2), (x + r * 1.08, y + r * 0.8), (x - r * 1.08, y + r * 0.8)]
            self.nodes.append(
                '<polygon points="'
                + " ".join(f"{a},{b}" for a, b in pts)
                + f'" fill="{fill}" stroke="{color}" stroke-width="1"/>'
            )

    def text(self, s, x, y, size=9, bold=False, anchor="start", color=C["ink"], rotate=0):
        rot = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
        self.nodes.append(
            f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}"{rot}>{html.escape(s)}</text>'
        )

    def axis(self, left, right, top, bottom, limits, ticks, fmt=str, zero=False):
        def scale(v):
            return left + (v - limits[0]) / (limits[1] - limits[0]) * (right - left)

        for t in ticks:
            x = scale(t)
            self.line(x, top, x, bottom, C["grid"], 0.6)
            self.text(fmt(t), x, bottom + 13, anchor="middle")
        self.line(left, bottom, right, bottom, C["muted"], 0.8)
        if zero and limits[0] < 0 < limits[1]:
            self.line(scale(0), top, scale(0), bottom, C["ink"], 1)
        return scale

    def interval(self, x, lo, hi, y, color=C["B"]):
        self.line(lo, y, hi, y, color, 1.3)
        self.line(lo, y - 3, lo, y + 3, color, 0.9)
        self.line(hi, y - 3, hi, y + 3, color, 0.9)
        self.marker(x, y, color, r=2.8)

    def finish(self):
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{self.h}pt" viewBox="0 0 {W} {self.h}">'
            + "".join(self.nodes)
            + "</svg>\n"
        )
        (OUT / (self.name + ".svg")).write_text(svg, encoding="utf-8", newline="\n")


f = Vector("Figure1", 448)
f.text("Study design and separate evaluation properties", 8, 17, 11, True)
f.rect(8, 36, 377, 60, "#EDF4F6", "#B9C9D1")
f.text("NOMO: 150 linked participants", 18, 53, 10.5, True)
f.text("Paired SMPL-NICP and CAESAR-NICP source pathways", 18, 70)
f.text("Fitted and canonical MHR states remain linked within participant", 18, 86)
f.text("Primary controlled studies: subsets of the same NOMO cohort", 8, 116, 10, True)
f.rect(8, 126, 180, 42, "#F6F8FA", "#B9C9D1")
f.rect(205, 126, 180, 42, "#F6F8FA", "#B9C9D1")
f.text("First evaluation", 18, 142, 10, True)
f.text("12 evaluation participants", 18, 158)
f.text("Disjoint internal replication", 215, 142, 10, True)
f.text("12 evaluation participants", 215, 158)
f.text("Four shared development participants; pathways stay linked", 8, 185)
f.rect(8, 199, 377, 43, "#EDF4F6", "#B9C9D1")
f.text("D-FAUST: 10 participants × 6 independently fitted observations", 18, 216, 10, True)
f.text("60 observations; repeated comparisons are nested within person", 18, 233)
f.text("Four properties, reported separately", 8, 263, 10, True)
boxes = [
    (8, 276, "Source fidelity", "Discrepancy from the declared", "digital source surface"),
    (205, 276, "Between-person variation", "Retained source-defined", "extent variation"),
    (8, 333, "Cross-path consistency", "Agreement between paired", "canonical representations"),
    (205, 333, "Between-pose variability", "Repeated D-FAUST fits after", "canonical transfer"),
]
for x, y, title, line1, line2 in boxes:
    f.rect(x, y, 180, 48, "#FFFFFF", "#B9C9D1")
    f.text(title, x + 9, y + 15, 10, True)
    f.text(line1, x + 9, y + 30)
    f.text(line2, x + 9, y + 42)
f.rect(8, 395, 377, 41, "#F5F3FA", "#C7C3D8")
f.text("Secondary: height–waist equation-response policies", 18, 411, 10, True)
f.text("q = −20H/W; arbitrary zero; response changes in percentage points", 18, 428)
l1 = f.finish()
rows = load("Figure2-manuscript-input")
f = Vector("Figure2", 464)
f.text("(a) Reconstruction workflow", 8, 17, 11, True)
for y, title, detail in [
    (
        30,
        "Existing 3D source representations",
        "NOMO, MPII, UCSC, FAUST and other evaluated sources",
    ),
    (
        83,
        "Source-specific geometry processing",
        "Saved frame/coordinate transforms and topology handling",
    ),
    (
        136,
        "Native MHR fitting",
        "Identity, articulation, morphology and skeletal-control permissions",
    ),
]:
    f.rect(8, y, 377, 41, "#EDF4F6", "#B9C9D1")
    f.text(title, 18, y + 16, 10, True)
    f.text(detail, 18, y + 32)
for start, end in [(71, 83), (124, 136)]:
    f.line(W / 2, start, W / 2, end, C["muted"], 0.9)
    f.line(W / 2 - 2.5, end - 3, W / 2, end, C["muted"], 0.9)
    f.line(W / 2 + 2.5, end - 3, W / 2, end, C["muted"], 0.9)
f.line(W / 2, 177, W / 2, 187, C["muted"], 0.9)
f.line(98, 187, 295, 187, C["muted"], 0.9)
for x, mid in [(8, 98), (205, 295)]:
    f.line(mid, 187, mid, 199, C["muted"], 0.9)
    f.line(mid - 2.5, 196, mid, 199, C["muted"], 0.9)
    f.line(mid + 2.5, 196, mid, 199, C["muted"], 0.9)
    f.rect(x, 199, 180, 52, "#F6F8FA", "#B9C9D1")
f.text("Own-pose reconstruction", 18, 216, 10, True)
f.text("Source-surface fidelity", 18, 234)
f.text("Canonical T90", 215, 216, 10, True)
f.text("Between-person variation and", 215, 232)
f.text("cross-path consistency", 215, 244)
f.text("(b) NOMO source-to-fitted surface fidelity", 8, 279, 11, True)
f.text("Three pathways for the same ten participants", 8, 294)
f.text("Means and original exploratory 95% participant-bootstrap CIs", 8, 309)
f.text("Mean [95% CI]", 384, 327, bold=True, anchor="end")
x = f.axis(128, 270, 334, 419, (0, 0.6), [0, 0.2, 0.4, 0.6], lambda t: num(t, 1))
for r, y in zip(rows, [340, 374, 408]):
    value = float(r["mean_engineering_cm_text"])
    lo, hi = map(float, r["mean_ci95_engineering_cm_text"])
    f.text(r["pathway"], 8, y + 3)
    f.interval(x(value), x(lo), x(hi), y, C["P"])
    f.text(f"{value:.3f} [{lo:.3f}, {hi:.3f}]", 384, y + 3, anchor="end")
f.text("Mean symmetric surface discrepancy (cm)", 199, 450, anchor="middle")
layout = f.finish()
a, b, ae, be = [
    load(n)
    for n in ("E2-1-T4-height", "E2-2-T7-height", "E2-1-paired-effects", "E2-2-paired-effects")
]
s3 = {"ratios": [], "fidelity_changes": [], "cross_path_changes": []}
for exp, label, table in [(1, "First", a), (2, "Replication", b)]:
    for path in ("SMPL-NICP", "CAESAR-NICP"):
        k = "arm" if exp == 1 else "condition"
        locked = one(
            table, collection=path, state="canonical", **{k: "locked" if exp == 1 else "B"}
        )
        released = one(
            table, collection=path, state="canonical", **{k: "released" if exp == 1 else "C"}
        )
        label2 = label + " / " + path.split("-")[0]
        s3["ratios"].append({"label": label2, "locked": locked, "released": released})
        effect = (
            one(ae, collection=path, state="fitted", metric="geometry_mean_cm")
            if exp == 1
            else one(be, collection=path, metric="surface_mean_cm", contrast="C-B")
        )
        s3["fidelity_changes"].append({"label": label2, "row": effect})
s3["cross_path_changes"] = [
    {
        "label": "First",
        "row": one(ae, collection="PAIRED_PATHWAYS", metric="cross_path_vertex_rms_cm"),
    },
    {
        "label": "Replication",
        "row": one(be, collection="PAIRED_PATHWAYS", metric="cross_path_rms", contrast="C-B"),
    },
]
f = Vector("Figure3", 470)
f.text("Controlled skeletal release: two internal evaluations", 8, 16, 11, True)
f.text("12 participants per evaluation; source pathways linked within person", 8, 31)
f.text("(a) Canonical/source vertical-extent SD ratio", 8, 54, 10, True)
f.marker(152, 68, C["B"])
f.text("Locked B", 160, 71)
f.marker(251, 68, C["C"])
f.text("Released C", 259, 71)
x = f.axis(147, 378, 79, 160, (0.15, 0.62), [0.2, 0.3, 0.4, 0.5, 0.6], lambda t: num(t, 1))
for row, y in zip(s3["ratios"], [88, 108, 128, 148]):
    f.text(row["label"], 8, y + 3)
    u, v = x(row["locked"]["sd_ratio"]), x(row["released"]["sd_ratio"])
    f.line(u, y, v, y, "#ABB9C0", 1.5)
    f.marker(u, y, C["B"])
    f.marker(v, y, C["C"])
f.text("SD ratio (dimensionless; point estimates)", 263, 188, anchor="middle")
f.text("(b) Mean source-surface error: released minus locked", 8, 214, 10, True)
x = f.axis(147, 378, 228, 309, (-0.18, -0.07), [-0.16, -0.12, -0.08], lambda t: num(t, 2))
for rec, y in zip(s3["fidelity_changes"], [237, 257, 277, 297]):
    row = rec["row"]
    f.text(rec["label"], 8, y + 3)
    f.interval(x(row["mean"]), x(row["ci95"][0]), x(row["ci95"][1]), y)
f.text("Change in surface error (cm)", 263, 337, anchor="middle")
f.text("(c) Canonical cross-path RMS: released minus locked", 8, 364, 10, True)
x = f.axis(147, 378, 377, 429, (0.25, 0.75), [0.3, 0.4, 0.5, 0.6, 0.7], lambda t: num(t, 1))
for rec, y in zip(s3["cross_path_changes"], [387, 414]):
    row = rec["row"]
    f.text(rec["label"], 8, y + 3)
    f.interval(x(row["mean"]), x(row["ci95"][0]), x(row["ci95"][1]), y, C["C"])
f.text("Change in cross-path RMS (cm)", 263, 457, anchor="middle")
l3 = f.finish()
rows = load("E3-T3-repeatability")
selected = []
f = Vector("Figure4", 464)
f.text("Between-pose variability", 8, 17, 11.5, True)
f.text("10 D-FAUST participants × 6 observations per participant", 8, 32)
f.text("Common raw-contour protocol; original 95% participant-bootstrap CIs", 8, 47)
for metric, title, heading, top, bottom, ys, lim, ticks in [
    (
        "sd",
        "(a) Within-person SD",
        70,
        88,
        216,
        [96, 117, 138, 159, 180, 201],
        (0, 3),
        [0, 1, 2, 3],
    ),
    (
        "range",
        "(b) Within-person range",
        273,
        291,
        419,
        [299, 320, 341, 362, 383, 404],
        (0, 7),
        [0, 2, 4, 6],
    ),
]:
    f.text(title, 8, heading, 10, True)
    f.text("Median [95% CI]", 384, top - 5, bold=True, anchor="end")
    x = f.axis(95, 274, top, bottom, lim, ticks)
    for site, y in zip(["height", "waist", "abdomen", "hip", "chest", "neck"], ys):
        r = one(rows, site=site, metric=metric)
        value = float(r["median"])
        ci = r["median_ci95"]
        selected.append(r)
        f.text("Vertical extent" if site == "height" else site.capitalize(), 8, y + 3)
        f.interval(x(value), x(ci[0]), x(ci[1]), y, C["P"])
        f.text(f"{value:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]", 384, y + 3, anchor="end")
    f.text(
        "Median within-person " + ("SD" if metric == "sd" else "range") + " (cm)",
        184,
        bottom + 30,
        anchor="middle",
    )
l4 = f.finish()
s5 = load("Figure5-manuscript-input")
f = Vector("Figure5", 515)
f.text("(a) Waist agreement with the dependent source proxy", 8, 16, 10.5, True)
f.text("149 participants; each stratum 149 observations; pooled canonical 298", 8, 30)
f.text("Original 95% participant-bootstrap intervals; positive favours P", 8, 44)
f.text("Mean", 384, 58, bold=True, anchor="end")
x = f.axis(153, 335, 62, 181, (-2.6, 2.7), [-2, -1, 0, 1, 2], zero=True)
for rec, y in zip(s5["panel_a"], [66, 85, 104, 123, 147, 166]):
    label = (
        rec["label"].replace("-NICP", "").replace("Pooled canonical / vs ", "Pooled canonical / ")
    )
    f.text(label, 8, y + 3)
    f.interval(x(rec["mean"]), x(rec["ci"][0]), x(rec["ci"][1]), y)
    f.text(num(rec["mean"], 3, True), 384, y + 3, anchor="end")
f.text("Comparator MAE − P MAE (cm)", 244, 210, anchor="middle")
f.line(8, 224, 385, 224, C["grid"])
f.text("(b) Height control and absolute equation-response error", 8, 242, 10.5, True)
f.text("149 participants; all pathways/states 596 observations; each path 298", 8, 256)
f.text("Source fixed / body fixed: one extent shared across both waist methods", 8, 270)
f.text("Mean", 384, 284, bold=True, anchor="end")
x = f.axis(
    153, 335, 289, 455, (-1.65, 1.25), [-1.5, -1, -0.5, 0, 0.5, 1], lambda t: num(t, 1), True
)
for rec, y in zip(s5["panel_b"], [292, 309, 326, 350, 367, 384, 408, 425, 442]):
    label = (
        rec["label"]
        .replace("-NICP", "")
        .replace("actual", "own extents")
        .replace("sourceH", "source fixed")
        .replace("bodyH", "body fixed")
    )
    f.text(label, 8, y + 3)
    f.interval(x(rec["mean"]), x(rec["ci"][0]), x(rec["ci"][1]), y)
    f.text(num(rec["mean"], 3, True), 384, y + 3, anchor="end")
f.text("B1 absolute response error − P absolute response error (pp)", W / 2, 485, anchor="middle")
f.text("Response error is relative to the named dependent source coordinate.", 8, 502)
l5 = f.finish()
policies = load("S2-T10-policy-tradeoffs")
s6 = []
for group, hs in [("full_source_matched", ("H1", "H2")), ("strict_common", ("H1", "H3_strict"))]:
    rows = [
        r for r in policies if r["comparison_group"] == group and r["policy_id"].split("/")[1] in hs
    ]
    assert len(rows) == 6
    s6.append(
        {
            "comparison_group": group,
            "rows": rows,
            "omitted_policy": "H3_t0.25" if group == "full_source_matched" else "H2",
            "membership_basis": "Original full nine-policy grid; third objective abs(log(canonical/source SD ratio)); no membership recomputation",
        }
    )
f = Vector("Figure6", 470)
f.text("Response agreement and cross-path consistency", 8, 16, 11, True)
for x0, shape, label in [
    (12, "circle", "H1: own extent"),
    (129, "square", "H2: source extent"),
    (265, "triangle", "H3: strict shared"),
]:
    f.marker(x0, 30, C["ink"], shape, False, 2.8)
    f.text(label, x0 + 8, 33)
f.marker(12, 46, C["ink"], r=2.8)
f.text("Filled: saved nondominated", 20, 49)
f.marker(199, 46, C["ink"], filled=False, r=2.8)
f.text("Outline: other saved policies", 207, 49)
for sel, top, bottom, title in zip(
    s6,
    [94, 301],
    [219, 426],
    [
        "(a) Matched source cohort: 149 participants",
        "(b) Strict shared-height cohort: 103 participants",
    ],
):
    f.text(title, 8, top - 21, 10, True)
    left, right = 61, 378
    x = f.axis(
        left, right, top, bottom, (0.15, 0.35), [0.15, 0.20, 0.25, 0.30, 0.35], lambda t: num(t, 2)
    )

    def y(v):
        return bottom - (v - 0.85) / (2.65 - 0.85) * (bottom - top)

    for tick in [1, 1.5, 2, 2.5]:
        yy = y(tick)
        f.line(left, yy, right, yy, C["grid"], 0.6)
        f.text(num(tick, 1), left - 7, yy + 3, anchor="end")
    f.text("Dependent-source MAE (pp)", 14, (top + bottom) / 2, anchor="middle", rotate=-90)
    f.text("Canonical cross-path MAE (pp)", (left + right) / 2, bottom + 30, anchor="middle")
    for row in sel["rows"]:
        method, h = row["policy_id"].split("/")
        xx, yy = x(row["cross_path_mae_pp"]), y(row["reference_mae_pp"])
        shape = "circle" if h == "H1" else "square" if h == "H2" else "triangle"
        f.marker(xx, yy, C[method], shape, row["non_dominated"], 3.3)
        label = (
            ("Offset" if method == "B3_offset" else method) + " / " + h.replace("H3_strict", "H3")
        )
        tx, anchor, dy = (xx - 7, "end", -5) if method == "P" else (xx + 7, "start", -5)
        if method == "B1" and h == "H2":
            dy = 12
        if method == "B1" and h == "H3_strict":
            dy = -8
        f.text(label, tx, yy + dy, anchor=anchor, color=C[method])
l6 = f.finish()
