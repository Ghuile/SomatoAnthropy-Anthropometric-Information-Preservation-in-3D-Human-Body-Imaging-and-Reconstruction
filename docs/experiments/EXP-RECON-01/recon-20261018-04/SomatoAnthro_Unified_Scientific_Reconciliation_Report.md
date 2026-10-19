# SomatoAnthro unified scientific reconciliation

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

Historical reconciliation precedes E5/S1/S2; it is not the final evidence synthesis.

## 1. Executive scientific assessment

The strongest supported result is an empirical restriction effect: native-MHR control permissions can suppress between-person digital extent variation while producing close agreement between alternative reconstructions. Releasing nine verified skeletal controls partly restores variation and improves source fidelity in E2-1 and its E2-2 heldout replication, while cross-path disagreement increases. These observations justify treating fidelity, diversity and consistency as separate objectives. They do not establish correct human anatomy.

A narrowly framed empirical SomatoAnthro manuscript is scientifically defensible with the listed limitations. Physical anthropometric accuracy, broad policy generalisation, new-method novelty and physiological body-fat accuracy remain unestablished. Defer E5 from this manuscript and qualify source scale/protocol/site definitions before a later engineering-sensitivity analysis.

## 2. Research objective and central question

> When does native-MHR fitting preserve source-body information while yielding consistent canonical bodies?

Operationally: preserve source-defined body information between people, without mistaking agreement between paths for correctness or repeated-observation consistency for accuracy. Source fidelity is measured against digital geometry. Diversity is represented primarily by Y-extent sample SD and individual extent error. Consistency has separate cross-path and cross-observation definitions. Anatomical validity and external accuracy are separate, unresolved targets. Stability is sensitivity of the tested fitting procedure, not a theorem about model identifiability.

Vector figure · Full caption

## 3. Original experiment scope and version registry

| experiment | version | subjects | branch_or_observation_rows |
| --- | --- | --- | --- |
| E0 | e0-unified-20261018-01 | 11655 | — |
| E4 | e4-20261018-03/report02 | 150 | 360 |
| E2 | e2-20261018-01/report03 | 150 | 360 |
| E2-1 | e2-1-20261018-01 | 16 | 32 |
| E2-2 | e2-2-20261018-01/presentation-v2 | 16 | 32 |
| E3 | e3-20261018-04 | 10 | 60 |

R-T1-experiment-inventory supplies exact input namespaces. E2 report03, E4 report02 and E2-2 presentation-v2 are pinned explicitly; earlier reports are not substituted. E2-2 presentation-v2 is a presentation of the same underlying experimental analysis. E0's final D-FAUST postrun supplement is retained separately from the earlier catalogue snapshot. Original code and all files within the selected evidence/report namespaces were fingerprinted before reconciliation.

## 4. Participant and observation inventory

Vector figure · Full caption

## 5. Data lineage and provenance

Private crosswalks retain verified subject, observation, sequence, fit and body identifiers, source representation, pathway, condition, partition, parameter/model/geometry references, hashes, frames, protocol and reference eligibility. E0 subject/observation/fit/candidate tables are separately indexed. NOMO branches lacking explicit observation UIDs remain marked unavailable; no new observation or biological identity was inferred from mesh similarity. Condition-level records are separate from participant membership.

## 6. Harmonised metric definitions

Signed preservation is MHR minus its own source. Pathway signed differences use A minus B. E4 disagreement change is abs(MHR_A−MHR_B)−abs(source_A−source_B), which can have a different sign from the signed pathway decomposition. MAE, RMSE, signed mean, P95 absolute error, between-person sample SD, within-person range, indexed vertex RMS and parameter coefficient norm remain separate estimands. All SD ratios use paired target/source populations and ddof=1.

R-T3-metric-protocol-harmonisation records quantity, frame, pose, LOD, site, extraction, reference, denominator, aggregation, missingness and limitations. The dictionary reuses the E2 registry and traces the E3/E4/intervention implementations; no replacement measurement engine was introduced.

## 7. Units, pose, LOD and reference comparability

NOMO values remain engineering centimetres. Native centimetre coordinates were historically multiplied by 0.01 into the working frame, with saved alignment/translation retained. That internal conversion is known, but it does not independently establish released-source physical scale. D-FAUST source metre calibration is conditional in these records. No new conversion to clinical centimetres was made. Dimensionless extent SD ratios are meaningful within their paired design; they do not justify pooling unrelated datasets.

## 8. Independently reproduced experimental findings

R-T4-verified-findings groups the checks by experiment. Core verification independently recalculated E2 bias/MAE/RMSE, all three-pathway contrasts and extent SD ratios, E4 four-value decomposition and reported primary/complementary fitted mean intervals, all intervention height summaries and saved surface mean/RMS/P95 summaries, and E3 historical/common/fixed-F01 measurement dispersion and canonical indexed geometry. It also independently reproduced E2 surface/measurement correlations. Secondary checks verified original job receipt counts, candidate ranking/freeze, clustered E3 association estimates and intervals, coefficient dispersion and E4 exploratory correlation point estimates. E4 correlation uncertainty intervals are retained from the original analysis and labelled accordingly.

E3 global RMS was recomputed directly from all saved canonical meshes; coefficient norms were recomputed from saved states. Local E3 region summaries were reaggregated from stored pair records. Reconciliation did not rerun native replay or independently regenerate all surfaces/contours. Historical native and contour verification remains evidence from those original experiments. Direct RMS arithmetic uses an explicit 1e−5 engineering-cm reproduction tolerance; other summaries use 1e−9, strictly as arithmetic tolerances, not acceptance margins.

## 9. Reconstruction fidelity and morphological preservation

| collection | n | source_sd | sd | sd_ratio | mae |
| --- | --- | --- | --- | --- | --- |
| SMPL-NICP | 150 | 10.784 | 1.8634 | 0.17279 | 8.029 |
| CAESAR-NICP | 150 | 10.794 | 1.8541 | 0.17177 | 8.0542 |
| SMPL-LBFGSB | 60 | 10.069 | 10.086 | 1.0017 | 0.78048 |

## 10. Parameter restrictions and diversity compression

Vector figure · Full caption

## 11. Controlled intervention and heldout replication

The following are new exploratory reconciliation effects: condition-after minus condition-before, two source-path outcomes averaged within each person, then mean across people. Intervals resample participants (2,000 percentile draws with key-derived seed 20261018); evaluation sets remain separate.

| experiment | partition | metric | participants | mean | mean_ci95 |
| --- | --- | --- | --- | --- | --- |
| E2-1 | evaluation | surface_mean_cm | 12 | -0.11671 | [-0.1713318465746375, -0.07898265302826202] |
| E2-1 | evaluation | fitted_absolute_height_error_cm | 12 | -2.6452 | [-3.6591222327018804, -1.5431860300154456] |
| E2-1 | evaluation | canonical_absolute_height_error_cm | 12 | -3.4995 | [-5.22050437424333, -1.7986821583161787] |
| E2-1 | evaluation | bound_contact | 12 | 0.375 | [0.16666666666666666, 0.625] |
| E2-2 | heldout | surface_mean_cm | 12 | -0.11737 | [-0.14015326726828967, -0.09573405196575106] |
| E2-2 | heldout | fitted_absolute_height_error_cm | 12 | -2.3144 | [-3.3198845378652475, -1.3630781289586922] |
| E2-2 | heldout | canonical_absolute_height_error_cm | 12 | -3.5686 | [-4.950050561911264, -2.314721133034636] |
| E2-2 | heldout | bound_contact | 12 | 0.58333 | [0.3333333333333333, 0.8333333333333334] |

The 192 new E2-2 completed jobs represent 12 new-to-E2-1 heldout people plus repeated development/policy/seed jobs. There were 16 reused E2-1 reference jobs, not renewed fitting allowances. All contributions and pairings are in fit-job-denominators. Group ablations are development evidence rather than independent full-cohort replications. G1/G2/G3/G4 and noG1/noG2 results are retained in R-T5 and the development policy ranking.

## 12. Representation-pathway sensitivity

| site | n | eligible | mean | mean_ci95 | mean_ci_family |
| --- | --- | --- | --- | --- | --- |
| abdomen | 149 | 150 | -0.12881 | [-0.20730492894015923, -0.05739930454306747] | [-0.22754121892488788, -0.032030838425276646] |
| chest | 1 | 150 | 0.84413 | — | — |
| height | 150 | 150 | 0.50003 | [0.40735367098324454, 0.6022789049676449] | [0.3937978493819105, 0.6343103987863379] |
| hip | 150 | 150 | 0.28859 | [0.22899972780489317, 0.34635443941336336] | [0.20994555329651876, 0.3636709183565739] |
| neck | 100 | 150 | -0.24497 | [-0.5562168476616338, 0.06870097586520615] | [-0.6222252509840436, 0.1806131257927217] |
| waist | 149 | 150 | -0.79401 | [-1.5612904065374271, 0.004063472187834194] | [-1.762903595864459, 0.21679144208098328] |

E4 is observational across historical representation/fitting paths. It cannot isolate topology because registration, optimisation, pose alignment and expression treatment also differ. E2-1/E2-2 isolate permission changes within the tested procedure, showing that better source fit can coexist with greater canonical disagreement. They do not prove that greater disagreement is anatomical improvement.

Vector figure · Full caption

## 13. Repeated-observation canonical consistency

| alignment | subjects | median | median_ci95 |
| --- | --- | --- | --- |
| saved_floor_frame | 10 | 2.0307 | [1.6813081046139722, 2.2345845435921285] |
| centroid_translation_only | 10 | 1.4978 | [1.295130898813281, 1.8084655791964515] |

| site | subjects | valid_observations | median |
| --- | --- | --- | --- |
| height | 10 | 60 | 2.1637 |
| waist | 10 | 60 | 2.9733 |
| abdomen | 10 | 60 | 3.0935 |
| hip | 10 | 60 | 2.708 |
| chest | 10 | 60 | 5.2311 |
| neck | 10 | 60 | 1.2115 |

The fixed-F01 site analysis excludes F01 as an evaluated outcome. Matched five-observation common-site and fixed-plane statistics are independently reproduced and retained in R-T7, alongside available-person and complete-six denominators. Historical strict missingness is not substituted for common-method coverage. Pose, soft tissue, registration, optimisation, root placement and measurement-plane movement remain confounded.

Vector figure · Full caption

## 14. Anthropometric site and measurement reliability

| collection | site | n | eligible | bias | mae | rmse |
| --- | --- | --- | --- | --- | --- | --- |
| CAESAR-NICP | abdomen | 149 | 150 | 0.37329 | 1.415 | 1.7227 |
| CAESAR-NICP | height | 150 | 150 | 3.2186 | 4.4971 | 5.6078 |
| CAESAR-NICP | hip | 150 | 150 | -0.68739 | 0.99441 | 1.3022 |
| CAESAR-NICP | waist | 149 | 150 | -2.7418 | 3.9477 | 5.5344 |
| SMPL-NICP | abdomen | 150 | 150 | 0.6119 | 1.4739 | 1.7825 |
| SMPL-NICP | height | 150 | 150 | 3.1494 | 4.4604 | 5.5475 |
| SMPL-NICP | hip | 150 | 150 | -0.55019 | 1.0123 | 1.2725 |
| SMPL-NICP | waist | 149 | 150 | 0.14815 | 3.4587 | 5.1801 |

The E2 atlas midpoint proxy uses frozen model-surface anchor candidates, not independently identified rib and iliac landmarks. Its paired source/fitted coverage is:

| collection | n | eligible | missing | mae |
| --- | --- | --- | --- | --- |
| CAESAR-NICP | 1 | 150 | 149 | 1.688 |
| SMPL-LBFGSB | 60 | 60 | 0 | 1.7465 |
| SMPL-NICP | 117 | 150 | 33 | 0.86317 |

Vector figure · Full caption

## 15. Optimisation stability and practical parameter ambiguity

| metric | participants | mean | mean_ci95 |
| --- | --- | --- | --- |
| surface_mean_cm | 12 | -0.0033506 | [-0.004927098791578669, -0.001826074167222656] |
| fitted_absolute_height_error_cm | 12 | -0.041022 | [-0.07633645546932656, -0.008310064425069928] |
| canonical_absolute_height_error_cm | 12 | -0.04353 | [-0.08230533801992547, -0.004619058086461324] |
| bound_contact | 12 | 0.041667 | [0.0, 0.125] |

R-T9-fitting-stability-identifiability retains participant-nested seed/initialisation results; parameter-bound-contacts reports branch fractions separately. Bound contact is neither automatic numerical divergence nor anatomical failure. E3 coefficient-space dispersion and indexed physical geometry quantify different objects; neither supplies a structural-identifiability proof. Self-intersections and anatomical plausibility are not comprehensively validated.

mechanism-evidence

## 16. Integrated fidelity/diversity/consistency framework

The desired joint behaviour is to retain genuine source-defined differences between people while limiting unnecessary variation across observations of the same person. NOMO and D-FAUST motivate these complementary objectives but do not jointly validate a new fitting objective. No SD/RMS pooling, universal trade-off law, new quality score or scalar claim-strength score is introduced. Better fit and larger between-person variance may still reflect source or optimisation artefacts; consistency may coexist with shared bias.

Vector figure · Full caption

## 17. Statistical validity and dependence

statistical-dependence-audit documents the independent units, paired records, convenience sampling, bootstrap levels, multiplicity families and inferential scope. E2/E4 are repeated descriptions of one cohort. E2-1/E2-2 intervention evaluation subsets are disjoint, but development is shared and all people are nested within the same NOMO source ecosystem. No old confidence intervals are averaged or pooled. New paired effects retain separate input participant lists in private provenance.

E3's six observations/person and 15 pairwise comparisons/person are clustered. Its within-subject-centred association statistics and whole-person bootstrap intervals reproduced independently from saved observation deviations; no independent-row p-values were introduced. Exploratory associations vary by site/predictor and missingness, and do not establish a universal reliability model or causality. E3-clustered-associations; surface-anthropometry-associations. Missingness is site/method dependent and often structural, so available-case results need not generalise to missing records.

## 18. Supported and unsupported claims

The claim ledger gives exact proposed manuscript wording, quantitative evidence, original sources, participant denominators, evidence type, confounders, alternatives, statistical/calibration limits, allowed interpretation and prohibited overinterpretation.

| claim_id | evidence_state | proposed_wording |
| --- | --- | --- |
| C01 | supported | Restrictive fitting substantially compresses between-person canonical Y-extent variation in this NOMO cohort. |
| C02 | supported | Releasing nine verified controls improves source fidelity and partially restores extent diversity on two separate evaluation subsets under the tested fitting procedure. |
| C03 | supported | Better source reconstruction coincides with greater cross-path canonical disagreement after control release in both evaluation subsets. |
| C04 | limited | Fitting changes matched digital pathway disagreement in a site-dependent manner; primary adjusted intervals support height/hip increases and an abdomen decrease. |
| C05 | supported | Digital anthropometric preservation depends on measurement definition, site and pathway. |
| C06 | supported | Independently fitted observations of the same D-FAUST person yield nonzero canonical geometry and measurement variability. |
| C07 | limited | The quarter-strength prior adds little surface fidelity and does not resolve the tested consistency/stability trade-off; Arm C remains the experimental reference. |
| C08 | limited | Released controls show bound contact and practical sensitivity under tested repeats; coefficient variation and physical geometry variation remain distinct. |
| C09 | unresolved | Independent physical anthropometric accuracy has not been established for NOMO. |
| C10 | limited | Global geometric residuals show site-specific exploratory associations, without establishing a general anthropometric reliability predictor. |
| C11 | limited | E0 supplies dataset-local lineage and selected saved-native reproducibility evidence, not a globally deduplicated human census or total fitting success rate. |
| C12 | unresolved | E0-E4 do not validate reconstruction-induced physiological body-fat estimation accuracy. |

R-T10-scientific-claim-ledger. Supported is always scoped to the wording; unresolved physical/physiological extensions are not publication-wide gates.

Vector figure · Full caption

## 20. Threats to validity and evidence discrepancies

Internal threats include optimisation/pose/identity coupling, representation-specific alignment and expression handling, limited control/seed interventions, root-frame sensitivity, source-derived measurement mapping and site missingness. Construct validity is restricted by engineering units, Y-extent rather than stature, unqualified atlas sites, raw versus tape procedures and limited external protocols. External validity is restricted by convenience samples, small intervention subsets and different dataset designs.

Historical E4 CLI/report-generator hash pins differ from the currently available files. Their scientific outputs passed the checked historical hashes, and independent arithmetic reproduced their table results. This establishes numerical reproduction of the saved evidence, not exact identity of the historical source code. No cause for the code drift is invented; its archived source version remains a provenance gap. Reconciliation input hashes freeze the available state and detect later changes.

Vector figure · Full caption

## 21. Remaining scientific gaps

R-T11-outstanding-research-gaps ranks minimum next actions and distinguishes essential-for-specific-claim from strengthening/optional work. A digital empirical paper can proceed without complete anatomical landmarks, perfect reconstruction, zero bounds, uniform agreement, zero within-person variation, significant effects or E5. Physical anthropometric accuracy cannot proceed without unit/protocol/site qualification. Broad cross-dataset causal policy claims require a genuinely compatible design.
