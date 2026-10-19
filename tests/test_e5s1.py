"""Analytical fixtures, not empirical evidence."""

import numpy as np
import pytest

from somatoanthropy.experiments.e5s1.core import (
    CELLS,
    complete_people,
    coordinate,
    evaluate,
    preference,
    response,
    summary,
)


@pytest.mark.parametrize(
    "hs,ws,hb,wm", [(180, 90, 171, 85.5), (170, 80, 175, 83), (160, 95, 158, 94)]
)
def test_analytical_response_and_sex_cancellation(hs, ws, hb, wm):
    q = evaluate(hs, ws, hb, wm)
    for sex in (0, 1):
        assert q["actual"] == pytest.approx(
            (64 - 20 * hb / wm + 12 * sex) - (64 - 20 * hs / ws + 12 * sex)
        )
    assert q["actual"] == pytest.approx(q["sourceH"] + q["height_contribution_pp"])
    assert q["cancellation_pp"] >= -1e-10
    assert q["compensating_waist_cm"] == ws * hb / hs
    assert response(hs, ws, hb, q["compensating_waist_cm"]) == pytest.approx(0, abs=1e-12)
    assert evaluate(hs * 100, ws * 100, hb * 100, wm * 100)["actual"] == pytest.approx(q["actual"])


@pytest.mark.parametrize("h,w", [(0, 80), (180, 0), (-1, 80), (180, np.nan), (np.inf, 80)])
def test_domain_and_no_clipping(h, w):
    with pytest.raises(ValueError):
        coordinate(h, w)


def test_unbounded_response_no_arbitrary_sex_or_clipping():
    assert coordinate(1000, 1) == -20000
    assert coordinate(1, 1000) == -0.02


def test_identical_waist_shared_height_and_direction():
    assert evaluate(180, 90, 170, 90)["sourceH"] == 0
    q = evaluate(180, 90, 180, 95)
    assert q["actual"] == q["sourceH"] == q["bodyH"]
    assert preference(2) == "P" and preference(-2) == "B1"
    assert preference(0) == "tie"
    assert evaluate(180, 90, 171, 85.5)["opposing"]


def test_complete_four_cells_and_no_duplicate_substitution():
    rows = [dict(subject_uid="a", pathway=p, state=s) for p, s in CELLS]
    assert complete_people(rows) == {"a"}
    assert not complete_people(rows[:-1])
    assert not complete_people([*rows[:-1], rows[0]])


def test_participant_clustering_bootstrap_reproducibility_and_missing():
    rows = [dict(subject_uid=p, x=v) for p, v in [("a", 1), ("a", 3), ("b", 9), ("b", 11)]]
    s = summary(rows, "x")
    assert s["people"] == 2 and s["observations"] == 4
    assert s["mean"] == 6 and s["median"] == 6
    assert s == summary(rows[::-1], "x")
    assert s["draws"] >= 2000
    with pytest.raises(ValueError):
        summary([dict(subject_uid="a", x=None)], "x")
    with pytest.raises(ValueError):
        summary(rows[:-1], "x")
