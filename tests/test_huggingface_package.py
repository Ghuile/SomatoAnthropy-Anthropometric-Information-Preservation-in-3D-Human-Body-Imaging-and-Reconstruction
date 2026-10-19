"""Packaging tests use only curated aggregate files and invented example values."""

import hashlib
import json
import runpy
import shutil
import tomllib
import zipfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
BUILD = runpy.run_path(str(ROOT / "scripts/prepare_huggingface.py"))
COMMIT = "a" * 40


def test_licence_scopes_preserve_upstream_notices():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]
    assert project["license"] == "MIT"
    assert "LICENSES/*.txt" in project["license-files"]
    assert (ROOT / "LICENSE").read_bytes() == (ROOT / "LICENSES/MIT.txt").read_bytes()
    assert (ROOT / "LICENSES/CC-BY-4.0.txt").read_bytes().startswith(b"Attribution 4.0")
    assert set(yaml.safe_load((ROOT / "CITATION.cff").read_text("utf-8"))["license"]) == {
        "MIT",
        "CC-BY-4.0",
    }
    for name in ("MHR-code", "MHR-assets", "clad-body"):
        assert b"Apache License" in (ROOT / f"third_party/{name}-Apache-2.0.txt").read_bytes()


def test_private_package_uses_allowlist_and_rejects_tampering(tmp_path):
    release = tmp_path / "source"
    files = [
        line.split("  ", 1)[1]
        for line in (ROOT / "MANIFEST.sha256").read_text("utf-8").splitlines()
    ]
    for name in files + ["MANIFEST.sha256"]:
        destination = release / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    # An unrelated private record is deliberately outside the curated allowlist.
    (release / "cohort-ledger.json").write_text(
        '{"private_fixture":"EXCLUDE_THIS_INVENTED_RECORD"}'
    )
    package, archive = tmp_path / "package", tmp_path / "private.zip"
    result = BUILD["build_package"](release, package, COMMIT, archive)
    assert result["aggregate_tables"] == 47 and result["csv_tables"] == 6
    assert result["uploaded"] is False
    assert not (package / "cohort-ledger.json").exists()
    assert all(
        b"EXCLUDE_THIS_INVENTED_RECORD" not in p.read_bytes()
        for p in package.rglob("*")
        if p.is_file()
    )
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == result["archive_sha256"]
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
    card = (package / "README.md").read_text("utf-8").split("---", 2)[1]
    assert yaml.safe_load(card)["license"] == "cc-by-4.0"
    assert (package / "LICENSE").read_bytes() == (ROOT / "LICENSES/CC-BY-4.0.txt").read_bytes()
    runpy.run_path(str(package / "examples/check_invented.py"))
    with pytest.raises(FileExistsError):
        BUILD["build_package"](release, package, COMMIT)
    path = package / "results/aggregate/NOMO-cohort-selection.json"
    path.write_text("[]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="RELEASE_HASH_MISMATCH"):
        BUILD["verify_package"](release, package)


def test_csv_exports_keep_scalar_values_and_reject_nested_rows():
    value = BUILD["table_csv"]([dict(n=2, mean=1.25, flag=True, unavailable=None)])
    assert value == b"n,mean,flag,unavailable\n2,1.25,true,\n"
    with pytest.raises(ValueError, match="NESTED_VALUES"):
        BUILD["table_csv"]([dict(interval=[1, 2])])


def test_builder_rejects_incorrect_git_commit_before_writing(tmp_path, monkeypatch):
    root = tmp_path / "checkout"
    (root / ".git").mkdir(parents=True)
    scope = BUILD["build_package"].__globals__
    monkeypatch.setattr(scope["subprocess"], "check_output", lambda *a, **k: "b" * 40)
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="SOURCE_COMMIT_DOES_NOT_MATCH"):
        BUILD["build_package"](root, output, COMMIT)
    assert not output.exists()
