"""Analytical fixtures for E2; real saved-body checks live in integration."""

import numpy as np
import pytest

from somatoanthropy.data.phase01_nomo import atomic_json
from somatoanthropy.experiments.e2.core import (
    assess_site,
    external_errors,
    height_diagnostics,
    midpoint_plane,
    paired_error,
    physical_cm,
    registry,
    summarise_errors,
    three_way,
)
from somatoanthropy.experiments.e4.core import bootstrap, seed_for
from somatoanthropy.geometry.nomo_caesar_mhr_fit04.core import transform


def test_midpoint_in_anatomical_frame():
    p, n = midpoint_plane([0, 1, 1], [0, 0, 0], [0, 1, 1])
    assert np.allclose(p, [0, 0.5, 0.5])
    assert np.allclose(n, [0, 1 / np.sqrt(2), 1 / np.sqrt(2)])


@pytest.mark.parametrize(
    "rib,crest,axis",
    [
        (None, [0, 0, 0], [0, 1, 0]),
        ([0, 0, 0], [0, 1, 0], [0, 1, 0]),
        ([0, 1, 0], [0, 0, 0], [0, 0, 0]),
    ],
)
def test_missing_or_invalid_landmark_not_invented(rib, crest, axis):
    with pytest.raises(ValueError):
        midpoint_plane(rib, crest, axis)


def test_fallback_does_not_decide_anatomical_validity():
    a = assess_site(fallback=True, contour_valid=True, evidence="HUMAN_LANDMARK_REVIEW")
    b = assess_site(fallback=False, contour_valid=True, evidence="NONE")
    assert a["site_assessment"] == "ANATOMICALLY_SUPPORTED"
    assert b["site_assessment"] == "REVIEW_REQUIRED"
    assert a["contour_assessment"] == b["contour_assessment"] == "VALID_CLOSED_CONTOUR"


def test_engineering_units_not_implicitly_physical():
    with pytest.raises(ValueError):
        physical_cm(1.7, "engineering_m", verified=False)
    assert physical_cm(1.7, "m", verified=True) == 170
    assert physical_cm(1700, "mm", verified=True) == 170


def test_height_translation_and_head_descriptor():
    v = np.array([[0, 0, 0], [0, 1, 0], [0, 1.8, 0], [0, 2, 0]])
    a = height_diagnostics(v, head_ids=[2, 3], neck_y=1.5)
    b = height_diagnostics(v + [2, 7, -1], head_ids=[2, 3], neck_y=8.5)
    assert a["vertical_extent_cm"] == b["vertical_extent_cm"] == 200
    assert np.isclose(a["above_neck_cm"] + a["below_neck_cm"], 200)
    assert a["max_minus_head_q99_cm"] > 0
    assert a["metric"] == "GLOBAL_Y_EXTENT_NOT_STATURE"


def test_rigid_transform_preserves_scale():
    m = np.eye(4)
    m[:3, 3] = [1, 2, 3]
    assert np.allclose(transform([[0, 0, 0]], m), [[1, 2, 3]])
    m[0, 0] = 2
    with pytest.raises(ValueError):
        transform([[0, 0, 0]], m)


def test_paired_error_and_external_qualification():
    assert paired_error(12, 10) == 2
    assert paired_error(None, 10) is None
    assert external_errors(10, 12, 11, compatible=False) is None
    assert external_errors(10, 12, 13, compatible=True) == {
        "source_error": -3,
        "mhr_error": -1,
        "delta_absolute": -2,
    }


def test_three_way_deduplicates_people_and_keeps_missingness():
    rows = [
        {"subject_uid": "p", "collection": c, "value": v}
        for c, v in zip(("SMPL-NICP", "SMPL-LBFGSB", "CAESAR-NICP"), (10, None, 11), strict=True)
    ]
    assert len(three_way(rows)) == 1
    assert three_way(rows)[0]["SMPL-LBFGSB"] is None
    with pytest.raises(ValueError):
        three_way(rows + [rows[0]])


def test_summary_uncertainty_and_missing_denominator():
    a, draws = summarise_errors([1, -2, 3], eligible=4, seed=3, replicates=2000)
    assert a["n"] == 3 and a["missing"] == 1 and a["eligible"] == 4
    assert a["mae"] == 2 and np.isclose(a["rmse"], np.sqrt(14 / 3))
    assert a["median_absolute"] == 2
    assert draws == summarise_errors([1, -2, 3], eligible=4, seed=3, replicates=2000)[1]
    assert bootstrap([1, 2], seed=3, replicates=2000) == bootstrap([1, 2], seed=3, replicates=2000)
    assert seed_for(3, "height") == seed_for(3, "height")


def test_versioned_outputs_cannot_overwrite(tmp_path):
    p = tmp_path / "e2.json"
    atomic_json(p, {"a": 1})
    atomic_json(p, {"a": 1})
    with pytest.raises(FileExistsError):
        atomic_json(p, {"a": 2})


def test_registry_separates_anatomical_waist_and_proxies():
    definitions = {r["id"]: r for r in registry()}
    assert definitions["waist_rib_iliac_midpoint"]["executable_in_cohort"] is False
    assert (
        definitions["waist_atlas_midpoint_proxy"]["anatomical_status"]
        == "UNQUALIFIED_MODEL_SURFACE_PROXY"
    )


def test_existing_indexed_engine_raw_tape_and_multi_loop():
    import trimesh

    from somatoanthropy.data.nomo_contact_sections import IndexedSections

    a = trimesh.creation.box(extents=[2, 2, 2])
    b = trimesh.creation.box(extents=[1, 2, 1])
    b.apply_translation([4, 0, 0])
    mesh = trimesh.util.concatenate([a, b])
    e = IndexedSections(mesh.vertices, mesh.faces)
    q = e.section([0, 0.123, 0], [0, 1, 0], [0, 0.123, 0])
    assert q["geometry_quality"] == "VALID" and q["closed_loop_count"] == 2
    assert np.isclose(q["raw_contour_cm"], 800)
    assert np.isclose(q["tape_envelope_cm"], 800)
    assert e.section([0, 0.123, 0], [0, 1, 0], [3, 0.123, 0])["geometry_quality"] == "INVALID"
    assert (
        e.section([0, 0.123, 0], [0, 1, 0], [0, 0.123, 0], np.zeros(len(mesh.faces), bool))[
            "geometry_quality"
        ]
        == "INVALID"
    )
