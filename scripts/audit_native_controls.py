"""Inspect the pinned native model's 204 controls without geometry or fitting."""

import argparse
import json
import sys
from pathlib import Path

from somatoanthropy.claims import compare_claims, control_domains
from somatoanthropy.data.phase01_nomo import atomic_json
from somatoanthropy.experiments.e2_1.core import parameter_audit
from somatoanthropy.native_probe import probe_controls
from somatoanthropy.reconstruction import check_hashes, load_native

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new control-audit output")
    pins = json.loads((ROOT / "configs/model_hashes.json").read_text("utf-8"))
    check_hashes(args.model_root, {k: v for k, v in pins.items() if "/lod0/" not in k})
    sys.path.insert(0, str(args.model_root / "assets/mhr/v1/code"))
    config = json.loads((ROOT / "configs/control_release.json").read_text("utf-8"))
    names = config["original_fitting"]["parameter_names"]
    model, _ = load_native(args.model_root / "assets/mhr/v1/lod1", 1, names, 20261018)
    audit = parameter_audit(probe_controls(model, names))
    expected = json.loads((ROOT / "configs/control_audit_204.json").read_text("utf-8"))
    compare_claims(audit, expected)
    control_domains(audit)
    atomic_json(args.output, audit)
    print("204 loaded native control mappings and domains match; no geometry forward or fitting.")


if __name__ == "__main__":
    main()
