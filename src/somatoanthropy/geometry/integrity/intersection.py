"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

Array = npt.NDArray[np.float64]
Indices = npt.NDArray[np.int64]


@dataclass
class Node:
    low: Array
    high: Array
    ids: Indices
    left: "Node | None" = None
    right: "Node | None" = None


def _build(ids: Indices, low: Array, high: Array, leaf_size: int) -> Node:
    node = Node(low[ids].min(0), high[ids].max(0), ids)
    if len(ids) > leaf_size:
        centers = (low[ids] + high[ids]) * 0.5
        axis = int(np.argmax(np.ptp(centers, axis=0)))
        ordered = ids[np.argsort(centers[:, axis], kind="stable")]
        middle = len(ids) // 2
        node.left = _build(ordered[:middle], low, high, leaf_size)
        node.right = _build(ordered[middle:], low, high, leaf_size)
    return node


def triangle_overlap(a: Array, b: Array, tolerance: float) -> npt.NDArray[np.bool_]:
    """Batched SAT, including in-plane edge axes for coplanar triangles.

    Test axes: two triangle normals, nine edge-edge cross products and six
    in-plane edge perpendiculars. Near-zero axes are redundant and skipped.
    Geometry is mesh-scale-normalized by the caller; axis projection epsilon
    is configured length tolerance times axis norm. No divisions by normals.
    """
    ea = np.roll(a, -1, axis=1) - a
    eb = np.roll(b, -1, axis=1) - b
    na = np.cross(ea[:, 0], ea[:, 1])
    nb = np.cross(eb[:, 0], eb[:, 1])
    axes = np.concatenate(
        [
            na[:, None],
            nb[:, None],
            np.cross(ea[:, :, None, :], eb[:, None, :, :]).reshape(-1, 9, 3),
            np.cross(na[:, None], ea),
            np.cross(nb[:, None], eb),
        ],
        axis=1,
    )
    pa = np.einsum("nvc,nac->nva", a, axes)
    pb = np.einsum("nvc,nac->nva", b, axes)
    lengths = np.linalg.norm(axes, axis=2)
    eps = tolerance * lengths
    separated = ((pa.max(1) < pb.min(1) - eps) | (pb.max(1) < pa.min(1) - eps)) & (lengths > 0)
    return np.asarray(~separated.any(1), dtype=np.bool_)


def self_intersections(
    triangles: Array, faces: Indices, face_ids: Indices, tolerance: float, leaf_size: int
) -> tuple[tuple[tuple[int, int], ...], int, int, int]:
    if not len(triangles):
        return ((), 0, 0, 0)
    low = triangles.min(1) - tolerance
    high = triangles.max(1) + tolerance
    root = _build(np.arange(len(triangles), dtype=np.int64), low, high, leaf_size)
    stack = [(root, root)]
    intersections: list[tuple[int, int]] = []
    candidate_count = tested_count = adjacent_count = 0
    while stack:
        x, y = stack.pop()
        if np.any(x.high < y.low) or np.any(y.high < x.low):
            continue
        if x is y and x.left is not None and (x.right is not None):
            stack.extend([(x.right, x.right), (x.left, x.right), (x.left, x.left)])
            continue
        if x.left is not None and x.right is not None:
            stack.extend([(x.right, y), (x.left, y)])
            continue
        if y.left is not None and y.right is not None:
            stack.extend([(x, y.right), (x, y.left)])
            continue
        xx, yy = np.meshgrid(x.ids, y.ids, indexing="ij")
        i, j = (xx.ravel(), yy.ravel())
        keep = i < j if x is y else i != j
        i, j = (i[keep], j[keep])
        keep = np.all(high[i] >= low[j], axis=1) & np.all(high[j] >= low[i], axis=1)
        i, j = (i[keep], j[keep])
        candidate_count += len(i)
        adjacent = (faces[i, :, None] == faces[j, None, :]).any(axis=(1, 2))
        adjacent_count += int(adjacent.sum())
        i, j = (i[~adjacent], j[~adjacent])
        tested_count += len(i)
        if len(i):
            overlap = triangle_overlap(triangles[i], triangles[j], tolerance)
            intersections.extend(
                (
                    (
                        min(int(face_ids[a]), int(face_ids[b])),
                        max(int(face_ids[a]), int(face_ids[b])),
                    )
                    for a, b in zip(i[overlap], j[overlap], strict=True)
                )
            )
    return (tuple(sorted(intersections)), candidate_count, tested_count, adjacent_count)
