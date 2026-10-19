"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
from typing import Any


def anon(uid: Any) -> Any:
    return "P-" + hashlib.sha256(uid.encode()).hexdigest()[:12]
