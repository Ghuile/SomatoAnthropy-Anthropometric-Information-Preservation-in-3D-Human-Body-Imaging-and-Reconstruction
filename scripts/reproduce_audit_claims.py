"""Reproduce the six audit claims from public summaries or licensed local records."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from somatoanthropy.claims import (
    assemble_claims,
    cohort_counts,
    compare_claims,
    control_domains,
    fallback_counts,
    frozen_claims,
    geometry_statistics,
    height_statistics,
    validate_record_linkage,
)
from somatoanthropy.data.phase01_nomo import atomic_json
from somatoanthropy.workflow import RecordStore

ROOT = Path(__file__).resolve().parents[1]


def licensed_claims(manifest: Path, output: Path):
    config = json.loads(manifest.read_text("utf-8"))
    if not config.get("files"):
        raise ValueError("EXPLICIT_INPUT_HASHES_REQUIRED")
    store = RecordStore(
        manifest.parent / config["input_root"], output.parent, input_pins=config["files"]
    )
    inputs = {}
    receipts = {}
    for label in [
        "cohort_manifest",
        "waist_pairs",
        "height_records",
        "geometry_records",
        "parameter_audit",
    ]:
        name = config[label]
        path = store.pin(name)
        if path.suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as stream:
                inputs[label] = list(csv.DictReader(stream))
        else:
            inputs[label] = store.read(name)
        receipts[label] = hashlib.sha256(path.read_bytes()).hexdigest()
    validate_record_linkage(inputs["height_records"], inputs["geometry_records"])
    result = assemble_claims(
        height_statistics(inputs["height_records"]),
        geometry_statistics(inputs["geometry_records"]),
        cohort_counts(inputs["cohort_manifest"]),
        fallback_counts(inputs["waist_pairs"]),
        control_domains(inputs["parameter_audit"]),
    )
    return result, dict(
        input_sha256=receipts,
        input_records_included=False,
        fitting_executed=False,
        rank_function="experiments.e2_1.core.variation",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["frozen", "licensed"])
    parser.add_argument(
        "--manifest", type=Path, help="Required only for licensed local-record replay"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new audit output file")
    if args.mode == "licensed":
        if args.manifest is None:
            parser.error("licensed requires --manifest")
        result, receipt = licensed_claims(args.manifest, args.output)
    else:
        result, receipt = frozen_claims(ROOT), None
    expected = json.loads((ROOT / "results/aggregate/claim-traceability.json").read_text("utf-8"))
    compare_claims(result, expected)
    atomic_json(args.output, result)
    if receipt is not None:
        atomic_json(args.output.with_suffix(".provenance.json"), receipt)
    print("Six audit claims reproduced and checked; no individual records exported.")


if __name__ == "__main__":
    main()
