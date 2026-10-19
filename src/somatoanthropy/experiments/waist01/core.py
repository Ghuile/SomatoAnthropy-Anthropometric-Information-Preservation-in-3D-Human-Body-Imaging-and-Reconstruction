"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
from collections import defaultdict

import numpy as np

VERSION = "waist01-20261018-01"
UPSTREAM = "a2140a74555a6382e1712ec1a5d8dc939b59e655"
SEED = 18012601
PHYSICAL_FIELD = "NaturalWAIST_Circ"


def key(value):
    return hashlib.sha256(value.encode()).hexdigest()[:20]


def canonical(vertices):
    """Engineering m Y-up -> Z-up +Y front, float32 as upstream, floor aligned."""
    v = np.asarray(vertices, float)
    if v.ndim != 2 or v.shape[1] != 3 or (not np.isfinite(v).all()):
        raise ValueError("FINITE_VERTICES_REQUIRED")
    out = np.column_stack((v[:, 0], -v[:, 2], v[:, 1])).astype(np.float32)
    out[:, 2] -= out[:, 2].min()
    return out


def descriptors(vertices, up=1):
    """Source axial envelope proxy; topology/pose dependent, not anatomical limbs."""
    z = np.asarray(vertices, float)[:, up]
    a, b, d, e = np.quantile(z, [0.05, 0.5, 0.9, 0.99])
    h = float(np.ptp(z))
    if h <= 0 or b <= a:
        raise ValueError("NONDEGENERATE_SOURCE_REQUIRED")
    return dict(
        source_axial_ratio=float((d - b) / (b - a)),
        source_top_tail=float((z.max() - e) / h),
        source_extent=h,
        descriptor="source vertex axial quantiles; not anatomical torso/leg lengths",
    )


def challenge(rows, per_group=12):
    """Round-robin within-family source ranks; D/B/C/A without replacement.

    G2/G3 targets remain anatomically unqualified when only envelope proxies
    exist. No comparative measurements or visual preferences enter this rule.
    """
    if len({r["subject_uid"] for r in rows}) != len(rows):
        raise ValueError("ONE_ROW_PER_PARTICIPANT")
    result, used = ([], set())
    families = sorted({r["dataset"] for r in rows})
    for group in ("G4", "G2", "G3", "G1"):
        queues = {}
        for ds in families:
            rs = [r for r in rows if r["dataset"] == ds]
            med = np.median([r["source_axial_ratio"] for r in rs])

            def rank(r):
                ratio = r["source_axial_ratio"]
                primary = (
                    (not r["historical_fallback"], -r["source_top_tail"])
                    if group == "G4"
                    else (ratio,)
                    if group == "G2"
                    else (-ratio,)
                    if group == "G3"
                    else (abs(ratio - med),)
                )
                return (*primary, r["subject_uid"])

            queues[ds] = sorted(rs, key=rank)
        count = 0
        while count < per_group:
            changed = False
            for ds in families:
                available = [r for r in queues[ds] if r["subject_uid"] not in used]
                if available and count < per_group:
                    r = available[0]
                    result.append(dict(r, challenge_group=group))
                    used.add(r["subject_uid"])
                    count += 1
                    changed = True
            if not changed:
                break
    return result


def eligibility(ref):
    if ref.get("conditioning_target"):
        return "CONDITIONING_SENSITIVITY_ONLY"
    if ref.get("tier") == "R1":
        return (
            "INDEPENDENT_PHYSICAL"
            if all(
                (ref.get(k) for k in ("units_verified", "site_verified", "independence_verified"))
            )
            else "R4_UNQUALIFIED_PHYSICAL"
        )
    if ref.get("tier") == "R2":
        return (
            "INDEPENDENT_SURFACE"
            if ref.get("independently_defined_site")
            else "R4_UNQUALIFIED_SITE"
        )
    return "DEPENDENT_ENGINEERING_PROXY" if ref.get("tier") == "R3" else "R4_UNAVAILABLE"


def advantage(ours, clad, reference):
    if any((v is None or not np.isfinite(v) or v <= 0 for v in (ours, clad, reference))):
        return None
    return float(abs(clad - reference) - abs(ours - reference))


def participant_values(rows, field):
    groups = defaultdict(list)
    for r in rows:
        if r.get(field) is not None and np.isfinite(r[field]):
            groups[r["subject_uid"]].append(float(r[field]))
    return np.array([np.mean(v) for _, v in sorted(groups.items())])


def statistics(rows, field="advantage_cm", replicates=2000):
    x = participant_values(rows, field)
    if not len(x):
        return dict(people=0, observations=len(rows), mean=None, median=None, ci95=None)
    rng = np.random.default_rng(SEED)
    means = x[rng.integers(0, len(x), (replicates, len(x)))].mean(1)
    return dict(
        people=len(x),
        observations=len(rows),
        mean=float(x.mean()),
        median=float(np.median(x)),
        ci95=np.quantile(means, [0.025, 0.975]).tolist() if len(x) > 1 else None,
        ours_fraction=float(np.mean(x > 0)),
        clad_fraction=float(np.mean(x < 0)),
        ties_fraction=float(np.mean(x == 0)),
    )


def errors(rows, field):
    valid = [r for r in rows if r.get(field) is not None and r.get("reference_cm") is not None]
    for r in valid:
        r = dict(r)
    groups = defaultdict(list)
    for r in valid:
        groups[r["subject_uid"]].append(r[field] - r["reference_cm"])
    if not groups:
        return dict(mae=None, rmse=None, bias=None, median_absolute=None, p95_absolute=None)
    ae = [float(np.mean(np.abs(v))) for v in groups.values()]
    return dict(
        mae=float(np.mean(ae)),
        rmse=float(np.sqrt(np.mean([np.mean(np.square(v)) for v in groups.values()]))),
        bias=float(np.mean([np.mean(v) for v in groups.values()])),
        median_absolute=float(np.median(ae)),
        p95_absolute=float(np.quantile(ae, 0.95)),
    )
