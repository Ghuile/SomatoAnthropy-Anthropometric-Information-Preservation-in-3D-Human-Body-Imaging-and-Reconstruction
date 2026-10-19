"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import numpy as np

from somatoanthropy.data.nomo_completion import skeleton_points
from somatoanthropy.experiments.e2.core import height_diagnostics
from somatoanthropy.experiments.e2.measure import compact, proxy_sites, section
from somatoanthropy.experiments.e4.geometry import positive_mesh
from somatoanthropy.geometry.anthropometry.mhr_sites import anchor_position
from somatoanthropy.geometry.mpii_mhr_fit01.metrics import distances, samples


def summaries(d):
    return dict(
        mean=float(d.mean()),
        median=float(np.median(d)),
        rms=float(np.sqrt(np.mean(d**2))),
        p95=float(np.quantile(d, 0.95)),
    )


def geometry(source, target, count, seed, source_labels, native_labels):
    sv, sf, sz = positive_mesh(*source)
    tv, tf, tz = positive_mesh(*target)
    sp, si, _ = samples(sv, sf, count, seed)
    tp, ti, _ = samples(tv, tf, count, seed + 1)
    a, b = (distances(sp, tv, tf), distances(tp, sv, sf))
    sl = source_labels[sf[si, 0]]
    tl = native_labels[tf[ti, 0]]
    regions = {}
    for label in sorted(set(sl) | set(tl)):
        values = np.concatenate((a[sl == label], b[tl == label]))
        regions[str(label)] = dict(n=len(values), **summaries(values))
    import trimesh

    mesh = trimesh.Trimesh(tv, tf, process=False)
    return dict(
        **summaries(np.concatenate((a, b))),
        source_to_mhr=summaries(a),
        mhr_to_source=summaries(b),
        regions=regions,
        samples_per_direction=count,
        seeds=[seed, seed + 1],
        units="engineering_m",
        physical_calibration="UNCONFIRMED",
        method="E4 area sampler and exact opposite indexed triangle distance; independent evaluation seed; equal directional weights",
        source_zero_area_faces=sz,
        target_zero_area_faces=tz,
        source_samples_sha256=__import__("hashlib").sha256(sp.tobytes()).hexdigest(),
        validity=dict(
            finite=True,
            watertight=bool(mesh.is_watertight),
            winding_consistent=bool(mesh.is_winding_consistent),
            duplicate_faces=int(len(tf) - len(np.unique(np.sort(tf, axis=1), axis=0))),
            self_intersections="NOT_TESTED",
        ),
        region_method="official dominant joint label at first sampled face corner; source labels transferred once from historical fitted vertices; unvalidated anatomical proxy",
    )


def regions(names):
    result = np.full(len(names), "torso", dtype="U16")
    for i, name in enumerate(names):
        if any((s in name for s in ("head", "jaw", "eye", "teeth", "neck", "tongue"))):
            result[i] = "head_neck"
        elif any(
            (s in name for s in ("finger", "thumb", "index", "middle", "ring", "pinky", "hand"))
        ):
            result[i] = "hands"
        elif any((s in name for s in ("foot", "ball", "toe"))):
            result[i] = "feet"
        elif any((s in name for s in ("leg", "knee"))):
            result[i] = "legs"
        elif "arm" in name or "clavicle" in name:
            result[i] = "arms"
    return result


def dimensions(joints):
    result = {}
    for name, a, b in (
        ("left_thigh", "l_upleg", "l_lowleg"),
        ("right_thigh", "r_upleg", "r_lowleg"),
        ("left_shank", "l_lowleg", "l_foot"),
        ("right_shank", "r_lowleg", "r_foot"),
        ("left_upper_arm", "l_uparm", "l_lowarm"),
        ("right_upper_arm", "r_uparm", "r_lowarm"),
        ("root_neck", "root", "c_neck"),
        ("neck_head", "c_neck", "c_head"),
        ("hip_width", "l_upleg", "r_upleg"),
        ("shoulder_width", "l_uparm", "r_uparm"),
        ("left_foot", "l_foot", "l_ball"),
        ("right_foot", "r_foot", "r_ball"),
    ):
        if a in joints and b in joints:
            delta = joints[b] - joints[a]
            result[name] = dict(
                length_cm=float(np.linalg.norm(delta) * 100), vertical_cm=float(delta[1] * 100)
            )
    for part in ("thigh", "shank", "upper_arm", "foot"):
        if "left_" + part in result and "right_" + part in result:
            a, b = (result[s + part]["length_cm"] for s in ("left_", "right_"))
            result[part + "_relative_asymmetry"] = float(abs(a - b) / ((a + b) / 2))
    return result


def measurements(mesh, atlas, masks, old, head):
    v, f = (mesh["vertices"], mesh["faces"])
    joints = skeleton_points(mesh)
    anchors = {k: anchor_position(v, f, a) for k, a in atlas["anchors"].items()}
    sites, engine = proxy_sites(v, f, anchors, joints, masks)
    fixed = {}
    for site in ("waist", "abdomen", "hip", "neck", "chest"):
        q = old["historical"]["source"][site]
        if "plane_origin_m" not in q or q.get("value") is None:
            fixed[site] = dict(
                geometry_quality="INVALID", reason="SOURCE_HISTORICAL_SITE_UNAVAILABLE"
            )
            continue
        allowed = (
            masks["pelvis" if site == "hip" else "torso"] if site != "neck" else head[f].all(1)
        )
        fixed[site] = compact(
            section(
                engine,
                q["plane_origin_m"],
                q["plane_normal"],
                joints["c_neck" if site == "neck" else "root"],
                allowed,
            )
        )
        fixed[site].update(
            quantity=q["quantity"],
            source_value=q["value"],
            source_fallback=q.get("fallback_applied", False),
            interpretation="fixed historical source plane; pose-sensitive engineering diagnostic; not a relocated anatomical site",
        )
    return dict(
        height=height_diagnostics(
            v, head_ids=np.flatnonzero(head), neck_y=float(joints["c_neck"][1])
        ),
        dimensions=dimensions(joints),
        proxy={k: compact(q) for k, q in sites.items()},
        fixed_source_plane=fixed,
    )
