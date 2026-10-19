"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

import hashlib
from collections.abc import Mapping
from copy import deepcopy
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any

import numpy as np
import numpy.typing as npt

from somatoanthropy.geometry.integrity.intersection import self_intersections
from somatoanthropy.geometry.integrity.model import (
    VALIDATOR_VERSION,
    MeshIntegrityReport,
    ValidationConfig,
)
from somatoanthropy.geometry.integrity.topology import inspect_topology

Array = npt.NDArray[np.float64]
Indices = npt.NDArray[np.int64]


def _ids(mask: npt.NDArray[np.bool_]) -> tuple[int, ...]:
    return tuple((int(x) for x in np.flatnonzero(mask)))


def _array(value: object, *, integer: bool = False) -> tuple[Any, bool]:
    try:
        result = np.asarray([] if value is None else value)
        if result.shape == (0,):
            result = result.reshape(0, 3)
        if result.ndim != 2 or result.shape[1] != 3:
            return (result, False)
        if integer:
            return (result, result.dtype.kind in "iu")
        if result.dtype.kind not in "iuf":
            return (result, False)
        return (np.asarray(result, dtype=np.float64), True)
    except (ValueError, TypeError, OverflowError):
        return (np.empty((0, 0)), False)


def _normals(
    mesh: Mapping[str, Any],
    faces: Indices,
    normal_vectors: Array,
    geometric_ids: Indices,
    vertex_count: int,
    face_count: int,
    config: ValidationConfig,
) -> tuple[str, tuple[int, ...], tuple[int, ...], tuple[str, ...]]:
    supplied = mesh.get("normals")
    if supplied is None:
        return ("not_supplied", (), (), ())
    n, valid = _array(supplied)
    if not valid:
        return ("malformed", (), (), ("malformed_normals",))
    finite = np.isfinite(n).all(1)
    lengths = np.zeros(len(n))
    maximum = np.max(np.abs(n), axis=1) if len(n) else np.zeros(0)
    nonzero = finite & (maximum > 0)
    lengths[nonzero] = np.linalg.norm(n[nonzero] / maximum[nonzero, None], axis=1)
    invalid = ~nonzero
    normalized = np.zeros_like(n)
    normalized[nonzero] = n[nonzero] / maximum[nonzero, None] / lengths[nonzero, None]
    index = mesh.get("face_normal_indices")
    errors = []
    if index is not None:
        ni, index_ok = _array(index, integer=True)
        if not index_ok or ni.shape != (face_count, 3) or np.any(ni < 0) or np.any(ni >= len(n)):
            return ("invalid_indices", _ids(invalid), (), ("invalid_normal_indices",))
        matched = normalized[ni[geometric_ids].astype(np.int64)]
    elif mesh.get("normal_binding") == "face" or len(n) == face_count != vertex_count:
        if len(n) != face_count:
            return ("malformed", _ids(invalid), (), ("normal_binding_length_mismatch",))
        matched = normalized[geometric_ids, None, :]
    elif mesh.get("normal_binding") == "vertex" or len(n) == vertex_count != face_count:
        if len(n) != vertex_count:
            return ("malformed", _ids(invalid), (), ("normal_binding_length_mismatch",))
        matched = normalized[faces[geometric_ids]]
    else:
        return ("unresolved_binding", _ids(invalid), (), ("normal_binding_unresolved",))
    dots = np.einsum("nic,nc->ni", matched, normal_vectors)
    bad = geometric_ids[(dots <= config.normal_dot_tolerance).any(1)]
    if invalid.any():
        errors.append("invalid_normals")
    return ("checked", _ids(invalid), tuple((int(x) for x in bad)), tuple(errors))


def validate_mesh(
    mesh: Mapping[str, Any],
    *,
    config: ValidationConfig | None = None,
    mesh_id: str | None = None,
    coordinate_frame_id: str | None = None,
) -> MeshIntegrityReport:
    """Detect/report only. Coordinates can be source-native or body-local.

    Malformed faces/indices are reported rather than truncated/triangulated.
    Subset diagnostics retain original face IDs and state incompleteness.
    Point sampling means sampling the supplied vertices, not uniform area
    sampling; that later operation must require usable_for_surface_area.
    """
    cfg = config or ValidationConfig()
    if not isinstance(cfg, ValidationConfig):
        raise TypeError("Typed validation configuration required")
    provenance = deepcopy(mesh.get("coordinate_provenance"))
    if coordinate_frame_id is None:
        coordinate_frame_id = mesh.get("coordinate_frame_id")
        if coordinate_frame_id is None and isinstance(provenance, dict):
            coordinate_frame_id = provenance.get("canonical_frame_id")
    if mesh_id is None:
        mesh_id = mesh.get("source_id")
    for identifier in (mesh_id, coordinate_frame_id):
        if identifier is not None and (
            not isinstance(identifier, str)
            or PurePosixPath(identifier).is_absolute()
            or PureWindowsPath(identifier).drive
            or PureWindowsPath(identifier).root
        ):
            raise ValueError("Portable IDs required; absolute paths are not IDs")
    if provenance is not None:
        if not isinstance(provenance, dict):
            raise ValueError("Coordinate provenance must be a mapping")
        from somatoanthropy.provenance.hashing import sha256_canonical

        sha256_canonical(provenance)

        def portable(value: object) -> None:
            if isinstance(value, str) and (
                PurePosixPath(value).is_absolute()
                or PureWindowsPath(value).drive
                or PureWindowsPath(value).root
            ):
                raise ValueError("Absolute path in coordinate provenance")
            if isinstance(value, dict):
                for item in value.values():
                    portable(item)
            if isinstance(value, list):
                for item in value:
                    portable(item)

        portable(provenance)
    v, vok = _array(mesh.get("vertices"))
    f, fok = _array(mesh.get("faces"), integer=True)
    if f.shape == (0, 3):
        fok = True
    nv = int(v.shape[0]) if v.ndim else 0
    nf = int(f.shape[0]) if f.ndim else 0
    errors: list[str] = []
    warnings: list[str] = []
    if not vok:
        errors.append("malformed_vertices")
        v = np.empty((0, 3))
    if not fok:
        errors.append("malformed_nontriangle_or_noninteger_faces")
        f = np.empty((0, 3), dtype=np.int64)
    if not nv or not nf:
        errors.append("empty_geometry")
    finite = np.isfinite(v).all(1)
    if not finite.all():
        errors.append("nonfinite_coordinates")
    invalid = np.any((f < 0) | (f >= len(v)), axis=1)
    if invalid.any():
        errors.append("invalid_face_indices")
    safe_ids = np.flatnonzero(~invalid).astype(np.int64)
    safe = f[safe_ids].astype(np.int64)
    f_valid = np.zeros((len(f), 3), dtype=np.int64)
    f_valid[safe_ids] = safe
    repeated = np.zeros(len(f), dtype=bool)
    repeated[safe_ids] = (
        (safe[:, 0] == safe[:, 1]) | (safe[:, 1] == safe[:, 2]) | (safe[:, 2] == safe[:, 0])
    )
    nonfinite_faces = np.zeros(len(f), dtype=bool)
    nonfinite_faces[safe_ids] = ~finite[safe].all(1)
    topology_ids = safe_ids[~repeated[safe_ids]]
    topology = inspect_topology(f_valid[topology_ids], topology_ids)
    referenced = set((int(x) for x in safe.ravel()))
    isolated = tuple((i for i in range(len(v)) if i not in referenced))
    vertex_groups: dict[tuple[float, ...], list[int]] = {}
    for i in np.flatnonzero(finite):
        vertex_groups.setdefault(tuple((float(x) for x in v[i])), []).append(int(i))
    duplicate_vertices = tuple(
        sorted((tuple(g) for g in vertex_groups.values() if len(g) > 1), key=lambda g: g[0])
    )
    face_groups: dict[tuple[int, ...], list[tuple[int, int]]] = {}
    cyclic_groups: dict[tuple[int, ...], list[int]] = {}
    for i in topology_ids:
        a, b, c = (int(x) for x in f_valid[i])
        cyclic = min((a, b, c), (b, c, a), (c, a, b))
        reverse = min((a, c, b), (c, b, a), (b, a, c))
        face_groups.setdefault(tuple(sorted((a, b, c))), []).append((int(i), int(cyclic < reverse)))
        cyclic_groups.setdefault(cyclic, []).append(int(i))
    same_duplicates = tuple(
        sorted((tuple(g) for g in cyclic_groups.values() if len(g) > 1), key=lambda g: g[0])
    )
    opposite = tuple(
        sorted(
            (
                (a, b)
                for group in face_groups.values()
                for a, sign in group
                for b, other in group
                if a < b and sign != other
            )
        )
    )
    duplicate_face_count = sum((len(group) - 1 for group in face_groups.values()))
    geometric_ids = safe_ids[~nonfinite_faces[safe_ids]]
    centered = np.zeros_like(v)
    numerical_ok = True
    if finite.any():
        with np.errstate(over="ignore", invalid="ignore", under="ignore"):
            delta = v[finite] - v[np.flatnonzero(finite)[0]]
            span = float(np.max(np.abs(delta)))
            numerical_ok = bool(np.isfinite(delta).all())
            if numerical_ok:
                centered[finite] = delta / (span if span else 1.0)
    if not numerical_ok:
        errors.append("floating_point_dynamic_range_unsupported")
        geometric_ids = np.empty(0, dtype=np.int64)
    triangles = centered[f_valid[geometric_ids]]
    edges = np.roll(triangles, -1, axis=1) - triangles
    cross = np.cross(edges[:, 0], edges[:, 1])
    magnitude = np.linalg.norm(cross, axis=1)
    local_scale_squared = np.sum(edges * edges, axis=2).max(1) if len(edges) else np.zeros(0)
    degenerate = magnitude <= cfg.area_relative_tolerance * local_scale_squared
    bad_geometry = tuple((int(x) for x in geometric_ids[degenerate]))
    normal_ids = geometric_ids[~degenerate]
    geometric_normals = cross[~degenerate] / magnitude[~degenerate, None]
    normals_status, bad_normals, inconsistent_normals, normal_errors = _normals(
        mesh, f_valid, geometric_normals, normal_ids, len(v), len(f), cfg
    )
    warnings.extend(normal_errors)
    if repeated.any():
        errors.append("repeated_triangle_indices")
    if bad_geometry:
        errors.append("geometrically_degenerate_triangles")
    if duplicate_face_count:
        errors.append("duplicate_faces")
    if duplicate_vertices:
        warnings.append("exact_duplicate_vertex_positions_not_welded")
    if topology.boundaries:
        warnings.append("open_boundary_edges")
    if topology.nonmanifold:
        warnings.append("nonmanifold_edges")
    if topology.nonmanifold_vertices:
        warnings.append("nonmanifold_vertex_links")
    if topology.inconsistent:
        warnings.append("inconsistent_adjacent_winding")
    if inconsistent_normals:
        warnings.append("normals_disagree_with_face_orientation")
    if isolated:
        warnings.append("isolated_vertices")
    if len(topology.components) > 1:
        warnings.append("multiple_face_components")
    pairs: tuple[tuple[int, int], ...] = ()
    candidates = tested = adjacent = 0
    if cfg.check_self_intersection and numerical_ok and vok and fok:
        pairs, candidates, tested, adjacent = self_intersections(
            triangles[~degenerate],
            f_valid[normal_ids],
            normal_ids,
            cfg.intersection_relative_tolerance,
            cfg.bvh_leaf_size,
        )
        intersection_status = (
            "checked" if len(normal_ids) == len(f) else "checked_valid_nondegenerate_subset"
        )
        if pairs:
            warnings.append("geometric_self_intersection_or_contact")
    else:
        intersection_status = (
            "not_checked_disabled"
            if not cfg.check_self_intersection
            else "not_checked_invalid_input"
        )
    base_surface = bool(
        vok
        and fok
        and nv
        and nf
        and finite.all()
        and (not invalid.any())
        and (not repeated.any())
        and (not bad_geometry)
        and (not duplicate_face_count)
        and numerical_ok
    )
    closed = bool(
        base_surface
        and (not topology.boundaries)
        and (not topology.nonmanifold)
        and (not topology.nonmanifold_vertices)
        and (not topology.inconsistent)
        and (intersection_status == "checked")
        and (not pairs)
    )
    digest = None
    if vok and fok:
        canonical_v = np.array(v, dtype="<f8", copy=True)
        canonical_v[canonical_v == 0] = 0
        canonical_v[np.isnan(canonical_v)] = np.nan
        h = hashlib.sha256()
        h.update(np.asarray([len(v), len(f)], dtype="<i8").tobytes())
        h.update(canonical_v.tobytes())
        h.update(str(f.dtype.kind).encode())
        h.update(np.asarray(f, dtype="<u8" if f.dtype.kind == "u" else "<i8").tobytes())
        digest = h.hexdigest()
    return MeshIntegrityReport(
        validator_version=VALIDATOR_VERSION,
        mesh_id=mesh_id,
        coordinate_frame_id=coordinate_frame_id,
        coordinate_provenance=provenance,
        configuration=cfg,
        geometry_sha256=digest,
        vertex_count=nv,
        face_count=nf,
        malformed_vertices=not vok,
        malformed_faces=not fok,
        finite_coordinates=bool(vok and finite.all()),
        nonfinite_vertex_ids=_ids(~finite),
        nonfinite_face_ids=_ids(nonfinite_faces),
        invalid_face_ids=_ids(invalid),
        repeated_index_face_ids=_ids(repeated),
        degenerate_face_ids=bad_geometry,
        exact_duplicate_vertex_groups=duplicate_vertices,
        same_winding_duplicate_groups=same_duplicates,
        opposite_winding_duplicate_pairs=opposite,
        duplicate_face_count=duplicate_face_count,
        boundary_edges=topology.boundaries,
        nonmanifold_edges=topology.nonmanifold,
        edge_incidence=topology.incidence,
        inconsistent_winding_edges=topology.inconsistent,
        nonmanifold_vertex_ids=topology.nonmanifold_vertices,
        orientation_consistent=not topology.inconsistent
        if len(topology_ids) == len(f) and fok and len(f)
        else None,
        components=topology.components,
        isolated_vertex_ids=isolated,
        normals_status=normals_status,
        invalid_normal_ids=bad_normals,
        normal_inconsistent_face_ids=inconsistent_normals,
        computed_normal_face_count=len(normal_ids),
        self_intersection_status=intersection_status,
        self_intersection_pairs=pairs,
        intersection_candidate_pair_count=candidates,
        intersection_tested_pair_count=tested,
        intersection_excluded_adjacent_pair_count=adjacent,
        usable_as_surface=base_surface,
        usable_for_surface_area=base_surface,
        usable_for_closed_volume=closed,
        usable_for_point_sampling=bool(vok and nv and finite.all()),
        warnings=tuple(sorted(set(warnings))),
        errors=tuple(sorted(set(errors))),
    )
