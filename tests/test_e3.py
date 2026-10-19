"""Numerical E3 contracts; fixtures never represent research participants."""

import numpy as np
import pytest

from somatoanthropy.experiments.e3.core import (
    angular_distance,
    cluster_association,
    dispersion,
    indexed_difference,
    local_plane,
    reference_site,
    validate_panel,
)


def test_incomplete_dispersion_and_sample_sd():
    assert dispersion([3])["sd"] is None
    assert dispersion([])["range"] is None
    d = dispersion([1, 3, 5])
    assert d["sd"] == 2
    assert d["range"] == 4
    assert d["pairwise_median"] == 2
    assert d["mad"] == 2


def test_indexed_translation_only_and_region():
    a = np.array([[0.0, 0, 0], [1, 1, 0], [2, 2, 0]])
    b = a + [0, 2, 0]
    assert indexed_difference(a, b)["rms_cm"] == 200
    assert indexed_difference(a - a.mean(0), b - b.mean(0))["rms_cm"] == 0
    b[2, 0] += 1
    assert indexed_difference(a[:2], b[:2])["rms_cm"] == 200
    with pytest.raises(ValueError):
        indexed_difference(a, b[:2])


def test_plane_transform_and_fixed_reference_excludes_self():
    p, n = local_plane([1, 4, 2], [0, 2, 0], [1, 3, 2])
    np.testing.assert_array_equal(p, [0, 1, 0])
    np.testing.assert_array_equal(n, [0, 1, 0])
    rows = [{"selection_id": "Invented-01-F02"}, {"selection_id": "Invented-01-F01"}]
    assert reference_site(rows)["selection_id"] == "Invented-01-F01"
    with pytest.raises(ValueError):
        local_plane([0, 0, 0], [0, 0, 0], [0, 0, 0])


def test_scalar_angle_wrap_is_periodic():
    assert angular_distance(2 * np.pi + 0.1, 0) == pytest.approx(0.1)
    assert angular_distance(-np.pi, np.pi) == pytest.approx(0)


def test_participant_cluster_association_and_determinism():
    groups = [("a", [1, 2, 3], [3, 2, 1]), ("b", [8, 9], [2, 1])]
    a = cluster_association(groups, seed=2, replicates=100)
    assert a == cluster_association(groups, seed=2, replicates=100)
    assert a["subjects"] == 2 and a["observations"] == 5
    assert a["within_subject_r"] == pytest.approx(-1)
    assert (
        cluster_association([("a", [1, 1], [2, 3])], seed=1, replicates=100)["within_subject_r"]
        is None
    )


def test_panel_identifies_people_sequences_frames_not_temporal_series():
    rows = [
        dict(
            subject_uid=f"s{i}",
            observation_uid=f"o{i}-{j}",
            fit_uid=f"f{i}-{j}",
            body_uid=f"b{i}-{j}",
            sequence_uid=f"q{i}-{j % 4}",
            frame=j,
            selection_id=f"Invented-{i + 1:02}-F{j + 1:02}",
        )
        for i in range(10)
        for j in range(6)
    ]
    validate_panel(rows)
    rows[0]["observation_uid"] = rows[1]["observation_uid"]
    with pytest.raises(ValueError):
        validate_panel(rows)


def test_dataset_local_identity_sequence_and_frame_separation():
    from somatoanthropy.production.DFAUST_FIT07.core import identifiers

    a = identifiers("a" * 64, "999999_motion_a", 1)
    b = identifiers("a" * 64, "999999_motion_b", 1)
    c = identifiers("a" * 64, "999999_motion_a", 2)
    assert a["subject_uid"] == b["subject_uid"] == c["subject_uid"]
    assert a["sequence_uid"] != b["sequence_uid"]
    assert a["sequence_uid"] == c["sequence_uid"]
    assert len({a["observation_uid"], b["observation_uid"], c["observation_uid"]}) == 3
    with pytest.raises(ValueError):
        identifiers("a" * 64, "unknown_motion", 1)


@pytest.mark.parametrize(
    "key,dim",
    [("identity_coeffs", 45), ("lbs_model_params", 204), ("face_expr_coeffs", 72)],
)
@pytest.mark.parametrize("bad", ["shape", "nan"])
def test_native_schema_and_finite_values(key, dim, bad):
    from somatoanthropy.geometry.anthropometry.approved_t90 import require_t90_parameters

    controls = {
        k: np.zeros((1, d), np.float32)
        for k, d in [
            ("identity_coeffs", 45),
            ("lbs_model_params", 204),
            ("face_expr_coeffs", 72),
        ]
    }
    reference = {"lbs_model_params": np.zeros((1, 204), np.float32)}
    if bad == "shape":
        controls[key] = np.zeros((1, dim - 1), np.float32)
    else:
        controls[key][0, 0] = np.nan
    with pytest.raises(ValueError):
        require_t90_parameters(controls, reference)


def test_t90_guard_allows_subject_morphology_and_rejects_articulation_change():
    from somatoanthropy.geometry.anthropometry.approved_t90 import require_t90_parameters

    controls = {
        k: np.zeros((1, d), np.float32)
        for k, d in [
            ("identity_coeffs", 45),
            ("lbs_model_params", 204),
            ("face_expr_coeffs", 72),
        ]
    }
    controls["identity_coeffs"][0, 2] = 4
    controls["lbs_model_params"][0, 130] = 1
    reference = {"lbs_model_params": np.zeros((1, 204), np.float32)}
    require_t90_parameters(controls, reference)
    assert controls["lbs_model_params"][0, 130] == 1
    controls["lbs_model_params"][0, 129] = 0.01
    with pytest.raises(ValueError):
        require_t90_parameters(controls, reference)


def test_actual_indexed_section_on_square_prism_and_region_failure():
    from somatoanthropy.data.nomo_contact_sections import IndexedSections

    v = np.array(
        [[x, y, z] for y in (0, 1) for x, z in ((-1, -1), (1, -1), (1, 1), (-1, 1))],
        float,
    )
    f = np.array(
        [[i, (i + 1) % 4, (i + 1) % 4 + 4] for i in range(4)]
        + [[i, (i + 1) % 4 + 4, i + 4] for i in range(4)]
    )
    engine = IndexedSections(v, f)
    q = engine.section([0, 0.5, 0], [0, 1, 0], [0, 0.5, 0], np.ones(8, bool))
    assert q["raw_contour_cm"] == pytest.approx(800)
    assert q["tape_envelope_cm"] == pytest.approx(800)
    assert q["geometry_quality"] == "VALID"
    assert (
        engine.section([0, 0.5, 0], [0, 1, 0], [0, 0.5, 0], np.zeros(8, bool))["geometry_quality"]
        == "INVALID"
    )


def test_fallback_and_anatomy_are_separate():
    from somatoanthropy.experiments.e2.core import assess_site

    q = assess_site(fallback=True, contour_valid=True, evidence="MODEL_PROXY")
    assert q["fallback_applied"]
    assert q["contour_assessment"] == "VALID_CLOSED_CONTOUR"
    assert q["site_assessment"] == "GEOMETRICALLY_SUPPORTED_PROXY"


def test_fixed_reference_exclusion_does_not_relabel_historical_ambiguity():
    from somatoanthropy.experiments.e3.measure import fields

    r = dict(
        subject_uid="s",
        observation_uid="o",
        fit_uid="f",
        body_uid="b",
        selection_id="Invented-01-F01",
        subject_label="Invented-01",
        sequence_uid="q",
        source_asset_hash="h",
        native_parameter_hash="p",
        mhr_model_revision="m",
        canonical_pose_id="T90",
    )
    q = dict(
        geometry_quality="VALID",
        raw_contour_cm=80,
        quality_state="SITE_AMBIGUOUS",
        fallback_applied=True,
    )
    a = fields(r, "waist", "A_historical_strict", q, eligible=False)
    b = fields(r, "waist", "C_fixed_F01_raw_contour_cm", q, eligible=False)
    assert a["result_value"] is None and not a["reference_excluded"]
    assert b["result_value"] is None and b["reference_excluded"]
    assert a["historical_quality_state"] == "SITE_AMBIGUOUS" and a["fallback"]


def test_cluster_centring_removes_between_subject_only_association():
    groups = [("a", [1, 2, 3], [1, 1, 1]), ("b", [11, 12, 13], [10, 10, 10])]
    q = cluster_association(groups, replicates=100)
    assert q["within_subject_r"] is None
    assert q["identified_bootstrap_draws"] == 0


def test_participant_bootstrap_not_six_independent_replicates():
    from somatoanthropy.experiments.e4.core import bootstrap

    a = bootstrap([1, 3], seed=4, replicates=2000)
    assert len(a["draws"]["median"]) == 2000
    assert set(a["draws"]["mean"]) <= {1, 2, 3}
    assert a == bootstrap([1, 3], seed=4, replicates=2000)
