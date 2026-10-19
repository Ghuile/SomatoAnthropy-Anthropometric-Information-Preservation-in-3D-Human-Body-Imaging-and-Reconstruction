# SomatoAnthropy

**Anthropometric Information Preservation in 3D Human-Body Imaging and Reconstruction**

## Overview

SomatoAnthropy studies what native MHR reconstruction preserves from existing body
surfaces. Its three contributions are a matched skeletal-control intervention,
definition-aware measurement and repeated-observation evaluation, and an analysis
of how height and waist policies affect derived equation responses.

The study distinguishes source fidelity, retained between-person variation,
cross-path consistency and within-person stability. Its simple offset waist
baseline and adverse findings remain part of the comparison.

## Repository contents

`src/somatoanthropy` contains selected research implementations; `configs` pins
scientific settings; `results/aggregate` contains frozen, participant-free result
tables. `tests` uses explicitly invented fixtures. Provenance and dependency
records are in `docs` and `environment`.

## Quick start

Use Python 3.11 in a fresh virtual environment. From this checkout:

```text
python -m venv .venv
```

Activate it (`.venv\Scripts\Activate.ps1` in PowerShell, or
`source .venv/bin/activate` on Linux/macOS), then:

```text
python -m pip install -e ".[review]"
python -m pytest
python scripts/verify_release.py
python scripts/reproduce_tables.py --output reproduced/tables
python scripts/reproduce_figures.py --output reproduced/figures
```

## Reproducing the paper

The table command reconstructs Tables 1–5 and S1–S3 with the manuscript's saved
rounding. The figure command plots the frozen aggregate values supporting
Figures 3–6; Figure 1 is the study diagram. Each output records its source table
and estimand. Figure 2 is the current workflow diagram and aggregate fidelity plot, with no participant body panels. Historical participant-derived panels remain excluded.
See [the output mapping](docs/reproducibility.md).

## Dataset access

Full-data work requires separately authorised source datasets, MHR assets,
frozen participant manifests, saved transforms and measurement attachments.
These are absent from this checkout. [Dataset interfaces and access](docs/datasets.md)
describe the seven surface families and separate NHANES conditioning interface.

## Reproducibility scope

Level 1 tests mathematical, geometric and software invariants without participant
data. Level 2 reconstructs tables and figures from frozen aggregates; it does
not rerun fitting or participant bootstraps. Level 3 exposes the licensed-data
methods and validates locally supplied inputs. The original private manifests
and external model runtime remain necessary for full historical recomputation.

## Citation and dependencies

Vasileios Nikolaou, Daqing Chen and Perry Xiao. *SomatoAnthropy: Anthropometric
Information Preservation in 3D Human-Body Imaging and Reconstruction*.
Research manuscript for Sensors; see [CITATION.cff](CITATION.cff).

MHR and clad-body are version-pinned external dependencies. Their software
licences do not settle participant-data or figure rights. See
[third-party notices](docs/third_party.md).

## Availability

This repository provides research source and aggregate verification material.
Raw datasets, participant records, source-derived meshes, model binaries and
private correspondence are excluded. GitHub remains private and Zenodo archival is deferred. Project-owned software is licensed under MIT; research documentation and aggregate data are CC BY 4.0. See [licence scope](docs/licensing.md). Third-party and dataset terms remain separate.

A companion dataset is planned at [Hugging Face](https://huggingface.co/datasets/Ghuile/SomatoAnthropy-Anthropometric-Information-Preservation-in-3DHumanBody-Imaging-and-Reconstruction). Its dataset card will describe the released contents and access conditions when available.

## Claim audit pipelines

The [claim-to-pipeline guide](docs/claim-pipelines.md) maps the Spearman, fallback,
cohort-selection, provider-category, mechanism-arm and zero-domain statements to
their data and implementations. The complete [204-control audit](configs/control_audit_204.json)
includes excluded controls and their authored bounds.

```text
python scripts/reproduce_audit_claims.py frozen --output reproduced/audit/claims.json
```

This public route checks the published summaries. The guide also gives the
licensed-record replay and native model-metadata audit routes; they export only
aggregate results or model metadata and perform no fitting.

## Audit evidence and manuscript figures

See the [audit update](docs/audit-update.md), [register reports](docs/experiments/REGISTER.md),
[data dictionary](docs/data-dictionary.md) and [changelog](CHANGELOG.md).
The current manuscript's Figure 2 is a workflow and aggregate plot. Figure 6 is a
projection of saved three-objective memberships; it displays six policies per panel
and retains membership from the complete nine-policy grid.

```powershell
python scripts/reproduce_manuscript_figures.py --output reproduced/manuscript
python scripts/check_manuscript_figures.py --input reproduced/manuscript
```

The manuscript SVG route reproduces the six original editorial vectors exactly.
The existing reproduce_figures.py command generates companion plots. CI runs tests,
release verification and both routes on every push. The repository remains private.
Zenodo archival is deferred by the authors. A DOI was reserved in an unpublished
draft, but no archive was uploaded and no DOI has been registered. Cite the
versioned GitHub release for now; see [release status](docs/release-status.json).

## Preparing the private Hugging Face companion

The package builder copies only explicitly curated aggregates, documentation,
approved illustrations and invented examples, and writes checksums and source
provenance. It performs no upload. See [the package guide](docs/huggingface-package.md).

```text
python scripts/prepare_huggingface.py --source-commit COMMIT_SHA --output reproduced/huggingface --archive reproduced/huggingface-private.zip
```
