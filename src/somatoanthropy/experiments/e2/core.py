"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import numpy as np

from somatoanthropy.experiments.e4.core import bootstrap, describe

PATHWAYS = ("SMPL-NICP", "SMPL-LBFGSB", "CAESAR-NICP")
VERSION = "E2-METROLOGY-v1"


def physical_cm(value, unit, *, verified):
    if not verified or unit not in ("m", "cm", "mm"):
        raise ValueError("INDEPENDENT_PHYSICAL_UNIT_EVIDENCE_REQUIRED")
    return value * {"m": 100, "cm": 1, "mm": 0.1}[unit]


def midpoint_plane(rib, crest, superior_axis):
    if rib is None or crest is None:
        raise ValueError("MISSING_LANDMARK")
    a, b, n = [np.asarray(x, float) for x in (rib, crest, superior_axis)]
    if any((x.shape != (3,) or not np.isfinite(x).all() for x in (a, b, n))):
        raise ValueError("INVALID_LANDMARK_FRAME")
    if np.linalg.norm(n) == 0 or (a - b) @ n <= 0:
        raise ValueError("INVALID_SUPERIOR_AXIS_OR_LANDMARK_ORDER")
    return ((a + b) / 2, n / np.linalg.norm(n))


def assess_site(*, fallback, contour_valid, evidence):
    status = {
        "HUMAN_LANDMARK_REVIEW": "ANATOMICALLY_SUPPORTED",
        "AGENT_VISUAL": "VISUALLY_SUPPORTED_APPROXIMATION",
        "MODEL_PROXY": "GEOMETRICALLY_SUPPORTED_PROXY",
    }.get(evidence, "REVIEW_REQUIRED")
    return dict(
        fallback_applied=bool(fallback),
        site_assessment=status,
        contour_assessment="VALID_CLOSED_CONTOUR" if contour_valid else "INVALID_GEOMETRY",
        external_comparability="PROTOCOL_UNKNOWN",
        evidence=evidence,
    )


def paired_error(mhr, source):
    if mhr is None or source is None:
        return None
    if not np.isfinite([mhr, source]).all():
        raise ValueError("NONFINITE_PAIRED_MEASUREMENT")
    return float(mhr - source)


def external_errors(source, mhr, observed, *, compatible):
    if not compatible or any((x is None for x in (source, mhr, observed))):
        return None
    a, b = (paired_error(source, observed), paired_error(mhr, observed))
    return dict(source_error=a, mhr_error=b, delta_absolute=abs(b) - abs(a))


def three_way(rows):
    result, seen = ({}, set())
    for r in rows:
        uid, collection = (r["subject_uid"], r["collection"])
        if collection not in PATHWAYS or (uid, collection) in seen:
            raise ValueError("DUPLICATE_OR_UNKNOWN_PATHWAY")
        seen.add((uid, collection))
        result.setdefault(uid, dict(subject_uid=uid, **dict.fromkeys(PATHWAYS)))
        result[uid][collection] = r["value"]
    return [result[k] for k in sorted(result)]


def summarise_errors(values, *, eligible, seed, replicates=2000):
    x = np.asarray(values, float)
    if eligible < len(x):
        raise ValueError("INVALID_PARTICIPANT_DENOMINATOR")
    result = describe(x)
    boot = bootstrap(x, seed=seed, replicates=replicates)
    draws = boot.pop("draws")
    result.update(boot)
    result.update(
        eligible=eligible,
        missing=eligible - len(x),
        median_absolute=float(np.median(np.abs(x))) if len(x) else None,
        p95_absolute=float(np.quantile(np.abs(x), 0.95)) if len(x) else None,
        loa_lower=float(x.mean() - 1.96 * x.std(ddof=1)) if len(x) > 1 else None,
        loa_upper=float(x.mean() + 1.96 * x.std(ddof=1)) if len(x) > 1 else None,
        paired_dz=float(x.mean() / x.std(ddof=1)) if len(x) > 1 and x.std(ddof=1) > 0 else None,
    )
    if len(x) > 1:
        rng = np.random.default_rng(seed)
        sample = x[rng.integers(0, len(x), size=(replicates, len(x)))]
        extra = dict(
            mae=np.abs(sample).mean(1),
            rmse=np.sqrt((sample**2).mean(1)),
            p95_absolute=np.quantile(np.abs(sample), 0.95, axis=1),
        )
        for key, value in extra.items():
            result[key + "_ci95"] = np.quantile(value, [0.025, 0.975]).tolist()
            draws[key] = value.tolist()
    return (result, draws)


def height_diagnostics(vertices, *, head_ids=None, neck_y=None):
    v = np.asarray(vertices, float)
    if v.ndim != 2 or v.shape[1] != 3 or (not np.isfinite(v).all()):
        raise ValueError("FINITE_3D_VERTICES_REQUIRED")
    low, top = (int(v[:, 1].argmin()), int(v[:, 1].argmax()))
    result = dict(
        metric="GLOBAL_Y_EXTENT_NOT_STATURE",
        vertical_extent_cm=float(np.ptp(v[:, 1]) * 100),
        highest_vertex=top,
        lowest_vertex=low,
        highest_xyz=v[top].tolist(),
        lowest_xyz=v[low].tolist(),
        above_neck_cm=None,
        below_neck_cm=None,
        head_region_extent_cm=None,
        max_minus_head_q99_cm=None,
    )
    if neck_y is not None:
        result.update(
            above_neck_cm=float((v[top, 1] - neck_y) * 100),
            below_neck_cm=float((neck_y - v[low, 1]) * 100),
        )
    if head_ids is not None and len(head_ids):
        y = v[np.asarray(head_ids), 1]
        result.update(
            head_region_extent_cm=float(np.ptp(y) * 100),
            head_vertex_count=len(y),
            max_minus_head_q99_cm=float((v[top, 1] - np.quantile(y, 0.99)) * 100),
            head_q99_y=float(np.quantile(y, 0.99)),
        )
    return result


def registry():
    base = dict(
        version=VERSION,
        coordinate_frame="saved source rigid working frame; native centimetre coordinates multiplied by 0.01 plus saved translation",
        units="engineering_cm; independent physical calibration unresolved",
        external_comparability="PROTOCOL_UNKNOWN",
        topology_dependence="source own topology; MHR LOD0 atlas; no source surface deformation",
    )
    definitions = [
        (
            "height_y_extent",
            "Global max(Y)-min(Y), not anatomical stature",
            "extreme vertices",
            "saved source / fitted / T90",
            "maximum minus minimum",
            "none",
            True,
            "GEOMETRIC_PROXY",
        ),
        (
            "waist_rib_iliac_midpoint",
            "Midpoint of last palpable rib lower margin and superior iliac crest",
            "independently identified rib and iliac crest",
            "upright; normal expiration per WHO STEPS",
            "plane in qualified anatomical frame; circumference",
            "no qualified landmarks: unavailable",
            False,
            "LANDMARKS_UNAVAILABLE",
        ),
        (
            "waist_historical",
            "Adaptive extremum in lower half of umbilicus-to-chest interval",
            "mapped model umbilicus and anterior chest features",
            "saved source / fitted / T90",
            "indexed closed raw contour",
            "umbilicus Y + 0.005 engineering m; canonical requires primary PROXY_VALID; released fallback when no selected level",
            True,
            "UNQUALIFIED_MODEL_SURFACE_PROXY",
        ),
        (
            "waist_atlas_midpoint_proxy",
            "Midpoint of lower_thorax_surface and upper_pelvis_surface atlas candidates; NOT rib/iliac crest",
            "frozen barycentric model surface candidates; source closest projection from own fit",
            "torso frame from c_spine0 to c_spine3",
            "indexed plane intersection; raw and convex tape kept separate",
            "missing/reversed anchors: unavailable",
            True,
            "UNQUALIFIED_MODEL_SURFACE_PROXY",
        ),
        (
            "abdomen_atlas_proxy",
            "Section through mapped umbilicus model surface",
            "mapped SMPL belly-button correspondence; source projected from own MHR",
            "global Y section in saved poses",
            "indexed raw and convex tape",
            "none",
            True,
            "UNQUALIFIED_MODEL_SURFACE_PROXY",
        ),
        (
            "hip_posterior_A_proxy",
            "Horizontal section at most posterior pelvic surface A within crotch-to-upper-pelvis slab",
            "official pelvic mask or nearest-face transferred source mask",
            "saved Y-up geometry; no repose",
            "existing clipped triangle extremum and indexed raw/tape section",
            "no valid pelvic slab: unavailable",
            True,
            "UNQUALIFIED_MODEL_SURFACE_PROXY",
        ),
        (
            "chest_atlas_proxy",
            "Mean level of mapped anterior chest features",
            "frozen model anterior chest points; not qualified nipples",
            "global Y in saved poses",
            "indexed torso-restricted raw/tape section",
            "invalid or excluded arm geometry: unavailable",
            True,
            "UNQUALIFIED_MODEL_SURFACE_PROXY",
        ),
        (
            "neck_historical",
            "Existing shoulder-free neck profile or historical canonical procedure",
            "c_neck/c_head rig interval where recorded",
            "saved historical pose",
            "retain exact historical definition; no common-method neck claim",
            "retain missing values",
            True,
            "UNQUALIFIED_MODEL_SURFACE_PROXY",
        ),
    ]
    return [
        dict(
            base,
            id=i,
            definition=d,
            landmarks=l,
            pose=p,
            algorithm=a,
            fallback=f,
            executable_in_cohort=e,
            anatomical_status=s,
            protocol_reference="WHO STEPS for anatomical target only; E2 implementation and historical pinned records for proxies",
        )
        for i, d, l, p, a, f, e, s in definitions
    ]
