"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


def persist(path: Path, data: bytes, *, replace: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".partial-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_json(path: Path, value: Any, *, replace: bool = False) -> None:
    persist(
        path,
        (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(),
        replace=replace,
    )


def write_npz(path: Path, **arrays: Any) -> None:
    import io

    if any((np.asarray(value).dtype.hasobject for value in arrays.values())):
        raise ValueError("Numeric arrays only; no pickle/object payload")
    stream = io.BytesIO()
    np.savez_compressed(stream, **arrays)
    persist(path, stream.getvalue())
