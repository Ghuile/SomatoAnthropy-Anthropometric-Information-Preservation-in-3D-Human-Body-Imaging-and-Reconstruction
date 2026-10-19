"""Descriptive paired agreement for one independent value per person."""

import numpy as np


def agreement(source, target):
    """Lin CCC uses population moments; limits use sample SD of target-source.

    The caller must collapse dependent observations within person first and
    supply a complete finite pair. Limits are descriptive normal-theory limits,
    not confidence intervals or evidence of anatomical/clinical validity.
    """
    x, y = np.asarray(source, float), np.asarray(target, float)
    if x.ndim != 1 or x.shape != y.shape or len(x) < 2 or not np.isfinite([x, y]).all():
        raise ValueError("AT_LEAST_TWO_COMPLETE_FINITE_PERSON_PAIRS_REQUIRED")
    dx, dy = x - x.mean(), y - y.mean()
    covariance = np.mean(dx * dy)
    denominator = np.mean(dx * dx) + np.mean(dy * dy) + (x.mean() - y.mean()) ** 2
    correlation_denominator = np.sqrt(np.sum(dx * dx) * np.sum(dy * dy))
    delta = y - x
    bias, sd = float(delta.mean()), float(delta.std(ddof=1))
    return dict(
        people=len(x),
        mean_source=float(x.mean()),
        mean_target=float(y.mean()),
        ccc=float(2 * covariance / denominator) if denominator > 0 else None,
        pearson_r=float(np.sum(dx * dy) / correlation_denominator)
        if correlation_denominator > 0
        else None,
        bias=bias,
        difference_sd=sd,
        loa_lower=bias - 1.96 * sd,
        loa_upper=bias + 1.96 * sd,
        mae=float(np.abs(delta).mean()),
        rmse=float(np.sqrt(np.mean(delta**2))),
        ccc_moment_ddof=0,
        difference_sd_ddof=1,
        loa_multiplier=1.96,
        independent_unit="one paired value per person",
        confidence_intervals_recomputed=False,
    )
