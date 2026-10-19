"""Verify the curated content manifest, numerical anchors, imports and Git objects."""

import argparse
import hashlib
import importlib
import json
import re
import subprocess
from pathlib import Path

from somatoanthropy.aggregate import check_anchors, check_paper_tables

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".py", ".md", ".json", ".toml", ".txt", ".cff", ".csv", ".svg", ".sha256"}
FORBIDDEN_COMPONENTS = {
    "agents.md",
    ".codex",
    ".chatgpt",
    ".env",
    ".aws",
    "correspondence",
    "clearance-register.json",
    "node_modules",
}
FORBIDDEN_EXTENSIONS = {
    ".npz",
    ".npy",
    ".h5",
    ".hdf5",
    ".obj",
    ".ply",
    ".fbx",
    ".model",
    ".pt",
    ".pth",
    ".zip",
    ".pdf",
    ".log",
}
CONTENT_PATTERNS = [
    (
        "personal path",
        re.compile(r"[A-Za-z]:[\\/](?:Users|SomatoSynth3D)|/h[o]me/|/mnt/[a-z]/", re.I),
    ),
    (
        "credential",
        re.compile(
            r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
        ),
    ),
    (
        "provider identifier",
        re.compile(r"\b(?:male_\d{3,}|female_\d{3,}|CSR\d{4}[A-Z]?|SPRING\d{4})\b", re.I),
    ),
]


def scan(name: str, payload: bytes) -> None:
    p = Path(name)
    if (
        any(x.lower() in FORBIDDEN_COMPONENTS for x in p.parts)
        or p.suffix.lower() in FORBIDDEN_EXTENSIONS
    ):
        raise ValueError("UNPERMITTED_RELEASE_PATH:" + name)
    if p.suffix.lower() in {".png", ".svg"} and not re.fullmatch(
        r"results/figures/Figure[1-6]\.(png|svg)", name
    ):
        raise ValueError("UNAPPROVED_FIGURE_PATH:" + name)
    if len(payload) > 2_000_000:
        raise ValueError("UNREVIEWED_LARGE_FILE:" + name)
    if p.suffix.lower() in TEXT_EXTENSIONS or p.name in {".gitignore", ".gitattributes"}:
        text = payload.decode("utf-8-sig")
        for label, pattern in CONTENT_PATTERNS:
            if pattern.search(text):
                raise ValueError("CONTENT_SCAN:" + label + ":" + name)
    if name.startswith("results/aggregate/") and p.suffix == ".json":
        forbidden = {
            "subject_uid",
            "body_uid",
            "fit_uid",
            "source_id",
            "source_path",
            "participant",
            "selection_id",
            "observation_uid",
            "cohort_ids",
        }

        def walk(value):
            if isinstance(value, dict):
                if forbidden.intersection(value):
                    raise ValueError("INDIVIDUAL_FIELD_IN_AGGREGATE:" + name)
                for v in value.values():
                    walk(v)
            elif isinstance(value, list):
                for v in value:
                    walk(v)

        walk(json.loads(payload))


def content_manifest(root: Path) -> dict[str, str]:
    result = {}
    for line in (root / "MANIFEST.sha256").read_text("utf-8").splitlines():
        digest, name = line.split("  ", 1)
        if not re.fullmatch("[a-f0-9]{64}", digest) or name in result:
            raise ValueError("MALFORMED_CONTENT_MANIFEST")
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or path.is_symlink():
            raise ValueError("MANIFEST_PATH_ESCAPES_ROOT")
        result[name] = digest
    for name, digest in result.items():
        data = (root / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("RELEASE_HASH_MISMATCH:" + name)
        scan(name, data)
    return result


def history(root: Path, expected: dict[str, str]) -> int:
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root)

    tracked = set(git("ls-files", "-z").decode().strip("\0").split("\0"))
    if tracked != set(expected) | {"MANIFEST.sha256"}:
        raise ValueError("TRACKED_FILE_SET_DIFFERS_FROM_RELEASE_MANIFEST")
    total = 0
    for line in git("rev-list", "--objects", "--all", "--reflog").decode().splitlines():
        oid, _, name = line.partition(" ")
        kind = git("cat-file", "-t", oid).decode().strip()
        if kind != "blob":
            continue
        if name not in expected and name != "MANIFEST.sha256":
            raise ValueError("UNPERMITTED_HISTORICAL_FILE:" + name)
        data = git("cat-file", "blob", oid)
        scan(name, data)
        if name in expected and hashlib.sha256(data).hexdigest() != expected[name]:
            raise ValueError("UNREVIEWED_HISTORICAL_BLOB:" + name)
        total += 1
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--git-history",
        action="store_true",
        help="Audit all local refs/reflogs; requires the curated Git checkout",
    )
    args = parser.parse_args()
    manifest = content_manifest(ROOT)
    source = json.loads((ROOT / "docs/source_manifest.json").read_text("utf-8"))
    for row in source["modules"]:
        name = (
            row["destination"]
            .removeprefix("src/")
            .removesuffix(".py")
            .replace("/", ".")
            .removesuffix(".__init__")
        )
        importlib.import_module(name)
    anchors, cells = check_anchors(ROOT), check_paper_tables(ROOT)
    result = dict(
        files=len(manifest),
        extracted_modules=len(source["modules"]),
        numerical_anchors=len(anchors),
        reconstructed_display_cells=cells,
        content_scan="passed",
        individual_results_included=False,
    )
    if args.git_history:
        result["historical_blobs_checked"] = history(ROOT, manifest)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
