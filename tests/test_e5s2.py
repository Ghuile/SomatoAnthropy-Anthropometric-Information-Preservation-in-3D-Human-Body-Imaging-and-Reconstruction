"""Analytical fixtures for derived estimands; never participant evidence."""

import numpy as np
import pytest

from somatoanthropy.experiments.e5s2.core import (
    HEIGHTS,
    THRESHOLDS,
    anchor,
    coordinate,
    pareto,
    rank,
    repeated_person,
    stats,
)


@pytest.mark.parametrize("h,w", [(0, 80), (-1, 80), (180, 0), (np.nan, 80), (180, np.inf)])
def test_invalid_formula_inputs(h, w):
    with pytest.raises(ValueError):
        coordinate(h, w)


@pytest.mark.parametrize("scale", [0.01, 1, 100])
def test_unit_invariance_and_same_person_sex_cancellation(scale):
    a, b = coordinate(180 * scale, 90 * scale), coordinate(170 * scale, 85 * scale)
    assert a == -40 and b == -40
    for sex in (0, 1):
        assert (64 + b + 12 * sex) - (64 + a + 12 * sex) == b - a


@pytest.mark.parametrize("t", THRESHOLDS)
def test_symmetric_anchor_and_fixed_threshold(t):
    assert anchor(180, 180 + t / 2, t) == anchor(180 + t / 2, 180, t)
    assert anchor(180, 180 + 2 * t, t) is None
    assert anchor(180, 180, t) == 180


@pytest.mark.parametrize("a,b", [(None, 180), (np.nan, 180), (0, 180), (180, -1)])
def test_no_anchor_imputation(a, b):
    assert anchor(a, b, 0.25) is None


def test_frozen_ladder_and_no_outcome_argument():
    assert THRESHOLDS == (1e-8, 0.001, 0.01, 0.1, 0.25)
    assert len(HEIGHTS) == 7
    with pytest.raises(TypeError):
        anchor(180, 180, 0.1, formula_error=0)


def test_person_statistical_quantities_and_deterministic_bootstrap():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    r = stats(x)
    assert r == stats(x)
    assert r["people"] == 4 and r["draws"] == 4000
    assert r["mean"] == r["median"] == 2.5
    assert r["sd"] == pytest.approx(np.sqrt(5 / 3))
    assert r["p90"] == pytest.approx(3.7)


@pytest.mark.parametrize("x", [[], [1], [1, np.nan], [[1, 2], [3, 4]]])
def test_person_stats_reject_missing_and_observation_matrices(x):
    with pytest.raises(ValueError):
        stats(x)


def test_rank_ties_and_no_undefined_rank_substitution():
    assert rank([1, 2, 2], [3, 1, 1]) == pytest.approx(-1)
    assert rank([1, 1], [2, 3]) is None


def test_six_observations_remain_one_person_and_fifteen_pairs():
    rs = [dict(q=float(i), observation_uid=str(i)) for i in range(6)]
    r = repeated_person(rs)
    assert r["observations"] == 6 and r["range_pp"] == 5
    assert r["sd_pp"] == pytest.approx(np.std(np.arange(6), ddof=1))
    assert r["mad_pp"] == 1.5
    assert r["mean_pairwise_absolute_pp"] == pytest.approx(35 / 15)
    with pytest.raises(ValueError):
        repeated_person(rs[:-1])
    with pytest.raises(ValueError):
        repeated_person([*rs[:-1], rs[0]])


def test_pareto_tradeoffs_and_identical_cohort_requirement():
    rows = [
        dict(
            policy_id=k,
            cohort=["a", "b"],
            cross_path_mae_pp=x,
            reference_mae_pp=y,
            sd_ratio_distance=z,
        )
        for k, x, y, z in [("a", 1, 2, 0.1), ("b", 2, 1, 0.1), ("c", 3, 3, 0.2)]
    ]
    r = pareto(rows)
    assert [x["non_dominated"] for x in r] == [True, True, False]
    assert r[-1]["dominated_by"] == ["a", "b"]
    rows[0]["cohort"] = ["a"]
    with pytest.raises(ValueError):
        pareto(rows)
