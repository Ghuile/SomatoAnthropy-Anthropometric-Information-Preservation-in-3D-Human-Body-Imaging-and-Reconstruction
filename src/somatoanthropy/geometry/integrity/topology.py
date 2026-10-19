"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from somatoanthropy.geometry.integrity.model import Component


@dataclass(frozen=True)
class Topology:
    incidence: tuple[tuple[int, int, tuple[int, ...]], ...]
    boundaries: tuple[tuple[int, int], ...]
    nonmanifold: tuple[tuple[int, int], ...]
    inconsistent: tuple[tuple[int, int], ...]
    nonmanifold_vertices: tuple[int, ...]
    components: tuple[Component, ...]


def inspect_topology(faces: npt.NDArray[np.int64], ids: npt.NDArray[np.int64]) -> Topology:
    edges: dict[tuple[int, int], list[tuple[int, int]]] = {}
    face_vertices: dict[int, tuple[int, ...]] = {}
    vertex_links: dict[int, list[tuple[int, int]]] = {}
    parent = {int(i): int(i) for i in ids}

    def root(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for row, face_id in zip(faces, ids, strict=True):
        a, b, c = (int(x) for x in row)
        fid = int(face_id)
        face_vertices[fid] = (a, b, c)
        for x, y in [(a, b), (b, c), (c, a)]:
            key = (min(x, y), max(x, y))
            edges.setdefault(key, []).append((fid, 1 if x < y else -1))
        for center, x, y in [(a, b, c), (b, c, a), (c, a, b)]:
            vertex_links.setdefault(center, []).append((x, y))
    boundary = []
    nonmanifold = []
    inconsistent = []
    incidence = []
    for key, adjacent in sorted(edges.items()):
        incident = tuple(sorted((fid for fid, _ in adjacent)))
        incidence.append((*key, incident))
        if len(adjacent) == 1:
            boundary.append(key)
        elif len(adjacent) > 2:
            nonmanifold.append(key)
        elif adjacent[0][1] == adjacent[1][1]:
            inconsistent.append(key)
        for face_id in incident[1:]:
            x, y = (root(incident[0]), root(face_id))
            parent[max(x, y)] = min(x, y)
    grouped: dict[int, list[int]] = {}
    for i in sorted(parent):
        grouped.setdefault(root(i), []).append(i)
    components = []
    for component_id, group in enumerate(sorted(grouped.values(), key=lambda g: g[0])):
        vertices = tuple(sorted({v for i in group for v in face_vertices[i]}))
        member = set(group)
        bad = tuple((e for e in inconsistent if edges[e][0][0] in member))
        components.append(Component(component_id, tuple(group), vertices, bad))
    bad_vertices = []
    for vertex, links in sorted(vertex_links.items()):
        graph: dict[int, list[int]] = {}
        for a, b in links:
            graph.setdefault(a, []).append(b)
            graph.setdefault(b, []).append(a)
        unseen = set(graph)
        stack = [min(unseen)]
        visited: set[int] = set()
        while stack:
            x = stack.pop()
            if x not in visited:
                visited.add(x)
                stack.extend(sorted(graph[x], reverse=True))
        degrees = [len(graph[x]) for x in sorted(graph)]
        if visited != unseen or any((d > 2 for d in degrees)) or degrees.count(1) not in (0, 2):
            bad_vertices.append(vertex)
    return Topology(
        tuple(incidence),
        tuple(boundary),
        tuple(nonmanifold),
        tuple(inconsistent),
        tuple(bad_vertices),
        tuple(components),
    )
