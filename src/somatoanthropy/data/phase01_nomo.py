"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

NAMESPACE = uuid.UUID("fa0a3a3f-d5e8-5145-830a-e6483870a915")


def linked_uid(kind: str, *parts: str) -> str:
    return kind + "-" + uuid.uuid5(NAMESPACE, "/".join(parts)).hex


def atomic_bytes(path: Path, payload: bytes) -> None:
    """Exclusive publication; interruption leaves only an unselected partial file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError("Existing different result: " + str(path))
        return
    temporary = path.with_name(path.name + ".partial-" + uuid.uuid4().hex)
    with temporary.open("xb") as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
    if os.name == "nt":
        temporary.rename(path)
    else:
        os.link(temporary, path)
        temporary.unlink()


def atomic_json(path: Path, value: Any) -> None:
    atomic_bytes(
        path,
        (
            json.dumps(
                value, indent=2, sort_keys=True, allow_nan=False, default=lambda x: x.tolist()
            )
            + "\n"
        ).encode("utf-8"),
    )
