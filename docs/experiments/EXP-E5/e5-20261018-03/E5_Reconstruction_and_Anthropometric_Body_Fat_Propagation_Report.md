# E5 — Reconstruction and anthropometric body-fat formula propagation

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

## 1. Executive scientific assessment

Existing reconstruction and metrology decisions materially change RFM formula outputs under the descriptive 1/3/5-pp engineering thresholds. Mean absolute source-to-canonical drift is CAESAR-NICP: 2.472 pp (95% CI 2.130–2.886; n=149), SMPL-NICP: 2.352 pp (95% CI 2.037–2.720; n=149). The complete-person mean source-agreement advantage for P over official clad-body is **-0.652 pp** (95% CI -0.872–-0.440; 149 people, four observations/person). Negative favours clad-body. This reverses the historical waist-MAE ranking under the full source/body-height formula comparison. These are dependent digital-reference findings, with no physiological ground truth.

## 2. Questions and hypotheses

E5-A asks how source → fitted → canonical input changes affect formula output. E5-B tests same-body waist-method response and dependent source-formula agreement. E5-C quantifies repeated-observation-associated variability. E5-D tests existing locked/released control conditions. No favourable direction was assumed; these retrospective convenience-cohort analyses are exploratory, not preregistered confirmatory tests.

## 3. Frozen evidence chain

E0 e0-unified-20261018-01 supplies lineage; E1 e1-20261018-02 supplies geometric/decision links; E2 report03 supplies direct measurements; E2-1 and E2-2 presentation-v2 supply separate controlled evaluation subsets; E3 e3-20261018-04 supplies repeated observations; E4 report02 supplies pathway crosswalks; WAIST waist01-20261018-02 supplies 852 body/pose and 4,260 method records; RECON recon-20261018-04 supplies metric/dependence definitions. All 4,260 original WAIST records equal their additive E1 wrappers field for field. Input byte hashes and historical-report protection are recorded privately. No earlier report revision substitutes for these versions.

## 4. Equations and published protocols

## 5. Formula response versus physiological accuracy

Paired RFM differences cancel the same-person sex constant: ΔF=−20(H1/W1−H0/W0). No sex assignment is needed for these differences. The −20H/W coordinates used to centre repeated observations have an arbitrary zero and are never complete BF estimates. The frozen handoff supplies no age eligibility; all complete absolute RFM outputs are withheld. No record is classified PROTOCOL_COMPATIBLE_ESTIMATE or INDEPENDENT_PHYSIOLOGICAL_VALIDATION. Off-protocol formula response is not body-fat prediction accuracy.

## 6. Participants and coverage

E5-T2-cohort-inventory. The primary NOMO population is 150 people, not 300 independent pathway records. The 60 LBFGSB people overlap those 150. WAIST also contains 10 D-FAUST people with 60 observations, 20 MPII people, 11 UCSC, 10 HBW, 10 FAUST, 10 HIT and 11 NHANES-conditioned bodies. Cross-dataset donor overlap is unresolved: dataset-local IDs are not proof of globally unique people. The two twelve-person controlled evaluation subsets are disjoint; development participants remain separate.

## 7. Input definitions and support

Height is mesh max(Y)−min(Y), not clinical stature. Historical E2 adaptive/fallback waist, E2 atlas waist proxy and WAIST P are separate frozen measurement series. E2_proxy_raw and E2_proxy_tape are never relabelled as adaptive waist. B1 is actual clad-body commit a2140a74555a6382e1712ec1a5d8dc939b59e655; B3_offset is mapped umbilicus +0.005 engineering m; B2 is 63% height. Neck and posterior-A/gluteal hip remain engineering proxies. All ratios retain consistent engineering units, without claiming independent physical calibration. Measurement values are not rewritten.

## 8. Source-to-MHR formula drift

| pathway | transition | people | mean | mean_absolute | mean_absolute_ci95 | p90_absolute | p95_absolute |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CAESAR-NICP | source_to_canonical | 149 | -1.880 | 2.472 | [2.130, 2.886] | 4.756 | 6.759 |
| CAESAR-NICP | source_to_fitted | 149 | -1.963 | 2.217 | [1.861, 2.580] | 5.777 | 6.480 |
| SMPL-NICP | source_to_canonical | 149 | -0.317 | 2.352 | [2.037, 2.720] | 4.962 | 5.696 |
| SMPL-NICP | source_to_fitted | 149 | -0.756 | 1.842 | [1.563, 2.144] | 4.958 | 6.179 |

E5-T3-reconstruction-drift includes all mapped-proxy raw/tape sensitivities. Missing source waist leaves 149 NICP source comparisons per path; LBFGSB historical source comparison is unavailable and not imputed. E5-T3S-pathway-contrasts gives within-person differences between pathway drifts. Each source reference is dependent on the prior fitting/site framework.

## 9. Fitted-to-canonical changes

| pathway | people | mean | mean_absolute | mean_absolute_ci95 | p95_absolute |
| --- | --- | --- | --- | --- | --- |
| CAESAR-NICP | 150 | -0.039 | 2.129 | [1.799, 2.509] | 5.284 |
| SMPL-NICP | 150 | 0.317 | 2.034 | [1.722, 2.394] | 5.052 |

E5-T3S-frozen-WAIST-fitted-canonical separately provides the unchanged WAIST P series, including all available LBFGSB fitted/canonical pairs. Canonical transfer incorporates articulation, pose correctives and any documented expression change. HIT historical neutral bodies are never renamed T90. LBFGSB expression-control differences remain linked in body-lineage.json. For complete triples, Δtotal=Δfit+Δcanonical was verified at numerical precision; the terms are not independent causal effects.

## 10. Same-body waist-method sensitivity

E5-T5-waist-method-sensitivity reports mean/median signed and absolute P-minus-comparator differences, P90/P95, person-level confidence intervals and descriptive exceedance fractions across all dataset/state strata. Each comparison holds one exact body height constant. E5-T5S-adaptive-fallback separates recorded adaptive and fallback subsets. Figures E5-3 and E5-S1 display canonical NICP method response and overall coverage.

## 11. P versus official clad-body

The official end-to-end comparison retains P raw extraction and clad-body’s original circumference extraction. It therefore includes both site and contour-functional changes. The common-extractor site_raw and site_tape comparisons hold the extraction functional fixed while moving the selected plane. They are reported separately; neither is evidence that the selected plane is anatomically correct. See E5-3 and E5-T5-waist-method-sensitivity.

## 12. Offset-only and fixed-height controls

The offset-only method is essential, not an optional omission. E5-T6-source-formula-agreement reports the P-minus-offset dependent-reference comparison alongside P-minus-clad. E5-T5-waist-method-sensitivity also retains B2/63% and mapped-umbilicus B3. A simple method can outperform the adaptive selector under the tested proxy, without establishing an independent anatomical advantage.

## 13. Dependent source-formula agreement

| pathway | state | mode | people | mean | mean_ci95 | proportion_people_mean_positive |
| --- | --- | --- | --- | --- | --- | --- |
| CAESAR-NICP | canonical | end_to_end | 149 | -0.869 | [-1.136, -0.623] | 0.302 |
| CAESAR-NICP | canonical | umbilicus_offset_raw | 149 | -0.350 | [-0.528, -0.177] | 0.060 |
| CAESAR-NICP | fitted | end_to_end | 149 | -1.314 | [-1.693, -0.960] | 0.275 |
| CAESAR-NICP | fitted | umbilicus_offset_raw | 149 | -1.433 | [-1.786, -1.094] | 0.047 |
| SMPL-NICP | canonical | end_to_end | 149 | -0.280 | [-0.529, -0.055] | 0.477 |
| SMPL-NICP | canonical | umbilicus_offset_raw | 149 | -0.286 | [-0.456, -0.128] | 0.081 |
| SMPL-NICP | fitted | end_to_end | 149 | -0.145 | [-0.514, 0.200] | 0.523 |
| SMPL-NICP | fitted | umbilicus_offset_raw | 149 | -0.336 | [-0.695, 0.012] | 0.255 |

The advantage is |Fcomparator−Fsource|−|FP−Fsource|: positive favours P. In the primary complete-person analysis, 30.9% favour P by their mean four-observation advantage; ties are separate. Actual source and reconstructed heights are used. E5-T6S-source-waist-common-height is the distinct counterfactual retaining the body height for both source and method waists, to expose height compensation. The source contour functional follows each recorded comparison (raw or tape); no protocol equivalence is inferred. This is source-formula agreement, never physiological accuracy.

## 14. D-FAUST repeated observations

| method | people | observations | mean | mean_ci95 |
| --- | --- | --- | --- | --- |
| B1 | 10 | 10 | 0.514 | [0.373, 0.655] |
| B3_offset | 10 | 10 | 0.567 | [0.468, 0.678] |
| P | 10 | 10 | 0.622 | [0.504, 0.770] |

These means are within-person sample SDs in pp, bootstrapped over ten people. E5-T7-repeated-observation-people reports every person’s n, SD, range, MAD, pairwise differences, maximum disagreement and height/waist ranges. E5-T7S-repeated-summary and E5-T7S-method-SD-comparisons include uncertainty and paired method contrasts. Own-site and fixed-F01 E3 raw/tape planes both exclude F01, retaining five observations/person. They are different atlas proxies from WAIST P. Pose, registration, deformation, fit, recovered morphology and site changes are confounded; this is not pure pose error. More stable does not imply anatomically better.

## 15. Locked/released controls

| experiment | partition | pathway | people | mean | mean_ci95 | mean_absolute |
| --- | --- | --- | --- | --- | --- | --- |
| E2-1 | evaluation | CAESAR-NICP | 12 | 0.756 | [0.102, 1.363] | 1.155 |
| E2-1 | evaluation | SMPL-NICP | 12 | 0.752 | [0.089, 1.362] | 1.136 |
| E2-2 | heldout | CAESAR-NICP | 12 | 0.816 | [0.261, 1.408] | 1.074 |
| E2-2 | heldout | SMPL-NICP | 12 | 0.803 | [0.247, 1.370] | 1.061 |

Existing saved E2 mapped waist proxies support twelve paired people per pathway in each evaluation subset. Positive C−B increases formula output; mean absolute change differs from mean signed change. Development and E2-2 quarter-prior D remain separate supplementary strata. Source-formula change |FC−FS|−|FB−FS| is negative when C agrees more closely:

| experiment | pathway | people | mean | mean_ci95 |
| --- | --- | --- | --- | --- |
| E2-1 | CAESAR-NICP | 1 | -0.997 | unavailable |
| E2-1 | SMPL-NICP | 11 | -0.961 | [-1.493, -0.438] |
| E2-2 | CAESAR-NICP | 0 | unavailable | unavailable |
| E2-2 | SMPL-NICP | 9 | -0.581 | [-1.005, -0.192] |

CAESAR source mapped-plane contours have very sparse support (one or zero in these evaluation subsets), so a general source-drift improvement claim is not justified there. E5-T8S-input-variation reports height and WHtR diversity; control-lineage.json preserves original policies, parameter/input hashes, bounds and status. No optimisation was executed.

## 16. Local mathematical sensitivity

∂F/∂H=−20/W and ∂F/∂W=20H/W². The derivatives are pp per declared input length unit; expressing the same geometry in a different unit changes their numerical scale. Observed per-record derivatives and first-order predictions are exported with exact finite differences. Their analytic behaviour is not an empirical physiological finding.

## 17. Height/waist contribution allocation

| pathway | people | mean_abs_height_phi | mean_abs_waist_phi | cancellation_fraction |
| --- | --- | --- | --- | --- |
| SMPL-NICP | 149 | 1.819 | 1.626 | 0.517 |
| CAESAR-NICP | 149 | 1.786 | 0.972 | 0.336 |

Four exact ratio combinations yield height-only, waist-only and nonlinear interaction terms. Half the interaction is allocated to each input, giving symmetric φH+φW=ΔF. The arbitrary formula constant is excluded without assigning sex. Opposing φ values identify cancellation; the exported cancelled magnitude is |φH|+|φW|−|ΔF|. E5-T4-height-waist-decomposition contains all primary and control strata. Figure E5-7 shows observed high-tail and cancellation cases, not prevalence estimates.

## 18. Geometry–formula relationships

| pathway | people | rho | ci95 |
| --- | --- | --- | --- |
| CAESAR-NICP | 149 | 0.669 | [0.574, 0.746] |
| SMPL-NICP | 149 | 0.301 | [0.142, 0.442] |

These Spearman associations use fitted-source global residuals and the exact same body’s source-to-canonical response; the pose of the metric differs from the canonical outcome. E5-T9-geometry-formula-associations separately reports fresh E1 regional and historical global strata. Fresh regional subsets are small and may have wide intervals. Direct height/waist correlations are deterministic formula-input relationships, not new physiological associations. No predictive generalisation or independent incremental-regional model is established. Low residuals cannot by themselves qualify a formula label.

## 19. Failure and missingness

E5-T11-failures-missingness preserves absent source waists, missing neck/hip, invalid contours and unsupported demographics. All successful numeric inputs are positive and finite; no missing contour is filled, no domain is floored and no formula output is clipped. Eligible body and person denominators are separate. Mathematical validity, anatomical compatibility and physical qualification are separate statuses.

## 20. Circumference-based secondary results

E5-T10-secondary-equation and E5-T10S-eligibility report sex-stratified, off-protocol paired responses and valid/excluded counts. For each fixed branch let x=A−N or W+Hip−N. Under a fixed common k, ΔF=a log10(x1/x0)−b log10(H1/H0), so the unknown common scale cancels. Absolute F changes by (a−b)log10(k), and is not scale invariant. Absolute military estimates are withheld. The common-scale assumption follows the saved engineering frame, without claiming observed clinical centimetres. Supporting WHtR and WHR remain descriptive ratios in supporting-indices.json.

## 21. Source and pose dependencies

NICP, LBFGSB, fitted and canonical states stay separate. E1 non-NOMO source panels have geometric residuals but no frozen compatible source waist, so no source-to-MHR formula response is invented. Their canonical WAIST records contribute method sensitivity. FIT09/NHANES is measurement-conditioned, never independent source-surface or physiological validation. Historical HIT neutral-pose and LBFGSB expression differences are explicit exceptions.

## 22. Decisions affecting labels

E5-T12S-decision-audit maps all 24 E1 decisions to matched-state quantification, association, input-definition implication or implementation-only evidence. Cranial envelope, feet/floor and torso effects cannot be isolated from these records. E1 found worse mean UCSC global discrepancy in current versus original saved correction states. A matching original/current waist series is absent from the E5 handoffs; no unmeasured BF effect is claimed. Neck/hip/abdomen mismatches chiefly limit the secondary equation and do not alter RFM directly.

## 24. Contrary evidence and negative results

The favourable historical P waist-MAE result (2.893 versus 3.543 engineering cm; advantage 0.649, CI 0.365–0.923, 149 people) is preserved as historical evidence, alongside SMPL-canonical support, inconclusive CAESAR-canonical waist agreement, fitted CAESAR favouring clad-body and offset-only outperforming the full adaptive selector. E5’s downstream full-height formula comparison can reverse that ranking. Canonicalisation does not universally reduce drift. Released controls alter formula outputs but source-reference support is sharply pathway dependent. Stability does not establish anatomical truth. No qualified absolute or physiological validation result is available.

## 25. Statistical uncertainty

All intervals use 2,000 deterministic percentile bootstrap replicates of dataset-local people; seeds are stored per result and in configuration. Complete clusters are retained. Where people have multiple records, estimates average within person first; absolute drift is averaged within person before averaging people. Main strata are balanced; unbalanced distribution summaries explicitly use person means. Repeated D-FAUST pairs are not independent people. Quantiles and threshold fractions describe the observed sample. These exploratory intervals are unadjusted for multiple comparisons; they do not establish population sampling, clinical relevance or scientific acceptance. Different sample supports must not be compared as independent error components.

## 26. Physical and anatomical limits

Engineering coordinate conversions are known internally but do not independently establish clinical scale. RFM ratios and common-scale paired log differences support formula response despite that gap. Mesh extent, right-ilium waist, narrowest military waist, navel abdomen, shoulder-free neck and posterior hip protocols are not interchangeable. Sex is only used when explicitly documented in frozen metadata; age is not inferred. No linked DXA or qualified independent body-composition reference exists in this programme.

## 27. Synthetic-label reliability

A synthetic body label must carry formula/version/branch, raw inputs and units, exact site/extraction method, source/fit/body/observation hashes, control policy, actual pose/expression state, dependence class and missingness/eligibility flags. E5-T12-label-reliability-metadata specifies these fields. synthetic-label-metadata.json exports all 4,260 original method records plus additive eligibility and arbitrary-zero response coordinates. It intentionally does not manufacture complete BF labels from missing demographics. Observed within-person ranges may accompany labels as engineering consistency descriptors, not calibrated error bars on true physiology.

## 29. Remaining scientific gaps

Independent clinical scale, verified original formula sites, linked age/sex metadata for complete labels and participant-matched body composition remain unresolved. Cross-dataset donor overlap is unknown. Other-family source waist comparisons and isolated correction effects lack compatible saved handoffs. Sparse CAESAR control-source contour support limits intervention-reference conclusions. New physiological-predictor or DXA-level claims would require new evidence; no extra acquisition/fitting was undertaken.
