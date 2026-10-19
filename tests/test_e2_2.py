"""Focused engineering invariants; real outcomes are integration evidence."""

import copy

import numpy as np
import pytest

from somatoanthropy.experiments.e2_2.core import (
    GROUPS,
    fit_config,
    policies,
    rank_candidates,
    select_heldout,
    starting_controls,
)


def test_heldout_selection_is_stable_excludes_prior_and_stratifies():
    people = [
        dict(subject_uid=f"p{i:03d}", height=float(i), baseline_error=float(i % 7))
        for i in range(150)
    ]
    excluded = {f"p{i:03d}" for i in range(16)}
    a = select_heldout(people, excluded)
    assert a == select_heldout(people[::-1], excluded)
    assert len(a) == 12 and not excluded & {r["subject_uid"] for r in a}
    for q in range(4):
        rows = [r for r in a if r["quartile"] == q]
        assert len(rows) == 3 and sum(r["stability_subset"] for r in rows) == 1
        assert {r["error_tertile"] for r in rows} == {0, 1, 2}


def test_groups_are_nonoverlapping_and_complete():
    names = [n for g in GROUPS.values() for n in g]
    assert len(names) == len(set(names)) == 9


def test_exact_group_only_and_leave_out_masks():
    from somatoanthropy.experiments.e2_1.core import RELEASE_NAMES

    indices = [139, 140, 141, 142, 143, 146, 149, 150, 153]
    base = dict(
        parameter_audit=[
            dict(name=n, index=i, released=True)
            for n, i in zip(RELEASE_NAMES, indices, strict=True)
        ],
        released_indices=indices,
    )
    pp = policies(base)
    assert pp["B"]["indices"] == [] and pp["C"]["indices"] == indices
    assert set(pp["G1"]["indices"]) == {139, 140}
    assert set(pp["G2"]["indices"]) == {149, 150, 153}
    assert set(pp["G3"]["indices"]) == {142, 143}
    assert set(pp["G4"]["indices"]) == {141, 146}
    for g in ("G1", "G2"):
        assert not set(pp[g]["indices"]) & set(pp["no" + g]["indices"])
        assert set(pp[g]["indices"]) | set(pp["no" + g]["indices"]) == set(indices)


@pytest.mark.parametrize("k", [2, 3, 6, 7, 9])
def test_group_prior_retains_nine_control_denominator(k):
    base = dict(
        original_fitting={},
        continuation=dict(rig_l2_weight=2e-5),
        released_indices=list(range(9)),
        control_bounds={},
    )
    p = dict(indices=list(range(k)), multiplier=1.0, seed="original")
    cfg = fit_config(base, p)
    values = np.arange(1, k + 1, dtype=float)
    assert cfg["continuation"]["rig_l2_weight"] * np.square(values).mean() == pytest.approx(
        2e-5 * np.square(values).sum() / 9
    )


def test_alternative_seed_and_initialization_are_separate_interventions():
    base = dict(
        original_fitting=dict(
            pose_names=["root_rx", "root_ry", "root_rz"],
            root_rotation_bound_radians=0.6,
        ),
        continuation=dict(
            rig_l2_weight=2e-5,
            source_sampling_seed=20261018,
            target_sampling_seed=20261019,
        ),
        released_indices=list(range(139, 148)),
        control_bounds={},
    )
    p = dict(
        indices=base["released_indices"],
        multiplier=4.0,
        seed="alternative",
        initialization="perturbed_pose",
    )
    cfg = fit_config(base, p)
    assert cfg["continuation"]["rig_l2_weight"] == 8e-5
    assert cfg["continuation"]["source_sampling_seed"] == 20261028
    initial = dict(
        identity_coeffs=np.zeros((1, 45)),
        lbs_model_params=np.zeros((1, 204)),
        face_expr_coeffs=np.zeros((1, 72)),
    )
    names = ["root_rx", "root_ry", "root_rz"] + [f"p{i}" for i in range(201)]
    alternative = starting_controls(initial, names, p, base)
    assert np.allclose(alternative["lbs_model_params"][0, :3], [0.01, -0.01, 0.005])
    assert np.array_equal(
        alternative["lbs_model_params"][:, 130:], initial["lbs_model_params"][:, 130:]
    )
    assert np.array_equal(alternative["identity_coeffs"], initial["identity_coeffs"])


def test_ranking_rejects_heldout_information_and_respects_pareto():
    a = dict(
        policy="a",
        partition="development",
        surface_cm=1.0,
        fitted_height_mae_cm=1.0,
        circumference_mae_cm=1.0,
        cross_path_rms_cm=1.0,
        bound_fraction=0.0,
        circumference_missing_fraction=0.0,
        control_count=2,
        multiplier=1.0,
        complete_native=True,
    )
    b = copy.deepcopy(a)
    b.update(policy="b", surface_cm=2.0, control_count=9)
    selected, rows = rank_candidates([a, b])
    assert selected["policy"] == "a" and next(r for r in rows if r["policy"] == "b")["dominated"]
    b["partition"] = "heldout"
    with pytest.raises(ValueError, match="DEVELOPMENT_ONLY"):
        rank_candidates([a, b])


def test_tied_development_tradeoffs_prefer_simpler_policy():
    a = dict(
        policy="full",
        partition="development",
        surface_cm=1.0,
        fitted_height_mae_cm=1.0,
        circumference_mae_cm=1.0,
        cross_path_rms_cm=1.0,
        bound_fraction=0.0,
        circumference_missing_fraction=0.0,
        control_count=9,
        multiplier=1.0,
        complete_native=True,
    )
    b = dict(a, policy="reduced", control_count=2)
    chosen, rows = rank_candidates([a, b])
    assert chosen["policy"] == "reduced"
    assert not any(r["dominated"] for r in rows)


def test_pose_start_clamps_to_original_bounds_and_preserves_input():
    initial = dict(
        identity_coeffs=np.ones((1, 45)),
        lbs_model_params=np.zeros((1, 204)),
        face_expr_coeffs=np.ones((1, 72)),
    )
    initial["lbs_model_params"][0, :3] = [0.599, -0.599, 0.599]
    names = ["root_rx", "root_ry", "root_rz"] + [f"p{i}" for i in range(201)]
    base = dict(original_fitting=dict(root_rotation_bound_radians=0.6, pose_names=names[:3]))
    out = starting_controls(initial, names, dict(initialization="perturbed_pose"), base)
    assert np.allclose(out["lbs_model_params"][0, :3], [0.6, -0.6, 0.6])
    assert np.allclose(initial["lbs_model_params"][0, :3], [0.599, -0.599, 0.599])
    assert np.array_equal(out["identity_coeffs"], initial["identity_coeffs"])
    assert np.array_equal(out["face_expr_coeffs"], initial["face_expr_coeffs"])
