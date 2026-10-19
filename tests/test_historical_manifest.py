"""The manifest repair stays confined to the exact incomplete upload revision."""

import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VERIFY = runpy.run_path(str(ROOT / "scripts/verify_release.py"))
UPLOAD = "05f8e8fac023daa4a3fc8b8c55ac06e09c8e7859"


def test_repair_is_confined_to_pinned_commit(tmp_path):
    receipts = tmp_path / "docs/historical-manifests"
    receipts.mkdir(parents=True)
    (receipts / (UPLOAD + ".sha256")).write_text("audited receipt\n", encoding="utf-8")
    read = VERIFY["historical_manifest"]
    assert read(tmp_path, UPLOAD, b"stale manifest") == "audited receipt\n"
    assert read(tmp_path, "a" * 40, b"original manifest") == "original manifest"
    with pytest.raises(FileNotFoundError):
        read(tmp_path / "missing", UPLOAD, b"stale manifest")
