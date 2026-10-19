# Aggregate data dictionary

The machine-readable [dictionary](data_dictionary.json) enumerates every released JSON field and table, including nested figure inputs. Counts are specific to each estimand; do not pool linked pathways/states. Null means missing or not estimable, never zero.

Engineering cm/m are working-frame lengths. Equation-response pp describe differences in q = −20H/W, with an arbitrary zero; they are not body-fat estimates. SD ratios, correlations and CCC are dimensionless. Frozen bootstrap intervals and descriptive Bland–Altman limits are distinct.

| Table | Units | Estimand |
|---|---|---|
| agreement-extent-waist.json | engineering cm except correlations/CCC | New descriptive audit extension: CCC population moments, Pearson r, and Bland-Altman target-source bias +/-1.96 sample SD; one value per person per stratum; no confidence intervals |
| agreement-waist-methods.json | engineering cm except correlations/CCC | New descriptive audit extension on the exact complete 149-person cohort: source versus body waist; state/pathway strata stay separate |
| canonical-fallback-strata.json | counts; dimensionless Spearman/SD ratios; engineering cm for extent/surface error | Saved canonical P-body fallback flag on the complete 149-person paired NICP cohort; overlapping participant strata |
| canonical-offset-minus-P.json | equation-response pp | Paired-person difference of absolute canonical cross-path q disagreement, offset minus P, H2 |
| claim-traceability.json | counts; dimensionless Spearman/SD ratios; engineering cm for extent/surface error | Six manuscript claim summaries, reconstructed from the explicitly named frozen result tables and full model-control metadata |
| E1-T3-global.json | Saved engineering working metres for geometric discrepancy; explicit cm display fields are separate. | Frozen E1-T3-global; grouped by the row labels. Original estimates/intervals are retained. |
| E1-T5-correction-comparisons.json | Saved engineering working metres for geometric discrepancy; explicit cm display fields are separate. | Frozen E1-T5-correction-comparisons; grouped by the row labels. Original estimates/intervals are retained. |
| E2-1-all-paired-effects.json | metric-dependent; cm, ratios or counts | Frozen paired-effect summaries with original intervals; partitions, metric, state and contrast specify denominator/sign |
| E2-1-height-all-arms.json | engineering cm; dimensionless ratios | Source-defined between-person extent SD and fitted/source or canonical/source SD ratios; partitions remain separate |
| E2-1-midpoint-waist-changes.json | engineering cm | Paired change in midpoint waist absolute error; C minus B unless contrast states otherwise; original intervals |
| E2-1-midpoint-waist.json | engineering cm | Midpoint-proxy signed target-source errors and absolute errors by state/arm on valid paired subset; n=1 is a case summary without interval |
| E2-1-paired-effects.json | Engineering cm for extent/circumference/errors; ratios/correlations dimensionless; counts integer. | Frozen paired-effects; grouped by the row labels. Original estimates/intervals are retained. |
| E2-1-T4-height.json | Engineering cm for extent/circumference/errors; ratios/correlations dimensionless; counts integer. | Frozen E2-1-T4-height; grouped by the row labels. Original estimates/intervals are retained. |
| E2-2-all-paired-effects.json | metric-dependent; cm, ratios or counts | Frozen paired-effect summaries with original intervals; partitions, metric, state and contrast specify denominator/sign |
| E2-2-group-arms.json | engineering cm | Development-only source-surface fidelity for planned control and rig-prior arms; n=4, no heldout inference for G1-G4/R4 |
| E2-2-height-all-arms.json | engineering cm; dimensionless ratios | Source-defined between-person extent SD and fitted/source or canonical/source SD ratios; partitions remain separate |
| E2-2-midpoint-waist.json | engineering cm | Midpoint-proxy signed target-source errors and absolute errors by state/arm on valid paired subset; n=1 is a case summary without interval |
| E2-2-paired-effects.json | Engineering cm for extent/circumference/errors; ratios/correlations dimensionless; counts integer. | Frozen paired-effects; grouped by the row labels. Original estimates/intervals are retained. |
| E2-2-regularization-arms.json | engineering cm | Development-only source-surface fidelity for planned control and rig-prior arms; n=4, no heldout inference for G1-G4/R4 |
| E2-2-T5-stability.json | Engineering cm for extent/circumference/errors; ratios/correlations dimensionless; counts integer. | Frozen E2-2-T5-stability; grouped by the row labels. Original estimates/intervals are retained. |
| E2-2-T7-height.json | Engineering cm for extent/circumference/errors; ratios/correlations dimensionless; counts integer. | Frozen E2-2-T7-height; grouped by the row labels. Original estimates/intervals are retained. |
| E2-T3-preservation.json | Engineering cm for extent/circumference/errors; ratios/correlations dimensionless; counts integer. | Frozen E2-T3-preservation; grouped by the row labels. Original estimates/intervals are retained. |
| E3-T2-geometry.json | Engineering cm for canonical RMS and girths/extents. | Frozen E3-T2-geometry; grouped by the row labels. Original estimates/intervals are retained. |
| E3-T3-repeatability.json | Engineering cm for canonical RMS and girths/extents. | Frozen E3-T3-repeatability; grouped by the row labels. Original estimates/intervals are retained. |
| E4-T4-change.json | Engineering cm for extent/circumference/errors; ratios/correlations dimensionless; counts integer. | Frozen E4-T4-change; grouped by the row labels. Original estimates/intervals are retained. |
| E5-T3-source-to-canonical.json | equation-response pp | Mean absolute and signed historical source-to-canonical q response; original 2000-draw person bootstrap |
| E5-T6S-primary-person-mean.json | Equation-response percentage points (q=-20H/W, arbitrary zero), except SD ratios dimensionless and eligibility thresholds cm. | Frozen E5-T6S-primary-person-mean; grouped by the row labels. Original estimates/intervals are retained. |
| E5S1-T3-three-way-formula-agreement.json | Equation-response percentage points (q=-20H/W, arbitrary zero), except SD ratios dimensionless and eligibility thresholds cm. | Frozen E5S1-T3-three-way-formula-agreement; grouped by the row labels. Original estimates/intervals are retained. |
| E5S1-T4-pathway-state-effects.json | equation-response pp | Saved participant-mean paired method contrasts by pathway/state; original intervals |
| E5S1-T5-error-compensation.json | Equation-response percentage points (q=-20H/W, arbitrary zero), except SD ratios dimensionless and eligibility thresholds cm. | Frozen E5S1-T5-error-compensation; grouped by the row labels. Original estimates/intervals are retained. |
| E5S1-T6-ranking-reversals.json | Equation-response percentage points (q=-20H/W, arbitrary zero), except SD ratios dimensionless and eligibility thresholds cm. | Frozen E5S1-T6-ranking-reversals; grouped by the row labels. Original estimates/intervals are retained. |
| Figure2-manuscript-input.json | engineering cm/metre strings | Exact frozen rows selected by original manuscript figure generator |
| Figure5-manuscript-input.json | panel_a cm; panel_b response pp | Exact frozen rows selected by original manuscript figure generator |
| height-variation-control-audit.json | Engineering cm for extent/circumference/errors; ratios/correlations dimensionless; counts integer. | Frozen height-variation-control-audit; grouped by the row labels. Original estimates/intervals are retained. |
| NOMO-cohort-selection.json | people counts | Frozen 150-person selection, provider source sex-category labels; labels not inferred from geometry or independently clinically verified |
| paper_tables.json | Exact manuscript display strings; units are in table captions/column labels. | Frozen paper_tables; grouped by the row labels. Original estimates/intervals are retained. |
| S2-T10-policy-tradeoffs.json | Equation-response percentage points (q=-20H/W, arbitrary zero), except SD ratios dimensionless and eligibility thresholds cm. | Frozen S2-T10-policy-tradeoffs; grouped by the row labels. Original estimates/intervals are retained. |
| S2-T3-height-eligibility.json | Equation-response percentage points (q=-20H/W, arbitrary zero), except SD ratios dimensionless and eligibility thresholds cm. | Frozen S2-T3-height-eligibility; grouped by the row labels. Original estimates/intervals are retained. |
| S2-T4-canonical-cross-path.json | Equation-response percentage points (q=-20H/W, arbitrary zero), except SD ratios dimensionless and eligibility thresholds cm. | Frozen S2-T4-canonical-cross-path; grouped by the row labels. Original estimates/intervals are retained. |
| S2-T6-repeated-consistency.json | Equation-response percentage points (q=-20H/W, arbitrary zero), except SD ratios dimensionless and eligibility thresholds cm. | Frozen S2-T6-repeated-consistency; grouped by the row labels. Original estimates/intervals are retained. |
| S2-T7-coordinate-diversity.json | Equation-response percentage points (q=-20H/W, arbitrary zero), except SD ratios dimensionless and eligibility thresholds cm. | Frozen S2-T7-coordinate-diversity; grouped by the row labels. Original estimates/intervals are retained. |
| S2-T8-dependent-reference.json | Equation-response percentage points (q=-20H/W, arbitrary zero), except SD ratios dimensionless and eligibility thresholds cm. | Frozen S2-T8-dependent-reference; grouped by the row labels. Original estimates/intervals are retained. |
| strict-height-mismatches.json | engineering cm; counts | Strict-height eligibility and summary of absolute released-source extent disagreements among the 47 ineligible people |
| UCSC-feet-before-after.json | engineering cm | Paired correction diagnostic, descriptive regional RMS means, not pooled vertex RMS |
| W-T4-dataset-agreement.json | Engineering cm for extent/circumference/errors; ratios/correlations dimensionless; counts integer. | Frozen W-T4-dataset-agreement; grouped by the row labels. Original estimates/intervals are retained. |
| W-T5-full-NOMO.json | Engineering cm for extent/circumference/errors; ratios/correlations dimensionless; counts integer. | Frozen W-T5-full-NOMO; grouped by the row labels. Original estimates/intervals are retained. |
| waist-fallback-counts.json | counts | Saved flags on exact 149-person complete paired cohort. Source is reused across body states; state rows are not independent source observations |

## Field definitions

| Field | Meaning |
|---|---|
| `CI95` | Original 95% participant-bootstrap interval for comparator-minus-P advantage. |
| `G1` | Original spine and neck control group. |
| `G2` | Original leg and foot control group. |
| `G3` | Original upper-arm and forearm control group. |
| `G4` | Original shoulder-width and hip-width control group. |
| `actual_preference` | Stratum/definition metadata: actual preference. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `after_cm` | Mean of participant regional foot RMS after correction, converted from working m to cm. |
| `alignment` | Stratum/definition metadata: alignment. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `all_translation_only` | True when recorded source alignment is translation-only; translation preserves extent. |
| `anchor_construction` | How linked source extents form the shared/source anchor. |
| `arm` | E2-1 source, historical A, locked B, released C or contextual comparator arm. |
| `audited_controls` | Number of all model parameters inspected, including unreleased and fixed-domain controls. |
| `before_cm` | Mean of participant regional foot RMS before correction, converted from working m to cm. |
| `bias` | Mean target minus source; in paired-effect tables, mean signed named contrast instead. |
| `body_fallback_count` | Number of reconstructed bodies whose saved P selector fallback flag is true. |
| `body_observations` | Linked body/pathway/state observations; not independent people. |
| `body_only` | Count with body fallback and no source fallback. |
| `body_pairs` | Paired body observations nested within participants. |
| `both_strata_people` | Unique complete people with fallback on one pathway and no fallback on the other; overlap of the two person strata. |
| `canonical_P_fallback` | Canonical reconstructed P-selector fallback summary on complete paired NICP people; source-side flags are separate. |
| `canonical_sd` | Between-person canonical extent SD. |
| `canonical_to_source_sd_ratio` | Canonical extent SD divided by source extent SD. |
| `caption` | Provenance or frozen display metadata: caption. No participant record is identified. |
| `ccc` | Lin concordance correlation coefficient: 2 population covariance/(population variance source + target + squared mean difference). |
| `ccc_moment_ddof` | Moment divisor convention for CCC: zero means divide by n. |
| `ci` | Original selected confidence interval endpoints; units follow figure panel. |
| `ci95` | Original exploratory 95% paired-person interval; not Bland–Altman limits. |
| `clinical_stature_qualified` | Whether independent clinical stature calibration is established; strict equality does not establish it. |
| `cohort` | Eligibility-defined population for this calculation. |
| `cohort_build_and_provider_categories` | Frozen distinct-person selection-stage and provider-category totals, before the 149-person paired analysis filter. |
| `collection` | Source representation pathway or paired-pathway aggregate. |
| `columns` | Provenance or frozen display metadata: columns. No participant record is identified. |
| `comparator_MAE` | Comparator mean absolute error against the named dependent source proxy. |
| `comparator_P95_AE` | Comparator P95_AE against the named source proxy; absolute errors where AE appears; fraction is dimensionless. |
| `comparator_RMSE` | Comparator RMSE against the named source proxy; absolute errors where AE appears; fraction is dimensionless. |
| `comparator_bias` | Comparator bias against the named source proxy; absolute errors where AE appears; fraction is dimensionless. |
| `comparator_fraction` | Comparator fraction against the named source proxy; absolute errors where AE appears; fraction is dimensionless. |
| `comparator_median_AE` | Comparator median_AE against the named source proxy; absolute errors where AE appears; fraction is dimensionless. |
| `comparison_group` | Common-participant set used for all objectives of a policy comparison. |
| `complete_six` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `condition` | E2-2 A=historical, B=locked, C=released, D=quarter prior; G1-G4/R4 are development-only mechanisms. |
| `confidence_intervals_recomputed` | False: the audit agreement extension does not recompute or claim manuscript confidence intervals. |
| `contrast` | Saved condition difference, e.g. C-B is released minus locked; repeat labels preserve their own order. |
| `control_domains` | Complete native model-control audit summary, separate from the nine released controls. |
| `controlled` | Stratum/definition metadata: controlled. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `controlled_preference` | Stratum/definition metadata: controlled preference. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `count` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `coverage` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `cross_path_mae_pp` | Canonical absolute q disagreement between linked source pathways, averaged within person then across people. |
| `dataset` | Source dataset family. |
| `denominator` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `development_mechanisms` | Four-person development summaries for B, C, G1–G4, noG1/noG2 and R025/R4, separately by linked pathway. |
| `difference_sd` | Sample SD (ddof=1) of target-minus-source paired differences. |
| `difference_sd_ddof` | Degrees of freedom removed when computing SD of differences: 1. |
| `differing_max_cm` | Absolute source-extent disagreement among the 47 strict-ineligible participants: max in engineering cm. |
| `differing_mean_cm` | Absolute source-extent disagreement among the 47 strict-ineligible participants: mean in engineering cm. |
| `differing_median_cm` | Absolute source-extent disagreement among the 47 strict-ineligible participants: median in engineering cm. |
| `differing_min_cm` | Absolute source-extent disagreement among the 47 strict-ineligible participants: min in engineering cm. |
| `direction` | Explicit subtraction order and direction of preference. |
| `discarded_constant_source_draws` | Bootstrap draws discarded because a ratio denominator had zero source variation. |
| `dominated_by` | Saved policy IDs dominating the row on that full point-estimate grid. |
| `draws` | Frozen bootstrap draws; not additional observations. |
| `effect` | Stratum/definition metadata: effect. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `eligible` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `eligible_people` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `estimand` | The population quantity or descriptive summary targeted by this table/row. |
| `explanation` | Provenance or frozen display metadata: explanation. No participant record is identified. |
| `fallback` | Saved reconstructed P-side selector fallback flag; true and false define the two overlapping-person strata. |
| `fallback_count` | Number with the table's declared reconstructed-measurement fallback. |
| `fallback_observations` | Canonical body/pathway observations with saved P fallback true; two observations per complete person. |
| `fallback_people` | Unique complete people with at least one canonical pathway using P fallback. |
| `female_source_category` | Count of provider female-labelled source records, not inferred biological sex. |
| `first` | First method/policy in the saved comparison. |
| `fitted_height_mae_cm` | Mean absolute fitted-versus-source vertical-extent difference within the declared development arm/pathway. |
| `fitted_sd` | Between-person fitted extent SD. |
| `fitted_to_source_sd_ratio` | Fitted extent SD divided by source extent SD. |
| `fraction_abs_gt_1_pp` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `fraction_abs_gt_3_pp` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `fraction_abs_gt_5_pp` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `height_eligible_people` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `height_policy` | H1 own extent, H2 source anchor, H3 shared anchor conditional on the named eligibility threshold. |
| `id` | Provenance or frozen display metadata: id. No participant record is identified. |
| `incomplete_people_excluded` | Otherwise eligible people excluded because one of the two canonical NICP pathways is missing. |
| `independent_unit` | Unit resampled or summarised for inference; linked records stay within person. |
| `index` | Zero-based native model-parameter index. |
| `interval` | Frozen uncertainty construction and exploratory status. |
| `invalid_source` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `invalid_target` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `iqr` | Saved iqr of the declared outcome, at the named observation/person level. |
| `label` | Provenance or frozen display metadata: label. No participant record is identified. |
| `loa_lower` | Descriptive lower Bland–Altman limit: bias minus 1.96 difference_sd. |
| `loa_multiplier` | Normal-theory SD multiplier, 1.96; these limits are not confidence intervals. |
| `loa_upper` | Descriptive upper Bland–Altman limit: bias plus 1.96 difference_sd. |
| `lod` | Stratum/definition metadata: lod. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `mae` | Mean absolute error/difference for the declared metric; not necessarily physiological accuracy. |
| `mae_ci95` | Original participant-bootstrap interval for MAE. |
| `male_source_category` | Count of provider male-labelled source records, not inferred biological sex. |
| `markdown` | Provenance or frozen display metadata: markdown. No participant record is identified. |
| `maximum` | Authored maximum for the named control in the zero-domain claim table; other tables use the maximum of their named outcome. |
| `mean` | Arithmetic mean of the named statistic; independent unit and aggregation are defined by the table/stratum. |
| `mean_absolute` | Mean absolute signed-response difference; distinct from the absolute value of the cohort mean. |
| `mean_absolute_ci95` | Original participant-bootstrap interval for mean absolute difference. |
| `mean_advantage` | Comparator absolute error minus P absolute error; positive favours P. |
| `mean_ci95` | Original 95% participant-bootstrap interval for the saved mean. |
| `mean_ci95_engineering_cm_text` | Exact original interval display strings, in the unit embedded in the key; no new conversion or inference. |
| `mean_ci95_engineering_m_text` | Exact original interval display strings, in the unit embedded in the key; no new conversion or inference. |
| `mean_ci_family` | Label of confidence interval family/coverage. |
| `mean_engineering_cm_text` | Exact original mean display string, in the unit embedded in the key. |
| `mean_engineering_m_text` | Exact original mean display string, in the unit embedded in the key. |
| `mean_source` | Arithmetic mean of the complete source values. |
| `mean_target` | Arithmetic mean of the complete target values. |
| `mechanism_groups` | Original E2-2 groups of released control names; G1 axial, G2 lower limb, G3 arm, G4 widths. |
| `median` | Median of the named statistic over the table's declared independent units. |
| `median_absolute` | Median absolute difference. |
| `median_advantage` | Median comparator-minus-P absolute error difference. |
| `median_ci95` | Original 95% participant-bootstrap interval for the saved median. |
| `method` | Saved functional/site definition; historical waist and E2 midpoint are distinct. |
| `metric` | Named outcome definition; _cm indicates engineering centimetres, ratios/correlations are dimensionless. |
| `minimum` | Authored minimum for the named control in the zero-domain claim table; other tables use the minimum of their named outcome. |
| `missing` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `mode` | Measurement functional comparison, e.g. end_to_end versus site controls. |
| `n` | Independent-unit count defined by the table/metric; do not sum linked pathways or states. |
| `n_observations` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `n_participants` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `name` | Native control name. |
| `negative_fraction` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `neither` | Count with neither selector fallback flag. |
| `non_dominated` | Frozen descriptive membership on the complete three-objective policy grid; not statistical dominance. |
| `nonfallback_observations` | Canonical body/pathway observations with saved P fallback false. |
| `nonfallback_people` | Unique complete people with at least one canonical pathway without P fallback. |
| `observation_median` | Saved observation median of the declared outcome, at the named observation/person level. |
| `observation_negative_fraction` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `observation_p90_absolute` | Saved observation p90 absolute of the declared outcome, at the named observation/person level. |
| `observation_p95_absolute` | Saved observation p95 absolute of the declared outcome, at the named observation/person level. |
| `observation_positive_fraction` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `observation_ties` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `observations` | Linked observations contributing to person-level aggregation; not independent people. |
| `ours_MAE` | P mean absolute error against the named dependent source proxy. |
| `ours_P95_AE` | P P95_AE against the named source proxy; absolute errors where AE appears; fraction is dimensionless. |
| `ours_RMSE` | P RMSE against the named source proxy; absolute errors where AE appears; fraction is dimensionless. |
| `ours_bias` | P bias against the named source proxy; absolute errors where AE appears; fraction is dimensionless. |
| `ours_fraction` | P fraction against the named source proxy; absolute errors where AE appears; fraction is dimensionless. |
| `ours_median_AE` | P median_AE against the named source proxy; absolute errors where AE appears; fraction is dimensionless. |
| `p90_absolute` | Saved p90 absolute of the declared outcome, at the named observation/person level. |
| `p95_absolute` | Saved p95 absolute of the declared outcome, at the named observation/person level. |
| `panel_a` | Figure 5 waist absolute-error advantages in engineering cm. |
| `panel_b` | Figure 5 equation-response advantages in pp, with original intervals. |
| `participant_p90_absolute` | Saved participant p90 absolute of the declared outcome, at the named observation/person level. |
| `participant_p95_absolute` | Saved participant p95 absolute of the declared outcome, at the named observation/person level. |
| `participants` | Dataset-local independent participants represented by this row. |
| `partition` | Development, first evaluation or disjoint heldout evaluation; populations must remain separate. |
| `pathway` | Linked source representation route; pathways do not create independent participants. |
| `pearson` | Pearson source-target correlation in the frozen height table. |
| `pearson_r` | Pearson product-moment correlation; measures association, separately from agreement. |
| `people` | Independent dataset-local participants in this specific estimand. |
| `people_with_nonzero_rig_morphology` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `person_negative_count` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `person_negative_fraction` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `person_positive_count` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `person_positive_fraction` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `person_ties` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `physiological_accuracy` | False/unqualified: agreement is with a dependent digital proxy, not clinical BF truth. |
| `policy` | Named formula-response control (actual, sourceH, bodyH) or height eligibility policy. |
| `policy_id` | Waist method/height policy pair. |
| `population` | Stratum/definition metadata: population. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `positive_favours` | Saved sign convention; consult this field before interpreting paired advantages. |
| `positive_fraction` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `primary_family` | Stratum/definition metadata: primary family. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `proportion_people_mean_negative` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `proportion_people_mean_positive` | Proportion in the named sign/threshold category, using the stated participant or observation denominator; range 0–1. |
| `q05` | Saved 05th percentile of the named outcome; quantile_unit identifies its level. |
| `q25` | Saved 25th percentile of the named outcome; quantile_unit identifies its level. |
| `q75` | Saved 75th percentile of the named outcome; quantile_unit identifies its level. |
| `q95` | Saved 95th percentile of the named outcome; quantile_unit identifies its level. |
| `quantile_unit` | Whether quantiles summarise observations or participant summaries. |
| `reference` | Named dependent source reference definition. |
| `reference_mae_pp` | Canonical absolute q deviation from the dependent source coordinate on the stated common cohort. |
| `region` | Stratum/definition metadata: region. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `released_controls` | Number of controls in the released fitting set. |
| `replicates` | Frozen bootstrap draws; not additional participants. |
| `rmse` | Root mean squared error/difference for the declared metric. |
| `rows` | Provenance or frozen display metadata: rows. No participant record is identified. |
| `rule` | Stratum/definition metadata: rule. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `schema_version` | Version of the compiled claim JSON schema. |
| `sd` | Sample standard deviation for the declared independent-unit statistic. |
| `sd_person_mean` | Sample SD across participant-mean observations. |
| `sd_ratio` | Target/source between-person SD ratio; dimensionless. |
| `sd_ratio_ci95` | Original participant-bootstrap interval for the target/source SD ratio. |
| `sd_ratio_distance` | Saved third Pareto objective: absolute natural logarithm of the canonical/source SD ratio. |
| `second` | Second method/policy in the saved comparison. |
| `seed` | Frozen pseudo-random bootstrap seed; preserving order is required for exact finite-draw replay. |
| `selected_observations` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `selected_people` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `selection` | Frozen retained/replacement/additional source-selection stage. |
| `selection_counts` | Counts by retained, replacement and additional frozen selection stage. |
| `site` | Stratum/definition metadata: site. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `slope` | Target-on-source regression slope for the declared extent table. |
| `source_and_body` | Count with both source and reconstructed-body selector fallback flags. |
| `source_csv_line` | Provenance or frozen display metadata: source csv line. No participant record is identified. |
| `source_csv_line_one_based` | Provenance or frozen display metadata: source csv line one based. No participant record is identified. |
| `source_fallback_count` | Number of valid person/source-pathway observations whose saved historical adaptive selector fallback flag is true; reused across states. |
| `source_file` | Provenance or frozen display metadata: source file. No participant record is identified. |
| `source_height_anchor_available` | Availability of the required source extent anchor. |
| `source_only` | Count with source fallback and no body fallback. |
| `source_row` | Provenance or frozen display metadata: source row. No participant record is identified. |
| `source_sd` | Between-person SD of the linked source coordinate/extent. |
| `source_sha256` | Provenance or frozen display metadata: source sha256. No participant record is identified. |
| `spearman` | Spearman source-target rank correlation in the frozen height table. |
| `state` | Source, own-pose fitted or canonical reconstructed state. |
| `statistic` | Named statistic/contrast applied to the metric. |
| `stratum` | Saved pathway/state/pooled comparison group. |
| `strict_eligible` | People whose source extents agree under the frozen strict threshold. |
| `strict_ineligible` | People whose source extents fail the frozen strict threshold (47). |
| `subjects` | Dataset-local independent participants represented by this row. |
| `subset` | Stratum/definition metadata: subset. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `surface_mean_cm` | Arithmetic mean of the saved per-person surface mean discrepancies for the declared development arm/pathway. |
| `text_y_precision` | Number of serialized decimal places in metre OBJ y coordinates. |
| `threshold_cm` | Source-extent equality tolerance in engineering cm; not a clinical threshold. |
| `total_people` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `transition` | Stratum/definition metadata: transition. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `uncertainty` | Frozen uncertainty procedure and adjustment/coverage statement. |
| `unit` | Recorded working unit; engineering cm/m do not assert independent physical calibration. |
| `unknown_flags` | Count without an evaluable saved source/body flag; zero in this complete-cohort audit. |
| `valid_observations` | Count/denominator for the named eligibility, missingness or sign category; remains specific to this row. |
| `variant` | Stratum/definition metadata: variant. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `variation` | Stratum/definition metadata: variation. Its value names the saved analysis convention; see the table estimand and audit methods. |
| `zero_domain_claims` | Three specifically questioned unreleased controls with authored minimum=maximum=0; nonzero transform columns do not override these limits. |
| `zero_domain_count` | Count of all audited controls whose authored minimum and maximum both equal zero (37); distinct from the three named exclusions. |
