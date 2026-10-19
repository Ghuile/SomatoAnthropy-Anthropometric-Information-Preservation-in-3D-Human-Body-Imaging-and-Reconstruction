"""Prepare a private aggregate companion; no network or upload operation exists."""

import argparse
import csv
import hashlib
import io
import json
import re
import runpy
import subprocess
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/Ghuile/SomatoAnthropy-Anthropometric-Information-Preservation-in-3D-Human-Body-Imaging-and-Reconstruction"
DATASET = "https://huggingface.co/datasets/Ghuile/SomatoAnthropy-Anthropometric-Information-Preservation-in-3DHumanBody-Imaging-and-Reconstruction"
DOCUMENTS = (
    "docs/data_dictionary.json",
    "docs/data-dictionary.md",
    "docs/aggregate_manifest.json",
    "docs/datasets.md",
    "docs/claim-pipelines.md",
    "docs/claim-pipeline-provenance.json",
    "docs/third_party.md",
    "docs/audit-update.md",
    "docs/manuscript-figure-provenance.json",
    "configs/control_audit_204.json",
    "third_party/MHR-assets-Apache-2.0.txt",
    "third_party/MHR-code-Apache-2.0.txt",
    "third_party/clad-body-Apache-2.0.txt",
    "LICENSES/MIT.txt",
    "LICENSES/CC-BY-4.0.txt",
)
CSV_TABLES = (
    "E2-2-height-all-arms",
    "waist-fallback-counts",
    "canonical-fallback-strata",
    "NOMO-cohort-selection",
    "agreement-extent-waist",
    "agreement-waist-methods",
)
EXAMPLE = '''"""Entirely invented lengths; no participant records or model assets."""
# SPDX-License-Identifier: MIT
import json
from pathlib import Path
from statistics import mean, stdev

source = [150.0, 160.0, 170.0, 180.0]
target = [152.0, 162.0, 172.0, 182.0]
actual = dict(n=4, bias_cm=mean(b-a for a,b in zip(source,target)),
              mae_cm=mean(abs(b-a) for a,b in zip(source,target)),
              sd_ratio=stdev(target)/stdev(source))
expected = json.loads(Path(__file__).with_name("invented_expected.json").read_text("utf-8"))
assert actual == expected
print(json.dumps(actual, sort_keys=True))
'''


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode()


def checksum(payload):
    return hashlib.sha256(payload).hexdigest()


def table_csv(rows):
    """Export scalar aggregate rows, retaining nulls as blank CSV cells."""
    if not rows or not all(isinstance(r, dict) for r in rows):
        raise ValueError("SCALAR_AGGREGATE_ROWS_REQUIRED")
    columns = list(dict.fromkeys(k for row in rows for k in row))
    if any(isinstance(v, (dict, list)) for row in rows for v in row.values()):
        raise ValueError("NESTED_VALUES_REMAIN_IN_CANONICAL_JSON")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, columns, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: str(v).lower() if isinstance(v, bool) else v for k, v in row.items()})
    return stream.getvalue().encode("utf-8")


def dataset_card(commit, tables):
    metadata = dict(
        pretty_name="SomatoAnthropy — aggregate evidence and invented examples",
        license="cc-by-4.0",
        tags=["tabular", "3d", "anthropometry", "reproducibility", "aggregate-statistics"],
        configs=[
            dict(config_name=name, data_files=[dict(split="aggregate", path=path)])
            for name, path in tables.items()
        ],
    )
    front = "---\n" + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True) + "---\n\n"
    return (
        front
        + f"""# SomatoAnthropy companion dataset

Prepared locally for private review. This package has not been uploaded by its
builder. Keep any remote repository private until publication is authorised.

## Contents and provenance

This is an aggregate research companion with 47 canonical JSON tables, six
convenience CSV tables, a data dictionary, approved illustrations, complete
model-control metadata and an entirely invented example. It contains no
participant records, meshes, fitted participant parameters, individual vectors,
private cohort membership, model binaries or private correspondence.

Source software snapshot: [{commit}]({REPOSITORY}/commit/{commit}).
The intended companion location is [Hugging Face]({DATASET}); this link does not
assert that files are available there. SOURCE.json records the source release
manifest hash and every copied file's hash. MANIFEST.sha256 covers package bytes.

## Populations and dependence

The frozen NOMO selection retains 109 original people, adds one replacement
and 40 additional people: 150 distinct people with provider female/male source
labels of 80/70. These labels are not independently validated biological sex.
The complete paired waist analysis uses 149 people and 298 canonical pathway
observations. E2-2 mechanism arms use four development people; heldout B/C rank
comparisons use 12 people. Pathways, states and repeated observations remain
linked within person. Table-specific denominators take precedence; rows are
aggregate statistics and do not constitute a participant-level dataset.

## Units, fields and uncertainty

See docs/data-dictionary.md and docs/data_dictionary.json for all 47 tables and
their fields. Engineering cm/m are saved working-frame lengths. Equation-response
pp denote changes in q = -20H/W with an arbitrary zero; they are not body-fat
measurements. Correlations and SD ratios are dimensionless. The source reference
shares mapped anchors and is not independent clinical ground truth. Frozen
bootstrap intervals and descriptive Bland–Altman limits are distinct.

The six CSV configurations are named by their source table. Their `aggregate`
split contains summary rows, not a new train/test split. Blank CSV cells denote
null; boolean cells use true/false. Canonical JSON retains original types,
precision, nested intervals and all unflattened tables. No split membership,
selection or uncertainty interval is regenerated by packaging.

## Use and limitations

Use this material to inspect published aggregate claims, compare definitions and
run software demonstrations. It does not permit reconstructing individual ranks
from marginal tables, rerunning participant fitting, clinical diagnosis or
establishing physiological validity. Development arm results remain exploratory.
Dataset source access and retained engineering interfaces are in docs/datasets.md.
Obtain source data from the providers under their terms; no access is granted here.

## Quick checks

```text
python examples/check_invented.py
```

The example uses four explicitly invented length pairs and checks their known
bias, mean absolute difference and SD ratio. It uses only the Python standard
library. Aggregate replay and full package verification are supplied by the
matching GitHub software snapshot; see PACKAGE.md for exact commands.

## Licensing and citation

Project-owned aggregate data, documentation and original illustrations: CC BY 4.0
(LICENSE and LICENSES/CC-BY-4.0.txt). Invented example code: MIT
(LICENSES/MIT.txt). MHR-derived control metadata and template illustrations retain
the upstream MHR notices in third_party/. No third-party dataset is relicensed.
The earlier v0.2.0 release's permissions remain unchanged.

Please cite CITATION.cff and the accompanying manuscript. No published Zenodo
archive or registered archive DOI is asserted. Zenodo archival remains deferred.
"""
    )


def build_package(root: Path, output: Path, commit: str, archive: Path | None = None):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("FULL_SOURCE_COMMIT_REQUIRED")
    if output.exists() or (archive is not None and archive.exists()):
        raise FileExistsError("Choose new package and archive paths")
    if (root / ".git").exists():
        actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        if actual != commit:
            raise ValueError("SOURCE_COMMIT_DOES_NOT_MATCH_CHECKOUT")
    verifier = runpy.run_path(str(root / "scripts/verify_release.py"))
    source_manifest = verifier["content_manifest"](root)
    aggregate = json.loads((root / "docs/aggregate_manifest.json").read_text("utf-8"))
    names = [r["file"] for r in aggregate]
    if len(names) != 47 or len(set(names)) != 47:
        raise ValueError("FROZEN_47_TABLE_SET_REQUIRED")
    if any(not re.fullmatch(r"results/aggregate/[A-Za-z0-9_-]+\.json", n) for n in names):
        raise ValueError("AGGREGATE_PATH_NOT_ALLOWED")
    illustrations = [f"results/manuscript-figures/Figure{i}.svg" for i in range(1, 7)]
    illustrations.append("results/template/template-controls.png")
    copies = list(DOCUMENTS) + names + illustrations
    payloads, receipts = {}, {}
    for name in copies:
        if name not in source_manifest:
            raise ValueError("UNMANIFESTED_PACKAGE_INPUT")
        payloads[name] = (root / name).read_bytes()
        receipts[name] = source_manifest[name]
    tables = {}
    for name in CSV_TABLES:
        source = f"results/aggregate/{name}.json"
        path = f"data/tables/{name}.csv"
        payloads[path] = table_csv(json.loads(payloads[source]))
        tables[name] = path
    payloads["LICENSE"] = payloads["LICENSES/CC-BY-4.0.txt"]
    payloads["README.md"] = dataset_card(commit, tables).encode("utf-8")
    payloads["docs/licensing.md"] = f"""# Companion package licence scope

Project-owned aggregate data, research documentation and original illustrations:
CC BY 4.0, in ../LICENSE and ../LICENSES/CC-BY-4.0.txt.
Invented example code: MIT, in ../LICENSES/MIT.txt.
MHR-derived control metadata and template illustrations retain the MHR notices
in ../third_party/.
No source dataset, model binary or participant record is supplied or relicensed.

The source software's separate scope is documented in
[the matching GitHub snapshot]({REPOSITORY}/blob/{commit}/docs/licensing.md).
Historical CC BY permissions remain available. Preparing this private companion
does not publish it or change remote access settings.
""".encode()
    payloads["NOTICE"] = (
        "Project-owned data/documentation: CC BY 4.0. Invented example code: MIT.\n"
        "Copyright (c) 2026 Vasileios Nikolaou, Daqing Chen and Perry Xiao.\n"
        "MHR-derived control metadata and template illustrations retain MHR notices.\n"
        "Source datasets are excluded and are not relicensed. See README.md and LICENSES/.\n"
    ).encode()
    payloads["examples/check_invented.py"] = EXAMPLE.encode()
    payloads["examples/invented_expected.json"] = encoded(
        dict(n=4, bias_cm=2.0, mae_cm=2.0, sd_ratio=1.0)
    )
    payloads["SOURCE.json"] = encoded(
        dict(
            repository=REPOSITORY,
            commit=commit,
            release_manifest_sha256=checksum((root / "MANIFEST.sha256").read_bytes()),
            copied_source_sha256=receipts,
            aggregate_tables=47,
            csv_tables=tables,
            participant_data_included=False,
            model_binaries_included=False,
            uploaded=False,
            preparation_status="local private package; no remote visibility changed",
        )
    )
    payloads["PACKAGE.md"] = f"""# Package verification

Use the matching GitHub commit {commit} and its review environment:

```text
python scripts/prepare_huggingface.py --verify PATH_TO_THIS_PACKAGE
```

Verification checks the complete file set, SHA-256 hashes, content scan, original
aggregate schema, CSV/JSON values and source table counts. To reproduce the
claim display from the source software checkout:

```text
python scripts/reproduce_audit_claims.py frozen --output reproduced/claims.json
```

The package builder has no network or upload operation. Keep this package and
any future Hub repository private until publication is authorised. Source input
hashes and the exact software commit are in SOURCE.json. Figures are the
approved aggregate/schematic vectors and generic template illustration; no
participant-derived imagery is included. Reproduction of fitting requires
separately authorised inputs and is outside this package.
""".encode()
    citation = yaml.safe_load((root / "CITATION.cff").read_text("utf-8"))
    citation.update(type="dataset", version=f"0.2.0-companion.{commit[:12]}", license="CC-BY-4.0")
    citation["message"] = "Please cite the accompanying manuscript and matching GitHub snapshot."
    citation["abstract"] = "Aggregate research evidence and invented examples; no participant data."
    payloads["CITATION.cff"] = yaml.safe_dump(citation, sort_keys=False).encode()
    for name, payload in payloads.items():
        verifier["scan"](name, payload)
    payloads["MANIFEST.sha256"] = "".join(
        f"{checksum(payloads[n])}  {n}\n" for n in sorted(payloads)
    ).encode()
    output.mkdir(parents=True, exist_ok=False)
    for name, payload in payloads.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(payload)
    result = verify_package(root, output)
    if archive is not None:
        archive.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
            for name in sorted(payloads):
                entry = zipfile.ZipInfo(name, date_time=(2026, 10, 19, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                bundle.writestr(entry, payloads[name])
        with zipfile.ZipFile(archive) as bundle:
            if set(bundle.namelist()) != set(payloads) or any(
                bundle.read(n) != p for n, p in payloads.items()
            ):
                raise ValueError("ARCHIVE_CONTENT_MISMATCH")
        result["archive_sha256"] = checksum(archive.read_bytes())
    return result


def verify_package(root: Path, package: Path):
    verifier = runpy.run_path(str(root / "scripts/verify_release.py"))
    original = verifier["content_manifest"](root)
    manifest = verifier["content_manifest"](package)
    present = {p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file()}
    if present != set(manifest) | {"MANIFEST.sha256"}:
        raise ValueError("PACKAGE_FILE_SET_MISMATCH")
    source = json.loads((package / "SOURCE.json").read_text("utf-8"))
    if source["release_manifest_sha256"] != checksum((root / "MANIFEST.sha256").read_bytes()):
        raise ValueError("MATCHING_SOURCE_SNAPSHOT_REQUIRED")
    names = {
        r["file"] for r in json.loads((root / "docs/aggregate_manifest.json").read_text("utf-8"))
    }
    copied = (
        set(DOCUMENTS)
        | names
        | {
            *(f"results/manuscript-figures/Figure{i}.svg" for i in range(1, 7)),
            "results/template/template-controls.png",
        }
    )
    generated = {
        "LICENSE",
        "README.md",
        "NOTICE",
        "SOURCE.json",
        "PACKAGE.md",
        "CITATION.cff",
        "MANIFEST.sha256",
        "docs/licensing.md",
        "examples/check_invented.py",
        "examples/invented_expected.json",
        *(f"data/tables/{n}.csv" for n in CSV_TABLES),
    }
    if present != copied | generated or set(source["copied_source_sha256"]) != copied:
        raise ValueError("PACKAGE_ALLOWLIST_MISMATCH")
    if any(
        source["copied_source_sha256"][n] != original[n] or manifest[n] != original[n]
        for n in copied
    ):
        raise ValueError("PACKAGE_SOURCE_HASH_MISMATCH")
    if (
        source["participant_data_included"]
        or source["model_binaries_included"]
        or source["uploaded"]
    ):
        raise ValueError("PACKAGE_SCOPE_MISMATCH")
    tables = list((package / "results/aggregate").glob("*.json"))
    if len(tables) != 47:
        raise ValueError("PACKAGE_TABLE_COUNT_MISMATCH")
    for path in tables:
        name = path.relative_to(package).as_posix()
        if checksum(path.read_bytes()) != source["copied_source_sha256"][name]:
            raise ValueError("PACKAGE_SOURCE_HASH_MISMATCH")
    for name, csv_path in source["csv_tables"].items():
        rows = json.loads((package / f"results/aggregate/{name}.json").read_text("utf-8"))
        if (package / csv_path).read_bytes() != table_csv(rows):
            raise ValueError("CSV_AND_JSON_DISAGREE")
    return dict(
        files=len(present),
        aggregate_tables=47,
        csv_tables=len(source["csv_tables"]),
        content_scan="passed",
        uploaded=False,
        commit=source["commit"],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify is not None:
        if args.output is not None or args.source_commit is not None or args.archive is not None:
            parser.error("--verify is a separate operation")
        result = verify_package(ROOT, args.verify)
    else:
        if args.output is None or args.source_commit is None:
            parser.error("preparation requires --source-commit and --output")
        result = build_package(ROOT, args.output, args.source_commit, args.archive)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
