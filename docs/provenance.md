# Source and result provenance

`source_manifest.json` identifies the source revision, dirty-tree status, exact
source bytes, selected definitions and extraction adaptations for each module.
The revision alone is insufficient: several completed experiment sources were
uncommitted, so individual SHA-256 pins identify the actual inspected bytes.
No source Git history is copied into this repository.

The extraction preserves the selected definition ASTs, renames the package,
removes unused imports/definitions and normalises formatting. The E1 HDF5 branch
uses the normally installed optional dependency instead of a machine-specific
import overlay. `workflow.RecordStore` supplies explicit local roots and pinned
input readers instead of original workspace discovery. The two E3 portable loops
retain computational statements while replacing file/cache handling; their
original source hashes and replay evidence are in `validation.json`.

New release glue comprises `aggregate.py`, `reconstruction.py`, `repeated.py`,
`workflow.py`, the four scripts and integration/dataset-engineering tests. It
provides packaging, local input configuration, frozen-output verification and
aggregate visualisation. It does not introduce a new fitted population.
Original test source hashes are retained in `test_provenance.json`.

`evidence_versions.json` pins the twelve authoritative reports used by the
manuscript and supplement. Reports themselves contain material outside this
release's scope and are not copied. `aggregate_manifest.json` records table
projections, source/result hashes and row counts. Missingness, adverse results,
original confidence intervals and denominators are retained.

One historical provenance gap remains: the reconciliation report records that
E4's historical CLI and report-generator source hashes differ from the currently
available files. Those exact historical entry-point bytes were unavailable.
The released numerical E4 functions are identified by their own current hashes;
this repository does not claim to recover the missing CLI/report revision.
Saved E4 outputs retain their original hashes and intervals. The reconciliation
report predates completed E5 work; its earlier deferral is not a later result.

`MANIFEST.sha256` lists every distributed file except itself. The verifier checks
hashes, permitted paths/content, imports and numerical anchors. In the curated
Git checkout, `--git-history` also verifies tracked files and all reachable or
reflog-referenced blobs. This is a bounded release audit, not a guarantee against
all possible future sensitive additions. Regenerate and review the manifest
before any later publication.
