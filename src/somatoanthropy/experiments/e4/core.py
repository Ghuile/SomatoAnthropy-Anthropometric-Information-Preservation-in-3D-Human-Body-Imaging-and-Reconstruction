"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

SITES = ("height", "abdomen", "waist", "hip", "neck", "chest")
PRIMARY = SITES[:4]
UNIT = "engineering_cm"


def seed_for(seed: int, *keys: str) -> int:
    digest = hashlib.sha256("/".join(keys).encode()).digest()
    return (seed + int.from_bytes(digest[:4], "little")) % (2**32 - 1)


def measurement(q: dict[str, Any], *, strict: bool = False) -> float | None:
    """Geometric validity takes precedence over inherited proxy-valid flags."""
    v = q.get("engineering_value_cm")
    if q.get("geometry_quality") != "VALID" or v is None:
        return None
    if not np.isfinite(v) or float(v) <= 0:
        return None
    if strict and (
        q.get("quality_state") == "SITE_AMBIGUOUS"
        or q.get("historical_quality_state") == "SITE_AMBIGUOUS"
        or q.get("fallback_applied", False)
    ):
        return None
    return float(v)


def compatible(records: list[dict[str, Any]], pose: str) -> bool:
    return bool(records) and all((r.get("unit") == UNIT and r.get("pose") == pose for r in records))


def paired_values(sa: float, sb: float, ma: float, mb: float) -> dict[str, float]:
    x = np.asarray([sa, sb, ma, mb], dtype=float)
    if not np.isfinite(x).all():
        raise ValueError("FINITE_FOUR_REPRESENTATION_VALUES_REQUIRED")
    ds, dm = (sa - sb, ma - mb)
    ea, eb = (ma - sa, mb - sb)
    change = dm - ds
    if not np.isclose(change, ea - eb, rtol=0, atol=1e-10):
        raise ValueError("SIGNED_DECOMPOSITION_FAILED")
    return dict(
        source_signed=ds,
        source_absolute=abs(ds),
        mhr_signed=dm,
        mhr_absolute=abs(dm),
        delta_signed=change,
        delta_absolute=abs(dm) - abs(ds),
        path_a=ea,
        path_b=eb,
    )


def unique_people(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = sorted(rows, key=lambda r: r["subject_uid"])
    if len({r["subject_uid"] for r in rows}) != len(rows):
        raise ValueError("ONE_OBSERVATION_PER_PARTICIPANT_PER_ESTIMAND_REQUIRED")
    return rows


def describe(values: list[float] | np.ndarray) -> dict[str, Any]:
    x = np.asarray(values, dtype=float)
    if not np.isfinite(x).all():
        raise ValueError("NONFINITE_SUMMARY_INPUT")
    result: dict[str, Any] = dict(n=len(x))
    keys = ("mean", "median", "sd", "mae", "rmse", "q05", "q25", "q75", "q95")
    result.update(dict.fromkeys(keys))
    if len(x):
        result.update(
            mean=float(x.mean()),
            median=float(np.median(x)),
            sd=float(x.std(ddof=1)) if len(x) > 1 else None,
            mae=float(np.abs(x).mean()),
            rmse=float(np.sqrt(np.mean(x**2))),
            **dict(zip(keys[5:], np.quantile(x, [0.05, 0.25, 0.75, 0.95]).tolist())),
        )
    return result


def bootstrap(values: list[float] | np.ndarray, *, seed: int, replicates: int) -> dict[str, Any]:
    x = np.asarray(values, dtype=float)
    if not np.isfinite(x).all() or replicates < 100:
        raise ValueError("FINITE_VALUES_AND_AT_LEAST_100_REPLICATES_REQUIRED")
    if len(x) < 2:
        return dict(mean_ci95=None, median_ci95=None, mean_ci_family=None, draws=[])
    rng = np.random.default_rng(seed)
    sample = x[rng.integers(0, len(x), size=(replicates, len(x)))]
    means, medians = (sample.mean(1), np.median(sample, axis=1))
    return dict(
        mean_ci95=np.quantile(means, [0.025, 0.975]).tolist(),
        median_ci95=np.quantile(medians, [0.025, 0.975]).tolist(),
        mean_ci_family=np.quantile(means, [0.00625, 0.99375]).tolist(),
        draws=dict(mean=means.tolist(), median=medians.tolist()),
    )


def effect(values: list[float]) -> dict[str, Any]:
    x = np.asarray(values)
    if not len(x):
        return dict(increased=None, decreased=None, unchanged=None, dz=None)
    sd = x.std(ddof=1) if len(x) > 1 else 0
    return dict(
        increased=float(np.mean(x > 1e-10)),
        decreased=float(np.mean(x < -1e-10)),
        unchanged=float(np.mean(np.abs(x) <= 1e-10)),
        dz=float(x.mean() / sd) if sd > 0 else None,
        zero_tolerance_purpose="1e-10 arithmetic roundoff only",
    )
