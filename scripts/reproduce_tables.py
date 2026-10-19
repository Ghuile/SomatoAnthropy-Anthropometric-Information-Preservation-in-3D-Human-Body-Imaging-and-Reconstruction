"""Level 2: preserve the manuscript's display cells and frozen bootstrap intervals."""

import argparse
import csv
from pathlib import Path

from somatoanthropy.aggregate import check_anchors, check_paper_tables, read


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reproduced/tables"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    anchors = check_anchors(root)
    cells = check_paper_tables(root)
    args.output.mkdir(parents=True, exist_ok=True)
    for table in read(root, "paper_tables"):
        (args.output / (table["id"] + ".md")).write_text(table["markdown"], encoding="utf-8")
        with (args.output / (table["id"] + ".csv")).open(
            "w", encoding="utf-8", newline=""
        ) as stream:
            writer = csv.writer(stream)
            writer.writerow(table["columns"])
            writer.writerows(table["rows"])
    print(
        f"8 paper tables; {len(anchors)} numerical anchors; {cells} reconstructed display cells verified."
    )


if __name__ == "__main__":
    main()
