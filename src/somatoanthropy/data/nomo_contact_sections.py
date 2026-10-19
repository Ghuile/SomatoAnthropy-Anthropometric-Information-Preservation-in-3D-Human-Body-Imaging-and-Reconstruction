"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import numpy as np
from scipy.spatial import ConvexHull

from somatoanthropy.geometry.fit03_anthropometry.core import (
    MeshMetrology,
    contains,
    project,
    simple_polygon,
)


def unavailable(reason, **details):
    check = details.pop("region_check", dict(valid=False, reason=reason))
    return dict(
        geometry_quality="INVALID",
        engineering_value_cm=None,
        points_m=[],
        raw_points_m=[],
        tape_points_m=[],
        raw_contour_cm=None,
        tape_envelope_cm=None,
        reason=reason,
        region_check=check,
        scientific_margins_approved=False,
        **details,
    )


class IndexedSections:
    """Do not weld a touching hand to a trunk with different mesh indices.

    Ordinary triangle crossings use indexed edges. Vertex/edge coincidences
    delegate to the existing indexed metrology implementation. No gap bridging,
    clipping, caps, surface deformation or new correspondence fitting occurs.
    """

    def __init__(self, vertices, faces):
        self.v = np.asarray(vertices, float)
        original = np.asarray(faces, np.int64)
        edges = original[:, [[0, 1], [1, 2], [2, 0]]].reshape(-1, 2)
        zero = np.all(self.v[edges[:, 0]] == self.v[edges[:, 1]], axis=1)
        parent = np.arange(len(self.v))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for a, b in edges[zero]:
            parent[find(b)] = find(a)
        if zero.any():
            mapping = np.array([find(i) for i in range(len(self.v))])
            original = mapping[original]
        self.authored_zero_edge_equivalences = int(
            np.count_nonzero(parent != np.arange(len(self.v)))
        )
        tri = self.v[original]
        good = (
            np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) > 1e-18
        )
        self.ids = np.flatnonzero(good)
        self.f = original[good]
        self.ignored_degenerate_faces = int((~good).sum())

    def section(self, point, normal, seed, allowed=None):
        point, normal, seed = map(lambda p: np.asarray(p, float), (point, normal, seed))
        normal = normal / np.linalg.norm(normal)
        d = (self.v - point) @ normal
        side = d[self.f]
        candidate = np.flatnonzero((side.min(1) <= 1e-10) & (side.max(1) >= -1e-10))
        if not len(candidate):
            return unavailable("NO_INTERSECTION")
        if np.any(np.abs(side[candidate]) <= 1e-10):
            q = MeshMetrology(dict(vertices=self.v, faces=self.f, length_units="m")).section(
                point, normal, seed
            )
            if q["status"] != "MEASURED":
                return unavailable(q.get("reason", "INVALID_INDEXED_SECTION"))
            raw = np.asarray(q["points_m"])
            supporting = self.ids[q["selected_face_ids"]]
            loops = q["closed_loop_count"]
        else:
            faces = self.f[candidate]
            edges = faces[:, [[0, 1], [1, 2], [2, 0]]]
            crossing = d[edges[:, :, 0]] * d[edges[:, :, 1]] < 0
            pairs = np.sort(edges[crossing], axis=1)
            nodes, inverse = np.unique(pairs, axis=0, return_inverse=True)
            segments = inverse.reshape(-1, 2)
            fraction = d[nodes[:, 0]] / (d[nodes[:, 0]] - d[nodes[:, 1]])
            xyz = self.v[nodes[:, 0]] + fraction[:, None] * (
                self.v[nodes[:, 1]] - self.v[nodes[:, 0]]
            )
            adjacency = [[] for _ in nodes]
            for i, (a, b) in enumerate(segments):
                adjacency[a].append((int(b), i))
                adjacency[b].append((int(a), i))
            remaining = set(range(len(nodes)))
            candidates, loops = ([], 0)
            while remaining:
                first = min(remaining)
                stack, component = ([first], set())
                while stack:
                    node = stack.pop()
                    if node in component:
                        continue
                    component.add(node)
                    stack.extend((n for n, _ in adjacency[node] if n not in component))
                remaining.difference_update(component)
                if any((len(adjacency[n]) != 2 for n in component)):
                    continue
                ordered, used, previous, current = ([], [], -1, first)
                while True:
                    ordered.append(current)
                    following, segment = next((x for x in adjacency[current] if x[0] != previous))
                    used.append(segment)
                    previous, current = (current, following)
                    if current == first:
                        break
                ring = xyz[ordered]
                xy = project(ring - point, normal)
                if not simple_polygon(xy):
                    continue
                loops += 1
                if contains(xy, project((seed - point)[None], normal)[0]):
                    candidates.append((ring, self.ids[candidate[used]]))
            if len(candidates) != 1:
                return unavailable("NO_UNIQUE_SIMPLE_INDEXED_TARGET_RING", closed_loop_count=loops)
            raw, supporting = candidates[0]
        outside = supporting[~np.asarray(allowed, bool)[supporting]] if allowed is not None else []
        check = dict(
            valid=not len(outside),
            supporting_face_count=len(supporting),
            outside_face_count=len(outside),
            outside_face_ids=np.asarray(outside, int).tolist(),
        )
        if len(outside):
            return unavailable("INDEXED_TARGET_RING_INCLUDES_EXCLUDED_REGION", region_check=check)
        xy = project(raw - point, normal)
        tape = raw[ConvexHull(xy).vertices]

        def girth(p):
            return float(np.linalg.norm(np.roll(p, -1, axis=0) - p, axis=1).sum() * 100)

        return dict(
            geometry_quality="VALID",
            reason="CLOSED_INDEXED_TARGET_RING",
            points_m=raw.tolist(),
            raw_points_m=raw.tolist(),
            tape_points_m=tape.tolist(),
            raw_contour_cm=girth(raw),
            tape_envelope_cm=girth(tape),
            plane_origin_m=point.tolist(),
            plane_normal=normal.tolist(),
            selected_face_ids=np.asarray(supporting, int).tolist(),
            region_check=check,
            closed_loop_count=loops,
            surface_contour_closed=True,
            ignored_degenerate_faces=self.ignored_degenerate_faces,
            authored_zero_edge_equivalences=self.authored_zero_edge_equivalences,
            connectivity="ORIGINAL_INDEX_CONNECTIVITY_WITH_EXPLICIT_ZERO_EDGE_EQUIVALENCE_NO_SPATIAL_WELD",
            scientific_margins_approved=False,
        )


def neck_section(engine, joints, allowed):
    """Smallest shoulder-free ring in a bounded neck-to-head search window.

    The 45–95% window and 2.5% lattice are engineering settings, not anatomical
    constants or scientific preservation margins. Boundary minima are withheld.
    """
    a, b = (joints["c_neck"], joints["c_head"])
    normal = (b - a) / np.linalg.norm(b - a)
    profile, results = ([], [])
    for t in np.linspace(0.45, 0.95, 21):
        p = a + t * (b - a)
        q = engine.section(p, normal, p, allowed)
        profile.append(
            dict(fraction=float(t), value_cm=q.get("tape_envelope_cm"), reason=q["reason"])
        )
        results.append(q)
    eligible = [i for i, q in enumerate(results) if q["geometry_quality"] == "VALID"]
    if not eligible:
        return unavailable("NO_SHOULDER_FREE_CLOSED_NECK_RING", search_profile=profile)
    chosen = min(eligible, key=lambda i: (results[i]["tape_envelope_cm"], i))
    if chosen in (0, len(results) - 1):
        return unavailable("NECK_MINIMUM_AT_SEARCH_BOUNDARY", search_profile=profile)
    q = results[chosen]
    q.update(
        points_m=q["tape_points_m"],
        engineering_value_cm=q["tape_envelope_cm"],
        quantity="tape_envelope_cm",
        reason="SHOULDER_EXCLUDED_NECK_PROFILE_MINIMUM",
        definition="BOUNDED_SHOULDER_FREE_NECK_PROFILE_TAPE_MINIMUM",
        selected_fraction=profile[chosen]["fraction"],
        search_profile=profile,
        interpretation_status="ENGINEERING_INTERPRETATION",
        clinical_validity="NOT_ESTABLISHED",
        iso_conformance_claim=False,
    )
    return q


def correct_trunk(engine, previous, masks):
    """Retain saved site heights; never insert an artificial torso bridge."""
    import copy

    result = copy.deepcopy(previous)
    for name in ("chest", "waist", "abdomen", "hip"):
        old = previous[name]
        if "plane_origin_m" not in old:
            continue
        q = engine.section(
            old["plane_origin_m"],
            [0, 1, 0],
            old["plane_origin_m"],
            masks["pelvis" if name == "hip" else "torso"],
        )
        quantity = "tape_envelope_cm" if name == "hip" else "raw_contour_cm"
        result[name].update(q, quantity=quantity, engineering_value_cm=q.get(quantity))
        result[name].update(
            quality_state="ENGINEERING_INTERPRETATION"
            if q["geometry_quality"] == "VALID"
            else "NOT_EVALUABLE",
            interpretation_status="ENGINEERING_INTERPRETATION",
            iso_conformance_claim=False,
            previous_geometry_quality=old["geometry_quality"],
            previous_reason=old["reason"],
        )
        if name == "hip" and q["geometry_quality"] == "VALID":
            result[name]["points_m"] = q["tape_points_m"]
    return result
