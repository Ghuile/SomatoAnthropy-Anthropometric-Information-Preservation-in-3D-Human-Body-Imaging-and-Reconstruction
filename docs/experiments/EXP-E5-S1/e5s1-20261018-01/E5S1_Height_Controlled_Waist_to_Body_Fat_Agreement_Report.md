# EXP-E5-S1 — Height-controlled waist-to-body-fat formula agreement

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

## 1. Executive scientific assessment

The original E5 end-to-end mean P advantage reproduces exactly: **−0.651978541 pp**, original 95% CI **[−0.872051437, −0.440086652]**, 149 people / 596 observations. Holding source height fixed changes the point estimate to **+0.139748546 pp**, new participant 95% CI **[−0.025859224, +0.323214446]**. Holding reconstructed height fixed gives **+0.150170121 pp**, CI **[−0.022452224, +0.342635559]**. The full-cohort controlled results therefore do not establish overall P superiority.

Height control produces **52/149 participant preference switches**: 44 from B1 to P and 8 from P to B1. The mean estimand shift is **0.791727 pp**, CI [0.5987842648026057, 0.9934660133468457]. Larger B1 cancellation explains much of this change mathematically. The result is conditional on pathway: source-height-controlled SMPL favours P; CAESAR favours B1, particularly fitted bodies. The simple offset-only baseline outperforms full P under controlled height. No physiological BF validation follows.

## 2. Research objective and original E5 reversal

Explain why lower waist-proxy disagreement can coexist with greater source-formula drift. WAIST's +0.649390 engineering-cm advantage is **canonical-only**, 149 people / 298 branch observations. E5's −0.651979 pp primary advantage averages **both fitted and canonical states**, four observations per person. This denominator distinction is material: fitted CAESAR is a contrary case in both experiments. Comparing those headline values alone conflates endpoint nonlinearity, reconstruction height and pose weighting.

## 3. Formula definitions and assumptions

Let Hs be the saved source Y extent, Hb the saved reconstructed Y extent, Ws the frozen source waist proxy and Wm the saved method waist. Actual drift is f(Hb,Wm)−f(Hs,Ws). Source-height drift is f(Hs,Wm)−f(Hs,Ws). Body-height drift is f(Hb,Wm)−f(Hb,Ws). Paired advantage is absolute second-method drift minus absolute first-method drift; positive favours the first method. At one observation, A_bodyH=(Hb/Hs)A_sourceH, so positive height scaling preserves its sign. Participant means may in principle differ because observation weights change; they are computed independently.

See T1: comparison definitions. These are three estimands, not three independent replications.

## 4. Frozen E5 and WAIST evidence

Inputs: E5 `e5-20261018-03`; WAIST `waist01-20261018-02`; E1 `e1-20261018-02`; E2 `e2-20261018-01/report03`; E4 `e4-20261018-03/report02`; RECON `recon-20261018-04`. Exact original E1 handoff preserves all 4,260 WAIST method records. Historical tables and private data were read without modification.

E5's `E5-T6S-source-waist-common-height` already implements **body-height control**, not source-height anchoring. Every saved P/B1 actual response and body-height-controlled advantage is reused and checked exactly; its full grouped table reproduces. E5's reconstruction decomposition already stores four mathematical height/waist cells, but not this complete method-specific participant transition analysis. E5 Shapley contribution/cancellation statistics average both evaluation orders. S1's waist-first ordered split is a distinct requested statistic and does not revise E5.

New work consists of source-height-controlled complete-person summaries, three-policy participant transitions, method-specific ordered cancellation, compensating waists, controlled-functional offset comparisons and identity-anchor eligibility/dispersion. All six WAIST canonical baseline means and original paired CIs reproduce exactly, including raw/tape and offset comparisons. No waist or height is remeasured.

## 5. Cohort and measurement eligibility

All 150 NOMO identities and 600 NICP fitted/canonical observations remain inventoried. One participant lacks the saved source waist reference in all four cells: **149 people / 596 body observations** form the common primary cohort for all three policies and all three methods. Participant UID, source hash, body UID, fit UID, mesh hash, parameter hash and pose are joined explicitly; repeated source paths/states stay nested within person. There is no imputation or outcome-based exclusion.

The common extractor has two additional B1-invalid body observations from one otherwise primary-eligible person. Raw/tape complete-four-cell comparisons therefore have **148 people / 592 observations**. All available three-method records yield 149 people / 594 observations; their within-person weights are explicit in the supplementary availability table. Pair-specific availability is reported separately: P versus offset retains all 149 people / 596 observations under both common functionals because it does not require B1. The matched sensitivity table compares all three functionals on the same 148-person cohort. These eligibility differences do not alter the 149-person primary denominator. T2, all-available triplets.

## 6. Exact source and MHR height definitions

Hs is the frozen `NOMO-CONTACT-v1` `vertical_extent_cm`, `SAVED_SURFACE_Y_EXTENT`, `geometry_quality=VALID`, in engineering cm, obtained from E4's saved source-site descriptor. Hb is the same saved MHR mesh Y extent recorded by WAIST/E5, `same saved mesh Y extent, not qualified physical stature`. Fitted and canonical Hb values are separate observations with distinct mesh hashes. Internal engineering metres to engineering cm use the historical scale factor 100; no physical calibration is inferred from it. No new alignment, floor/head adjustment, averaging or stature estimation is performed.

Source pose is recorded as `RELEASED_SOURCE_AND_SAVED_FITTED_MHR`; own fitted/canonical identity and pinned T90 transfer are verified. Exact anatomical pose equality between source pathways is unverified. Feet alignment, pose and head-envelope conventions can change extent. Source and body descriptors are digital geometric quantities, not clinically qualified standing stature.

## 7. Actual end-to-end agreement

The unchanged historical E5 estimate and original seed/CI above reproduce exactly. The new 4,000-draw interval for the same mean is [−0.861860527, −0.448111465]; it is a newly calculated uncertainty interval and is **not** labelled the unchanged historical interval. P is preferred by 46/149 participant mean advantages, B1 by 103/149, with zero numerical ties.

## 8. Source-height-controlled agreement

| first | second | people | observations | mean | median | mean_ci95 | person_positive_count | person_negative_count | person_ties |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P | B1 | 149 | 596 | 0.140 | 0.027 | [-0.026, 0.323] | 82 | 67 | 0 |
| P | B3_offset | 149 | 596 | -0.261 | -0.023 | [-0.399, -0.128] | 53 | 77 | 19 |
| B1 | B3_offset | 149 | 596 | -0.401 | -0.034 | [-0.536, -0.282] | 56 | 93 | 0 |

P has a positive full-cohort point estimate against B1, with an interval spanning zero. This measures **waist-attributable formula disagreement against a dependent source proxy**. It does not independently validate anatomical waist localisation. Nonlinear inverse-waist sensitivity means waist MAE alone cannot fix the formula ranking.

## 9. Reconstructed-height-controlled agreement

| first | second | mean | median | mean_ci95 |
| --- | --- | --- | --- | --- |
| P | B1 | 0.150 | 0.027 | [-0.022, 0.343] |
| P | B3_offset | -0.272 | -0.024 | [-0.416, -0.135] |
| B1 | B3_offset | -0.422 | -0.034 | [-0.564, -0.297] |

This reuses E5's common-body-height estimand and compares against Ws evaluated at Hb, which is not the source's measured formula coordinate. Its full-cohort advantage remains uncertain around zero. Observation-level preference is invariant relative to sourceH because Hb/Hs is positive; participant-level results are evaluated after the stipulated aggregation.

## 10. Full-cohort statistical results

| policy | mean | median | mean_ci95 | person_positive_fraction | person_negative_fraction | person_ties |
| --- | --- | --- | --- | --- | --- | --- |
| actual | -0.652 | -0.256 | [-0.862, -0.448] | 0.309 | 0.691 | 0 |
| sourceH | 0.140 | 0.027 | [-0.026, 0.323] | 0.550 | 0.450 | 0 |
| bodyH | 0.150 | 0.027 | [-0.022, 0.343] | 0.550 | 0.450 | 0 |

| method | policy | mean_absolute | median_absolute | mean_absolute_ci95 | observation_p90_absolute | observation_p95_absolute |
| --- | --- | --- | --- | --- | --- | --- |
| P | actual | 2.221 | 1.739 | [1.973, 2.490] | 5.321 | 6.403 |
| P | sourceH | 1.441 | 1.104 | [1.283, 1.610] | 3.863 | 5.054 |
| P | bodyH | 1.488 | 1.153 | [1.324, 1.666] | 4.031 | 5.192 |
| B1 | actual | 1.569 | 1.378 | [1.392, 1.771] | 3.434 | 4.488 |
| B1 | sourceH | 1.581 | 1.144 | [1.398, 1.781] | 4.069 | 5.467 |
| B1 | bodyH | 1.638 | 1.162 | [1.445, 1.850] | 4.326 | 5.677 |
| B3_offset | actual | 1.619 | 1.472 | [1.456, 1.806] | 3.725 | 4.510 |
| B3_offset | sourceH | 1.179 | 0.907 | [1.052, 1.314] | 2.821 | 4.019 |
| B3_offset | bodyH | 1.216 | 0.942 | [1.085, 1.354] | 2.948 | 4.349 |

The independent resampling unit is the participant. All four body observations are averaged within person before equal-person averaging. New uncertainty uses NumPy default_rng(51812601), 4000 draws, sorted participant UIDs and percentile intervals. Median advantages are medians of participant means; median absolute drift is the median of participant mean absolute drifts. Both participant and observation P90/P95 are explicitly retained in machine-readable tables. Method-specific drift, height/waist distributions, ties, invalid counts and bootstrap median intervals are included. No confirmatory p-value threshold or unapproved scientific margin is introduced; intervals describe available-sample uncertainty.

## 11. Pathway and pose-state differences

| stratum | people | observations | mean | mean_ci95 |
| --- | --- | --- | --- | --- |
| SMPL-NICP | 149 | 298 | 0.651 | [0.406, 0.897] |
| CAESAR-NICP | 149 | 298 | -0.371 | [-0.582, -0.156] |
| fitted | 149 | 298 | 0.008 | [-0.237, 0.270] |
| canonical | 149 | 298 | 0.272 | [0.116, 0.443] |
| CAESAR-NICP/canonical | 149 | 149 | -0.036 | [-0.235, 0.168] |
| CAESAR-NICP/fitted | 149 | 149 | -0.707 | [-1.034, -0.377] |
| SMPL-NICP/canonical | 149 | 149 | 0.579 | [0.376, 0.791] |
| SMPL-NICP/fitted | 149 | 149 | 0.722 | [0.364, 1.085] |

SourceH gives SMPL-NICP +0.651 pp, but CAESAR-NICP −0.371 pp. Both pathway intervals exclude zero in opposite directions. Canonical-only combined advantage is +0.271779 pp with an interval above zero; fitted-only is +0.007718 pp with an interval spanning zero. Fitted CAESAR remains a clear contrary result (−0.707 pp). The paired contrasts resample the same people and directly compare pathway and state effects; neither source pathway is an independent donor cohort.

## 12. SomatoSynth3D versus clad-body

The controlled result is conditional, not a general win. P's actual source-formula drift is greater overall, despite its canonical waist-proxy advantage. Fixed-height B1 has smaller actual drift in both pathways on average; after removing source/body height differences, SMPL changes direction while CAESAR remains B1-favouring. Differences in source representation, pose and site/functional behaviour remain plausible explanations. No retuning, new waist selector or source-reference replacement was allowed.

## 13. Offset-only baseline

The full-cohort P-minus-offset advantage is −0.261393 pp under sourceH, CI [−0.399201, −0.128350], and −0.271900 pp under bodyH, CI [−0.416464, −0.134571]. Thus the simple mapped umbilicus +0.005 engineering-metre baseline outperforms full P under both controlled endpoints. Nineteen participant means tie numerically; many body observations tie because P uses the same fallback. Offset beats B1 under controlled height too. The existing evidence supports distinguishing the value of body-specific site information from the incremental adaptive contour-profile optimisation; this endpoint does not support claiming the full adaptive selector is best.

## 14. Height–waist compensation

DW=f(Hs,Wm)−f(Hs,Ws); DH=f(Hb,Wm)−f(Hs,Wm); Dtotal=DW+DH exactly. This is an ordered mathematical decomposition, not an independent causal partition of anatomy. C=|DW|+|DH|−|Dtotal| is nonnegative within floating-point tolerance; opposing signs indicate cancellation.

| method | mean | median | mean_ci95 | opposing_observation_fraction |
| --- | --- | --- | --- | --- |
| P | 0.640 | 0.382 | [0.531, 0.767] | 0.451 |
| B1 | 1.366 | 0.804 | [1.136, 1.606] | 0.686 |
| B3_offset | 0.945 | 0.471 | [0.785, 1.117] | 0.589 |

B1 cancellation averages 1.365921 pp versus P 0.640088 pp. Opposing contributions occur in 68.62% of B1 observations versus 45.13% of P observations; offset is intermediate. For each body:

`A_sourceH − A_actual = (C_B1 − C_P) − (|DH_B1| − |DH_P|)`.

The identity is verified numerically for every comparison. Paired cancellation differences quantify both terms and their participant uncertainty. The mean B1-minus-P cancellation difference is +0.725833 pp; the mean difference in absolute height contributions is −0.065894 pp. Their difference exactly equals the +0.791727 pp mean advantage shift. Increased cancellation and method-specific height sensitivity explain the estimand shift algebraically; they do not prove improved anatomical measurement or physiology. The case table retains instances where cancellation does not align with the winner.

## 15. Compensating-waist derivation and empirical findings

Setting f(Hb,Wcomp)=f(Hs,Ws) yields **Wcomp=Ws·Hb/Hs**. It is a mathematical counterfactual, not an anatomical waist. Each private record retains source waist, actual measured waist, Wcomp, distance to each reference, exact formula drift and preferred method. T7 counts cases where a farther source waist gives closer actual formula agreement; offset distribution reports Wcomp−Ws. T5 includes signed source-waist errors and compensating-waist distances by method, pathway and state. Inverse-waist nonlinearity means distance to Wcomp alone is not used to rank formula errors. Figure S1-5 shows real favourable, contrary and unchanged examples with private record links, selected only for illustration after the full cohort analysis.

## 16. Participant-level ranking reversals

| actual_preference | controlled_preference | count | denominator | fraction |
| --- | --- | --- | --- | --- |
| P | P | 38 | 149 | 0.255 |
| P | B1 | 8 | 149 | 0.054 |
| B1 | P | 44 | 149 | 0.295 |
| B1 | B1 | 59 | 149 | 0.396 |

The 52 switches comprise 44 B1→P and 8 P→B1. Thirty-eight people favour P in both actual and sourceH comparisons; 59 favour B1 in both. The mean shift is +0.791727 pp, median +0.238475 pp. This is the change in evaluation estimand, not a causal intervention effect. T6 also records observation-level changes, bodyH transitions and all pathway/state strata. Numerical ties use 1e-10 pp; |advantage|≤0.1 pp is a purely descriptive small-difference flag, not a clinical equivalence threshold. Associations relate participant shifts to signed height discrepancy and compensation; they are descriptive.

## 17. End-to-end versus common-contour sensitivity

| mode | first | second | people | observations | mean | mean_ci95 |
| --- | --- | --- | --- | --- | --- | --- |
| end_to_end | P | B1 | 149 | 596 | 0.140 | [-0.026, 0.323] |
| end_to_end | P | B3_offset | 149 | 596 | -0.261 | [-0.399, -0.128] |
| end_to_end | B1 | B3_offset | 149 | 596 | -0.401 | [-0.536, -0.282] |
| site_raw | P | B1 | 148 | 592 | 0.126 | [-0.045, 0.313] |
| site_raw | P | B3_offset | 148 | 592 | -0.251 | [-0.393, -0.120] |
| site_raw | B1 | B3_offset | 148 | 592 | -0.378 | [-0.506, -0.261] |
| site_tape | P | B1 | 148 | 592 | 0.160 | [-0.014, 0.348] |
| site_tape | P | B3_offset | 148 | 592 | -0.237 | [-0.383, -0.103] |
| site_tape | B1 | B3_offset | 148 | 592 | -0.397 | [-0.528, -0.276] |

End-to-end retains original P raw circumference against official clad-body convex/hull output and a raw source proxy: a functional mismatch. Common raw compares saved identical indexed raw extractors at both sites with the raw source proxy. Common tape compares all sites with the saved tape-envelope functional and its tape source proxy. Offset is evaluated under the same respective functional. The 148-person complete common-raw/tape P–B1 intervals still span zero; offset's advantage over P persists. The reference is never swapped between raw and tape by outcome. Common-functional missingness and all-available estimates remain explicit rather than silently replacing the primary cohort.

## 18. Identity-anchored height-policy evaluation

Only **103/150** identities have source heights agreeing across both pathways to the frozen 1e-8 engineering-cm tolerance with the documented descriptor/pose protocol and verified own-pose linkage. All 103 have complete end-to-end waist endpoints. **47 identities are ineligible for one cross-path identity anchor** because their frozen source height descriptors disagree (range among those identities: 0.000400 to 0.233800 engineering cm). No averaging or favourable source selection resolves this. Their pathway-specific sourceH sensitivities remain available in the full-cohort analysis; they are not represented as a single identity descriptor. No source height is manufactured for another dataset.

| method | policy | people | mean_absolute | mean_absolute_ci95 | coordinate_sd_of_person_means_pp | mean_within_person_four_body_sd_pp |
| --- | --- | --- | --- | --- | --- | --- |
| P | A_reconstructed_extent | 103 | 2.096 | [1.802, 2.405] | 4.916 | 1.260 |
| P | B_source_identity_anchor | 103 | 1.332 | [1.155, 1.511] | 4.709 | 1.053 |
| B1 | A_reconstructed_extent | 103 | 1.477 | [1.255, 1.739] | 3.951 | 0.663 |
| B1 | B_source_identity_anchor | 103 | 1.273 | [1.092, 1.473] | 4.117 | 0.361 |
| B3_offset | A_reconstructed_extent | 103 | 1.539 | [1.340, 1.764] | 4.459 | 0.846 |
| B3_offset | B_source_identity_anchor | 103 | 1.016 | [0.884, 1.162] | 4.408 | 0.440 |

For the eligible 103 people, anchoring reduces mean absolute source-formula drift for P, B1 and offset. This reduction partly uses the reference height on both sides by construction. Dispersion does not uniformly shrink: between-person coordinate dispersion falls for P but rises for B1; within-person four-body dispersion falls for all three. Ranking consistency counts switches and mixed body preferences: among the 103 eligible people, 33 switch participant preference (25 B1→P and 8 P→B1). Mixed preferences across the four bodies increase from 71 to 89 identities after anchoring, a contrary policy finding. Height anchoring removes one input source of variability, while remaining source/site/pathway differences still matter. It changes the reported label and **hides reconstruction height errors unless Hb and Hb−Hs remain separately stored**.

This is a practical candidate only for these documented saved-identity engineering descriptors, conditional on their acquisition/pose conventions. Clinical stature, exact cross-path anatomical pose equality and robust anatomical invariance are unqualified. A future generator must supply a consistent identity descriptor explicitly; these data do not demonstrate that every arbitrary future synthetic identity has one. Qualified clinical identity-anchor availability is zero.

## 20. Physical calibration and anatomical limitations

All lengths are engineering units; a common unit conversion establishes dimensional consistency, not physical calibration. Source-waist references depend on historical MHR-mapped landmarks and the project selector (R3). They are neither independent observed waists nor independently specified anatomical source sites. Mesh extent is not clinical stature; project waist sites do not implement the original right-ilium RFM protocol. Acquisition pose, feet and head-envelope differences remain relevant. No linked independent BF observations are introduced. The clinical validation in the original RFM paper does not transfer automatically to these digital proxies.

## 21. Implications for synthetic BF labelling

Store formula version, saved measurement method/site, contour functional, geometric height, optional eligible identity anchor, source reference, pose and policy together. Keep source/formula drift, actual geometry error and physiological accuracy distinct. Consistent descriptors can make an engineering label more reproducible, but compensation may make a less accurate waist seem better under actual-height RFM. Retain anthropometric and geometric errors separately so lower formula drift cannot conceal them. No absolute BF labels or new prediction models are produced here.
