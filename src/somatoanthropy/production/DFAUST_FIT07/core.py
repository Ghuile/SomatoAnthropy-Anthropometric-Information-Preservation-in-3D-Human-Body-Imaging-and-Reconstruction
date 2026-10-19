"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

from somatoanthropy.data.identity import subject_uid
from somatoanthropy.data.phase01_nomo import linked_uid


def identifiers(container_sha: str, key: str, frame: int) -> dict[str, str]:
    provider, label = key.split("_", 1)
    if not provider.isdigit() or not label or type(frame) is not int or (frame < 0):
        raise ValueError("INVALID_PROVIDER_FRAME")
    return dict(
        subject_uid=subject_uid("DFAUST", provider),
        sequence_uid=linked_uid("SEQ", "DFAUST", container_sha, key),
        source_record_uid=linked_uid("SRC", "DFAUST", container_sha, key, str(frame)),
        observation_uid=linked_uid("OBS", "DFAUST", container_sha, key, str(frame)),
    )
