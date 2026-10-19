"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

VERSION = "e5s1-20261018-01"
SEED = 51812601
DRAWS = 4000
TOL = 1e-10
METHODS = ("P", "B1", "B3_offset")
POLICIES = ("actual", "sourceH", "bodyH")
CELLS = {(p, s) for p in ("SMPL-NICP", "CAESAR-NICP") for s in ("fitted", "canonical")}


def coordinate(h: float, w: float) -> float:
    """Zero-origin response coordinate; never an absolute BF estimate."""
    if not np.isfinite([h, w]).all() or min(h, w) <= 0:
        raise ValueError("POSITIVE_FINITE_HEIGHT_AND_WAIST_REQUIRED")
    return float(-20 * h / w)


def response(h0: float, w0: float, h1: float, w1: float) -> float:
    coordinate(h0, w0)
    coordinate(h1, w1)
    return float(-20 * (h1 / w1 - h0 / w0))


def evaluate(hs: float, ws: float, hb: float, wm: float) -> dict[str, Any]:
    actual = response(hs, ws, hb, wm)
    waist = response(hs, ws, hs, wm)
    height = response(hs, wm, hb, wm)
    body = response(hb, ws, hb, wm)
    cancellation = abs(waist) + abs(height) - abs(actual)
    if cancellation < -TOL or abs(actual - waist - height) > TOL:
        raise ArithmeticError("EXACT_DECOMPOSITION_FAILED")
    comp = ws * hb / hs
    return dict(
        actual=actual,
        sourceH=waist,
        bodyH=body,
        waist_contribution_pp=waist,
        height_contribution_pp=height,
        cancellation_pp=cancellation,
        opposing=waist * height < 0,
        compensating_waist_cm=comp,
        waist_error_cm=wm - ws,
        compensating_distance_cm=abs(wm - comp),
        four_coordinates=[
            coordinate(hs, ws),
            coordinate(hb, ws),
            coordinate(hs, wm),
            coordinate(hb, wm),
        ],
        decomposition_residual_pp=actual - waist - height,
    )


def preference(a: float, tol: float = TOL) -> str:
    return "P" if a > tol else "B1" if a < -tol else "tie"


def complete_people(rows: list[dict[str, Any]]) -> set[str]:
    groups: dict[str, list[Any]] = defaultdict(list)
    for r in rows:
        groups[r["subject_uid"]].append((r["pathway"], r["state"]))
    return {k for k, v in groups.items() if len(v) == 4 and set(v) == CELLS}


def summary(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    """Resample people after within-person means; reject missing/nonfinite values.

    Median is of participant means; observation quantiles are explicitly named.
    The same random indices are used across methods/policies in a fixed cohort.
    """
    groups: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        x = r[field]
        if x is None or not np.isfinite(x):
            raise ValueError("NO_IMPUTATION_OR_SILENT_ROW_DROPPING")
        groups[r["subject_uid"]].append(float(x))
    if not groups:
        raise ValueError("EMPTY_COHORT")
    vs = [np.array(groups[k]) for k in sorted(groups)]
    if len({len(x) for x in vs}) != 1:
        raise ValueError("UNBALANCED_STRATUM_REQUIRES_EXPLICIT_PROTOCOL")
    means = np.array([x.mean() for x in vs])
    ae = np.array([np.abs(x).mean() for x in vs])
    obs = np.concatenate(vs)
    idx = np.random.default_rng(SEED).integers(0, len(vs), (DRAWS, len(vs)))

    def ci(x: Any) -> Any:
        return np.quantile(x[idx].mean(1), [0.025, 0.975]).tolist()

    return dict(
        people=len(vs),
        observations=len(obs),
        mean=float(means.mean()),
        median=float(np.median(means)),
        mean_ci95=ci(means),
        median_ci95=np.quantile(np.median(means[idx], axis=1), [0.025, 0.975]).tolist(),
        mean_absolute=float(ae.mean()),
        median_absolute=float(np.median(ae)),
        mean_absolute_ci95=ci(ae),
        observation_median=float(np.median(obs)),
        observation_p90_absolute=float(np.quantile(abs(obs), 0.9)),
        observation_p95_absolute=float(np.quantile(abs(obs), 0.95)),
        participant_p90_absolute=float(np.quantile(ae, 0.9)),
        participant_p95_absolute=float(np.quantile(ae, 0.95)),
        person_positive_count=int(np.sum(means > TOL)),
        person_negative_count=int(np.sum(means < -TOL)),
        person_ties=int(np.sum(abs(means) <= TOL)),
        person_positive_fraction=float(np.mean(means > TOL)),
        person_negative_fraction=float(np.mean(means < -TOL)),
        observation_positive_fraction=float(np.mean(obs > TOL)),
        observation_negative_fraction=float(np.mean(obs < -TOL)),
        observation_ties=int(np.sum(abs(obs) <= TOL)),
        sd_person_mean=float(means.std(ddof=1)) if len(vs) > 1 else None,
        seed=SEED,
        draws=DRAWS,
    )
