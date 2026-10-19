"""Independent expected values for the added descriptive agreement estimator."""

import numpy as np
import pytest

from somatoanthropy.agreement import agreement


def test_perfect_and_shifted_agreement_distinguish_correlation_from_agreement():
    a = agreement([0, 1, 2], [0, 1, 2])
    assert a["ccc"] == pytest.approx(1)
    assert a["pearson_r"] == pytest.approx(1)
    b = agreement([0, 1, 2], [1, 2, 3])
    assert b["ccc"] == pytest.approx(4 / 7)
    assert b["pearson_r"] == pytest.approx(1)
    assert b["bias"] == b["loa_lower"] == b["loa_upper"] == 1


def test_limits_use_sample_difference_sd():
    a = agreement([0, 1, 2], [0, 2, 4])
    assert a["bias"] == 1
    assert a["difference_sd"] == 1
    assert a["loa_lower"] == pytest.approx(-0.96)
    assert a["loa_upper"] == pytest.approx(2.96)
    assert a["rmse"] == pytest.approx(np.sqrt(5 / 3))


def test_invalid_pairs_and_unidentified_constant_correlation():
    with pytest.raises(ValueError):
        agreement([1, 2], [1, np.nan])
    with pytest.raises(ValueError):
        agreement([1], [1])
    a = agreement([2, 2], [2, 2])
    assert a["ccc"] is None and a["pearson_r"] is None
