"""Portable E3 orchestration using the frozen geometry and bootstrap functions."""

from collections import defaultdict
from itertools import combinations

import numpy as np

from somatoanthropy.experiments.e2.measure import section
from somatoanthropy.experiments.e3.analysis import summary_stats
from somatoanthropy.experiments.e3.core import (
    SEED,
    SITES,
    dispersion,
    indexed_difference,
    local_plane,
    reference_site,
)
from somatoanthropy.experiments.e3.measure import common, fields
from somatoanthropy.experiments.e4.core import seed_for


def geometry_summary(observations, load_arrays):
    """Six indexed meshes per person; aggregate their 15 pairs before inference.

    Each input has subject_uid, observation_uid and canonical_mesh. Units are
    engineering metres. A caller may subset common indexed vertices beforehand.
    """
    groups = defaultdict(list)
    for row in observations:
        groups[row["subject_uid"]].append(row)
    person_rows = []
    for uid, rows in sorted(groups.items()):
        if len(rows) != 6 or len({r["observation_uid"] for r in rows}) != 6:
            raise ValueError("SIX_DISTINCT_OBSERVATIONS_PER_PERSON_REQUIRED")
        meshes = [load_arrays(r["canonical_mesh"]) for r in rows]
        if any(not np.array_equal(m["faces"], meshes[0]["faces"]) for m in meshes):
            raise ValueError("MATCHED_INDEXED_TOPOLOGY_REQUIRED")
        vertices = np.stack([m["vertices"] for m in meshes])
        centered = vertices - vertices.mean(1)[:, None, :]
        for alignment, data in [
            ("saved_floor_frame", vertices),
            ("centroid_translation_only", centered),
        ]:
            values = [
                indexed_difference(data[a], data[b])["rms_cm"] for a, b in combinations(range(6), 2)
            ]
            person_rows.append(
                dict(subject_uid=uid, alignment=alignment, pair_count=15, **dispersion(values))
            )
    aggregate = []
    for alignment in ["saved_floor_frame", "centroid_translation_only"]:
        values = [r["median"] for r in person_rows if r["alignment"] == alignment]
        aggregate.append(
            dict(
                region="global_surface",
                alignment=alignment,
                **summary_stats(values, seed_for(SEED, "global_surface", alignment)),
            )
        )
    return dict(persons=person_rows, aggregate=aggregate)


# The computational loop is retained from E3 measure.run; file/cache handling is supplied by the caller.
def measurement_records(panel, load_arrays, atlas, masks):
    all_records, states = ([], [])
    for subject in sorted({r["subject_uid"] for r in panel["rows"]}):
        rows = [r for r in panel["rows"] if r["subject_uid"] == subject]
        ref = reference_site(rows)
        refmesh = load_arrays(ref["canonical_mesh"])
        refsites, _, refjoints = common(refmesh, atlas, masks)
        reference_planes = {}
        for site, q in refsites.items():
            if q.get("geometry_quality") == "VALID" and "plane_origin_m" in q:
                p, n = local_plane(q["plane_origin_m"], q["plane_normal"], refjoints["root"])
                reference_planes[site] = (p, n)
        for r in rows:
            mesh = load_arrays(r["canonical_mesh"])
            sites, engine, joints = common(mesh, atlas, masks)
            state = dict(
                selection_id=r["selection_id"],
                root=joints["root"].tolist(),
                common=sites,
                historical={},
                fixed={},
                reference_id=ref["selection_id"],
            )
            records = []
            for site, q in sites.items():
                for functional in ("raw_contour_cm", "tape_envelope_cm"):
                    records.append(
                        fields(r, site, "B_common_" + functional, q, functional=functional)
                    )
                if site in reference_planes:
                    p, n = reference_planes[site]
                    allowed = (
                        masks["pelvis"]
                        if site == "hip"
                        else masks["torso"]
                        if site != "neck"
                        else None
                    )
                    fixed = section(
                        engine,
                        joints["root"] + p,
                        n,
                        joints["root"] + p if site == "neck" else joints["root"],
                        allowed,
                    )
                    fixed["reference_selection_id"] = ref["selection_id"]
                    state["fixed"][site] = fixed
                    for functional in ("raw_contour_cm", "tape_envelope_cm"):
                        records.append(
                            fields(
                                r,
                                site,
                                "C_fixed_F01_" + functional,
                                fixed,
                                functional=functional,
                                eligible=r["selection_id"] != ref["selection_id"],
                            )
                        )
            for old in r["historical"]:
                site = old["definition"]
                detail = r["details"][site]
                q = dict(detail)
                q["geometry_quality"] = (
                    "VALID"
                    if detail.get("closed_loop_count", 0) > 0
                    and len(detail.get("points_m", [])) >= 3
                    else "INVALID"
                )
                q["historical_quality_state"] = old["quality_state"]
                q["historical_engineering_value_cm"] = old["engineering_value_cm"]
                functional = old["quantity"]
                q[functional] = old["engineering_value_cm"]
                a = fields(
                    r,
                    site,
                    "A_historical_strict",
                    q,
                    functional=functional,
                    eligible=old["quality_state"] == "PROXY_VALID",
                )
                a["measurement_protocol_version"] = old["version"]
                records.append(a)
                if "plane_origin_m" in detail:
                    audited = section(
                        engine,
                        detail["plane_origin_m"],
                        detail["plane_normal"],
                        joints["root"],
                        masks["pelvis"] if site == "hip" else masks["torso"],
                    )
                    audited.update(
                        fallback_applied=old["fallback_applied"],
                        historical_quality_state=old["quality_state"],
                    )
                    q["indexed_reextraction"] = audited
                    q["root_local_plane_m"], q["root_local_normal"] = [
                        x.tolist()
                        for x in local_plane(
                            detail["plane_origin_m"], detail["plane_normal"], joints["root"]
                        )
                    ]
                    for fun in ("raw_contour_cm", "tape_envelope_cm"):
                        records.append(
                            fields(r, site, "A_inclusive_indexed_" + fun, audited, functional=fun)
                        )
                state["historical"][site] = q
            all_records.extend(records)
            states.append(state)
    return dict(records=all_records, states=states)


def measurement_summary(panel, metrology):
    rows = panel["rows"]
    records = list(metrology["records"])
    for r in metrology["records"]:
        if r["method"].startswith("B_common_") and r["site"] != "height":
            method = r["method"].replace("B_common_", "B_heldout_F01_")
            records.append(
                dict(
                    r,
                    method=method,
                    comparison_type=method,
                    result_value=None if r["selection_id"].endswith("F01") else r["result_value"],
                    reference_excluded=r["selection_id"].endswith("F01"),
                )
            )
    uids = sorted({r["subject_uid"] for r in rows})
    aliases = {r["subject_uid"]: r["subject_label"] for r in rows}
    participant, aggregate = ([], [])
    methods = sorted({r["method"] for r in records})
    for method in methods:
        for site in SITES:
            recs = [r for r in records if r["method"] == method and r["site"] == site]
            for uid in uids:
                rr = [r for r in recs if r["subject_uid"] == uid]
                vals = [r["result_value"] for r in rr if r["result_value"] is not None]
                participant.append(
                    dict(
                        subject_uid=uid,
                        participant=aliases[uid],
                        site=site,
                        method=method,
                        selected=6,
                        expected_evaluated=5 if method.startswith(("C_", "B_heldout_")) else 6,
                        fallback=sum((r["fallback"] for r in rr)),
                        **dispersion(vals),
                    )
                )
            pp = [p for p in participant if p["method"] == method and p["site"] == site]
            for subset in ("available_at_least_two", "complete_six"):
                eligible = [
                    p for p in pp if p["n"] >= 2 and (subset != "complete_six" or p["n"] == 6)
                ]
                for metric in ("sd", "range", "pairwise_median", "mad"):
                    aggregate.append(
                        dict(
                            method=method,
                            site=site,
                            subset=subset,
                            metric=metric,
                            valid_observations=sum((p["n"] for p in pp)),
                            selected_observations=60,
                            complete_six=sum((p["n"] == 6 for p in pp)),
                            **summary_stats(
                                [p[metric] for p in eligible],
                                seed_for(SEED, method, site, subset, metric),
                            ),
                        )
                    )
    return dict(participants=participant, aggregate=aggregate)
