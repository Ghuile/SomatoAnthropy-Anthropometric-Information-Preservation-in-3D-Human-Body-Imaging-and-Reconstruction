"""Invented records test source conversion, linkage and NHANES missingness."""

import copy
import hashlib
import json
import zipfile

import numpy as np
import pytest

from somatoanthropy.experiments.e1.inputs import pair_meshes
from somatoanthropy.experiments.e4.inputs import index_unique, linked_pair
from somatoanthropy.geometry.fit09_nhanes_mhr.source import choose, eligible_profile
from somatoanthropy.production.DFAUST_FIT07.core import identifiers
from somatoanthropy.workflow import RecordStore


def test_historical_selection_rules_on_invented_eligible_records():
    from somatoanthropy.geometry.hbw_mhr_fit08.selection import select as hbw
    from somatoanthropy.production.HIT_MHR_FIT05.core import choose as hit
    from somatoanthropy.production.MPII_MHR_FIT01.prepare import select as mpii
    from somatoanthropy.production.NOMO_PAIRED_NICP.core import select_additional
    from somatoanthropy.production.UCSC_MHR_FIT02.prepare import select as ucsc

    existing = ["male_example_old", "female_example_old"]
    available = existing + [
        f"{group}_example_{i}" for group in ["male", "female"] for i in range(6)
    ]
    picked = select_additional(existing, available, count=4)
    assert picked == select_additional(existing, available[::-1], count=4)
    assert not set(picked) & set(existing)
    assert sum(x.startswith("male_") for x in picked) == 2
    candidates = [
        dict(source_id=f"example-{i:03}", height_extent_m=1.5 + i / 1000) for i in range(120)
    ]
    selected = mpii(candidates, {"example-000"}, seed=7)
    assert len(selected) == 100
    assert selected == mpii(candidates[::-1], {"example-000"}, seed=7)
    candidates = [
        dict(
            source_id=f"example-{i:03}",
            source_sex_group="male" if i % 2 else "female",
            raw_height_proxy=150 + i,
        )
        for i in range(20)
    ]
    assert len(ucsc(candidates, set(), 7, maximum=12)) == 12
    assert ucsc(candidates, set(), 7) == ucsc(candidates[::-1], set(), 7)
    candidates = [
        dict(
            subject_id=f"example-{i}",
            source_split="train",
            hit_gender_label="male",
            path=f"male/train/example-{i}",
        )
        for i in range(6)
    ]
    assert len(hit(candidates, {"example-0"}, maximum=4)) == 4
    assert hit(candidates, {"example-0"}) == hit(candidates[::-1], {"example-0"})
    candidates = [
        dict(source_id=f"example-{i}", split="val", npy=f"example-{i}.npy") for i in range(10)
    ]
    assert hbw(candidates) == hbw(candidates[::-1])
    with pytest.raises(ValueError, match="split"):
        hbw([dict(r, split="test") for r in candidates])


def test_nhanes_additional_selection_keeps_imputations_as_one_person():
    from somatoanthropy.production.NHANES_FIT09.prepare import stratified_selection

    population = [
        dict(
            private_family_key=["2005-2006", 900000 + i, "primary"],
            seqn=900000 + i,
            source_gender_code=1 + i % 2,
            targets_cm=[150 + i / 10, 70 + i / 5, 20 + i / 20, 40 + i / 10],
        )
        for i in range(100)
    ]
    excluded = set(range(900000, 900010))
    a = stratified_selection(population, excluded, 50, "invented")
    assert a == stratified_selection(population[::-1], excluded, 50, "invented")
    assert len(a) == 50 and len({r["seqn"] for r in a}) == 50
    assert not {r["seqn"] for r in a} & excluded
    assert sum(r["source_gender_code"] == 1 for r in a) == 25
    with pytest.raises(ValueError, match="Repeated source family"):
        stratified_selection([population[0], population[0]], set(), 50, "invented")


def test_dfaust_six_frame_selection_preserves_pilots_and_distinct_motions():
    from somatoanthropy.production.DFAUST_FIT07.frame60 import select_panel

    sequences, pilots = [], []
    labels = [
        "shake_arms",
        "jumping_jacks",
        "knees",
        "hips",
        "one_leg_jump",
        "punching",
        "shake_shoulders",
    ]
    for i in range(10):
        for label in labels:
            key = f"{900000 + i}_{label}"
            row = dict(
                partition="invented",
                key=key,
                frames=21,
                container_sha256="a" * 64,
                subject_uid=identifiers("a" * 64, key, 0)["subject_uid"],
            )
            sequences.append(row)
            if label == "punching":
                pilots.append(
                    dict(
                        row,
                        frame=3,
                        fit_uid=f"invented-fit-{i}",
                        existing_fit_directory=f"invented/{i}",
                    )
                )
    panel = select_panel(dict(sequences=sequences), pilots)
    assert panel == select_panel(dict(sequences=sequences[::-1]), pilots[::-1])
    assert len(panel) == 60
    reused = [r for r in panel if r["reuse_existing_fit"]]
    assert len(reused) == 10 and all(r["frame"] == 3 for r in reused)
    assert all(r["frame"] in (0, 10) for r in panel if not r["reuse_existing_fit"])


def test_faust_candidate_selection_respects_qualification_before_error():
    from somatoanthropy.production.FAUST_FIT06.core import select_candidates

    good = dict(
        subject_uid="invented-person",
        native_parameter_valid=True,
        historical_native_replay="PASS",
        human_review=dict(human_fitted="ACCEPT"),
        candidate_assessment=dict(
            technical_lod0="PASS",
            invalid_sites=0,
            severe_regional_defect=False,
            ambiguous_sites=0,
            fallback_sites=0,
        ),
        ranking_metrics=dict(
            definition="invented-common", normalized_symmetric_rms=1.0, normalized_p95=2.0
        ),
        observation_uid="invented-a",
        body_uid="invented-body-a",
    )
    rejected = dict(
        good,
        human_review=dict(human_fitted="REJECT"),
        body_uid="invented-body-b",
        ranking_metrics=dict(
            definition="invented-common", normalized_symmetric_rms=0.0, normalized_p95=0.0
        ),
    )
    assert select_candidates([rejected, good]) == {"invented-person": "invented-body-a"}


def test_linkage_keeps_observations_together_and_paths_distinct():
    a = identifiers("a" * 64, "999999_invented_motion", 0)
    b = identifiers("a" * 64, "999999_invented_motion", 1)
    assert a["subject_uid"] == b["subject_uid"]
    assert a["sequence_uid"] == b["sequence_uid"]
    assert a["observation_uid"] != b["observation_uid"]
    with pytest.raises(ValueError, match="INVALID_PROVIDER_FRAME"):
        identifiers("a" * 64, "999999_invented_motion", -1)
    first = dict(subject_uid="invented", source_id="example", body_uid="a", collection="SMPL-NICP")
    second = dict(first, body_uid="b", collection="CAESAR-NICP")
    assert linked_pair(first, second, "primary")["subject_uid"] == "invented"
    with pytest.raises(ValueError, match="CROSS_PARTICIPANT"):
        linked_pair(first, dict(second, subject_uid="another"), "primary")
    with pytest.raises(ValueError, match="INDEPENDENT_NATIVE"):
        linked_pair(first, dict(second, body_uid="a"), "primary")
    with pytest.raises(ValueError, match="DUPLICATE_LINK"):
        index_unique([first, first], ("subject_uid", "collection"))


def panels(category=1):
    fields = {
        k: dict(state=0, value=v)
        for k, v in dict(
            RIAGENDR=category,
            RIDAGEYR=40,
            BMDSTATS=1,
            BMXHT=170,
            BMXWAIST=85,
            BMXARMC=30,
            BMXTHICR=50,
        ).items()
    }
    fields.update(
        {k: dict(state=1, value=None) for k in ["BMIHT", "BMIWAIST", "BMIARMC", "BMITHICR"]}
    )
    return [dict(panel=i, fields=copy.deepcopy(fields)) for i in range(1, 6)]


def test_nhanes_requires_consistent_observed_fields_in_all_five_panels():
    source = panels()
    r = eligible_profile(999999, source)
    assert r["targets_m"] == [1.7, 0.85, 0.3, 0.5]
    assert r["source_fields"]["BMIWAIST"]["value"] is None
    source[0]["fields"]["BMXWAIST"]["value"] = 86
    with pytest.raises(ValueError, match="INCONSISTENT"):
        eligible_profile(999999, source)
    source = panels()
    for p in source:
        p["fields"]["BMXWAIST"] = dict(state=1, value=None)
    with pytest.raises(ValueError, match="MISSING_OR_INVALID_BMXWAIST"):
        eligible_profile(999999, source)
    with pytest.raises(ValueError, match="FIVE_PANEL_LINKAGE"):
        eligible_profile(999999, panels()[:-1])


def test_nhanes_frozen_selection_is_input_order_independent():
    eligible = [
        eligible_profile(900000 + 10 * category + i, panels(category))
        for category in [1, 2]
        for i in range(6)
    ]
    assert choose(eligible) == choose(list(reversed(eligible)))
    assert len(choose(eligible)) == 10


@pytest.mark.parametrize("dataset", ["HBW", "HIT"])
def test_native_centimetre_datasets_use_saved_alignment(tmp_path, dataset):
    source = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0]])
    faces = [[0, 1, 2]]
    np.savez(tmp_path / "source.npz", vertices=source, faces=faces)
    np.savez(tmp_path / "fitted.npz", vertices=source * 100, faces=faces)
    translation = np.array([0.2, 0.3, 0.4])
    (tmp_path / "transforms.json").write_text(
        json.dumps(
            dict(
                source_to_fitting_rotation=np.eye(3).tolist(),
                native_to_fitting_translation_m=translation.tolist(),
            )
        )
    )
    row = dict(
        dataset=dataset,
        surface_eligible=True,
        fitted_mesh="fitted.npz",
        fitted_parameters="params.npz",
        source_path="source.npz",
        source_sha256=hashlib.sha256((tmp_path / "source.npz").read_bytes()).hexdigest(),
        lod=0,
        unit="engineering_m",
    )
    a, b, _ = pair_meshes(RecordStore(tmp_path, tmp_path / "outputs"), row)
    np.testing.assert_allclose(a[0], source)
    np.testing.assert_allclose(b[0], source + (translation if dataset == "HIT" else 0))


def test_faust_validates_the_archive_member_bytes(tmp_path):
    raw = b"ply\nformat ascii 1.0\nelement vertex 3\nproperty float x\nproperty float y\nproperty float z\nelement face 1\nproperty list uchar int vertex_indices\nend_header\n0 0 0\n1 0 0\n0 1 0\n3 0 1 2\n"
    with zipfile.ZipFile(tmp_path / "invented.zip", "w") as archive:
        archive.writestr("invented.ply", raw)
    np.savez(
        tmp_path / "fitted.npz", vertices=[[0.0, 0, 0], [1, 0, 0], [0, 1, 0]], faces=[[0, 1, 2]]
    )
    (tmp_path / "transforms.json").write_text("{}")
    row = dict(
        dataset="FAUST",
        surface_eligible=True,
        fitted_mesh="fitted.npz",
        source_path="invented.zip",
        source_member="invented.ply",
        source_sha256=hashlib.sha256(raw).hexdigest(),
        lod=0,
        unit="engineering_m",
    )
    store = RecordStore(tmp_path, tmp_path / "outputs")
    a, b, _ = pair_meshes(store, row)
    np.testing.assert_array_equal(a[0], b[0])
    with pytest.raises(ValueError, match="SOURCE_MEMBER_HASH_MISMATCH"):
        pair_meshes(store, dict(row, source_sha256="0" * 64))
