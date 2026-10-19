"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from somatoanthropy.geometry.anthropometry.model import (
    AnthropometryError,
    Plane,
    SectionConfig,
    Vec3,
    portable_json,
    vector,
)
from somatoanthropy.geometry.integrity import MeshIntegrityReport, ValidationConfig, validate_mesh

Node = tuple[int, int]


def _pair(a: Node, b: Node) -> tuple[Node, Node]:
    return (a, b) if a <= b else (b, a)


@dataclass(frozen=True)
class Polyline:
    loop_id: int
    points: tuple[Vec3, ...]
    node_ids: tuple[Node, ...]
    closed: bool


@dataclass(frozen=True)
class SectionResult:
    plane: Plane
    segments: tuple[tuple[Vec3, Vec3], ...]
    polylines: tuple[Polyline, ...]
    diagnostics_json: str
    integrity_report_identity: str

    @property
    def diagnostics(self) -> dict[str, Any]:
        import json

        return json.loads(self.diagnostics_json)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("diagnostics_json")
        return {**data, "diagnostics": self.diagnostics}


def section_report(mesh: Mapping[str, Any]) -> MeshIntegrityReport:
    if mesh.get("length_units", "m") != "m":
        raise AnthropometryError("SECTION_METRE_COORDINATES_REQUIRED")
    report = validate_mesh(mesh, config=ValidationConfig(check_self_intersection=False))
    if report.malformed_vertices or report.malformed_faces or report.invalid_face_ids:
        raise AnthropometryError("INVALID_TRIANGULAR_MESH", {"errors": list(report.errors)})
    if report.nonfinite_face_ids:
        raise AnthropometryError(
            "NONFINITE_REFERENCED_GEOMETRY", {"face_ids": list(report.nonfinite_face_ids)}
        )
    if "floating_point_dynamic_range_unsupported" in report.errors:
        raise AnthropometryError("UNSUPPORTED_NUMERICAL_RANGE")
    if report.face_count == 0:
        raise AnthropometryError("EMPTY_GEOMETRY")
    return report


def mesh_section(
    mesh: Mapping[str, Any], plane: Plane, *, config: SectionConfig | None = None
) -> SectionResult:
    """Finite triangular mesh and plane in declared metre coordinates.

    Endpoint connectivity follows source topology, never proximity. Coplanar
    patches contribute their boundary edges, with internal indexed edges omitted
    and reported; duplicate coplanar faces make estimator eligibility fail.
    Within-tolerance vertices are projected in temporary intersection output.
    """
    return _section(mesh, plane, config or SectionConfig(), section_report(mesh))


def _section(
    mesh: Mapping[str, Any], plane: Plane, config: SectionConfig, report: MeshIntegrityReport
) -> SectionResult:
    v = np.asarray(mesh["vertices"], dtype=np.float64)
    f = np.asarray(mesh["faces"], dtype=np.int64)
    p, n = (np.asarray(plane.point), np.asarray(plane.normal))
    with np.errstate(over="ignore", invalid="ignore"):
        distances = (v - p) @ n
    referenced = np.unique(f)
    if not np.isfinite(distances[referenced]).all():
        raise AnthropometryError("UNSUPPORTED_NUMERICAL_RANGE")
    side = np.where(
        distances > config.tolerance_m, 1, np.where(distances < -config.tolerance_m, -1, 0)
    )
    nodes: dict[Node, Vec3] = {}
    generated: list[tuple[Node, Node]] = []
    coplanar: list[int] = []
    touching_vertices: list[int] = []
    edge_faces: list[int] = []
    crossing_faces: list[int] = []
    local_degenerate: list[int] = []
    patch_edges: Counter[tuple[Node, Node]] = Counter()
    degenerate = set(report.degenerate_face_ids) | set(report.repeated_index_face_ids)
    duplicate_ids = {i for group in report.same_winding_duplicate_groups for i in group}
    duplicate_ids.update((i for pair in report.opposite_winding_duplicate_pairs for i in pair))
    local_duplicates: list[int] = []

    def vertex(i: int) -> Node:
        key = (i, i)
        nodes[key] = vector(v[i] - distances[i] * n)
        return key

    def edge(a: int, b: int) -> Node:
        a, b = sorted((a, b))
        key = (a, b)
        if key not in nodes:
            fraction = distances[a] / (distances[a] - distances[b])
            q = v[a] + fraction * (v[b] - v[a])
            q -= np.dot(q - p, n) * n
            nodes[key] = vector(q)
        return key

    for face_id, tri in enumerate(f):
        ids = [int(i) for i in tri]
        s = side[tri]
        if np.all(s > 0) or np.all(s < 0):
            continue
        if face_id in degenerate:
            local_degenerate.append(face_id)
            continue
        if face_id in duplicate_ids:
            local_duplicates.append(face_id)
        zeros = [i for i in ids if side[i] == 0]
        if len(zeros) == 3:
            coplanar.append(face_id)
            for a, b in zip(ids, ids[1:] + ids[:1], strict=True):
                patch_edges[_pair(vertex(a), vertex(b))] += 1
            continue
        if len(zeros) == 2:
            edge_faces.append(face_id)
            generated.append(_pair(vertex(zeros[0]), vertex(zeros[1])))
            continue
        hits = [vertex(i) for i in zeros]
        for a, b in zip(ids, ids[1:] + ids[:1], strict=True):
            if side[a] * side[b] < 0:
                hits.append(edge(a, b))
        hits = sorted(set(hits))
        if len(hits) == 2:
            crossing_faces.append(face_id)
            generated.append((hits[0], hits[1]))
        elif len(hits) == 1:
            touching_vertices.append(face_id)
    internal = {pair for pair, count in patch_edges.items() if count >= 2}
    generated.extend((pair for pair, count in patch_edges.items() if count == 1))
    counts = Counter(generated)
    pairs = sorted((pair for pair in counts if pair not in internal))
    adjacency: dict[Node, set[Node]] = {}
    zero_segments = 0
    kept: list[tuple[Node, Node]] = []
    for node_a, node_b in pairs:
        if (
            node_a == node_b
            or np.linalg.norm(np.asarray(nodes[node_a]) - nodes[node_b]) <= config.tolerance_m
        ):
            zero_segments += 1
            continue
        kept.append((node_a, node_b))
        adjacency.setdefault(node_a, set()).add(node_b)
        adjacency.setdefault(node_b, set()).add(node_a)
    branched = sorted((node for node, peers in adjacency.items() if len(peers) > 2))
    unused = set(kept)
    paths: list[Polyline] = []
    while unused:
        available = {node for pair in unused for node in pair}
        endpoints = sorted((node for node in available if len(adjacency[node]) != 2))
        start = endpoints[0] if endpoints else min(available)
        path = [start]
        current = start
        while True:
            candidates = sorted(
                (peer for peer in adjacency[current] if _pair(current, peer) in unused)
            )
            if not candidates:
                break
            following = candidates[0]
            unused.remove(_pair(current, following))
            path.append(following)
            current = following
            if current == start or len(adjacency[current]) != 2:
                break
        closed = path[0] == path[-1] and len(path) >= 4
        paths.append(Polyline(len(paths), tuple((nodes[i] for i in path)), tuple(path), closed))
    diagnostics = {
        "section_version": "somatosynth-indexed-plane-section-v1",
        "configuration": asdict(config),
        "ordinary_crossing_face_ids": crossing_faces,
        "vertex_touch_face_ids": touching_vertices,
        "plane_edge_face_ids": edge_faces,
        "coplanar_face_ids": coplanar,
        "coplanar_internal_edges_omitted": len(internal),
        "coplanar_nonmanifold_edge_count": sum((count > 2 for count in patch_edges.values())),
        "duplicate_generated_segment_count": sum((count - 1 for count in counts.values())),
        "local_degenerate_face_ids": local_degenerate,
        "local_duplicate_face_ids": local_duplicates,
        "zero_length_segment_count": zero_segments,
        "branched_node_ids": branched,
        "closed_loop_count": sum((path.closed for path in paths)),
        "open_polyline_count": sum((not path.closed for path in paths)),
        "endpoint_policy": "shared-index-vertex-or-edge-no-proximity-weld",
        "coplanar_policy": "indexed-patch-boundary-with-diagnostics",
        "integrity_self_intersection_status": report.self_intersection_status,
        "integrity_warnings": list(report.warnings),
        "integrity_errors": list(report.errors),
    }
    return SectionResult(
        plane,
        tuple(((nodes[a], nodes[b]) for a, b in kept)),
        tuple(paths),
        portable_json(diagnostics),
        report.identity,
    )
