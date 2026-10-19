"""Recompute descriptive agreement from separately authorised local person pairs."""

import argparse
import json
from pathlib import Path

from somatoanthropy.agreement import agreement
from somatoanthropy.data.phase01_nomo import atomic_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Local JSON list of labelled series; each has source and target numeric arrays, one pair/person",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for row in json.loads(args.input.read_text(encoding="utf-8")):
        labels = {
            key: row[key] for key in ("dataset", "pathway", "state", "site", "method", "unit")
        }
        rows.append(dict(labels, **agreement(row["source"], row["target"])))
    atomic_json(args.output, rows)
    print(f"{len(rows)} descriptive agreement series written; individual pairs remain local.")


if __name__ == "__main__":
    main()
