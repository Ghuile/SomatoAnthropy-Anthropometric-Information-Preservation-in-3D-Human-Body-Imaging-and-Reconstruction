"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import re

import numpy as np
from scipy.stats import linregress, pearsonr, spearmanr

RELEASE_NAMES = (
    "scale_spine_length",
    "scale_neck_length",
    "scale_shoulder_width",
    "scale_uparms",
    "scale_lowarms",
    "scale_hip_width",
    "scale_uplegs",
    "scale_lowlegs",
    "scale_foot_length",
)


def parameter_audit(probe):
    bounds = {}
    for s in probe["limits"]:
        match = re.fullmatch(
            "ParameterLimit\\(type=MinMax, weight=([^,]+), param=(\\d+), min=([^,]+), max=([^\\)]+)\\)",
            s,
        )
        if match:
            bounds[int(match[2])] = dict(
                weight=float(match[1]), minimum=float(match[3]), maximum=float(match[4]), source=s
            )
    rows = []
    for r in probe["rows"]:
        i, name = (r["index"], r["name"])
        limits = bounds.get(i)
        include = name in RELEASE_NAMES
        if include and (
            limits is None
            or limits["minimum"] >= limits["maximum"]
            or (not r["affected_joint_channels"])
            or any((x["channel"] not in ("tx", "ty", "tz") for x in r["affected_joint_channels"]))
        ):
            raise ValueError("UNSUPPORTED_BODY_LENGTH_CONTROL:" + name)
        reason = (
            "Verified independent body segment/joint-offset control with nonzero authored domain"
            if include
            else "Excluded articulation, flexible duplicate, zero-domain, eye/hand/finger or alignment control"
        )
        rows.append(
            dict(
                r,
                revision=probe["model_revision"],
                historical_status="FIXED_AT_NEUTRAL"
                if i >= 130
                else "ORIGINAL_PERMISSION_RETAINED",
                fixed_value=0 if i >= 130 else None,
                released=include,
                bounds=limits,
                justification=reason,
                canonical_policy="preserve indices 130:204; replace authored articulation only",
                parameter_effect="local joint rest-translation offsets, not a whole-body scale"
                if include
                else "see exact joint/channel mapping",
            )
        )
    if {r["name"] for r in rows if r["released"]} != set(RELEASE_NAMES):
        raise ValueError("EXACT_VERIFIED_CONTROL_SET_REQUIRED")
    return rows


def choose_cohort(people, seed):
    rows = sorted(people, key=lambda r: (r["height"], r["subject_uid"]))
    if len(rows) != 150 or len({r["subject_uid"] for r in rows}) != 150:
        raise ValueError("FROZEN_PRIMARY_150_REQUIRED")
    rng = np.random.default_rng(seed)
    selected = []
    for quartile, chunk in enumerate(np.array_split(np.arange(150), 4)):
        q = [rows[int(i)] for i in chunk]
        picked = []
        for cross in (False, True):
            pool = sorted([r for r in q if r["crossover"] == cross], key=lambda r: r["subject_uid"])
            if len(pool) < 2:
                raise ValueError("INSUFFICIENT_STRATUM; explicit allocation deviation required")
            picked.extend((pool[int(i)] for i in rng.choice(len(pool), 2, replace=False)))
        picked.sort(key=lambda r: r["subject_uid"])
        dev = int(rng.integers(0, 4))
        selected.extend(
            (
                dict(r, quartile=quartile, partition="development" if i == dev else "evaluation")
                for i, r in enumerate(picked)
            )
        )
    return selected


def canonical_controls(controls, reference):
    shapes = dict(identity_coeffs=(1, 45), lbs_model_params=(1, 204), face_expr_coeffs=(1, 72))
    if any(
        (
            np.asarray(controls[k]).shape != shape or not np.isfinite(controls[k]).all()
            for k, shape in shapes.items()
        )
    ):
        raise ValueError("INVALID_NATIVE_DIMENSIONS_OR_VALUES")
    result = {k: np.asarray(v).copy() for k, v in controls.items()}
    result["lbs_model_params"][:, :130] = np.asarray(reference)[:, :130]
    return result


def variation(source, target):
    x, y = (np.asarray(source, float), np.asarray(target, float))
    if x.shape != y.shape or not np.isfinite([x, y]).all() or len(x) < 2:
        raise ValueError("PAIRED_FINITE_PARTICIPANTS_REQUIRED")
    error = y - x
    return dict(
        n=len(x),
        mean=float(y.mean()),
        sd=float(y.std(ddof=1)),
        minimum=float(y.min()),
        maximum=float(y.max()),
        iqr=float(np.quantile(y, 0.75) - np.quantile(y, 0.25)),
        bias=float(error.mean()),
        mae=float(np.abs(error).mean()),
        rmse=float(np.sqrt(np.mean(error**2))),
        source_sd=float(x.std(ddof=1)),
        sd_ratio=float(y.std(ddof=1) / x.std(ddof=1)),
        slope=float(linregress(x, y).slope),
        pearson=float(pearsonr(x, y).statistic) if np.ptp(y) else None,
        spearman=float(spearmanr(x, y).statistic) if np.ptp(y) else None,
    )
