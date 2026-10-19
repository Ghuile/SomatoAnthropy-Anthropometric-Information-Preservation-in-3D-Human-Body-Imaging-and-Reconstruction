"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

VERSION = "e5-20261018-03"
SEED = 5182026
REPLICATES = 2000
REGISTRY = [
    dict(
        formula="RFM-2018",
        equation="64 - 20*H/W + 12*s; s=0 male, s=1 female",
        units="H,W in one common length unit",
        sites="Standing stadiometer height; right-ilium uppermost lateral border waist, end expiration",
        eligibility="Absolute: documented source sex and adult eligibility; paired response: same person, positive H/W, consistent scale. All project sites OFF_PROTOCOL; age unavailable suppresses absolute output.",
        source="https://doi.org/10.1038/s41598-018-29362-1",
    ),
    dict(
        formula="CIRC-male-DoD",
        equation="86.010*log10(A-N) - 70.041*log10(H) + 36.76",
        units="inches for absolute equation; positive H and A-N",
        sites="Stadiometer; abdomen at umbilicus; neck directly below larynx",
        eligibility="Documented male branch; engineering paired response only when scale common; physical absolute withheld",
        source="https://pmc.ncbi.nlm.nih.gov/articles/PMC4831679/",
    ),
    dict(
        formula="CIRC-female-DoD",
        equation="163.205*log10(W+Hip-N) - 97.684*log10(H) - 78.387",
        units="inches for absolute equation; positive H and W+Hip-N",
        sites="Stadiometer; narrowest torso waist; widest buttock hip; neck per AR600-9",
        eligibility="Documented female branch; engineering paired response only when scale common; physical absolute withheld",
        source="https://pmc.ncbi.nlm.nih.gov/articles/PMC10282178/",
    ),
]


def positive(*values: float | None) -> bool:
    return all((v is not None and np.isfinite(v) and (v > 0) for v in values))


def rfm(h: float, w: float, sex: int) -> float:
    """Absolute raw equation; callers must separately qualify metadata/protocol."""
    if sex not in (0, 1) or not positive(h, w):
        raise ValueError("POSITIVE_INPUTS_AND_EXPLICIT_SEX_CODING_REQUIRED")
    return float(64 - 20 * h / w + 12 * sex)


def response(h0: float, w0: float, h1: float, w1: float) -> float:
    if not positive(h0, w0, h1, w1):
        raise ValueError("INVALID_RFM_DOMAIN")
    return float(-20 * (h1 / w1 - h0 / w0))


def vector_response(
    h0: ArrayLike, w0: ArrayLike, h1: ArrayLike, w1: ArrayLike
) -> NDArray[np.float64]:
    a = np.asarray([h0, w0, h1, w1], dtype=float)
    if not np.isfinite(a).all() or (a <= 0).any():
        raise ValueError("INVALID_RFM_DOMAIN")
    return np.asarray(-20 * (a[2] / a[3] - a[0] / a[1]), dtype=np.float64)


def derivatives(h: float, w: float) -> tuple[float, float]:
    if not positive(h, w):
        raise ValueError("INVALID_RFM_DOMAIN")
    return (-20 / w, 20 * h / w**2)


def decompose(h0: float, w0: float, h1: float, w1: float) -> dict[str, Any]:
    total = response(h0, w0, h1, w1)
    height = response(h0, w0, h1, w0)
    waist = response(h0, w0, h0, w1)
    interaction = total - height - waist
    ph, pw = (height + interaction / 2, waist + interaction / 2)
    dh, dw = derivatives(h0, w0)
    return dict(
        drift_pp=total,
        absolute_pp=abs(total),
        height_only_pp=height,
        waist_only_pp=waist,
        interaction_pp=interaction,
        phi_height_pp=ph,
        phi_waist_pp=pw,
        cancellation=ph * pw < 0,
        cancelled_magnitude_pp=abs(ph) + abs(pw) - abs(total),
        dF_dH_pp_per_engineering_cm=dh,
        dF_dW_pp_per_engineering_cm=dw,
        first_order_pp=dh * (h1 - h0) + dw * (w1 - w0),
        delta_height_cm=h1 - h0,
        delta_waist_cm=w1 - w0,
        WHtR_0=w0 / h0,
        WHtR_1=w1 / h1,
        formula_zero_origin_inputs=[-20 * h0 / w0, -20 * h1 / w0, -20 * h0 / w1, -20 * h1 / w1],
    )


def circumference(
    h: float, waist: float, neck: float, hip: float | None = None, *, branch: str, unit: str = "in"
) -> float:
    if unit not in ("in", "cm"):
        raise ValueError("ORIGINAL_UNIT_REQUIRED")
    if branch not in ("male", "female") or not positive(h, waist, neck):
        raise ValueError("EXPLICIT_BRANCH_AND_INPUTS_REQUIRED")
    if branch == "female" and (not positive(hip)):
        raise ValueError("HIP_REQUIRED")
    a, b, c = (86.01, 70.041, 36.76) if branch == "male" else (163.205, 97.684, -78.387)
    x = waist - neck if branch == "male" else waist + float(hip or 0) - neck
    if x <= 0:
        raise ValueError("NONPOSITIVE_LOG_ARGUMENT")
    scale = 2.54 if unit == "cm" else 1
    return a * math.log10(x / scale) - b * math.log10(h / scale) + c


def circ_response(inputs0: dict[str, Any], inputs1: dict[str, Any], *, branch: str) -> float:
    """For fixed k, F(k*x1,k*H1)-F(k*x0,k*H0)=a log(x1/x0)-b log(H1/H0)."""
    if branch not in ("male", "female"):
        raise ValueError("DOCUMENTED_BRANCH_REQUIRED")
    xs = []
    for q in (inputs0, inputs1):
        required = (
            ("height", "abdomen", "neck")
            if branch == "male"
            else ("height", "waist", "hip", "neck")
        )
        if not positive(*(q.get(k) for k in required)):
            raise ValueError("MISSING_SECONDARY_INPUTS")
        x = q["abdomen"] - q["neck"] if branch == "male" else q["waist"] + q["hip"] - q["neck"]
        if x <= 0:
            raise ValueError("NONPOSITIVE_LOG_ARGUMENT")
        xs.append(x)
    a, b = (86.01, 70.041) if branch == "male" else (163.205, 97.684)
    return a * math.log10(xs[1] / xs[0]) - b * math.log10(inputs1["height"] / inputs0["height"])


def absolute_eligibility(record: dict[str, Any], h: float, w: float) -> dict[str, Any]:
    """Never guess demographics or promote mesh proxies to clinical stature."""
    reasons = []
    if not positive(h, w):
        reasons.append("MISSING_OR_INVALID_HEIGHT_WAIST")
    if record.get("source_sex_category") not in ("male", "female"):
        reasons.append("UNDOCUMENTED_SEX")
    if record.get("age_years") is None or record["age_years"] < 20:
        reasons.append("AGE_ELIGIBILITY_UNVERIFIED")
    return dict(
        absolute_rfm=None
        if reasons
        else float(rfm(h, w, int(record["source_sex_category"] == "female"))),
        classification="FORMULA_RESPONSE_ONLY" if reasons else "OFF_PROTOCOL_ESTIMATE",
        absolute_exclusions=reasons,
        site_compatibility="OFF_PROTOCOL: mesh extent and project waist differ from published stature/ilium protocol",
        physical_calibration=record.get("physical_calibration", "UNQUALIFIED"),
        physiological_validation=False,
    )


def seed_for(*keys: Any) -> int:
    return (
        SEED
        + int.from_bytes(hashlib.sha256("/".join(map(str, keys)).encode()).digest()[:4], "little")
    ) % (2**32 - 1)


def summarize(
    rows: list[dict[str, Any]], field: str = "drift_pp", key: str = "subject_uid"
) -> dict[str, Any]:
    """Equal person weighting; resample complete person clusters, never method rows.

    Within a stratum, per-person means of x and abs(x) are the estimands.
    Distribution quantiles use all observations with equal total person weight.
    """
    groups = defaultdict(list)
    for r in rows:
        if r.get(field) is not None and np.isfinite(r[field]):
            groups[r[key]].append(float(r[field]))
    result = dict(
        people=len(groups),
        observations=sum(map(len, groups.values())),
        replicates=REPLICATES,
        seed=seed_for(field, *sorted(groups)),
        independent_unit="dataset-local person",
    )
    if not groups:
        return dict(
            result,
            mean=None,
            mean_absolute=None,
            median=None,
            median_absolute=None,
            p90_absolute=None,
            p95_absolute=None,
            mean_ci95=None,
            mean_absolute_ci95=None,
        )
    values = [np.asarray(groups[k]) for k in sorted(groups)]
    means = np.array([x.mean() for x in values])
    abss = np.array([abs(x).mean() for x in values])
    balanced = len({len(x) for x in values}) == 1
    x = np.concatenate(values)
    rng = np.random.default_rng(result["seed"])
    idx = rng.integers(0, len(values), size=(REPLICATES, len(values)))
    result.update(
        mean=float(means.mean()),
        mean_absolute=float(abss.mean()),
        median=float(np.median(x)) if balanced else float(np.median(means)),
        median_absolute=float(np.median(abs(x))) if balanced else float(np.median(abss)),
        p90_absolute=float(np.quantile(abs(x), 0.9)) if balanced else float(np.quantile(abss, 0.9)),
        p95_absolute=float(np.quantile(abs(x), 0.95))
        if balanced
        else float(np.quantile(abss, 0.95)),
        sd_person_mean=float(means.std(ddof=1)) if len(means) > 1 else None,
        mean_ci95=np.quantile(means[idx].mean(1), [0.025, 0.975]).tolist()
        if len(means) > 1
        else None,
        mean_absolute_ci95=np.quantile(abss[idx].mean(1), [0.025, 0.975]).tolist()
        if len(means) > 1
        else None,
        positive_fraction=float(np.mean([np.mean(v > 0) for v in values])),
        negative_fraction=float(np.mean([np.mean(v < 0) for v in values])),
        proportion_people_mean_positive=float(np.mean(means > 0)),
        proportion_people_mean_negative=float(np.mean(means < 0)),
        quantile_unit="observations; balanced person weight"
        if balanced
        else "person means; unbalanced observations",
        **{
            f"fraction_abs_gt_{t}_pp": float(np.mean([np.mean(abs(v) > t) for v in values]))
            for t in (1, 3, 5)
        },
    )
    return result


def grouped(
    rows: list[dict[str, Any]], keys: list[str], field: str = "drift_pp"
) -> list[dict[str, Any]]:
    groups = defaultdict(list)
    for r in rows:
        groups[tuple((r.get(k) for k in keys))].append(r)
    return [
        dict(zip(keys, k), **summarize(v, field))
        for k, v in sorted(groups.items(), key=lambda x: str(x[0]))
    ]
