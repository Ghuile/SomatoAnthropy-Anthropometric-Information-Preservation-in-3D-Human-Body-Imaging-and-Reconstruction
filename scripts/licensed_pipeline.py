"""Explicit local licensed-input entry points; default action checks availability."""

import argparse
import importlib
import json
from pathlib import Path

import numpy as np

from somatoanthropy.data.nomo.meshes import read_mesh
from somatoanthropy.experiments.e1.core import COUNT, surface_pair
from somatoanthropy.experiments.e1.inputs import pair_meshes
from somatoanthropy.experiments.e2_1.optimizer import optimise
from somatoanthropy.experiments.e2_2.core import fit_config, policies, starting_controls
from somatoanthropy.geometry.anthropometry.t90_remeasurement import transfer_t90
from somatoanthropy.geometry.mpii_mhr_fit01.storage import write_npz
from somatoanthropy.geometry.nomo_caesar_mhr_fit04.core import transform
from somatoanthropy.geometry.nomo_caesar_mhr_fit04.source import surface_mask
from somatoanthropy.reconstruction import check_hashes, clad_api, load_native, native_forward
from somatoanthropy.repeated import geometry_summary
from somatoanthropy.workflow import RecordStore

ROOT = Path(__file__).resolve().parents[1]


def setup(manifest, output):
    config = json.loads(manifest.read_text(encoding="utf-8"))
    root = (manifest.parent / config["input_root"]).resolve()
    store = RecordStore(
        root, output, config.get("sources"), config.get("aggregate_sources"), config.get("files")
    )
    missing = []
    for name, digest in config.get("files", {}).items():
        try:
            store.pin(name, digest)
        except FileNotFoundError:
            missing.append(name)
    requirements = config.get("requirements", [])
    return (
        config,
        store,
        dict(
            ready=bool(config.get("files")) and not missing,
            checked_files=len(config.get("files", {})),
            missing=missing,
            requirements=requirements,
        ),
    )


def native_assets(store, config, lod, seed):
    pins = json.loads((ROOT / "configs/model_hashes.json").read_text("utf-8"))
    # Model assets are obtained separately; installed upstream code is checked too.
    check_hashes(store.root, {p: h for p, h in pins.items() if "/code/" not in p})
    module = importlib.import_module("mhr")
    package_root = Path(module.__file__).resolve().parent.parent
    code_pins = {p.split("/code/")[1]: h for p, h in pins.items() if "/code/mhr/" in p}
    check_hashes(package_root, code_pins)
    return load_native(
        store.root / f"assets/mhr/v1/lod{lod}",
        lod,
        config["original_fitting"]["parameter_names"],
        seed,
    )


def run(action, config, store):
    if action == "geometry":
        rows = store.read(config["geometry_records"])
        output = []
        for r in rows:
            source, target, metadata = pair_meshes(store, r)
            output.append(
                dict(
                    record_id=r["record_id"],
                    subject_uid=r["subject_uid"],
                    metadata=metadata,
                    **surface_pair(source, target, count=COUNT, seed=r["evaluation_seed"]),
                )
            )
        store.save("geometry.json", output)
    elif action == "repeated":
        store.save(
            "repeated.json", geometry_summary(store.read(config["repeated_records"]), store.arrays)
        )
    elif action == "waist":
        from somatoanthropy.experiments.waist01.measure import one

        pins = json.loads((ROOT / "configs/clad_body_hashes.json").read_text("utf-8"))["files"]
        api = clad_api(pins)
        atlas, masks = store.read(config["atlas"]), store.arrays(config["region_masks"])
        store.save(
            "waist.json",
            [one(store, r, api, atlas, masks) for r in store.read(config["waist_records"])],
        )
    elif action in ("continue-controls", "replay"):
        base = json.loads((ROOT / "configs/control_release.json").read_text("utf-8"))
        names = base["original_fitting"]["parameter_names"]
        lod = 1 if action == "continue-controls" else 0
        model, faces = native_assets(store, base, lod, config["native_seed"])
        for job in store.read(config["native_jobs"]):
            if (
                len(Path(job["job_id"]).parts) != 1
                or job["job_id"] in (".", "..")
                or ":" in job["job_id"]
            ):
                raise ValueError("SINGLE_COMPONENT_JOB_ID_REQUIRED")
            initial = store.arrays(job["parameters"])
            folder = store.private / job["job_id"]
            if folder.exists():
                raise FileExistsError("EXISTING_JOB_PRESERVED:" + job["job_id"])
            if action == "continue-controls":
                p = policies(base)["R025" if job["policy"] == "D" else job["policy"]]
                fit = fit_config(base, p)
                source = read_mesh(store.pin(job["source_mesh"]).read_bytes())
                sv = transform(source.vertices, job["source_to_working"])
                controls, result = optimise(
                    model,
                    names,
                    faces,
                    sv,
                    source.faces[surface_mask(sv, source.faces)],
                    starting_controls(initial, names, p, base),
                    job["initial_translation"],
                    fit,
                    "released" if p["indices"] else "locked",
                    folder,
                )
                write_npz(folder / "fitted_pose.npz", **controls)
                store.save(job["job_id"] + "/result.json", result)
            else:
                reference = store.arrays(config["t90_reference"])["lbs_model_params"]
                canonical = transfer_t90(initial, reference)
                for state, controls in [("fitted", initial), ("canonical", canonical)]:
                    v, sk = native_forward(model, controls)
                    vv, ss = native_forward(model, controls)
                    if (
                        not np.isfinite(v).all()
                        or not np.isfinite(sk).all()
                        or np.max(abs(v - vv)) > 1e-5
                        or not np.array_equal(sk, ss)
                    ):
                        raise ValueError("NONREPRODUCIBLE_NATIVE_FORWARD")
                    shift = (
                        np.asarray(job["initial_translation"])
                        if state == "fitted"
                        else np.array([0, -v[:, 1].min() * 0.01, 0])
                    )
                    write_npz(
                        folder / (state + "_lod0.npz"),
                        vertices=v.astype(float) * 0.01 + shift,
                        faces=faces,
                        skeleton=sk.reshape(-1, 8),
                        joint_names=np.array([j.name for j in model.character.skeleton.joints]),
                        floor_translation_m=np.array(0 if state == "fitted" else shift[1]),
                    )
                write_npz(folder / "canonical_pose.npz", **canonical)
    else:
        module = importlib.import_module("somatoanthropy.experiments." + action + ".analysis")
        sequence = {
            "e5": ["reconstruction", "waist", "repeated", "decomposition", "associations"],
            "e5s1": [
                "cohort",
                "responses",
                "compensation",
                "reversals",
                "contours",
                "policy",
                "statistics",
            ],
            "e5s2": [
                "cohort",
                "consistency",
                "repeated",
                "diversity",
                "reference",
                "compare",
                "select",
            ],
        }[action]
        for name in sequence:
            getattr(module, name)(store)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=[
            "check",
            "geometry",
            "repeated",
            "waist",
            "continue-controls",
            "replay",
            "e5",
            "e5s1",
            "e5s2",
        ],
        nargs="?",
        default="check",
    )
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "configs/licensed_inputs.example.json"
    )
    parser.add_argument("--output", type=Path, default=Path("reproduced/licensed"))
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Explicitly run the requested licensed-data operation",
    )
    args = parser.parse_args()
    config, store, status = setup(args.manifest, args.output)
    if args.action == "check" or not args.execute:
        print(json.dumps(status, indent=2))
        return
    if not status["ready"]:
        parser.error(
            "Licensed inputs are absent; run check and configure hash-pinned local files first."
        )
    for name, source in config.get("seed_records", {}).items():
        store.save(name, store.read(source))
    run(args.action, config, store)


if __name__ == "__main__":
    main()
