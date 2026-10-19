"""Audit additions: report integrity, schema coverage and template input isolation."""

import hashlib
import json
import runpy
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def test_released_register_has_distinct_original_and_abridged_hashes():
    records = json.loads((ROOT / "docs/evidence_versions.json").read_text("utf-8"))
    assert len(records) == 12
    for row in records:
        content = (ROOT / "docs/experiments" / row["path"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == row["sha256"]
        assert row["sha256"] != row["original_sha256"]
        assert b"abridged" in content


def test_every_aggregate_field_and_file_is_documented():
    dictionary = json.loads((ROOT / "docs/data_dictionary.json").read_text("utf-8"))
    schemas = {r["file"]: r for r in dictionary["tables"]}

    def walk(value):
        if isinstance(value, dict):
            assert set(value).issubset(dictionary["fields"])
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    for path in (ROOT / "results/aggregate").glob("*.json"):
        assert path.relative_to(ROOT).as_posix() in schemas
        walk(json.loads(path.read_text("utf-8")))


def test_template_settings_never_import_participant_controls():
    make = runpy.run_path(str(ROOT / "scripts/render_mhr_template.py"))["template_controls"]
    spec = json.loads((ROOT / "configs/control_release.json").read_text("utf-8"))
    settings = make(spec)
    assert len(settings) == 19
    for label, controls in settings:
        assert np.count_nonzero(controls["identity_coeffs"]) == 0
        assert np.count_nonzero(controls["face_expr_coeffs"]) == 0
        assert np.count_nonzero(controls["lbs_model_params"]) == (label != "neutral")
        assert np.count_nonzero(controls["lbs_model_params"][:, :130]) == 0
    # Each setting owns its own arrays; changing a panel cannot contaminate another.
    settings[1][1]["lbs_model_params"][:] = 9
    assert np.count_nonzero(settings[0][1]["lbs_model_params"]) == 0
