"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations
import re
import uuid
SPEC = 'SS3D-IDENTITY-v1'
NAMESPACE = uuid.UUID('fa0a3a3f-d5e8-5145-830a-e6483870a915')
PATTERN = re.compile('SS3D-([A-Z][A-Z0-9]*)-([A-Za-z0-9][A-Za-z0-9_-]{7,127})\\Z')

def dataset_of(uid: str) -> str:
    match = PATTERN.fullmatch(uid)
    if match is None:
        raise ValueError('NONCOMPLIANT_SUBJECT_UID:' + uid)
    return match.group(1)

def subject_uid(dataset: str, source_key: str, *, existing: str | None=None) -> str:
    if not re.fullmatch('[A-Z][A-Z0-9]*', dataset) or not source_key or '\x00' in source_key:
        raise ValueError('INVALID_IDENTITY_SOURCE_KEY')
    if existing is not None:
        if dataset_of(existing) != dataset:
            raise ValueError('SUBJECT_DATASET_REASSIGNMENT')
        return existing
    key = '5172126/v3/' + source_key if dataset == 'NOMO' else SPEC + '/' + dataset + '/' + source_key
    return f'SS3D-{dataset}-' + uuid.uuid5(NAMESPACE, key).hex
