"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from collections import defaultdict

import numpy as np
from numpy.typing import NDArray
from scipy.spatial import cKDTree
from trimesh.triangles import closest_point

from somatoanthropy.experiments.e4.core import bootstrap, describe
from somatoanthropy.geometry.mpii_mhr_fit01.metrics import mesh, samples

VERSION = "e1-20261018-02"
SEED = 18102601
COUNT = 4096
REGION_NOTE = "Fit-dependent native-weight engineering proxy; projected source assignment is not independent anatomical annotation"


def checked_pair(a, b):
    if a["dataset"] == "NHANES":
        raise ValueError("CONDITIONING_HAS_NO_OBSERVED_SOURCE_SURFACE")
    if a["state"] != "fitted":
        raise ValueError("SOURCE_RECONSTRUCTION_REQUIRES_FITTED_POSE")
    if any((a.get(k) != b.get(k) for k in ("subject_uid", "body_uid", "fit_uid"))):
        raise ValueError("EXACT_BODY_LINEAGE_REQUIRED")


def dimensions(vertices):
    v = np.asarray(vertices, float)
    if v.ndim != 2 or v.shape[1] != 3 or (not np.isfinite(v).all()):
        raise ValueError("FINITE_NX3_REQUIRED")
    return dict(
        extent=np.ptp(v, axis=0).tolist(),
        floor=float(v[:, 1].min()),
        top=float(v[:, 1].max()),
        upper_q99=float(np.quantile(v[:, 1], 0.99)),
    )


def canonical_controls(fit, canon, reference):

    def normalize(d):
        return {
            key: np.asarray(d.get(key, d.get(alias))).reshape(1, size)
            for key, alias, size in [
                ("identity_coeffs", "identity", 45),
                ("lbs_model_params", "model", 204),
                ("face_expr_coeffs", "expression", 72),
            ]
        }

    a, b = (normalize(fit), normalize(canon))
    if not all((np.isfinite(v).all() for d in (a, b) for v in d.values())):
        raise ValueError("FINITE_NATIVE_CONTROLS_REQUIRED")
    return dict(
        identity_preserved=bool(np.array_equal(a["identity_coeffs"], b["identity_coeffs"])),
        morphology_preserved=bool(
            np.array_equal(a["lbs_model_params"][:, 130:], b["lbs_model_params"][:, 130:])
        ),
        expression_preserved=bool(np.array_equal(a["face_expr_coeffs"], b["face_expr_coeffs"])),
        pinned_articulation=bool(
            np.array_equal(b["lbs_model_params"][:, :130], reference["lbs_model_params"][:, :130])
        ),
        fitted_articulation_distance=float(
            np.linalg.norm(a["lbs_model_params"][:, :130] - b["lbs_model_params"][:, :130])
        ),
        morphology_nonzero=int(np.count_nonzero(a["lbs_model_params"][:, 130:])),
    )


def select_people(rows, maximum):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["subject_uid"]].append(row.get("source_extent") or 0)
    order = sorted(grouped, key=lambda uid: (float(np.median(grouped[uid])), uid))
    ids = (
        np.rint(np.linspace(0, len(order) - 1, min(maximum, len(order)))).astype(int)
        if order
        else []
    )
    return [order[i] for i in ids]


def statistics(values):
    return describe(values)


def participant_summary(rows, field, *, seed=SEED):
    groups = defaultdict(list)
    for r in rows:
        if r.get(field) is not None:
            groups[r["subject_uid"]].append(r[field])
    x = [float(np.mean(groups[k])) for k in sorted(groups)]
    ci = bootstrap(x, seed=seed, replicates=2000)["mean_ci95"]
    return dict(
        participants=len(x),
        observations=sum((len(v) for v in groups.values())),
        **statistics(x),
        mean_ci95=ci,
    )


class TriangleQuery:
    """Existing exact centroid-radius bound, additionally returning nearest face IDs."""

    def __init__(self, v, f):
        self.v, self.f = mesh(v, f)
        self.tri = self.v[self.f]
        self.centers = self.tri.mean(1)
        self.radii = np.linalg.norm(self.tri - self.centers[:, None], axis=2).max(1)
        self.tree, self.vtree = (cKDTree(self.centers), cKDTree(self.v))

    def query(self, points):
        p = np.asarray(points, float)
        upper = self.vtree.query(p)[0]
        ds = np.empty(len(p))
        face: NDArray[np.int64] = np.empty(len(p), dtype=np.int64)
        for start in range(0, len(p), 128):
            candidates = self.tree.query_ball_point(
                p[start : start + 128], upper[start : start + 128] + float(self.radii.max()) + 1e-12
            )
            for k, ids in enumerate(candidates, start):
                ids = np.asarray(ids, dtype=int)
                ids = ids[
                    np.linalg.norm(self.centers[ids] - p[k], axis=1)
                    <= upper[k] + self.radii[ids] + 1e-12
                ]
                cp = closest_point(self.tri[ids], np.broadcast_to(p[k], (len(ids), 3)))
                distance = np.linalg.norm(cp - p[k], axis=1)
                best = int(np.argmin(distance))
                ds[k], face[k] = (distance[best], ids[best])
        return (ds, face)


def _positive(v, f):
    v, f = mesh(v, f)
    tri = v[f]
    good = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) > 0
    return (v, f[good], good)


def _stats(a, b):
    d = np.concatenate((a, b))
    return dict(
        symmetric_mean=float(d.mean()),
        median=float(np.median(d)),
        rms=float(np.sqrt(np.mean(d * d))),
        p95=float(np.quantile(d, 0.95)),
        source_to_mhr_mean=float(a.mean()) if len(a) else None,
        mhr_to_source_mean=float(b.mean()) if len(b) else None,
        source_samples=len(a),
        mhr_samples=len(b),
        coverage_fraction_at_0p02=float(np.mean(d <= 0.02)),
    )


def surface_pair(source, fitted, *, count, seed, region_faces=None, retain=False):
    a, af, ag = _positive(*source)
    b, bf, bg = _positive(*fitted)
    ap, ai, _ = samples(a, af, count, seed)
    bp, bi, _ = samples(b, bf, count, seed + 1)
    da, nearest = TriangleQuery(b, bf).query(ap)
    db, source_nearest = TriangleQuery(a, af).query(bp)
    global_ = _stats(da, db)
    global_.update(
        samples_per_direction=count,
        seeds=[seed, seed + 1],
        source_zero_area_faces_masked=int((~ag).sum()),
        target_zero_area_faces_masked=int((~bg).sum()),
        method="area-uniform samples to exact opposite triangles; equal directional count",
        no_posthoc_alignment=True,
    )

    def normals(v, f):
        t = v[f]
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        return n / np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-30)

    an, bn = (normals(a, af), normals(b, bf))
    na = np.abs(np.einsum("ij,ij->i", an[ai], bn[nearest]))
    nb = np.abs(np.einsum("ij,ij->i", bn[bi], an[source_nearest]))
    global_["unoriented_normal_agreement"] = float(np.r_[na, nb].mean())
    regions = []
    for name, mask in (region_faces or {}).items():
        mask = np.asarray(mask, bool)[bg]
        sa, sb = (mask[nearest], mask[bi])
        if not sa.any() or not sb.any():
            regions.append(
                dict(
                    region=name,
                    available=False,
                    source_samples=int(sa.sum()),
                    mhr_samples=int(sb.sum()),
                    reason="NO_SAMPLES_IN_ONE_DIRECTION",
                )
            )
            continue
        region = dict(
            region=name,
            available=True,
            **_stats(da[sa], db[sb]),
            source_sample_coverage=float(sa.mean()),
            mhr_sample_coverage=float(sb.mean()),
            interpretation=REGION_NOTE,
            normal_agreement=float(np.r_[na[sa], nb[sb]].mean()),
        )
        region["sample_extent_delta"] = (np.ptp(bp[sb], axis=0) - np.ptp(ap[sa], axis=0)).tolist()
        regions.append(region)
    result = dict(global_metric=global_, regions=regions)
    result["global"] = result.pop("global_metric")
    if retain:
        result["sample_points"] = dict(
            source=ap.tolist(),
            mhr=bp.tolist(),
            source_distance=da.tolist(),
            mhr_distance=db.tolist(),
        )
    return result


def region_faces(masks, faces):
    if len(masks["dominant_joint"]) != int(faces.max()) + 1:
        raise ValueError("NATIVE_LOD0_REGION_TOPOLOGY_REQUIRED")
    names = masks["joint_names"][masks["dominant_joint"]]
    vertices = {
        "head_neck": np.char.startswith(names, "c_neck") | np.isin(names, ["c_head", "c_jaw"]),
        "abdomen": np.isin(names, ["c_spine0", "c_spine1"]),
        "thorax": np.isin(names, ["c_spine2", "c_spine3"]),
        "upper_limbs": np.isin(
            names,
            [s + "_" + j for s in ("l", "r") for j in ("uparm", "lowarm", "wrist", "wrist_twist")],
        ),
        "lower_limbs": np.isin(
            names, [s + "_" + j for s in ("l", "r") for j in ("upleg", "lowleg")]
        ),
        "feet": np.isin(
            names,
            [
                s + "_" + j
                for s in ("l", "r")
                for j in ("foot", "ball", "talocrural", "subtalar", "transversetarsal")
            ],
        ),
    }
    return dict(
        torso=masks["torso"],
        pelvis=masks["pelvis"],
        **{k: np.sum(v[faces], axis=1) >= 2 for k, v in vertices.items()},
    )
