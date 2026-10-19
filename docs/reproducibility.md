# Reproduction levels and executable interfaces

## Level 1: installation and invented fixtures

Follow the README in a clean Python 3.11 environment. The public suite exercises
triangle distances, native control mathematics with an optional invented torch
model, T90 preservation, contours, formula responses, clustered statistics,
dataset transforms, linkage and missingness. It needs no licensed participant
files. Optional native/comparator tests skip when their distributions are absent.
`python -m ruff check .` and `python -m ruff format --check .` check the release.
No type checker is configured. `python -m pip check` checks the base/review tier.

## Level 2: frozen aggregates

`python scripts/reproduce_tables.py --output reproduced/tables` writes Markdown
and CSV for Tables 1–5 and S1–S3. `paper_tables.json` preserves exact manuscript
labels and rounding. Machine-readable detail tables preserve original precision,
confidence intervals and denominators. `aggregate.py` compares numerical anchors
and reconstructs display cells from these detailed tables. Original manuscript
and input hashes are recorded in `aggregate_manifest.json`.

`python scripts/reproduce_figures.py --output reproduced/figures` produces six
PNG/SVG aggregate illustrations plus captions, input IDs and output hashes:

| Output | Inputs and interpretation |
|---|---|
| Figure 1 | Study architecture and cohort dependencies; schematic |
| Figure 2 | Source/native/T90 workflow schematic and E1 paired NOMO surface means/intervals; no body images |
| Figure 3 | E2-1/E2-2 extent ratios, fidelity change and cross-path RMS change |
| Figure 4 | E3 common-measurement SD and range with original person-bootstrap intervals; an aggregate companion to the manuscript, not an individual scatter plot |
| Figure 5 | WAIST P/B1/offset comparisons and S1 actual/source/constructed-height response comparison |
| Figure 6 | S2 conditional policy trade-offs for the 149-person and strict 103-person groups |

These commands reproduce saved aggregate values and their visualisation. They do
not independently refit bodies, reconstruct missing participant observations or
rerun bootstraps from aggregate tables. Charts are reviewer companions; they are
not claimed to be pixel-identical to every manuscript panel. No body-render panel
or residual map from the earlier Figure 2 is included.

## Level 3: separately licensed inputs

First inspect availability without running analysis:

```text
python scripts/licensed_pipeline.py check --manifest configs/licensed_inputs.example.json
python scripts/licensed_pipeline.py --help
```

The example correctly reports `ready: false`. Copy it to an ignored local JSON
file and configure `input_root`, `files` (relative file path to SHA-256), `sources`
(experiment name to frozen record folder), and `aggregate_sources` (experiment
name to original table folder). `seed_records` maps an output record name to its
pinned input file, for analyses requiring saved prerequisites. Every consumed
input must remain within the declared root. Use a new output directory for each
operation; differing existing outputs are rejected.

The following actions are implemented. Supplying an action without `--execute`
only checks availability. Running one requires an explicit `--execute`, licensed
inputs and, where relevant, the separate native/comparator environment. Real-data
native fitting/regeneration was not run as part of release preparation.

| Action | Additional manifest keys and input schema |
|---|---|
| `geometry` | `geometry_records`: list of E1 records described in datasets.md, each with `record_id`, `subject_uid` and `evaluation_seed` |
| `repeated` | `repeated_records`: six `subject_uid`, `observation_uid`, `canonical_mesh` records/person; NPZ `vertices` in engineering metres and indexed `faces` |
| `waist` | `waist_records`, `atlas`, `region_masks`; records match the fields consumed by `experiments/waist01/measure.py:one`; saved mesh, skeleton, atlas, region and source-reference attachments are required |
| `continue-controls` | `native_jobs`, `native_seed`; each job has `job_id`, `parameters`, `policy` (B/C/D or E2-2 policy key), `source_mesh`, `source_to_working`, `initial_translation`; uses LOD1 and the frozen continuation |
| `replay` | `native_jobs`, `native_seed`, `t90_reference`; each job supplies `job_id`, `parameters`, `initial_translation`; regenerates LOD0 fitted and T90 geometry through native MHR |
| `e5` | Saved E5 `catalogue.json` and `controls.json` as seed records; E1/E2/E3/E4/WAIST-01 source mappings used by the original analysis functions |
| `e5s1` | E5 `catalogue.json`, E4 `cohorts.json`, WAIST-01 `paired.json`, `e5-long.json`, `measurements.json`, E5 `source-agreement.json`, E1 `e5-method-records.json` and frozen source attachments, via experiment mappings |
| `e5s2` | E5-S1 `cohort.json`, E5 `catalogue.json`, WAIST-01 `measurements.json`; saved `height-qualification.json` as a seed record; original height qualification must be supplied |

Read each retained function's record-key accesses for the complete attachment
schema; the release does not fabricate substitute participant ledgers. Source
versions are fixed in `evidence_versions.json`. A check validates declared files,
not scientific eligibility or completeness of an arbitrary user manifest.

The staged original fitter is also callable as
`geometry.mpii_mhr_fit01.fit.optimise(model, names, faces, source, source_faces, config, output)`.
E2-1 evaluation, E2-2 analysis, E4 paired analysis and E3 measurement extraction
are reusable Python functions. The release is not a universal automated ingestion
or historical batch launcher. Full exact historical recomputation additionally
needs the non-distributed selection/linkage records, saved native inputs,
measurement atlas/masks and compatible external runtimes.

Release validation recomputed E5-S1/S2 tables and E3 statistics locally against
frozen records without new fitting. See `validation.json` for measured scope.
Licensed-data entry-point syntax and default checks are tested; native execution
is conditional and was not validated against real model assets in the clean
public environment.


The 0.2.0 [audit update](audit-update.md) supersedes prior unresolved project-licence and Figure 2 statements: project-owned release material is CC BY 4.0 with LSBU approval reported by the lead author. Current manuscript Figure 2 has no participant imagery. Dataset restrictions and excluded historical imagery remain unchanged.


## Native template mechanism illustration

With the pinned official native runtime and locally supplied LOD0 atlas/masks:

```text
python scripts/render_mhr_template.py --model-root local_model_root --atlas local/atlas.json --region-masks local/region-masks.npz --output reproduced/template
```

The model root must contain the assets/mhr/v1 layout described in configs/model_hashes.json. Install the official compatible MHR/PyMomentum runtime separately; review dependencies alone do not provide it. This command has been exercised with the recorded native runtime. It generates only zero-identity/zero-expression native template bodies, at neutral and each separate authored bound. No participant parameters, meshes, fitted poses or study data are accepted. The illustration uses the authored zero articulation, not the study's T90 transfer. Generic local atlas attachments define P and offset sites; B1 uses the pinned 61%-height plane. Local attachment hashes, control labels and template plane heights are saved, with no participant provenance fields. See the MHR Apache-2.0 asset notice in third_party/.

## Local audit-statistic replay

recompute_agreement.py takes an authorised local JSON list with dataset, pathway, state, site, method, unit, and source/target numeric arrays (one pair/person). It writes aggregate CCC, Pearson r and descriptive Bland–Altman limits. recompute_small_n.py takes contrast, seed and differences (one difference/person), invoking the original 2000-draw paired bootstrap. Both require --input and a new --output path. Neither publishes input arrays. These CLI routes were checked with clearly invented values; the release contains no real person arrays. Exact published small-n interval recomputation additionally requires the licensed original vectors in frozen order and the original seed.
