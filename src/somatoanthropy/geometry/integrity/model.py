"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from somatoanthropy.provenance.hashing import sha256_canonical

VALIDATOR_VERSION = "somatosynth-mesh-integrity-v1"


@dataclass(frozen=True)
class ValidationConfig:
    area_relative_tolerance: float = 64 * np.finfo(np.float64).eps
    intersection_relative_tolerance: float = 64 * np.finfo(np.float64).eps
    normal_dot_tolerance: float = 64 * np.finfo(np.float64).eps
    check_self_intersection: bool = True
    bvh_leaf_size: int = 8

    def __post_init__(self) -> None:
        for value in (
            self.area_relative_tolerance,
            self.intersection_relative_tolerance,
            self.normal_dot_tolerance,
        ):
            if not np.isfinite(value) or not 0 <= value < 1:
                raise ValueError("Engineering relative tolerances must be finite in [0,1)")
        if type(self.check_self_intersection) is not bool:
            raise ValueError("Intersection check must be explicit bool")
        if type(self.bvh_leaf_size) is not int or self.bvh_leaf_size < 1:
            raise ValueError("Positive integer BVH leaf size required")


@dataclass(frozen=True)
class Component:
    component_id: int
    face_ids: tuple[int, ...]
    vertex_ids: tuple[int, ...]
    inconsistent_edge_ids: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class MeshIntegrityReport:
    validator_version: str
    mesh_id: str | None
    coordinate_frame_id: str | None
    coordinate_provenance: dict[str, Any] | None
    configuration: ValidationConfig
    geometry_sha256: str | None
    vertex_count: int
    face_count: int
    malformed_vertices: bool
    malformed_faces: bool
    finite_coordinates: bool
    nonfinite_vertex_ids: tuple[int, ...]
    nonfinite_face_ids: tuple[int, ...]
    invalid_face_ids: tuple[int, ...]
    repeated_index_face_ids: tuple[int, ...]
    degenerate_face_ids: tuple[int, ...]
    exact_duplicate_vertex_groups: tuple[tuple[int, ...], ...]
    same_winding_duplicate_groups: tuple[tuple[int, ...], ...]
    opposite_winding_duplicate_pairs: tuple[tuple[int, int], ...]
    duplicate_face_count: int
    boundary_edges: tuple[tuple[int, int], ...]
    nonmanifold_edges: tuple[tuple[int, int], ...]
    edge_incidence: tuple[tuple[int, int, tuple[int, ...]], ...]
    inconsistent_winding_edges: tuple[tuple[int, int], ...]
    nonmanifold_vertex_ids: tuple[int, ...]
    orientation_consistent: bool | None
    components: tuple[Component, ...]
    isolated_vertex_ids: tuple[int, ...]
    normals_status: str
    invalid_normal_ids: tuple[int, ...]
    normal_inconsistent_face_ids: tuple[int, ...]
    computed_normal_face_count: int
    self_intersection_status: str
    self_intersection_pairs: tuple[tuple[int, int], ...]
    intersection_candidate_pair_count: int
    intersection_tested_pair_count: int
    intersection_excluded_adjacent_pair_count: int
    usable_as_surface: bool
    usable_for_surface_area: bool
    usable_for_closed_volume: bool
    usable_for_point_sampling: bool
    warnings: tuple[str, ...]
    errors: tuple[str, ...]

    @property
    def degenerate_face_count(self) -> int:
        return len(self.degenerate_face_ids)

    @property
    def duplicate_vertex_count(self) -> int:
        return sum((len(group) - 1 for group in self.exact_duplicate_vertex_groups))

    @property
    def boundary_edge_count(self) -> int:
        return len(self.boundary_edges)

    @property
    def nonmanifold_edge_count(self) -> int:
        return len(self.nonmanifold_edges)

    @property
    def connected_component_count(self) -> int:
        return len(self.components)

    @property
    def isolated_vertex_count(self) -> int:
        return len(self.isolated_vertex_ids)

    @property
    def self_intersection_count(self) -> int | None:
        return (
            len(self.self_intersection_pairs)
            if self.self_intersection_status.startswith("checked")
            else None
        )

    @property
    def largest_component_face_fraction(self) -> float:
        return max((len(c.face_ids) for c in self.components), default=0) / max(self.face_count, 1)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        for name in (
            "degenerate_face_count",
            "duplicate_vertex_count",
            "boundary_edge_count",
            "nonmanifold_edge_count",
            "connected_component_count",
            "isolated_vertex_count",
            "self_intersection_count",
            "largest_component_face_fraction",
        ):
            result[name] = getattr(self, name)
        return result

    @property
    def identity(self) -> str:
        import json

        return sha256_canonical(json.loads(json.dumps(self.to_dict(), allow_nan=False)))
