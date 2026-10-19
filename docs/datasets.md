# Dataset interfaces and data engineering

The release retains the data processing that determines the scientific result.
It excludes acquisition credentials, migration utilities and participant ledgers.
Obtain data from each provider under its applicable terms; this repository grants
no dataset access or redistribution rights.

| Family and provider | Retained interface and interpretation |
|---|---|
| [MPII Human Shape](https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/software-and-datasets/humanshape), v1.0 | `data/mpii_humanshape/loader.py` parses points and template topology. E1 selects the saved CAESAR variant, applies `source_to_working`, and restores the fitted translation. Provider code and dataset have distinct conditions. |
| [UCSC Body Models](https://graphics.soe.ucsc.edu/data/BodyModels/index.html) | OBJ parsing plus the saved source-to-working matrix. No new scale or alignment is estimated during evaluation. |
| [NOMO](https://zenodo.org/records/5172126), v3 | OBJ parsing; linked SMPL-NICP and CAESAR-NICP representations; saved 4x4 transforms and independent native candidates. Historical SMPL-LBFGSB is a wholly overlapping subset. |
| [HIT](https://hit.is.tue.mpg.de/index.html) | Prepared source NPZ; saved source rotation; native centimetres converted to metres with the original fitting translation. The saved neutral-state exception is retained when interpreting historical outputs. |
| [FAUST](https://faust.is.tue.mpg.de/) | PLY archive-member parsing without mesh processing; member SHA-256; saved transforms. |
| [D-FAUST](https://dfaust.is.tue.mpg.de/) | HDF5 container/key/zero-based frame; container SHA-256; indexed faces and saved transforms. Sequence, frame and participant linkage are distinct. Requires optional h5py. |
| [HBW](https://shapy.is.tuebingen.mpg.de/datasets.html) | Prepared source NPZ; native fitted centimetres converted to metres. Image or scan access is arranged with the provider. |
| [NHANES](https://www.cdc.gov/nchs/nhanes/) | Optional numerical conditioning only: accepted 2005–2006 training membership, five linked panels, observed-value/missing-cause rules and deterministic selection. No observed source surface exists. |

All seven geometric branches are implemented in `experiments/e1/inputs.py`.
`pair_meshes(store, record)` returns source and fitted vertices/faces plus unit,
LOD and alignment metadata. `canonical_mesh` handles the saved canonical unit
convention. Records must declare `dataset`, `surface_eligible`, `lod`, `unit`,
`fitted_mesh` and the family-specific source keys consumed by these functions.
An ineligible source surface raises an error; it is not replaced or imputed.

`workflow.RecordStore` resolves explicit local paths, rejects root escapes and
verifies SHA-256. When its `input_pins` mapping is nonempty, every consumed input
must be pinned. NPZ loading disables pickle. Keep local configuration in an
ignored `*.local.json` file. A record can contain a provider-local identifier,
but such records and the generated individual outputs must stay local.

`data/identity.py` preserves the dataset namespace; `data/phase01_nomo.py` and
`production/DFAUST_FIT07/core.py` derive stable linked identifiers. These are
pseudonyms, not anonymisation: never publish them as a privacy measure. A family
namespace does not prove independence between different datasets.
`experiments/e4/inputs.py` rejects duplicate linkage, mismatched participants,
incorrect representation pairings and a reused native candidate.

The optional NHANES `eligible_profile` and `choose` functions live in
`geometry/fit09_nhanes_mhr/source.py`. They retain the original two-category,
five-per-category selection rule, observed positive targets and panel agreement.
They do not create a train/test split or perform the prior acceptance/quarantine
review. Supply that frozen membership separately. Missing comment fields retain
their coded cause; missing targets, age or source category are not assigned.

The historical cohorts are fixed inputs, not outputs of a fresh random selection.
No original participant manifests, model parameters, meshes, topology assets,
atlases or masks are distributed. Unit and axis conversion tests use invented
triangles; identity and missingness tests use invented records. Source hashes
and retained definitions are listed in `source_manifest.json`.

## Historical cohort and candidate selection

The pure selectors are retained for inspection and replay on an already eligible
inventory. Calling a selector grants no fitting authority and does not replace a
frozen study manifest. No real cohort is selected during release verification.

| Module | Retained rule |
|---|---|
| `production/MPII_MHR_FIT01/prepare.py:select` | Historical protected MPII selection: height deciles and hash ordering, 100 additional records; this specific historical rule is not a new default population budget. |
| `production/UCSC_MHR_FIT02/prepare.py:select` | Recorded source categories and height deciles; exclude existing identities; at most 50 additional eligible people. |
| `production/NOMO_PAIRED_NICP/core.py:select_additional` | Frozen paired study: balance recorded source groups and hash order; exclude retained people; default 40 additions. |
| `production/HIT_MHR_FIT05/core.py:choose` | Training split, provider category/path consistency, duplicate rejection and balanced deterministic ordering. |
| `production/FAUST_FIT06/core.py:select_candidates` | Select among completed candidates only after native replay, human review and technical/measurement qualification; stable lexicographic ranking. |
| `production/DFAUST_FIT07/frame60.py:select_panel` | Retain pilot fits exactly; six observations per person; early baseline candidate and distinct motion midpoints; no repeated-frame padding or inferred timestamps. |
| `geometry/hbw_mhr_fit08/selection.py:select` | Exactly ten distinct validation families; reject test/relabelled splits. |
| `production/NHANES_FIT09/prepare.py:stratified_selection` | Exclude existing families; source-category allocation and deterministic diversity in four observed targets; repeated imputations remain one person. |

These functions consume provider metadata and prior qualification decisions; they
do not replace the provider's access process, private linkage or scientific
review. Tests exercise order independence, split exclusion, pilot reuse and
identity uniqueness with invented inventories.
