"""Independent numerical expectations on invented inputs and frozen aggregates."""

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
import trimesh

from somatoanthropy.aggregate import check_anchors, check_paper_tables
from somatoanthropy.experiments.e1.inputs import pair_meshes
from somatoanthropy.geometry.mpii_mhr_fit01.metrics import compare, distances
from somatoanthropy.reconstruction import clad_api
from somatoanthropy.repeated import geometry_summary
from somatoanthropy.workflow import RecordStore

ROOT = Path(__file__).resolve().parents[1]


def test_artifact_provenance_rejects_changed_figure_bytes(tmp_path):
    import runpy

    verify = runpy.run_path(str(ROOT / "scripts/verify_release.py"))["artifact_provenance"]
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/aggregate_manifest.json").write_text("[]")
    figures = tmp_path / "results/figures"
    figures.mkdir(parents=True)
    data = b"<svg>invented fixture</svg>\n"
    (figures / "Figure1.svg").write_bytes(data)
    (figures / "captions_and_provenance.json").write_text(
        json.dumps([dict(outputs={"Figure1.svg": hashlib.sha256(data).hexdigest()})])
    )
    assert verify(tmp_path) == dict(aggregate_files=0, figure_files=1)
    (figures / "Figure1.svg").write_bytes(data.replace(b"\n", b"\r\n"))
    with pytest.raises(ValueError, match="ARTIFACT_PROVENANCE_MISMATCH"):
        verify(tmp_path)


def test_frozen_publication_values_and_display_rounding():
    assert len(check_anchors(ROOT)) >= 89
    assert check_paper_tables(ROOT) >= 67


def test_triangle_interior_distance_is_not_distance_to_a_vertex():
    v = np.array([[0.0, 0, 0], [2, 0, 0], [0, 2, 0]])
    f = np.array([[0, 1, 2]])
    actual = distances([[0.5, 0.5, 3], [0.5, 0.5, 0], [3, 0, 0]], v, f)
    np.testing.assert_allclose(actual, [3, 0, 1], atol=1e-14)
    pair = compare(v, f, v + [0, 0, 0.25], f, count=64, seed=7)
    for key in ["symmetric_mean", "rms", "p95"]:
        assert pair[key] == pytest.approx(0.25)


def test_six_observations_produce_fifteen_dependent_pairs():
    face = np.array([[0, 1, 2]])
    base = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]])
    arrays, rows = {}, []
    for person, scale in [("invented-a", 1), ("invented-b", 2)]:
        for i in range(6):
            name = f"{person}-{i}"
            rows.append(dict(subject_uid=person, observation_uid=name, canonical_mesh=name))
            arrays[name] = dict(vertices=base + [scale * i / 100, 0, 0], faces=face)
    result = geometry_summary(rows, arrays.__getitem__)
    assert all(r["pair_count"] == 15 for r in result["persons"])
    assert result["aggregate"][0]["subjects"] == 2
    # Pair differences 1 (five), 2 (four), 3 (three), 4 (two), 5 (one).
    assert result["aggregate"][0]["median"] == pytest.approx(3)
    assert result["aggregate"][1]["median"] == pytest.approx(0, abs=1e-12)
    with pytest.raises(ValueError, match="SIX_DISTINCT"):
        geometry_summary(rows[:-1], arrays.__getitem__)


def test_nomo_adapter_preserves_saved_transform(tmp_path):
    source = tmp_path / "source.obj"
    source.write_text("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
    np.savez(
        tmp_path / "fitted.npz",
        vertices=np.array([[2.0, 3, 4], [3, 3, 4], [2, 4, 4]]),
        faces=[[0, 1, 2]],
    )
    import hashlib

    store = RecordStore(tmp_path, tmp_path / "outputs")
    matrix = np.eye(4)
    matrix[:3, 3] = [2, 3, 4]
    row = dict(
        dataset="NOMO",
        surface_eligible=True,
        fitted_mesh="fitted.npz",
        source_path="source.obj",
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_to_working=matrix.tolist(),
        lod=0,
        unit="engineering_m",
    )
    source_mesh, target_mesh, meta = pair_meshes(store, row)
    np.testing.assert_array_equal(source_mesh[0], target_mesh[0])
    assert meta["no_posthoc_alignment"]
    with pytest.raises(ValueError, match="INPUT_ESCAPES"):
        store.pin("../outside")


def test_record_store_source_table_contract_and_hash_rejection(tmp_path):
    input_root = tmp_path / "inputs"
    input_root.mkdir()
    (input_root / "value.json").write_text("{}")
    store = RecordStore(input_root, tmp_path / "output", input_pins={"value.json": "0" * 64})
    with pytest.raises(ValueError, match="HASH_MISMATCH"):
        store.read("value.json")
    store.table("aggregate", [dict(n=2, mean=3.0)])
    assert store.src_table("aggregate") == [dict(n=2, mean=3.0)]


def test_pinned_official_comparator_on_invented_prism():
    if importlib.util.find_spec("clad_body") is None:
        pytest.skip("Optional pinned comparator distribution is absent")
    pins = json.loads((ROOT / "configs/clad_body_hashes.json").read_text("utf-8"))["files"]
    body, convert, measure, _ = clad_api(pins)
    mesh = trimesh.creation.box(extents=[0.4, 0.3, 1.8])
    mesh.vertices[:, 2] += 0.9
    result = measure(body(mesh, source="invented rectangular prism"), only=["waist_cm"])
    assert result["waist_cm"] == pytest.approx(140)
    assert result["_waist_pct"] == pytest.approx(61)
    assert result["_waist_z"] == pytest.approx(1.098)
    assert "body_fat_pct" not in result
    assert convert(np.array([[0.0, 0, 0], [40, 180, -30]])).dtype == np.float32
