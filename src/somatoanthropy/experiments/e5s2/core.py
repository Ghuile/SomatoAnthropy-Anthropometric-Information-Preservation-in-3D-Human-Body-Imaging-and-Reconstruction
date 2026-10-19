"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.stats import rankdata

from somatoanthropy.experiments.e5s1.core import coordinate as coordinate

VERSION = "e5s2-20261019-01"
SEED = 51912601
DRAWS = 4000
METHODS = ("P", "B1", "B3_offset", "B2")
MODES = ("end_to_end", "site_raw", "site_tape")
THRESHOLDS = (1e-08, 0.001, 0.01, 0.1, 0.25)
HEIGHTS = ("H1", "H2", "H3_strict", "H3_t0.001", "H3_t0.01", "H3_t0.1", "H3_t0.25")
PATHS = ("SMPL-NICP", "CAESAR-NICP")


def valid(*values: Any) -> bool:
    return all((v is not None and np.isfinite(v) and (v > 0) for v in values))


def anchor(a: float, b: float, tolerance: float) -> float | None:
    if not valid(a, b):
        return None
    return float(np.median([a, b])) if abs(a - b) <= tolerance else None


def indices(n: int) -> Any:
    return np.random.default_rng(SEED).integers(0, n, (DRAWS, n))


def stats(values: Any) -> dict[str, Any]:
    """Exactly one value per person; caller supplies explicit matched aggregation."""
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < 2 or (not np.isfinite(x).all()):
        raise ValueError("AT_LEAST_TWO_FINITE_PERSON_VALUES_REQUIRED")
    boot = x[indices(len(x))]

    def ci(z: Any) -> Any:
        return np.quantile(z, [0.025, 0.975]).tolist()

    return dict(
        people=len(x),
        mean=float(x.mean()),
        median=float(np.median(x)),
        sd=float(x.std(ddof=1)),
        p90=float(np.quantile(x, 0.9)),
        p95=float(np.quantile(x, 0.95)),
        mean_ci95=ci(boot.mean(1)),
        median_ci95=ci(np.median(boot, axis=1)),
        sd_ci95=ci(boot.std(1, ddof=1)),
        p90_ci95=ci(np.quantile(boot, 0.9, axis=1)),
        p95_ci95=ci(np.quantile(boot, 0.95, axis=1)),
        seed=SEED,
        draws=DRAWS,
    )


def rank(a: Any, b: Any) -> float | None:
    a, b = (rankdata(a), rankdata(b))
    if np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def repeated_person(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) != 6 or len({r["observation_uid"] for r in rows}) != 6:
        raise ValueError("EXACTLY_SIX_DISTINCT_OBSERVATIONS_REQUIRED")
    x = np.array([r["q"] for r in rows])
    pair = [abs(x[j] - x[i]) for i in range(6) for j in range(i + 1, 6)]
    return dict(
        sd_pp=float(x.std(ddof=1)),
        range_pp=float(np.ptp(x)),
        mad_pp=float(np.median(abs(x - np.median(x)))),
        mean_pairwise_absolute_pp=float(np.mean(pair)),
        observations=6,
    )


def pareto(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Minimise inconsistency, dependent error and distance from source SD ratio 1.

    All rows must share the exact cohort. Diversity matching is descriptive, not
    maximisation of variance or a validated physiological objective.
    """
    if len({tuple(r["cohort"]) for r in rows}) != 1:
        raise ValueError("PARETO_REQUIRES_IDENTICAL_PARTICIPANTS")
    fields = ("cross_path_mae_pp", "reference_mae_pp", "sd_ratio_distance")
    result = []
    for r in rows:
        dominators = [
            q["policy_id"]
            for q in rows
            if all((q[k] <= r[k] for k in fields)) and any((q[k] < r[k] for k in fields))
        ]
        result.append(dict(r, non_dominated=not dominators, dominated_by=dominators))
    return result
