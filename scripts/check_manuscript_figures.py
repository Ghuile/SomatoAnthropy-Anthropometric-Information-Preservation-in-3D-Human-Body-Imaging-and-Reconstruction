"""Check regenerated manuscript SVGs against the released original SVG hashes."""

import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
records = json.loads((root / "docs/manuscript-figure-provenance.json").read_text("utf-8"))[
    "outputs"
]
for name, digest in records.items():
    if hashlib.sha256((args.input / Path(name).name).read_bytes()).hexdigest() != digest:
        raise ValueError("MANUSCRIPT_FIGURE_CHANGED:" + name)
print("Six original manuscript SVG hashes reproduced exactly.")
