"""Replay the original full control audit from a saved native parameter probe."""

import argparse
import hashlib
import json
from pathlib import Path

from somatoanthropy.claims import compare_claims, control_domains
from somatoanthropy.data.phase01_nomo import atomic_json
from somatoanthropy.experiments.e2_1.core import parameter_audit

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new control-audit output")
    payload = args.probe.read_bytes()
    if hashlib.sha256(payload).hexdigest() != args.sha256:
        raise ValueError("NATIVE_PROBE_HASH_MISMATCH")
    probe = json.loads(payload)
    # Strip local runtime/resource fields before calling the frozen algorithm.
    audit = parameter_audit({k: probe[k] for k in ["rows", "limits", "model_revision"]})
    expected = json.loads((ROOT / "configs/control_audit_204.json").read_text("utf-8"))
    compare_claims(audit, expected)
    control_domains(audit)
    atomic_json(args.output, audit)
    print("204 control rows reproduce the original audit; no model forward or fitting executed.")


if __name__ == "__main__":
    main()
