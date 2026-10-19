"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

import json
import math
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any

import numpy as np

from somatoanthropy.provenance.hashing import sha256_canonical

Vec3 = tuple[float, float, float]


def portable_json(value: Any) -> str:
    """Freeze portable deterministic metadata, excluding runtime timestamps."""

    def visit(item: Any) -> None:
        if isinstance(item, str) and (
            PurePosixPath(item).is_absolute()
            or PureWindowsPath(item).drive
            or PureWindowsPath(item).root
        ):
            raise ValueError("Absolute paths are not deterministic identities")
        if isinstance(item, dict):
            for key, child in item.items():
                if "timestamp" in key.lower() or key.lower() in {"created_at", "updated_at"}:
                    raise ValueError("Runtime timestamps are not deterministic identities")
                visit(key)
                visit(child)
        if isinstance(item, (list, tuple)):
            for child in item:
                visit(child)

    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    parsed = json.loads(encoded)
    visit(parsed)
    sha256_canonical(parsed)
    return encoded


def vector(value: Any, *, unit: bool = False) -> Vec3:
    a = np.asarray(value, dtype=np.float64)
    if a.shape != (3,) or not np.isfinite(a).all():
        raise ValueError("Finite three-dimensional vector required")
    if unit:
        maximum = float(np.max(np.abs(a)))
        if maximum == 0:
            raise ValueError("Nonzero plane normal/axis required")
        a = a / maximum
        a = a / np.linalg.norm(a)
    return (float(a[0]), float(a[1]), float(a[2]))


@dataclass(frozen=True)
class Plane:
    point: Vec3
    normal: Vec3

    def __post_init__(self) -> None:
        object.__setattr__(self, "point", vector(self.point))
        object.__setattr__(self, "normal", vector(self.normal, unit=True))


@dataclass(frozen=True)
class SectionConfig:
    tolerance_m: float = 1e-10
    max_search_sections: int = 100000

    def __post_init__(self) -> None:
        if type(self.max_search_sections) is not int or self.max_search_sections < 2:
            raise ValueError("Explicit search resource bound must be integer >= 2")
        if not math.isfinite(self.tolerance_m) or self.tolerance_m <= 0:
            raise ValueError("Positive finite explicit numerical tolerance in metres required")


class AnthropometryError(ValueError):
    """Fail closed: structured reason/diagnostics, never a plausible value."""

    def __init__(self, reason: str, diagnostics: dict[str, Any] | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.diagnostics = diagnostics or {}

    def to_dict(self) -> dict[str, Any]:
        return {"status": "NOT_MEASURABLE", "reason": self.reason, "diagnostics": self.diagnostics}
