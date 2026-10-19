"""Replay the frozen participant bootstrap from authorised local paired differences."""

import argparse
import json
from pathlib import Path

from somatoanthropy.data.phase01_nomo import atomic_json
from somatoanthropy.experiments.e2_1.analysis import paired_summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Local JSON list: contrast, seed, differences (one number/person)",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [
        dict(
            contrast=row["contrast"],
            seed=row["seed"],
            **paired_summary(row["differences"], row["seed"]),
        )
        for row in json.loads(args.input.read_text(encoding="utf-8"))
    ]
    atomic_json(args.output, rows)
    print(
        f"{len(rows)} participant-bootstrap summaries written; no individual differences exported."
    )


if __name__ == "__main__":
    main()
