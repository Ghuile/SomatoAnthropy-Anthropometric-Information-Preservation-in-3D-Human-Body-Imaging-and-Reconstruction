"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import copy
import hashlib
import json

import numpy as np
from scipy.stats import rankdata

GROUPS = {
    "G1": ["scale_spine_length", "scale_neck_length"],
    "G2": ["scale_uplegs", "scale_lowlegs", "scale_foot_length"],
    "G3": ["scale_uparms", "scale_lowarms"],
    "G4": ["scale_shoulder_width", "scale_hip_width"],
}
SEED = 20261022
PERTURBATION = {"root_rx": 0.01, "root_ry": -0.01, "root_rz": 0.005}
RANKING = "Development only: Pareto minimization of independent global surface mean, fitted height MAE, mean fixed-plane waist/abdomen/hip MAE, canonical cross-path vertex RMS, any-bound fraction and circumference missingness. Among nondominated policies, minimize worst fractional rank, then mean fractional rank, then control count, then prefer lambda multiplier nearest 1, then policy ID. SD ratio and repeat sensitivity are descriptive, not selection targets. No universal quality margins. Incomplete native policies remain failures and are ineligible for the candidate."


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def policies(base):
    audit = base["parameter_audit"]
    indices = {r["name"]: r["index"] for r in audit if r["released"]}
    if set(indices) != {n for g in GROUPS.values() for n in g}:
        raise ValueError("VERIFIED_NINE_CONTROL_GROUP_PARTITION_REQUIRED")
    full = base["released_indices"]
    result = {
        "B": dict(indices=[], multiplier=1.0, seed="original", initialization="original"),
        "C": dict(indices=full, multiplier=1.0, seed="original", initialization="original"),
    }
    for g, names in GROUPS.items():
        result[g] = dict(
            indices=[i for i in full if i in [indices[n] for n in names]],
            multiplier=1.0,
            seed="original",
            initialization="original",
        )
    for g in ("G1", "G2"):
        result["no" + g] = dict(
            indices=[i for i in full if i not in result[g]["indices"]],
            multiplier=1.0,
            seed="original",
            initialization="original",
        )
    for name, multiplier in (("R025", 0.25), ("R4", 4.0)):
        result[name] = dict(
            indices=full, multiplier=multiplier, seed="original", initialization="original"
        )
    for prefix, seed, initialization in (
        ("S1", "alternative", "original"),
        ("I1", "original", "perturbed_pose"),
    ):
        for arm in ("B", "C"):
            result[prefix + "-" + arm] = dict(result[arm], seed=seed, initialization=initialization)
    return result


def fit_config(base, policy):
    result = {
        k: copy.deepcopy(base[k])
        for k in ("original_fitting", "continuation", "released_indices", "control_bounds")
    }
    active = policy["indices"]
    result["released_indices"] = active or base["released_indices"]
    result["continuation"]["rig_l2_weight"] = (
        base["continuation"]["rig_l2_weight"]
        * policy["multiplier"]
        * (len(active) / 9 if active else 1)
    )
    if policy["seed"] == "alternative":
        result["continuation"].update(source_sampling_seed=20261028, target_sampling_seed=20261029)
    return result


def starting_controls(initial, names, policy, base):
    out = {k: np.asarray(v).copy() for k, v in initial.items()}
    if policy["initialization"] == "perturbed_pose":
        bound = base["original_fitting"]["root_rotation_bound_radians"]
        for name, delta in PERTURBATION.items():
            if name not in base["original_fitting"]["pose_names"]:
                raise ValueError("PERTURBATION_OUTSIDE_ORIGINAL_MASK")
            i = names.index(name)
            out["lbs_model_params"][0, i] = np.clip(
                out["lbs_model_params"][0, i] + delta, -bound, bound
            )
    if not np.array_equal(out["lbs_model_params"][:, 130:], initial["lbs_model_params"][:, 130:]):
        raise ValueError("INITIALIZATION_CHANGED_FIXED_MORPHOLOGY")
    return out


def select_heldout(people, excluded):
    if len(people) != 150 or len({p["subject_uid"] for p in people}) != 150:
        raise ValueError("EXACT_PRIMARY_150_REQUIRED")
    ordered = sorted(people, key=lambda r: (r["height"], r["subject_uid"]))
    rng = np.random.default_rng(SEED)
    selected = []
    for quartile, chunk in enumerate(np.array_split(np.arange(150), 4)):
        pool = [ordered[int(i)] for i in chunk if ordered[int(i)]["subject_uid"] not in excluded]
        if len(pool) < 3:
            raise ValueError("INSUFFICIENT_ELIGIBLE_QUARTILE; explicit deviation required")
        pool.sort(key=lambda r: (r["baseline_error"], r["subject_uid"]))
        for tertile, ids in enumerate(np.array_split(np.arange(len(pool)), 3)):
            i = int(rng.choice(ids))
            selected.append(
                dict(
                    pool[i],
                    quartile=quartile,
                    error_tertile=tertile,
                    partition="heldout",
                    stability_subset=tertile == 1,
                )
            )
    return selected


def rank_candidates(rows):
    if not rows or any((r["partition"] != "development" for r in rows)):
        raise ValueError("DEVELOPMENT_ONLY_RANKING_REQUIRED")
    keys = (
        "surface_cm",
        "fitted_height_mae_cm",
        "circumference_mae_cm",
        "cross_path_rms_cm",
        "bound_fraction",
        "circumference_missing_fraction",
    )
    eligible = [
        r
        for r in rows
        if r["complete_native"] and all((r[k] is not None and np.isfinite(r[k]) for k in keys))
    ]
    if not eligible:
        raise ValueError("NO_COMPLETE_DEVELOPMENT_POLICY")
    values = np.array([[r[k] for k in keys] for r in eligible])
    ranks = np.column_stack(
        [rankdata(values[:, j], method="average") for j in range(len(keys))]
    ) / len(eligible)
    scored = []
    for i, r in enumerate(eligible):
        dominated = any(
            (np.all(other <= values[i]) and np.any(other < values[i]) for other in values)
        )
        scored.append(
            dict(
                r,
                dominated=dominated,
                worst_fractional_rank=float(ranks[i].max()),
                mean_fractional_rank=float(ranks[i].mean()),
            )
        )
    chosen = min(
        [r for r in scored if not r["dominated"]],
        key=lambda r: (
            r["worst_fractional_rank"],
            r["mean_fractional_rank"],
            r["control_count"],
            abs(np.log(r["multiplier"])),
            r["policy"],
        ),
    )
    return (chosen, scored)
