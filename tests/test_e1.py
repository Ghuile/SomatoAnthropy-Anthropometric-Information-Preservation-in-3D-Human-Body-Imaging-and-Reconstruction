"""Engineering fixtures test estimators, never stand in for human evidence."""

import numpy as np
import pytest

from somatoanthropy.experiments.e1.core import (
    canonical_controls,
    checked_pair,
    dimensions,
    participant_summary,
    select_people,
    statistics,
    surface_pair,
)


def triangle(z=0.0):
    return np.array([[0, 0, z], [1, 0, z], [0, 1, z]], float), np.array([[0, 1, 2]])


def test_surface_is_triangle_distance_not_vertex_distance():
    a, f = triangle()
    out = surface_pair((a, f), (a, f), count=100, seed=7)
    assert out["global"]["rms"] < 1e-12
    assert out["global"]["samples_per_direction"] == 100


def test_parallel_surfaces_have_known_distance():
    a, f = triangle()
    b, _ = triangle(0.2)
    out = surface_pair((a, f), (b, f), count=100, seed=7)
    assert out["global"]["symmetric_mean"] == pytest.approx(0.2)
    assert out["global"]["p95"] == pytest.approx(0.2)


def test_sampling_is_deterministic():
    a, f = triangle()
    assert surface_pair((a, f), (a, f), count=30, seed=1) == surface_pair(
        (a, f), (a, f), count=30, seed=1
    )


def test_extent_is_translation_invariant_and_floor_is_not():
    a, _ = triangle()
    b = a + [0, 3, 0]
    assert dimensions(a)["extent"] == dimensions(b)["extent"]
    assert dimensions(b)["floor"] - dimensions(a)["floor"] == 3


def test_sampling_people_is_bounded_and_order_invariant():
    rows = [dict(subject_uid=str(i), source_extent=i) for i in range(25)]
    assert select_people(rows, 10) == select_people(rows[::-1], 10)
    assert len(select_people(rows, 10)) == 10


def test_repeated_observations_receive_one_person_weight():
    rows = [
        dict(subject_uid="A", x=1),
        dict(subject_uid="A", x=3),
        dict(subject_uid="B", x=8),
    ]
    assert participant_summary(rows, "x", seed=2)["mean"] == 5
    assert participant_summary(rows, "x", seed=2)["participants"] == 2


@pytest.mark.parametrize("field", ["subject_uid", "body_uid", "fit_uid"])
def test_link_requires_exact_body_lineage(field):
    a = dict(subject_uid="A", body_uid="B", fit_uid="F", state="fitted", dataset="NOMO")
    b = dict(a, **{field: "wrong"})
    with pytest.raises(ValueError, match="LINEAGE"):
        checked_pair(a, b)


def test_source_t90_is_not_reconstruction_pair():
    a = dict(subject_uid="A", body_uid="B", fit_uid="F", state="canonical", dataset="NOMO")
    with pytest.raises(ValueError, match="FITTED"):
        checked_pair(a, a)


def test_nhanes_has_no_source_surface():
    a = dict(subject_uid="A", body_uid="B", fit_uid="F", state="fitted", dataset="NHANES")
    with pytest.raises(ValueError, match="CONDITIONING"):
        checked_pair(a, a)


def test_native_transfer_audits_all_groups_without_changing_them():
    fit = dict(
        identity_coeffs=np.ones((1, 45)),
        lbs_model_params=np.ones((1, 204)),
        face_expr_coeffs=np.ones((1, 72)),
    )
    canon = {k: v.copy() for k, v in fit.items()}
    canon["lbs_model_params"][:, :130] = 0
    reference = dict(lbs_model_params=np.zeros((1, 204)))
    out = canonical_controls(fit, canon, reference)
    assert (
        out["identity_preserved"]
        and out["morphology_preserved"]
        and out["expression_preserved"]
        and out["pinned_articulation"]
    )
    canon["face_expr_coeffs"][:] = 0
    assert not canonical_controls(fit, canon, reference)["expression_preserved"]
    assert np.all(fit["lbs_model_params"] == 1)


def test_nonfinite_statistics_are_rejected():
    with pytest.raises(ValueError):
        statistics([1, float("nan")])


def test_degenerate_triangles_are_recorded():
    a, f = triangle()
    f = np.concatenate((f, [[0, 0, 0]]))
    out = surface_pair((a, f), triangle(), count=50, seed=3)
    assert out["global"]["source_zero_area_faces_masked"] == 1


def test_regions_do_not_index_unrelated_source_vertices():
    a, f = triangle()
    b = np.vstack((a, [[0, 0, 4]]))
    out = surface_pair((a, f), (b, f), count=40, seed=1, region_faces={"torso": np.array([True])})
    assert out["regions"][0]["source_samples"] == 40
    assert out["regions"][0]["interpretation"].startswith("Fit-dependent")
