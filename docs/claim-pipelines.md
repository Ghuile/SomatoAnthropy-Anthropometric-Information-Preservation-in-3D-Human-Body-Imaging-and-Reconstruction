# Claim-to-pipeline guide

The six questioned claims are pre-existing experimental results or summaries of frozen records. Commit `3777873` omitted their supporting fields/tables. Commit `5c1553b` added the expanded aggregate tables; this update adds a complete model-control audit, explicit claim mapping and runnable replay pipelines. The original research manuscript and frozen experiment results are unchanged. GitHub remains private; Zenodo is deferred.

| Claim | Definition and population | Released inputs |
|---|---|---|
| Spearman .8392→.9860 / .8112→.9790 | Source versus canonical extent ranks; B→C on the 12-person E2-2 heldout subset; SMPL then CAESAR | E2-2-height-all-arms.json: heldout/canonical/B,C/spearman |
| 229/69 fallback split | P-side fallback/nonfallback over 298 complete canonical NICP body observations from 149 people. Strata contain 119/39 people, with nine in both; they are not independent groups | waist-fallback-counts.json and canonical-fallback-strata.json |
| 109 + 1 + 40 | Retained, replacement and additional distinct participant selections; one incomplete original was replaced | NOMO-cohort-selection.json |
| 80/70 | Female/male provider source-record categories; not independently validated biological sex or imputed physiology | NOMO-cohort-selection.json |
| Group-arm findings | Four development participants with linked pathways. G1 spine/neck, G2 leg/foot, G3 arms, G4 widths; noG1/noG2 omit a group. R025 and R4 use quarter/fourfold skeletal prior | E2-2-height-all-arms.json, E2-2-group-arms.json, E2-2-regularization-arms.json; experiments/e2_2/core.py |
| Zero-domain exclusions | Hip height (147), hip depth (148), ankle height (152): authored minimum=maximum=0. A nonzero transform column is compatible with a fixed authored domain | configs/control_audit_204.json; experiments/e2_1/core.parameter_audit |

The compiled values are in results/aggregate/claim-traceability.json. Source hashes, original algorithm files and public input/output hashes are in claim-pipeline-provenance.json. The complete 204-control audit is model metadata; it contains no participant parameters, fitted geometry or model weights. The original nine released rows remain unchanged and are checked against their subset of this complete audit.

## Public aggregate route

```text
python scripts/reproduce_audit_claims.py frozen --output reproduced/audit/claims.json
python scripts/verify_release.py
```

This reconstructs the displayed claims from the frozen aggregate inputs and checks all scalar summaries. It does not recover participant ranks or independently recompute person-membership counts from marginal tables. Spearman recomputation and unique-person fallback counts require the separately licensed original records. Original confidence intervals are not re-estimated. CI exercises this public route on every push for Python 3.11 and 3.12.

## Licensed original-record route

```text
python scripts/reproduce_audit_claims.py licensed --manifest local/audit-inputs.json --output reproduced/licensed-audit/claims.json
```

Start from configs/claim_inputs.example.json and supply actual local SHA-256 hashes. Paths resolve below the declared input root and inputs remain read-only. The five input roles are:

1. cohort_manifest: original JSON with participants containing source_id and selection; only category/stage counts are output.
2. waist_pairs: frozen WAIST paired.json records; only eligible canonical NOMO SMPL-NICP/CAESAR-NICP rows with complete linked pathways enter this claim. Saved P fallback flags define the strata.
3. height_records: original individual-height.csv, with partition, collection, condition, state, source_extent_cm, native_extent_cm and case. The original variation() implementation computes ranks and extent summaries. Case labels remain local.
4. geometry_records: original individual-geometry.csv; the original describe() summarizes saved per-person mean_cm values by development condition/pathway. No geometry is regenerated.
5. parameter_audit: original full 204-row model-control audit JSON.

The route was exercised on the frozen research inputs: four Spearman values, the 229/69 observation split, overlapping-person counts, the 150-person selection/categories and all twenty condition/pathway mechanism summaries match the released scalar results to 1e-12. Compared arms/states must retain the same people and source extents within pathway; geometry records must match the development height population. Outputs contain summaries and labelled input hashes only. Individual records, IDs, case labels and file paths are not exported. This comparison verifies replay consistency; it is not scientific acceptance or new external validation. No fitting, selection changes or participant-level bootstrap runs occur.

## Control-domain pipeline

With a separately obtained saved native probe:

```text
python scripts/recompute_control_audit.py --probe local/native-probe.json --sha256 ACTUAL_SHA256 --output reproduced/control-audit.json
```

The original parameter_audit parses authored MinMax limits and retains the actual joint/channel coefficients. The route strips runtime/resource fields, verifies the probe hash and compares all 204 resulting rows with the released audit.

With the pinned official MHR runtime and assets in the configured assets/mhr/v1 layout:

```text
python scripts/audit_native_controls.py --model-root local_model_root --output reproduced/native-controls.json
```

This reads the native transform matrix and parameter limits using the original E2-1 probe loop, checks asset/code hashes and matches the frozen full audit. It does not forward a body, fit parameters or load participant inputs. Model binaries and the optional native runtime are acquired separately. The review-only environment supports the public and saved-probe routes; it does not supply PyMomentum/MHR.

Both control routes were exercised: the saved original probe and the loaded pinned LOD1 CPU model each reproduce all 204 audit rows. The extracted mapping/limits loop also matches the original query's syntax tree. These checks establish consistency with the pinned model metadata, not anatomical validity or fitting quality.

## Scientific boundaries

Ranks describe ordering, SD ratios describe spread, and neither proves exact dimension recovery. Fallback strata are associations under a dependent source reference and can overlap within person. G1–G4/R4 results are development-only, with interacting optimization freedoms; group effects are not uniquely additive anatomical mechanisms. Provider categories do not establish clinical sex metadata. Zero-width authored domains do not mean zero-effect transform columns.
