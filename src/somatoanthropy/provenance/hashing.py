"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

import hashlib
import json
import math
from pathlib import PurePosixPath, PureWindowsPath


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate(value: object, active: set[int], portable: bool = False) -> None:
    if value is None or type(value) in (bool, int):
        return
    if isinstance(value, str):
        if portable and (
            PurePosixPath(value).is_absolute()
            or PureWindowsPath(value).drive
            or PureWindowsPath(value).root
        ):
            raise ValueError("Absolute path values are not portable inputs.")
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Non-finite numbers are unsupported.")
        return
    if not isinstance(value, (dict, list)):
        raise ValueError("Only JSON-compatible YAML values are supported.")
    if id(value) in active:
        raise ValueError("Cyclic structures are unsupported.")
    active.add(id(value))
    if isinstance(value, dict):
        if any((not isinstance(key, str) for key in value)):
            raise ValueError("Mapping keys must be strings.")
        for key, item in value.items():
            _validate(key, active, portable)
            _validate(item, active, portable)
    else:
        for item in value:
            _validate(item, active, portable)
    active.remove(id(value))


def sha256_canonical(value: object) -> str:
    """Hash compact sorted JSON, preserving scalar types and list order."""
    _validate(value, set())
    data = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )
    return sha256_bytes(data.encode("utf-8"))
