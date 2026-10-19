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
and estimand. Figure 2 body panels are withheld pending publication clearance.
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
private correspondence are excluded. Public distribution remains subject to
the authors' final approval and applicable rights clearance. No blanket
open-source licence is granted while institutional licensing authority is unresolved.
