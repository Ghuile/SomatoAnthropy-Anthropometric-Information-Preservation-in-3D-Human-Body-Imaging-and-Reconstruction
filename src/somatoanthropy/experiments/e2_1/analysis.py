"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import numpy as np

from somatoanthropy.experiments.e4.core import bootstrap, describe


def paired_summary(values, seed):
    result = describe(values)
    boot = bootstrap(values, seed=seed, replicates=2000)
    return dict(
        result,
        ci95=boot["mean_ci95"],
        uncertainty="2000 participant-level paired percentile bootstrap; exploratory, unadjusted",
    )


def ratio_effect(source, locked, released, seed):
    x, b, c = (np.asarray(q, float) for q in (source, locked, released))
    if len(x) < 2 or not np.isfinite([x, b, c]).all() or np.ptp(x) == 0:
        raise ValueError("FINITE_VARYING_PAIRED_PARTICIPANTS_REQUIRED")
    rng = np.random.default_rng(seed)
    ids = rng.integers(0, len(x), (2000, len(x)))
    denom = x[ids].std(1, ddof=1)
    keep = denom > 0
    draws = (c[ids].std(1, ddof=1)[keep] - b[ids].std(1, ddof=1)[keep]) / denom[keep]
    return dict(
        n=len(x),
        mean=float((c.std(ddof=1) - b.std(ddof=1)) / x.std(ddof=1)),
        ci95=np.quantile(draws, [0.025, 0.975]).tolist(),
        discarded_constant_source_draws=int((~keep).sum()),
        statistic="SD(C)/SD(source) minus SD(B)/SD(source)",
    )


def value(q, quantity):
    return q.get(quantity) if q.get("geometry_quality") == "VALID" else None


def anthropometric_rows(record):
    out = []
    for arm, r in record["arms"].items():
        if r["status"] != "EVALUATED":
            continue
        for state in ("fitted", "canonical"):
            for site in ("waist", "abdomen", "hip", "chest", "neck"):
                quantity = "tape_envelope_cm" if site in ("hip", "neck") else "raw_contour_cm"
                methods = ["E2_midpoint_proxy"] if site == "waist" else ["E2_surface_proxy"]
                if state == "fitted":
                    methods += ["fixed_historical_source_plane"]
                for method in methods:
                    fixed = method == "fixed_historical_source_plane"
                    sq = record["source_historical" if fixed else "source_proxy"].get(site, {})
                    tq = r[state]["fixed_source_plane" if fixed else "proxy"].get(site, {})
                    source = sq.get("value") if fixed else value(sq, quantity)
                    target = value(tq, quantity)
                    error = None if source is None or target is None else target - source
                    out.append(
                        dict(
                            subject_uid=record["subject_uid"],
                            collection=record["collection"],
                            partition=record["partition"],
                            arm=arm,
                            state=state,
                            site=site,
                            quantity=quantity,
                            method=method,
                            source=source,
                            target=target,
                            error=error,
                            source_valid=source is not None,
                            target_valid=target is not None,
                            source_reason=sq.get("reason"),
                            target_reason=tq.get("reason"),
                            fallback_applied=sq.get("fallback_applied", False),
                            anatomical_evidence="UNQUALIFIED",
                            proxy_status=True,
                        )
                    )
    return out
