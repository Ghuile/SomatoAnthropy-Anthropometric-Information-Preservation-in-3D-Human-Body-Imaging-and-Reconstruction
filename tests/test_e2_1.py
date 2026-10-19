"""Controlled-ablation invariants, separate from native integration evidence."""

import numpy as np
import pytest

from somatoanthropy.experiments.e2_1.core import (
    canonical_controls,
    choose_cohort,
    parameter_audit,
    variation,
)


def fixtures():
    return [
        dict(subject_uid=f"p{i:03d}", height=float(i), crossover=i % 2 == 0) for i in range(150)
    ]


def test_stable_stratified_selection_and_reserved_partition():
    rows = choose_cohort(fixtures(), 20261018)
    assert rows == choose_cohort(fixtures()[::-1], 20261018)
    assert len(rows) == len({r["subject_uid"] for r in rows}) == 16
    assert sum(r["crossover"] for r in rows) == 8
    for quartile in range(4):
        q = [r for r in rows if r["quartile"] == quartile]
        assert len(q) == 4 and sum(r["partition"] == "development" for r in q) == 1


def test_canonical_keeps_all_morphology_and_expression():
    c = dict(
        identity_coeffs=np.ones((1, 45)),
        lbs_model_params=np.arange(204, dtype=float)[None],
        face_expr_coeffs=np.ones((1, 72)),
    )
    t = np.zeros((1, 204))
    out = canonical_controls(c, t)
    assert np.array_equal(out["lbs_model_params"][:, 130:], c["lbs_model_params"][:, 130:])
    assert np.array_equal(out["face_expr_coeffs"], c["face_expr_coeffs"])
    assert np.all(out["lbs_model_params"][:, :130] == 0)
    assert c["lbs_model_params"][0, 130] == 130


def test_variation_and_paired_size_agreement_are_distinct():
    a = variation([150, 160, 170], [170, 160, 150])
    assert a["sd_ratio"] == 1
    assert a["mae"] > 0 and a["slope"] == -1


def test_parameter_manifest_does_not_blindly_unlock_74_controls():
    probe = dict(
        model_revision="pin",
        rows=[dict(index=i, name=f"p{i}", affected_joint_channels=[]) for i in range(204)],
        limits=[],
    )
    with pytest.raises(ValueError):
        parameter_audit(probe)


@pytest.mark.parametrize("key", ["identity_coeffs", "lbs_model_params", "face_expr_coeffs"])
def test_invalid_native_dimensions_rejected(key):
    c = dict(
        identity_coeffs=np.zeros((1, 45)),
        lbs_model_params=np.zeros((1, 204)),
        face_expr_coeffs=np.zeros((1, 72)),
    )
    c[key] = np.zeros((2, 3))
    with pytest.raises(ValueError):
        canonical_controls(c, np.zeros((1, 204)))


def test_paired_bootstrap_resamples_people_jointly():
    from somatoanthropy.experiments.e2_1.analysis import paired_summary, ratio_effect

    x = np.array([150.0, 160.0, 170.0, 180.0])
    q = ratio_effect(x, 160 + (x - 160) * 0.2, 160 + (x - 160) * 0.7, 42)
    assert q["n"] == 4 and q["mean"] == pytest.approx(0.5)
    assert q["ci95"] == pytest.approx([0.5, 0.5])
    assert q == ratio_effect(x, 160 + (x - 160) * 0.2, 160 + (x - 160) * 0.7, 42)
    p = paired_summary([-2.0, -2.0, -2.0], 42)
    assert p["mean"] == -2 and p["ci95"] == [-2.0, -2.0]


def test_exact_surface_distance_and_sampler_use_independent_topology():
    from somatoanthropy.geometry.mpii_mhr_fit01.metrics import distances, samples

    v = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]])
    f = np.array([[0, 1, 2]])
    points, _, _ = samples(v, f, 40, 2026)
    assert np.array_equal(points, samples(v, f, 40, 2026)[0])
    assert np.allclose(distances(points + [0, 0, 0.2], v, f), 0.2)


def test_fallback_and_contour_evidence_are_separate():
    from somatoanthropy.experiments.e2.core import assess_site

    q = assess_site(fallback=True, contour_valid=True, evidence="NONE")
    assert q["contour_assessment"] == "VALID_CLOSED_CONTOUR"
    assert q["site_assessment"] == "REVIEW_REQUIRED"
    assert q["evidence"] == "NONE"


def test_exclusive_writes_preserve_existing_results(tmp_path):
    from somatoanthropy.data.phase01_nomo import atomic_bytes

    p = tmp_path / "result"
    atomic_bytes(p, b"original")
    atomic_bytes(p, b"original")
    with pytest.raises(FileExistsError):
        atomic_bytes(p, b"different")
    assert p.read_bytes() == b"original"


def test_interrupted_adam_recovery_and_changed_protocol_rejected(tmp_path, monkeypatch):
    """Synthetic numerical recovery only; native gradients are tested separately."""
    import copy

    torch = pytest.importorskip("torch")

    from somatoanthropy.experiments.e2_1 import optimizer as opt

    class Tiny(torch.nn.Module):
        def forward(self, identity, controls, expression, apply_correctives):
            v = torch.tensor([[0.0, 0, 0], [100.0, 0, 0], [0, 100.0, 0], [0, 0, 100.0]])
            return (v + identity.mean() + controls.mean())[None], torch.zeros((1, 1, 8))

    f = np.array([[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])
    source = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]) + 0.005
    initial = dict(
        identity_coeffs=np.zeros((1, 45)),
        lbs_model_params=np.zeros((1, 204)),
        face_expr_coeffs=np.zeros((1, 72)),
    )
    config = dict(
        original_fitting=dict(
            pose_names=["root_rx"],
            root_rotation_bound_radians=0.6,
            pose_bound_radians=1.8,
            robust_delta_metres=0.03,
            identity_l2_weight=1e-6,
            pose_l2_weight=2e-5,
            gradient_clip_norm=1.0,
            identity_bound=3.0,
        ),
        released_indices=[139],
        control_bounds={"139": dict(minimum=-1.1, maximum=1.1)},
        continuation=dict(
            identity_lr=0.015,
            pose_lr=0.002,
            translation_lr=0.001,
            rig_lr=0.01,
            samples=32,
            source_sampling_seed=3,
            target_sampling_seed=4,
            iterations=4,
            timeout_seconds=60,
            rig_l2_weight=2e-5,
            checkpoint_every=2,
        ),
    )
    names = ["p" + str(i) for i in range(204)]
    names[3] = "root_rx"
    monkeypatch.setattr(opt, "resources", lambda *args: None)
    args = (Tiny(), names, f, source, f, initial, [0.0, 0, 0], config, "released")
    expected, reference = opt.optimise(*args, tmp_path / "reference")
    original_write = opt.atomic_bytes

    def interrupted(path, payload):
        original_write(path, payload)
        raise RuntimeError("simulated power interruption after durable checkpoint")

    monkeypatch.setattr(opt, "atomic_bytes", interrupted)
    with pytest.raises(RuntimeError, match="simulated power"):
        opt.optimise(*args, tmp_path / "resumed")
    monkeypatch.setattr(opt, "atomic_bytes", original_write)
    actual, result = opt.optimise(*args, tmp_path / "resumed")
    assert result["resumed_from_iteration"] == 2
    assert result["history"] == reference["history"]
    assert all(np.array_equal(actual[k], expected[k]) for k in actual)
    changed = copy.deepcopy(config)
    changed["continuation"]["rig_lr"] *= 2
    with pytest.raises(ValueError, match="CHECKPOINT_MATCHING_PROTOCOL_CHANGED"):
        opt.optimise(*args[:7], changed, "released", tmp_path / "resumed")
