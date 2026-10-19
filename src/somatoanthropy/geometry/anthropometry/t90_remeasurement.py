"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

POSE_ID = "T90_REFERENCE_ARTICULATION_TRANSFER_CANDIDATE"
ARTICULATION_END = 130


def cohort_ids(ordered: Sequence[str], packaged: Sequence[str]) -> list[str]:
    """Use an existing cohort exactly; never select replacements or create splits."""
    if (
        len(ordered) != 60
        or len(packaged) != 60
        or len(set(ordered)) != 60
        or (set(ordered) != set(packaged))
    ):
        raise ValueError("Expected the same 60 unique packaged identities")
    return list(ordered)


def transfer_t90(original: dict[str, Any], reference_parameters: Any) -> dict[str, np.ndarray]:
    """Transfer reviewed articulation only, preserving all morphology and expression."""
    shapes = {"identity_coeffs": (1, 45), "lbs_model_params": (1, 204), "face_expr_coeffs": (1, 72)}
    result = {}
    for name, shape in shapes.items():
        value = np.asarray(original[name])
        if value.shape != shape or not np.isfinite(value).all():
            raise ValueError("Invalid native controls: " + name)
        result[name] = value.copy()
    reference = np.asarray(reference_parameters)
    if reference.shape != (1, 204) or not np.isfinite(reference).all():
        raise ValueError("Invalid native T90 reference controls")
    result["lbs_model_params"][:, :ARTICULATION_END] = reference[:, :ARTICULATION_END]
    return result
