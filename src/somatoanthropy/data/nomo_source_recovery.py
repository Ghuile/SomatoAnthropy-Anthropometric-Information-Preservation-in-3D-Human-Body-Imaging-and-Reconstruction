"""Frozen source-reference contour definitions; no delivery or participant IO."""

from __future__ import annotations

import numpy as np
import trimesh
from scipy.spatial import ConvexHull

from somatoanthropy.geometry.anthropometry.mhr_sites import anchor_position, surface_anchor
from somatoanthropy.geometry.anthropometry.model import Plane
from somatoanthropy.geometry.anthropometry.section import mesh_section
from somatoanthropy.geometry.anthropometry.three_landmark_hip import locate_landmarks
from somatoanthropy.geometry.fit03_anthropometry.core import contains, project, simple_polygon

from .nomo_contact_seams import SourceSeamSections
from .nomo_contact_sections import IndexedSections


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def split_trace(points, faces, seed):
    """Split an indexed closed trace only where its existing segments intersect.

    Select the unique simple cycle containing the torso seed. Preserve all other
    cycles as diagnostics. Every resulting edge retains its original supporting
    face. This is an explicit engineering cycle decomposition, not mesh repair,
    smoothing, a convex hull, a gap fill, or physical/anatomical qualification.
    """
    p, ids = (np.asarray(points, float), np.asarray(faces, int))
    discarded = []
    if not contains(p, seed):
        raise ValueError("NO_UNIQUE_SEED_CYCLE")
    for _ in range(128):
        if simple_polygon(p):
            return (p, ids, discarded)
        roundoff = 16 * np.finfo(float).eps * max(float(np.abs(p).max()), 0.001)
        repeated = next(
            (
                (i, j)
                for i in range(len(p))
                for j in range(i + 2, len(p))
                if np.linalg.norm(p[i] - p[j]) <= roundoff
            ),
            None,
        )
        if repeated is not None:
            i, j = repeated
            children = [(p[i:j], ids[i:j]), (np.vstack((p[j:], p[:i])), np.r_[ids[j:], ids[:i]])]
            eligible = [
                k
                for k, (child, _) in enumerate(children)
                if len(child) >= 3 and contains(child, seed)
            ]
            if len(eligible) != 1:
                raise ValueError("NO_UNIQUE_SEED_CYCLE")
            chosen = eligible[0]
            discarded.append(children[1 - chosen][0])
            p, ids = children[chosen]
            continue
        intersection = None
        for i, a in enumerate(p):
            ab = p[(i + 1) % len(p)] - a
            for j in range(i + 2, len(p)):
                if i == 0 and j == len(p) - 1:
                    continue
                c, d = (p[j], p[(j + 1) % len(p)])
                den = cross(ab, d - c)
                if abs(den) <= 1e-18:
                    continue
                t, u = (cross(c - a, d - c) / den, cross(c - a, ab) / den)
                if 1e-12 < t < 1 - 1e-12 and 1e-12 < u < 1 - 1e-12:
                    intersection = (i, j, a + t * ab)
                    break
            if intersection is not None:
                break
        if intersection is None:
            raise ValueError("UNRESOLVED_NONSIMPLE_SOURCE_TRACE")
        i, j, x = intersection
        children = [
            (np.vstack((x, p[i + 1 : j + 1])), np.r_[ids[i], ids[i + 1 : j], ids[j]]),
            (np.vstack((x, p[j + 1 :], p[: i + 1])), np.r_[ids[j], ids[j + 1 :], ids[:i], ids[i]]),
        ]
        eligible = [i for i, (child, _) in enumerate(children) if contains(child, seed)]
        if len(eligible) != 1:
            raise ValueError("NO_UNIQUE_SEED_CYCLE")
        chosen = eligible[0]
        discarded.append(children[1 - chosen][0])
        p, ids = children[chosen]
    raise ValueError("SOURCE_TRACE_DECOMPOSITION_LIMIT")


def indexed_traces(engine, point, normal):
    """All degree-two closed components with original face IDs per segment."""
    d = (engine.v - point) @ normal
    side = d[engine.f]
    candidate = np.flatnonzero((side.min(1) < 0) & (side.max(1) > 0))
    if not len(candidate):
        return []
    if np.any(np.abs(side[candidate]) <= 1e-10):
        section = mesh_section(
            dict(vertices=engine.v, faces=engine.f, length_units="m"),
            Plane(tuple(point), tuple(normal)),
        )
        if section.diagnostics["branched_node_ids"]:
            return []
        traces = []
        for path in section.polylines:
            if not path.closed:
                continue
            support = []
            for a, b in zip(path.node_ids[:-1], path.node_ids[1:], strict=True):
                vertices = set(a + b)
                fits = [
                    k
                    for k in np.flatnonzero((side.min(1) <= 1e-10) & (side.max(1) >= -1e-10))
                    if vertices.issubset(set(engine.f[k]))
                ]
                if not fits:
                    break
                support.append(engine.ids[fits[0]])
            if len(support) == len(path.points) - 1:
                traces.append((np.asarray(path.points[:-1]), np.asarray(support)))
        return traces
    edges = engine.f[candidate][:, [[0, 1], [1, 2], [2, 0]]]
    pairs = np.sort(edges[d[edges[:, :, 0]] * d[edges[:, :, 1]] < 0], axis=1)
    nodes, inverse = np.unique(pairs, axis=0, return_inverse=True)
    segments = inverse.reshape(-1, 2)
    t = d[nodes[:, 0]] / (d[nodes[:, 0]] - d[nodes[:, 1]])
    xyz = engine.v[nodes[:, 0]] + t[:, None] * (engine.v[nodes[:, 1]] - engine.v[nodes[:, 0]])
    adjacency = [[] for _ in nodes]
    for k, (a, b) in enumerate(segments):
        adjacency[a].append((int(b), k))
        adjacency[b].append((int(a), k))
    remaining, traces = (set(range(len(nodes))), [])
    while remaining:
        first = min(remaining)
        stack, component = ([first], set())
        while stack:
            node = stack.pop()
            if node in component:
                continue
            component.add(node)
            stack.extend((a for a, _ in adjacency[node] if a not in component))
        remaining.difference_update(component)
        if any((len(adjacency[a]) != 2 for a in component)):
            continue
        order, used, previous, current = ([], [], -1, first)
        while True:
            order.append(current)
            following, k = next((x for x in adjacency[current] if x[0] != previous))
            used.append(k)
            previous, current = (current, following)
            if current == first:
                break
        traces.append((xyz[order], engine.ids[candidate[used]]))
    return traces


class SurfaceCycleSections(SourceSeamSections):
    """Fallback for closed, wholly target-region source traces with local folds."""

    def __init__(self, vertices, faces):
        self.original_faces = np.asarray(faces, int)
        super().__init__(vertices, faces)

    def section(self, point, normal, seed, allowed=None):
        previous = IndexedSections.section(self, point, normal, seed, allowed)
        if (
            previous["geometry_quality"] == "VALID"
            or previous["reason"] == "INDEXED_TARGET_RING_INCLUDES_EXCLUDED_REGION"
            or allowed is None
        ):
            return previous
        point, normal, seed = (np.asarray(x, float) for x in (point, normal, seed))
        normal /= np.linalg.norm(normal)
        basis = project(np.eye(3), normal)
        seed_xy = (seed - point) @ basis
        eligible, rejected = ([], [])
        for raw, supporting in indexed_traces(self, point, normal):
            xy = (raw - point) @ basis
            if not contains(xy, seed_xy):
                continue
            outside = supporting[~np.asarray(allowed, bool)[supporting]]
            if len(outside):
                rejected.append(
                    dict(
                        reason="CLOSED_TRACE_INCLUDES_EXCLUDED_REGION",
                        outside_face_ids=outside.tolist(),
                    )
                )
                continue
            try:
                p, ids, discarded = split_trace(xy, supporting, seed_xy)
            except ValueError as error:
                rejected.append(dict(reason=str(error)))
                continue
            ring = point + p @ basis.T
            residual = 0.0
            for a, b, fid in zip(ring, np.roll(ring, -1, axis=0), ids, strict=True):
                matches = np.flatnonzero(supporting == fid)
                supported = False
                for k in matches:
                    start, end = (raw[k], raw[(k + 1) % len(raw)])
                    edge = end - start
                    t = np.array([np.dot(x - start, edge) / np.dot(edge, edge) for x in (a, b)])
                    errors = np.linalg.norm(np.array([a, b]) - (start + t[:, None] * edge), axis=1)
                    if np.all(t >= -1e-10) and np.all(t <= 1 + 1e-10) and (errors.max() <= 1e-10):
                        residual = max(residual, float(errors.max()))
                        supported = True
                        break
                if not supported:
                    break
            if supported:
                eligible.append((ring, ids, raw, discarded, basis, residual))
        if len(eligible) != 1:
            previous["cycle_recovery_diagnostics"] = rejected
            return previous
        ring, ids, raw, discarded, basis, residual = eligible[0]
        tape = ring[ConvexHull((ring - point) @ basis).vertices]

        def length(p):
            return float(np.linalg.norm(np.roll(p, -1, axis=0) - p, axis=1).sum() * 100)

        return dict(
            geometry_quality="VALID",
            reason="CLOSED_SOURCE_SURFACE_CYCLE_AT_ACTUAL_INTERSECTIONS"
            if discarded
            else "CLOSED_INDEXED_SOURCE_TARGET_WITH_OTHER_COMPONENT_FAILURE",
            points_m=ring.tolist(),
            raw_points_m=ring.tolist(),
            tape_points_m=tape.tolist(),
            raw_contour_cm=length(ring),
            tape_envelope_cm=length(tape),
            plane_origin_m=point.tolist(),
            plane_normal=normal.tolist(),
            selected_face_ids=ids.tolist(),
            surface_contour_closed=True,
            fabricated_segments=0,
            segment_support_maximum_residual_m=residual,
            original_crossed_trace_m=raw.tolist(),
            original_crossed_trace_cm=length(raw),
            discarded_closed_cycles_m=[(point + p @ basis.T).tolist() for p in discarded],
            discarded_closed_cycle_count=len(discarded),
            region_check=dict(
                valid=True,
                supporting_face_count=len(ids),
                outside_face_count=0,
                complete_original_trace_checked=True,
            ),
            previous_indexed_reason=previous["reason"],
            interpretation_status="ENGINEERING_INTERPRETATION",
            iso_conformance_claim=False,
            scientific_margins_approved=False,
            source_protocol_compatible=False,
        )


def recover_hip(engine, seed, upper, pelvis):
    """Repeat the original A-only rule with stable source-template pelvic labels."""
    attachment = surface_anchor(engine.v, engine.original_faces, pelvis, seed, 1, False)
    crotch = anchor_position(engine.v, engine.original_faces, attachment)
    lo, hi = (float(crotch[1]), float(upper[1]))
    if not lo < seed[1] < hi:
        raise ValueError("CROTCH_ROOT_UPPER_PELVIS_ORDER_INVALID")
    landmark = locate_landmarks(engine.v, engine.original_faces, pelvis, lo, hi)["A"]
    point = [float(seed[0]), float(landmark["point_m"][1]), float(seed[2])]
    q = engine.section(point, [0, 1, 0], point, pelvis)
    q.update(
        selected_landmark="A",
        landmarks={"A": landmark},
        crotch_point_m=crotch.tolist(),
        crotch_surface_anchor=attachment,
        upper_gluteal_point_m=np.asarray(upper).tolist(),
        search_interval_world_y_m=[lo, hi],
        excluded_landmarks=["B", "C"],
        region_transfer="SAME_PINNED_SOURCE_TEMPLATE_MAJORITY_AS_CONTACT_V1",
        quantity="tape_envelope_cm",
        engineering_value_cm=q.get("tape_envelope_cm"),
        source_protocol_compatible=False,
        iso_conformance_claim=False,
    )
    if q["geometry_quality"] == "VALID":
        q["points_m"] = q["tape_points_m"]
    return q


def certify_source_segments(engine, raw, point, normal, allowed):
    """Check full coverage by original mesh-plane segments, not endpoint proximity.

    A chosen outside-tape envelope may bridge concavities by its definition;
    this check applies to its underlying closed raw surface contour instead.
    """
    raw = np.asarray(raw, float)
    mesh = trimesh.Trimesh(engine.v, engine.f, process=False)
    segments, local = trimesh.intersections.mesh_plane(
        mesh, np.asarray(normal), np.asarray(point), return_faces=True
    )
    ids = engine.ids[local]
    segments = segments[np.asarray(allowed, bool)[ids]]
    used, maximum_gap = (set(), 0.0)
    for a, b in zip(raw, np.roll(raw, -1, axis=0), strict=True):
        edge = b - a
        length = np.linalg.norm(edge)
        if length <= 1e-12:
            raise ValueError("ZERO_LENGTH_OUTPUT_EDGE")
        t = (segments - a) @ edge / (length * length)
        residual = np.linalg.norm(segments - (a + t[..., None] * edge), axis=2)
        collinear = np.all(residual <= 1e-10, axis=1)
        intervals = sorted(
            (
                (max(0.0, float(x.min())), min(1.0, float(x.max())))
                for x in t[collinear]
                if x.max() >= 0 and x.min() <= 1
            )
        )
        end = 0.0
        for lo, hi in intervals:
            maximum_gap = max(maximum_gap, max(0.0, lo - end) * length)
            end = max(end, hi)
        maximum_gap = max(maximum_gap, (1 - end) * length)
        used.update(ids[np.asarray(allowed, bool)[ids]][collinear].tolist())
    if maximum_gap > 1e-10:
        raise ValueError("OUTPUT_SEGMENT_NOT_FULLY_SUPPORTED_BY_SOURCE_SURFACE")
    return dict(
        all_raw_segments_supported=True,
        maximum_uncovered_length_m=maximum_gap,
        original_supporting_face_count=len(used),
        fabricated_segments=0,
        arithmetic_tolerance_m=1e-10,
    )
