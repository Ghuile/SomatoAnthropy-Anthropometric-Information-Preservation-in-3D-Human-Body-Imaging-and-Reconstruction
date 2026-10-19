"""An arms-out replay cannot silently change identity, morphology or expression."""

import numpy as np
import pytest

from somatoanthropy.geometry.anthropometry.t90_remeasurement import (
    cohort_ids,
    transfer_t90,
)


def controls():
    return {
        "identity_coeffs": np.arange(45, dtype=np.float32)[None],
        "lbs_model_params": np.arange(204, dtype=np.float32)[None],
        "face_expr_coeffs": np.arange(72, dtype=np.float32)[None],
    }


def test_transfer_preserves_non_articulation_and_does_not_mutate_inputs():
    original = controls()
    reference = -np.ones((1, 204), dtype=np.float32)
    result = transfer_t90(original, reference)
    np.testing.assert_array_equal(result["lbs_model_params"][:, :130], reference[:, :130])
    np.testing.assert_array_equal(
        result["lbs_model_params"][:, 130:], original["lbs_model_params"][:, 130:]
    )
    for key in ("identity_coeffs", "face_expr_coeffs"):
        np.testing.assert_array_equal(result[key], original[key])
    result["identity_coeffs"][0, 0] = 100
    assert original["identity_coeffs"][0, 0] == 0
    assert original["lbs_model_params"][0, 0] == 0


def test_malformed_and_nonfinite_controls_fail_before_replay():
    for bad in (np.zeros((204,)), np.full((1, 204), np.nan)):
        with pytest.raises(ValueError):
            transfer_t90(controls(), bad)
    original = controls()
    original["identity_coeffs"][0, 0] = np.inf
    with pytest.raises(ValueError):
        transfer_t90(original, np.zeros((1, 204)))


def test_cohort_preserves_order_but_rejects_missing_extra_or_duplicate_ids():
    ids = [f"subject-{i}" for i in range(60)]
    assert cohort_ids(ids, list(reversed(ids))) == ids
    for other in (ids[:-1], ids[:-1] + ["extra"], ids[:-1] + [ids[0]]):
        with pytest.raises(ValueError):
            cohort_ids(ids, other)
