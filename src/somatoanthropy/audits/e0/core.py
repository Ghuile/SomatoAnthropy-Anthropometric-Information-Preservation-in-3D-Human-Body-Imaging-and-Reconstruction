"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from zipfile import BadZipFile

import numpy as np


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inspect_parameters(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return dict(status="unavailable", reason="FILE_ABSENT_AT_CHECK")
    try:
        with np.load(path, allow_pickle=False) as archive:
            groups = [
                ("identity_coeffs", "lbs_model_params", "face_expr_coeffs"),
                ("identity", "model", "expression"),
            ]
            keys = next((g for g in groups if set(g) <= set(archive.files)), None)
            if keys is None:
                raise ValueError("REQUIRED_NATIVE_CONTROL_KEYS_ABSENT")
            arrays = [archive[k] for k in keys]
            dimensions = [list(a.shape) for a in arrays]
            if any(
                (a.shape not in ((n,), (1, n)) for a, n in zip(arrays, (45, 204, 72), strict=True))
            ):
                raise ValueError("INCOMPATIBLE_NATIVE_DIMENSIONS")
            if any((a.dtype.kind not in "fi" or not np.isfinite(a).all() for a in arrays)):
                raise ValueError("NONFINITE_OR_NONNUMERIC_CONTROLS")
            return dict(
                status="verified",
                reason="STRUCTURE_AND_FINITE_VALUES_ONLY",
                dimensions=dimensions,
                keys=list(keys),
                sha256=sha(path),
                native_replay="not_attempted",
            )
    except (OSError, ValueError, TypeError, EOFError, KeyError, BadZipFile) as error:
        return dict(status="failed", reason=type(error).__name__ + ":" + str(error)[:200])


def compare_replay(
    v: Any, f: Any, saved_v: Any, saved_f: Any, unit: str, atol: float = 1e-05
) -> dict[str, Any]:
    if v.shape != saved_v.shape or not np.array_equal(f, saved_f):
        return dict(status="unavailable", reason="DIRECT_INDEXED_TOPOLOGY_MISMATCH")
    if not np.isfinite(v).all() or not np.isfinite(saved_v).all():
        return dict(status="failed", reason="NONFINITE_GEOMETRY")
    delta = np.linalg.norm(v.astype(float) - saved_v.astype(float), axis=1)
    maximum = float(np.abs(v - saved_v).max())
    return dict(
        status="verified" if maximum <= atol else "failed",
        unit=unit,
        maximum_component=maximum,
        mean_vertex=float(delta.mean()),
        p95_vertex=float(np.percentile(delta, 95)),
        maximum_vertex=float(delta.max()),
        arithmetic_atol=atol,
        scientific_acceptance="not_applicable",
    )
