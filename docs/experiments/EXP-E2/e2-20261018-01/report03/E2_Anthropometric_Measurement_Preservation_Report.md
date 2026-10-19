# E2 Anthropometric Measurement Preservation and Anatomical Validation

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

## 1. Objective and hypotheses

Characterise direct digital measurement preservation (E2-A), external anthropometric eligibility/agreement (E2-B), and method/site/pose sensitivity (E2-C). H2.1 asks whether preservation changes differ by site; H2.2 concerns localisation; H2.3 concerns pose and cranial envelopes; H2.4 concerns fallback validity; H2.5 concerns pathways; H2.6 concerns independent physical observations. These are descriptive follow-up hypotheses on engineering-exposed participants, not untouched confirmatory tests. No scientific equivalence margins are approved.

## 2. Relationship to E0 and E4

Inputs are the frozen E0 `e0-unified-20261018-01` and E4 `e4-20261018-03/report02`. E4 measured changes in cross-path disagreement; E2 measures each native body's difference from its own source. E4's results and SITE_AMBIGUOUS/fallback fields remain historical evidence. E2 adds independent quality dimensions and alternate proxy measurements. Full E0/E4 directory fingerprints and source/package hashes are checked at verification. No fits, native forwards, source deformations, source dataset copies or migrations were needed.

## 3. Cohorts and linkage

## 4. Measurement definitions

E2-T2 and `measurement-registry.json` retain distinct IDs for global extent, intended anatomical waist, historical adaptive waist, atlas midpoint proxy, mapped umbilical abdomen, posterior pelvic A hip, chest proxy and historical neck. Raw closed-contour perimeter and convex tape envelope remain separate. Height is computed from actual vertices; girths use existing `IndexedSections`, with authored zero-edge equivalences and no arbitrary spatial welding. The E2 proxy source sites project their own fitted MHR atlas to source geometry: they do not supply independent anatomical annotation.

## 5. Standards and protocol compatibility

## 6. Historical workflow audit

`approved_t90.measure_approved_sites` searches the lower half of the mapped umbilicus-to-anterior-chest interval with `select_adaptive`. Its canonical fallback `waist_above_abdomen.apply_fallback` chooses **umbilicus Y + 0.005 engineering m** when the candidate is not PROXY_VALID. Released-pose `nomo_released_metrology.measure` uses that same offset when the adaptive result has no selected level. Neither implementation locates a palpable rib or iliac crest. Floating-point profile endpoints can also produce INVALID_PROFILE_COORDINATES; those original selection reasons are preserved, not treated as anatomical diagnoses. A new universal metrology engine was unnecessary.

The frozen atlas explicitly declares no qualified anatomical anchors. `lower_thorax_surface` and `upper_pelvis_surface` are model surface candidates, not verified rib/crest landmarks. Consequently the premise that the existing fallback already implements the intended rib-to-iliac midpoint is **not supported by the code**. This does not make every fallback contour anatomically implausible.

## 7. Waist validation and E4 reinterpretation

Selection method, site assessment, contour validity and external comparability are kept separate. A fallback with a valid closed contour remains eligible for engineering analysis. No independent human landmark review was fabricated. The supported E2 method uses the midpoint of the two frozen atlas candidates with a normal from c_spine0 to c_spine3; source candidates are projected from the corresponding fitted body. This is a **torso-frame atlas midpoint proxy**, never relabelled WHO waist. No site was chosen to minimise preservation error.

| collection | state | eligible | historical_valid | fallback_used | primary_used | midpoint_proxy_valid | mean_plane_y_shift_cm | median_local_range_cm | anatomically_supported |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAESAR-NICP | canonical | 150 | 150 | 116 | 34 | 150 | 2.1081 | 0.6317 | 0 |
| CAESAR-NICP | fitted | 150 | 150 | 70 | 80 | 150 | -1.0438 | 0.7657 | 0 |
| CAESAR-NICP | source | 150 | 149 | 150 | 0 | 1 | 3.7204 | 1.5308 | 0 |
| SMPL-LBFGSB | canonical | 60 | 60 | 32 | 28 | 60 | 0.6688 | 0.3972 | 0 |
| SMPL-LBFGSB | fitted | 60 | 0 | 0 | 0 | 60 | unavailable | 0.3492 | 0 |
| SMPL-LBFGSB | source | 60 | 0 | 0 | 0 | 60 | unavailable | 0.2929 | 0 |
| SMPL-NICP | canonical | 150 | 150 | 113 | 37 | 150 | 2.1047 | 0.6170 | 0 |
| SMPL-NICP | fitted | 150 | 150 | 63 | 87 | 150 | -1.3057 | 0.7566 | 0 |
| SMPL-NICP | source | 150 | 149 | 57 | 93 | 117 | -0.5707 | 0.7132 | 0 |

The perturbations are ±0.005 **engineering m** along the plane normal, not calibrated physical millimetres. Local range includes the baseline and both offsets and requires all three contours. Historical planes and baseline values remain intact. Twenty-four deterministic waist-error ranks were selected before full E2 remeasurement; materials include successful and failed proxy extractions, front and side views, source and fitted surfaces. The four waist-review sheets distinguish candidate anchors, historical contours and proxy contours. Their purpose is inspectable review evidence, not an invented human judgement.

E4's zero strict subset results from its filtering definition, not proof that all waists are invalid. E2 reports the all-geometrically-valid, primary-both, fallback-present-unreviewed, anatomically-reviewed-fallback and strict-anatomical subsets separately in `waist-subset-sensitivity.csv`. No independent rib/crest annotations are available, so the latter anatomical subsets remain empty. E2 therefore changes the interpretation of the strict exclusion, while leaving E4's recorded zero unchanged.

## 8. Height, posture and cranial-envelope analysis

| collection | diagnostic | n | mean | mean_ci95 | sd |
| --- | --- | --- | --- | --- | --- |
| CAESAR-NICP | above_neck_difference | 150 | -0.6148 | [-0.7812621221972733, -0.45085268725553557] | 1.0118 |
| CAESAR-NICP | below_neck_difference | 150 | 3.8335 | [3.230562313501154, 4.427361871324911] | 3.8482 |
| CAESAR-NICP | canonical_minus_fitted | 150 | 1.6753 | [0.8340287108191579, 2.5802689665673895] | 5.4520 |
| CAESAR-NICP | canonical_minus_source | 150 | 4.8939 | [3.4482291040655952, 6.439708596950196] | 9.3451 |
| CAESAR-NICP | fitted_minus_source | 150 | 3.2186 | [2.4721470542345996, 3.971386587047004] | 4.6075 |
| CAESAR-NICP | head_extent_difference | 150 | -0.5144 | [-0.6457755083862272, -0.3839057429280565] | 0.8474 |
| CAESAR-NICP | robust_top_effect | 150 | 1.3993 | [1.2715234588746742, 1.5329628071958017] | 0.8001 |
| SMPL-LBFGSB | above_neck_difference | 60 | -0.3389 | [-0.395448970794673, -0.28746566263834256] | 0.2173 |
| SMPL-LBFGSB | below_neck_difference | 60 | 0.2784 | [0.19209685172264773, 0.3630973681776464] | 0.3479 |
| SMPL-LBFGSB | canonical_minus_fitted | 60 | -0.1683 | [-0.425546850853912, 0.10198919888585704] | 1.0765 |
| SMPL-LBFGSB | canonical_minus_source | 60 | -0.2287 | [-0.5144153592387802, 0.042596044341727306] | 1.1260 |
| SMPL-LBFGSB | fitted_minus_source | 60 | -0.0605 | [-0.17493242287014318, 0.0416022796817167] | 0.4199 |
| SMPL-LBFGSB | head_extent_difference | 60 | -0.3281 | [-0.413642169301348, -0.2468631805725078] | 0.3362 |
| SMPL-LBFGSB | robust_top_effect | 60 | -0.3524 | [-0.41114611446451693, -0.2921727064904759] | 0.2400 |
| SMPL-NICP | above_neck_difference | 150 | -0.5849 | [-0.7503887384682917, -0.42850312074253766] | 0.9949 |
| SMPL-NICP | below_neck_difference | 150 | 3.7343 | [3.121869672283393, 4.36608970195677] | 3.8510 |
| SMPL-NICP | canonical_minus_fitted | 150 | 1.7024 | [0.8740401328472048, 2.59868122414546] | 5.4936 |
| SMPL-NICP | canonical_minus_source | 150 | 4.8518 | [3.3480304934487846, 6.45847709384829] | 9.3319 |
| SMPL-NICP | fitted_minus_source | 150 | 3.1494 | [2.437249338011068, 3.867849219066725] | 4.5822 |
| SMPL-NICP | head_extent_difference | 150 | -0.5160 | [-0.6723332106404594, -0.3732576598958298] | 0.9017 |
| SMPL-NICP | robust_top_effect | 150 | -0.1741 | [-0.30303470940413024, -0.04626872261116333] | 0.7889 |

Every historical extent was independently recomputed from the pinned LOD0 vertices. `fitted_minus_source` measures the actual direct discrepancy; `canonical_minus_fitted` measures the within-native articulation/corrective-associated change with identity and morphology fixed. All primary expression controls are preserved; LBFGSB canonical expression differs and remains a confounder. No inference regenerates or edits a body. Floor translations cancel in max-minus-min extent and cannot explain these differences.

The source neck plane is inherited from its fitted MHR rig, so above-/below-neck contributions are an exact **geometric partition** in the declared working frame, not independent source skeletal measurements. They sum to the observed height discrepancy. Native thigh/shank, root-to-neck and neck-to-head Euclidean lengths, vertical projections and angles are stored per branch; source rig segments are unavailable. A transferred official dominant-joint head/neck region gives upper-envelope descriptors; this is an engineering segmentation and is tessellation dependent. `robust_top_effect` is the change in discrepancy when substituting head-region Y-q99 for max Y, holding the floor metric fixed. It quantifies descriptor sensitivity, not removable hair volume.

Actual source/fitted/T90 bodies and head endpoints appear in the height gallery. Neither hair, scalp nor skull is independently identified. Posture-associated changes can be quantified within the native model, but cannot be subtracted as a validated causal fraction of source-to-MHR error. Head-envelope differences can be described; hairstyle incorporation remains a plausible, unconfirmed interpretation. Scaling errors, physiological posture effects and hair causes are not established by a shared mean shift.

The endpoint partition is also **relative-frame dependent**: translating only the fitted surface upward adds the translation to its top endpoint term and subtracts it from its bottom term, leaving total extent unchanged. The positive lower-end term therefore does not establish that the lower body was lengthened. The height engineering note demonstrates this invariance on every branch and provides versioned endpoint tags and explicit measurement-state metadata. This additive layer corrects no body, canonical selection or physical stature value. Endpoint-region counts route unusual maxima/minima to review without automatic exclusion.

An additional engineering finding is substantial height-variation compression in the primary NICP pathways. The saved morphology/rig-control slice 130:204 is exactly neutral for every primary candidate, while all 60 LBFGSB bodies retain nonzero values. The historical placement code explicitly declares native scale/length controls fixed at neutral; this is a documented parameter restriction, not evidence that all anatomical segment proportions were preserved merely because the controls stayed unchanged. Identity shape coefficients still vary. The common-60 analysis below checks that the contrast is not just caused by using different people. Association with frozen rig controls and differences in conversion/fitting pathways is a concrete target for a future controlled parameter ablation; causal attribution is not established without that experiment. No production configuration, fitting allowance or protected dataset was changed.

| population | collection | people | source_sd | fitted_sd | canonical_sd | canonical_to_source_sd_ratio | canonical_on_source_slope | people_with_nonzero_rig_morphology |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pathway_all_available | SMPL-NICP | 150 | 10.7840 | 6.7787 | 1.8634 | 0.1728 | 0.1405 | 0 |
| pathway_all_available | CAESAR-NICP | 150 | 10.7940 | 6.7459 | 1.8541 | 0.1718 | 0.1400 | 0 |
| pathway_all_available | SMPL-LBFGSB | 60 | 10.0694 | 9.8639 | 10.0865 | 1.0017 | 0.9954 | 60 |
| same_60_people | SMPL-NICP | 60 | 9.4656 | 5.3182 | 1.9527 | 0.2063 | 0.1743 | 0 |
| same_60_people | CAESAR-NICP | 60 | 9.4666 | 5.2753 | 1.9439 | 0.2053 | 0.1748 | 0 |
| same_60_people | SMPL-LBFGSB | 60 | 10.0694 | 9.8639 | 10.0865 | 1.0017 | 0.9954 | 60 |

See height variation and `height-variation-control-audit.csv`. The resulting regression-to-a-narrow-height-range pattern is stronger evidence of a representation/fitting restriction to investigate than a speculative hair explanation. The observed control restriction is verified; its causal share of the discrepancy remains unresolved.

## 9. E2-A digital preservation

The sign is MHR minus source. Rows below use historical source and own fitted MHR values, with site-specific geometrically valid pairs. Canonical-versus-source rows are reported separately in the full table because they also change articulation. LBFGSB girth baselines are historically absent rather than imputed.

| collection | site | n | eligible | mean | mean_ci95 | mae | rmse | median_absolute | p95_absolute | sd | loa_lower | loa_upper |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAESAR-NICP | abdomen | 149 | 150 | 0.3733 | [0.12001279173426806, 0.6479241006434796] | 1.4150 | 1.7227 | 1.2388 | 3.1871 | 1.6874 | -2.9340 | 3.6806 |
| CAESAR-NICP | chest | 1 | 150 | -0.3849 | unavailable | 0.3849 | 0.3849 | 0.3849 | 0.3849 | unavailable | unavailable | unavailable |
| CAESAR-NICP | height | 150 | 150 | 3.2186 | [2.487310550469885, 3.9586675843622245] | 4.4971 | 5.6078 | 3.7724 | 10.3366 | 4.6075 | -5.8121 | 12.2493 |
| CAESAR-NICP | hip | 150 | 150 | -0.6874 | [-0.8740956701744877, -0.5147454022036093] | 0.9944 | 1.3022 | 0.6794 | 2.6970 | 1.1097 | -2.8623 | 1.4876 |
| CAESAR-NICP | neck | 104 | 150 | -1.8473 | [-2.397917696644077, -1.299866840135323] | 2.5332 | 3.3869 | 2.1484 | 6.1485 | 2.8524 | -7.4381 | 3.7435 |
| CAESAR-NICP | waist | 149 | 150 | -2.7418 | [-3.565333045528485, -1.9815271411934898] | 3.9477 | 5.5344 | 2.4555 | 11.0784 | 4.8237 | -12.1963 | 6.7127 |
| SMPL-LBFGSB | abdomen | 0 | 60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| SMPL-LBFGSB | chest | 0 | 60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| SMPL-LBFGSB | height | 60 | 60 | -0.0605 | [-0.16322534637959893, 0.04582843680804326] | 0.3337 | 0.4208 | 0.2992 | 0.7092 | 0.4199 | -0.8835 | 0.7625 |
| SMPL-LBFGSB | hip | 0 | 60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| SMPL-LBFGSB | neck | 0 | 60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| SMPL-LBFGSB | waist | 0 | 60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| SMPL-NICP | abdomen | 150 | 150 | 0.6119 | [0.3420574033546415, 0.8892152182204297] | 1.4739 | 1.7825 | 1.3488 | 3.3550 | 1.6798 | -2.6805 | 3.9043 |
| SMPL-NICP | chest | 33 | 150 | -0.7029 | [-1.4533033352696876, 0.0009078481164703809] | 1.5880 | 2.1585 | 1.1477 | 4.5218 | 2.0725 | -4.7650 | 3.3591 |
| SMPL-NICP | height | 150 | 150 | 3.1494 | [2.448150773396282, 3.8826605013745814] | 4.4604 | 5.5475 | 3.6971 | 10.4715 | 4.5822 | -5.8318 | 12.1305 |
| SMPL-NICP | hip | 150 | 150 | -0.5502 | [-0.7310132883398114, -0.36997107361863113] | 1.0123 | 1.2725 | 0.8696 | 2.4691 | 1.1512 | -2.8066 | 1.7062 |
| SMPL-NICP | neck | 102 | 150 | -2.1426 | [-2.664171623783064, -1.6610685883906326] | 2.6218 | 3.3681 | 2.1964 | 6.7289 | 2.6115 | -7.2611 | 2.9759 |
| SMPL-NICP | waist | 149 | 150 | 0.1481 | [-0.6773186512853543, 0.9562151952772965] | 3.4587 | 5.1801 | 1.8773 | 11.0414 | 5.1955 | -10.0350 | 10.3313 |

Bias, MAE, RMSE, median/P95 absolute differences, sample SD and Bland–Altman limits are generated per pathway and measurement. These are proxy preservation statistics, not physical error tolerances. No acceptance threshold was imposed. Figure E2-4 shows the primary paired agreement data and biases; full 95% MAE/RMSE/P95 intervals and 98.75% four-site mean intervals are in E2-T3.

## 10. E2-B external anthropometry

The acquired MAT files link to 150/150 people and contain 63 distinct exact field names. The existing narrow MAT reader was reused without field renaming or unit inference. Positive, zero, negative and nonfinite values are counted separately; no undocumented zero-missingness convention was imposed. `NaturalWAIST_Circ`, `TrouserWAIST_Circ`, `HIP_Circ`, `Head_Top_Height`, `Neck_Circ` and other original fields remain distinct in private records. E2-T6 inventories every field.

There are **0 defensibly eligible physical-accuracy pairs**. No same-person calibration-and-validation cycle was introduced. Physical agreement errors and Figure E2-6 were not fabricated. This eligibility result does not invalidate the independently supported digital analyses.

## 11. Sixty-person three-pathway crossover

The common E2 atlas, indexed extraction, pelvic A rule and quantity definitions are reapplied to all three unchanged canonical bodies. Height uses the same extent definition. The participant-level wide table contains all 60 people, including unavailable outcomes. Historical results remain available separately. Native hip historical procedure differences are avoided for the common-method comparison, while expression and source-pathway differences remain.

| site | method | contrast | n | mean | mean_ci95 | mae | sd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| abdomen | E2_proxy_raw | SMPL-LBFGSB minus CAESAR-NICP | 60 | -4.8622 | [-5.6476684491787115, -4.092375063405152] | 4.9930 | 3.1365 |
| abdomen | E2_proxy_raw | SMPL-NICP minus CAESAR-NICP | 60 | 0.0143 | [-0.14178607146049088, 0.165879977444883] | 0.4580 | 0.6182 |
| abdomen | E2_proxy_raw | SMPL-NICP minus SMPL-LBFGSB | 60 | 4.8765 | [4.1258332401934785, 5.6285788579803215] | 4.9755 | 3.0169 |
| waist | E2_proxy_raw | SMPL-LBFGSB minus CAESAR-NICP | 60 | -3.5747 | [-4.439964537401752, -2.734393341164851] | 3.9491 | 3.4563 |
| waist | E2_proxy_raw | SMPL-NICP minus CAESAR-NICP | 60 | -0.0528 | [-0.19906393632099134, 0.08010356125060249] | 0.4162 | 0.5562 |
| waist | E2_proxy_raw | SMPL-NICP minus SMPL-LBFGSB | 60 | 3.5219 | [2.694529784596656, 4.324291259010831] | 3.9026 | 3.3226 |
| hip | E2_proxy_tape | SMPL-LBFGSB minus CAESAR-NICP | 60 | -2.1520 | [-2.9151934820774734, -1.4377443939127175] | 2.7642 | 2.8605 |
| hip | E2_proxy_tape | SMPL-NICP minus CAESAR-NICP | 60 | 0.0460 | [-0.14125794582314632, 0.22483727635738948] | 0.4927 | 0.7412 |
| hip | E2_proxy_tape | SMPL-NICP minus SMPL-LBFGSB | 60 | 2.1980 | [1.474824350064862, 2.910483321113209] | 2.8009 | 2.8899 |
| height | historical | SMPL-LBFGSB minus CAESAR-NICP | 60 | -7.1189 | [-9.30757843201359, -4.866673396453258] | 9.2163 | 8.7361 |
| height | historical | SMPL-NICP minus CAESAR-NICP | 60 | -0.0222 | [-0.07397472982605346, 0.030917987599970317] | 0.1637 | 0.2128 |
| height | historical | SMPL-NICP minus SMPL-LBFGSB | 60 | 7.0967 | [4.7603888558844725, 9.094011137758692] | 9.1926 | 8.7463 |

See E2-T7, paired traces and actual three-way bodies. Source and fitted contrasts are included in the full tables. Matching controls identity, not every factor in optimisation, expression, correspondence or pose. Cross-path consistency cannot identify the most accurate anatomy. All three direct-preservation pathways remain separately reported.

## 12. Statistics and uncertainty

The human participant is the independent sampling unit. Each statistic rejects duplicate people within its estimand; no pooling of repeated CAESAR branches occurs. E4's deterministic seed derivation, descriptive statistics and 2,000-draw participant bootstrap are reused. Bootstrap draws for bias, median, MAE, RMSE and P95 are saved privately. Mean intervals are percentile 95%; four-primary-site Bonferroni 98.75% intervals are available within pathway/state/method families. Analyses across alternate methods, secondary neck/chest, crossover contrasts and sensitivities are exploratory. There are no formal confirmatory p-values or approved equivalence conclusions. Observed SD describes between-person variation; algorithm alternatives are not calibrated uncertainty. Bootstrap intervals describe the selected exposed cohort under participant-resampling assumptions, not representative-population coverage.

## 13. Ablations and sensitivity

| collection | n | eligible | mean | mean_ci95 | mae | rmse | p95_absolute |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CAESAR-NICP | 1 | 150 | 1.6880 | unavailable | 1.6880 | 1.6880 | 1.6880 |
| SMPL-LBFGSB | 60 | 60 | 1.7315 | [1.4613188581543146, 1.9851185120753165] | 1.7465 | 2.0196 | 3.1847 |
| SMPL-NICP | 117 | 150 | -0.2133 | [-0.4075202467965775, -0.022017247032188176] | 0.8632 | 1.0965 | 2.0738 |

Participant records also retain a source-plane MHR diagnostic, plane offsets, raw/tape values, and the original historical waist contour re-extraction. These distinguish relocation, plane orientation, circumference functional and geometry differences without claiming one is anatomical truth. `surface-measurement-associations.csv` reports exploratory Spearman associations with E4's saved surface residuals; correlation is not agreement or causation.

**Matched method contrasts on common eligible people:**

| collection | contrast | n | eligible | mean | mean_ci95 | mae |
| --- | --- | --- | --- | --- | --- | --- |
| CAESAR-NICP | horizontal_source_to_mhr_error | 4 | 150 | -0.1795 | [-1.2546126404497215, 0.9731944510105173] | 1.0751 |
| CAESAR-NICP | own_plane_minus_source_plane_error | 1 | 150 | -0.0481 | unavailable | 0.0481 |
| CAESAR-NICP | proxy_minus_historical_absolute_error | 1 | 150 | -19.2950 | unavailable | 19.2950 |
| CAESAR-NICP | proxy_minus_historical_signed_error | 1 | 150 | 22.6710 | unavailable | 22.6710 |
| SMPL-LBFGSB | horizontal_source_to_mhr_error | 60 | 60 | 1.8024 | [1.510372140668975, 2.102985551099976] | 1.8407 |
| SMPL-LBFGSB | own_plane_minus_source_plane_error | 60 | 60 | 0.0057 | [0.0016588852239797182, 0.01035684846231816] | 0.0123 |
| SMPL-LBFGSB | proxy_minus_historical_absolute_error | 0 | 60 | unavailable | unavailable | unavailable |
| SMPL-LBFGSB | proxy_minus_historical_signed_error | 0 | 60 | unavailable | unavailable | unavailable |
| SMPL-NICP | horizontal_source_to_mhr_error | 116 | 150 | -0.0567 | [-0.27403987083967046, 0.14673278307011675] | 0.9366 |
| SMPL-NICP | own_plane_minus_source_plane_error | 117 | 150 | -0.0024 | [-0.011261785434025342, 0.006102464876314236] | 0.0233 |
| SMPL-NICP | proxy_minus_historical_absolute_error | 117 | 150 | -2.1030 | [-2.7810549703895036, -1.4667377380196116] | 2.4488 |
| SMPL-NICP | proxy_minus_historical_signed_error | 117 | 150 | -0.5993 | [-1.375389138732402, 0.19491403345434202] | 2.9434 |

The alternate midpoint proxy has poor source-CAESAR extraction coverage: 1/150 valid contours with a torso-normal plane and 4/150 with a horizontal plane at the same midpoint. All native MHR midpoint contours are valid in both orientations. These are method/topology/region-selection failures, not evidence of participant anatomical invalidity. The horizontal ablation does not resolve this limitation. The historical CAESAR preservation panel remains available on its own valid sites. Native segment diagnostics are in `native-segment-diagnostics.csv`.

| collection | state | eligible | oblique_valid | horizontal_valid | mean_tilt_degrees | anatomical_validated |
| --- | --- | --- | --- | --- | --- | --- |
| CAESAR-NICP | source | 150 | 1 | 4 | 2.7601 | 0 |
| CAESAR-NICP | fitted | 150 | 150 | 150 | 2.7601 | 0 |
| CAESAR-NICP | canonical | 150 | 150 | 150 | 0.6514 | 0 |
| SMPL-LBFGSB | source | 60 | 60 | 60 | 2.1827 | 0 |
| SMPL-LBFGSB | fitted | 60 | 60 | 60 | 2.1827 | 0 |
| SMPL-LBFGSB | canonical | 60 | 60 | 60 | 0.6877 | 0 |
| SMPL-NICP | source | 150 | 117 | 116 | 2.7325 | 0 |
| SMPL-NICP | fitted | 150 | 150 | 150 | 2.7325 | 0 |
| SMPL-NICP | canonical | 150 | 150 | 150 | 0.6514 | 0 |

## 14. Failures, missingness and review coverage

E2-T8 retains extraction reasons, source/MHR availability, methods and poses. No imputation occurred. Figure E2-8 shows source/fitted coverage. Anatomically unreviewed sites are kept in the engineering panel with explicit status. A failed contour is distinct from a valid fallback, an unknown anatomical site, an unavailable external protocol and a historically absent source baseline. The 24 waist-case selection manifest and height/crossover selection manifest identify exact protected participants and reproducible ranks. New independent human/expert reviews and inter-rater agreement are **not available**; rendering does not substitute for them. Any subsequent agent-assisted observations must be separately recorded and are not expert validation.

## 15. Scientific interpretation of the hypotheses

H2.1 receives descriptive evidence of site-dependent digital changes from direct paired statistics. H2.2 receives evidence of measurement-method sensitivity; its anatomical component is unresolved because the alternate anchors are proxies. H2.3 receives quantified within-native pose/corrective-associated changes and cranial descriptor sensitivities; the causal allocation of source-to-MHR discrepancy to physiology, hair or reconstruction remains unresolved. H2.4 is **not disproved by fallback use**: geometrically valid fallback values exist, but physical rib/crest placement is unverified. H2.5 is supported descriptively where common-method within-person intervals show pathway differences; it does not isolate the optimiser. H2.6 remains untestable as independent physical accuracy with the currently qualified metadata.

The descriptive Bland–Altman limits use mean ±1.96 sample SD; no distributional or physical-coverage guarantee is established. In particular the strong height-dependent bias makes a single cohort mean correction inappropriate.

## 16. Threats to validity

Engineering-exposed convenience cohort; no untouched confirmatory sample. Shared fitted-atlas source projection introduces dependence in localisation. Dominant-joint segmentation is an engineering anatomical-region approximation. Global extent is pose sensitive and is not standard stature. Head quantiles depend on tessellation; source original scans, hair/scalp labels and palpable landmarks are absent. LBFGSB expression handling differs. Canonical and source poses are not identical. Source region transfer and exact zero-edge equivalences carry topology assumptions. Raw contour and tape-envelope are different functionals. Bootstrap limits do not include all annotation, model and calibration uncertainty. No external clinical, physiological or body-fat validity follows.

## 17. Implications for SomatoAnthro

E2 supports a reproducible claim about preservation and method dependence of **digital engineering anthropometric proxies** on existing source/native pairs. It narrows a stronger claim of anatomically correct or physically calibrated measurements. E4's strict waist zero is evidence of a conservative rule, not cohort-wide anatomical failure. Do not market atlas midpoint proxies as verified WHO/ISO waist. Preserve negative, small, large and missing outcomes in paper tables. No body-fat equation was implemented or evaluated.
