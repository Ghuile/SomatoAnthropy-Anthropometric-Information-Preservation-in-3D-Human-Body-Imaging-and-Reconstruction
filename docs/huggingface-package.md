# Private Hugging Face companion

The companion is prepared locally. The builder performs no upload, creates no
remote repository and changes no remote visibility. Keep the package and any
future Hub repository private until the author authorises publication.

```text
python scripts/prepare_huggingface.py --source-commit FULL_GITHUB_COMMIT_SHA --output reproduced/huggingface --archive reproduced/huggingface-private.zip
python scripts/prepare_huggingface.py --verify reproduced/huggingface
python reproduced/huggingface/examples/check_invented.py
```

Use the exact source commit of this software checkout. Both output destinations
must be new. The package contains all 47 canonical aggregate JSON tables and six
scalar CSV exports: E2-2 extent statistics, waist fallback counts, canonical
fallback strata, NOMO selection counts and two descriptive agreement tables.
Each CSV has its own dataset configuration; their aggregate split is a set of
summary rows, not a new participant split. Blank CSV cells denote null values;
canonical JSON remains authoritative for types, precision and nested values.

The dataset card documents populations, provider categories, linked dependence,
engineering units, response pp, uncertainty and limitations. Data dictionaries,
source SHA-256 receipts, the matching GitHub commit, six approved manuscript
vectors, a generic template illustration and upstream notices accompany it.
The invented example has four artificial length pairs and uses no model assets.

Only the explicit package allowlist is copied. Extra files in the source
workspace do not enter it. Source and package manifests, exact CSV/JSON equality,
content scans and archive bytes are verified. The builder rejects existing
destinations; it never replaces a package or input record.

Participant records, per-person vectors, private manifests, meshes, fitted
participant parameters, model binaries, credentials, correspondence and private
paths are excluded. Aggregate statements about cohorts do not expose membership.
Dataset provider terms remain separate from project licences. The package is an
aggregate companion, with no individual-level fitting or clinical ground truth.

Project-owned data/docs are CC BY 4.0; the invented example code is MIT.
Template-derived illustrations retain their MHR Apache-2.0 asset notice.
The existing v0.2.0 tag/archive and deferred Zenodo status are preserved.
