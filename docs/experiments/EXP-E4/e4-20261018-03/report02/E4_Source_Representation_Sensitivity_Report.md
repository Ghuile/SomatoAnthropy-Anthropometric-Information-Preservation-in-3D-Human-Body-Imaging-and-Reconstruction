# E4 Source Representation Sensitivity Report

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

## 1. Research objective and hypotheses

Determine how independent source-to-native-MHR pathways transform the differences between two fitted representations of the same NOMO participant. The principal estimand is Δ_abs = |M_A−M_B|−|S_A−S_B|. Positive values indicate amplification and negative values indicate suppression of digital disagreement. Neither direction establishes improved accuracy against the person. H4.1 concerns sensitivity of native morphology; H4.2 concerns nonuniform site effects; H4.3 concerns suppression, preservation or amplification; H4.4 concerns the association between global reconstruction residuals and local measurement changes. Representation, optimisation, pose, localisation and source fit quality are inseparable pathway factors here; this is not a controlled topology experiment.

**Principal observed findings, common four-value subsets:**

| Site | Complete people | Mean |source A−B| | Mean |fitted MHR A−B| | Mean Δ_abs | 95% percentile CI | 98.75% four-primary-site CI |
|---|---|---|---|---|---|---|
| height | 150/150 | 0.0193 | 0.5193 | 0.5000 | [0.4074, 0.6023] | [0.3938, 0.6343] |
| abdomen | 149/150 | 0.4374 | 0.3086 | -0.1288 | [-0.2073, -0.0574] | [-0.2275, -0.0320] |
| waist | 149/150 | 3.6952 | 2.9012 | -0.7940 | [-1.5613, 0.0041] | [-1.7629, 0.2168] |
| hip | 150/150 | 0.0501 | 0.3387 | 0.2886 | [0.2290, 0.3464] | [0.2099, 0.3637] |
| neck | 100/150 | 1.0555 | 0.8105 | -0.2450 | [-0.5562, 0.0687] | secondary/case |
| chest | 1/150 | 2.7004 | 3.5445 | 0.8441 | case only / unavailable | secondary/case |

The height, hip and abdomen mean intervals exclude zero even using the four-site Bonferroni intervals. The waist mean interval crosses zero; its negative point estimate does not resolve the mean direction. Neck is secondary and uncertain; chest is a single case. Zero is not an approved equivalence or scientific acceptance margin. This dataset was already inspected during E0 and engineering development: E4 is a prespecified engineering follow-up, not an untouched confirmatory sample.

## 2. Cohort construction

| Cohort | Source-ID intersection | Both native candidates | All four required geometries | Pinned T90 articulation pairs | Identity/expression/morphology all preserved |
|---|---|---|---|---|---|
| primary | 4132 | 150 | 150 | 150 | 150 |
| complementary | 4069 | 60 | 60 | 60 | 0 |

There are 60 overlapping participants and 150 distinct people across both studies. The 60-person LBFGSB/CAESAR study is analysed separately; there is no pooled 210-person analysis. Exact E0 subject/body links, existing NOMO identity namespace, source-file SHA-256, frozen NICP manifest and package metadata establish linkage. No identity is inferred from geometry. Each branch retains its own native body and fit ID, controls, sources and measurement provenance. Both fitted and T90 meshes are retained, giving six saved geometries per participant contrast when both poses are counted. All four source/fitted geometries are available for both cohorts. Availability of an asset is distinct from scientific qualification and from independent native replay.

Private `cohorts.json` contains per-person four-representation records, transforms, fitting references, controls, measurement definitions and hashes. Source-ID intersections are 4,132 and 4,069; these are availability intersections rather than fitted sample sizes. The cohort contains engineering-exposed existing fits, not a new split or a random population sample.

## 3. Experimental methodology

Let A be SMPL-NICP (primary) or SMPL-LBFGSB (complementary), and B be CAESAR-NICP. Signed differences always use **A minus B**, the reverse of E0's named CAESAR-minus-SMPL contrast. Absolute differences are unchanged by this sign choice. Compute d_source=S_A−S_B, d_MHR=M_A−M_B, Δ_signed=d_MHR−d_source and pathway shifts e_A=M_A−S_A, e_B=M_B−S_B. Verify Δ_signed=e_A−e_B. All four values must be finite, geometrically valid engineering observations of the same participant and site. Pairwise contrast denominators can exceed the four-value intersection and are saved separately in `six-contrast-statistics.csv`.

Primary comparison: unchanged released sources and their own saved fitted-pose MHR surfaces. Existing rigid source-to-working transforms have unit scale; native centimetre coordinates use the saved 0.01 working conversion. The fitted bodies approximate their source poses; exact cross-path articulation equality has not been established. This is an engineering pathway comparison with residual pose differences, not an isolated shape effect. Canonical MHR/MHR uses exact pinned articulation [0:130]; identity, expression and morphology [130:204] checks are recorded separately. Source-to-T90 changes are explicitly exploratory because the released sources were not reposed. No scale is fitted to improve agreement.

Height is maximum-minus-minimum Y, not posture-corrected stature. Abdomen uses the mapped navel contour; waist uses the project's adaptive lower-half navel-to-chest rule with its historical ambiguity/fallback flags; NICP hip uses posterior-A outside tape. Girths use raw contours except hip/neck outside tape. Contact/seam and source recovery revisions select existing closed rings or cycles and retain original surfaces. Neck follows the saved shoulder-exclusion/contact procedure for the current NICP records. LBFGSB's saved canonical hip/neck definitions differ from the NICP revision and remain explicit pathway/protocol confounders. None of these are independently annotated anatomical measurements or an ISO conformance claim. `measurement-records.json` preserves per-value protocol, site, pose, validity, reasons and detail references. Definitions are traced to existing project configurations and metrology code rather than retroactively changed to increase completeness.

Fresh cross-path surface diagnostics reuse the existing area-uniform sampler and exact point-to-triangle distance engine: 1,024 points per direction, independent fixed per-participant seeds derived from seed 4182026, equal directional weights, original scale and all positive-area faces. Zero-area triangles are excluded from queries only; stored meshes remain unchanged. Mean, median, RMS and P95 pool both directional samples. Maximum is sample-dependent and is not exact Hausdorff distance. Identically ordered native LOD0 topology also permits exact indexed vertex displacement summaries. Source-to-MHR metrics reuse provenance-pinned existing LOD1 results with 4,096 samples/direction where available; other pathways use fresh LOD0 diagnostics. These LOD/sample/stage differences are retained and not treated as an identical residual estimator. Primary cross-path frames reuse saved branch frames; complementary frames reconcile historical source origins by documented translation only. Canonical packages retain saved floor alignment. No new rigid or scale optimisation is performed. Geometry before and after canonicalisation remains pose-sensitive.

Each statistic has one row per participant. Resampling uses 2,000 paired participant bootstrap replicates and deterministic hash-derived seeds. Percentile 95% intervals are descriptive; 98.75% intervals conservatively address the four primary site means within the main study. Standardised dz is mean paired change divided by its sample SD. Secondary, companion, pose, proxy sensitivity and correlation intervals are exploratory and unadjusted. Chest n=1 receives no bootstrap interval. CIs condition on this convenience sample; they do not address source selection bias, uncertain calibration, model systematic error or anatomical validity. No significance or favourable result is required for completion. The Bonferroni tail estimates use a finite bootstrap and should not be read as precise population coverage guarantees.

## 4. Original source disagreement

| Site | n | Signed source mean | Source MAE | Source RMS | Source P95 absolute |
|---|---|---|---|---|---|
| height | 150 | 0.0193 | 0.0193 | 0.0471 | 0.1249 |
| abdomen | 149 | -0.3115 | 0.4374 | 0.6495 | 1.2192 |
| waist | 149 | -3.5257 | 3.6952 | 5.2258 | 10.6313 |
| hip | 150 | 0.0150 | 0.0501 | 0.2125 | 0.0625 |
| neck | 100 | 0.4442 | 1.0555 | 1.8700 | 4.7789 |
| chest | 1 | -2.7004 | 2.7004 | 2.7004 | 2.7004 |

## 5. Native-MHR disagreement

| Site | n | Signed MHR mean | MHR MAE | MHR RMS | Signed Δ mean | Path A change | Path B change |
|---|---|---|---|---|---|---|---|
| height | 150 | -0.0499 | 0.5193 | 0.7987 | -0.0693 | 3.1494 | 3.2186 |
| abdomen | 149 | -0.0528 | 0.3086 | 0.4240 | 0.2587 | 0.6320 | 0.3733 |
| waist | 149 | -0.6358 | 2.9012 | 5.1367 | 2.8900 | 0.1481 | -2.7418 |
| hip | 150 | 0.1522 | 0.3387 | 0.4565 | 0.1372 | -0.5502 | -0.6874 |
| neck | 100 | 0.3328 | 0.8105 | 1.4910 | -0.1115 | -2.1782 | -2.0667 |
| chest | 1 | 3.5445 | 3.5445 | 3.5445 | 6.2449 | 5.8600 | -0.3849 |

Path A/B columns use the same four-value subset. In particular, mean height shifts of 3.1494 and 3.2186 show that small cross-path differences can coexist with common source-to-MHR changes. Source-fit agreement and native/native agreement are different endpoints.

The selected body gallery uses all 150 primary participants. Rank by sum of four core canonical absolute discrepancies divided by mean source Y extent, break ties by stable UID, select ranks 1, 75 and 150. This is a fixed outcome-stratified illustration rule, not a favourable-fit selection. Per-row viewpoints and scale are shared; display translations centre X/Z and put the lowest vertex at a common baseline without changing dimensions. Source, fitted and T90 states are labelled separately.

## 6. Reconstruction-associated disagreement changes

| Site | n | Median Δ_abs | Median 95% CI | SD Δ_abs | Paired dz | Increased | Decreased |
|---|---|---|---|---|---|---|---|
| height | 150 | 0.3155 | [0.2453, 0.3851] | 0.6067 | 0.8242 | 98.0% | 2.0% |
| abdomen | 149 | -0.0744 | [-0.1462, -0.0104] | 0.4844 | -0.2659 | 40.9% | 59.1% |
| waist | 149 | -0.3923 | [-1.0054, -0.1371] | 4.8548 | -0.1636 | 40.3% | 59.7% |
| hip | 150 | 0.2309 | [0.1917, 0.2830] | 0.3736 | 0.7725 | 93.3% | 6.7% |
| neck | 100 | 0.0311 | [-0.0789, 0.1440] | 1.6200 | -0.1512 | 54.0% | 46.0% |
| chest | 1 | 0.8441 | case only / unavailable | unavailable | unavailable | 100.0% | 0.0% |

The signed decomposition was checked for every complete participant/site/state/rule. Independent decimal arithmetic and direct saved-table verification are recorded in `numerical-verification.json`. All six E0 common-subset counts and mean absolute changes reproduce exactly to floating-point precision; this includes the opposite signed cross-path convention and unchanged absolute convention. No E0 number was overwritten. Full mean/median/SD/MAE/RMS/quantile summaries, raw participant changes, bootstrap draws and seeds are saved.

## 7. Regional and anthropometric analysis

| Cohort | Contrast | People | Mean symmetric distance (eng m) | Median across people | Mean participant P95 (eng m) | Samples/direction | LOD |
|---|---|---|---|---|---|---|---|
| complementary | canonical_cross_path | 60 | 0.025060 | 0.020337 | 0.080929 | [1024] | [0] |
| complementary | fitted_cross_path | 60 | 0.009722 | 0.009078 | 0.023874 | [1024] | [0] |
| complementary | source_cross_path | 60 | 0.009073 | 0.008969 | 0.022730 | [1024] | [0] |
| complementary | source_to_mhr_a | 60 | 0.003042 | 0.002913 | 0.008673 | [1024] | [0] |
| complementary | source_to_mhr_b | 60 | 0.004503 | 0.004154 | 0.012804 | [4096] | [1] |
| primary | canonical_cross_path | 150 | 0.000735 | 0.000662 | 0.002123 | [1024] | [0] |
| primary | fitted_cross_path | 150 | 0.002884 | 0.002238 | 0.007071 | [1024] | [0] |
| primary | source_cross_path | 150 | 0.002104 | 0.001202 | 0.004009 | [1024] | [0] |
| primary | source_to_mhr_a | 150 | 0.004920 | 0.004429 | 0.014397 | [4096] | [1] |
| primary | source_to_mhr_b | 150 | 0.004985 | 0.004578 | 0.014883 | [4096] | [1] |

The symmetric mean column is the mean of participant-specific surface means; the P95 column is the mean of participant-specific P95s, not the pooled-vertex population P95. Distances use engineering metres, not independently calibrated physical error. Cross-source and cross-MHR surfaces quantify morphological discrepancies without choosing a superior candidate. The 1,024-point new diagnostics are finite-sample estimates; no new fitting, native generation or clinical geometric threshold is involved.

Global two-path fitting residual versus Δ_abs:

| Site | Complete people | Spearman rho | 95% paired CI |
|---|---|---|---|
| height | 150 | 0.248 | [0.0937, 0.3964] |
| abdomen | 149 | -0.111 | [-0.2686, 0.0562] |
| waist | 149 | 0.129 | [-0.0401, 0.2913] |
| hip | 150 | 0.163 | [0.0037, 0.3298] |
| neck | 100 | -0.175 | [-0.3792, 0.0428] |

Associations describe monotonic relationships and do not establish causation or explain all residual variation. Body-size, original-disagreement and cross-source/canonical geometric associations are also in `geometry-associations.csv`; these are separate exploratory predictors, not a fitted causal model. The same paired participants are resampled for each correlation. Correlation magnitude and uncertainty, rather than an arbitrary significance gate, inform H4.4.

| Cohort | Official region proxy | People | Mean indexed RMS (eng m) |
|---|---|---|---|
| primary | torso | 150 | 0.001782 |
| primary | pelvis | 150 | 0.001721 |
| primary | neck_head_jaw_weight_region | 150 | 0.001631 |
| complementary | torso | 60 | 0.082078 |
| complementary | pelvis | 60 | 0.079083 |
| complementary | neck_head_jaw_weight_region | 60 | 0.097370 |

Official native torso/pelvis face masks and dominant neck/head/jaw joint weights provide reproducible engineering region proxies. Their indexed displacement is available at common T90 topology; regional correlations with canonical girths are in `regional-associations.csv`. They do not establish independent source-region anatomical truth. Fine source-specific abdominal/waist surface accuracy remains unavailable because the existing projected/consensus localisation is fit-dependent; no new anatomical map was invented.

## 8. Complementary LBFGSB/CAESAR study

| Canonical site | People | Signed mean A−B | Mean absolute difference | Signed-mean 95% CI |
|---|---|---|---|---|
| abdomen | 60/60 | -4.8622 | 4.9930 | [-5.6269, -4.0597] |
| chest | 60/60 | -3.0577 | 3.2048 | [-3.6397, -2.5032] |
| height | 60/60 | -7.1189 | 9.2163 | [-9.2571, -4.9894] |
| hip | 60/60 | -1.8522 | 2.5405 | [-2.5558, -1.1367] |
| neck | 60/60 | -1.8898 | 3.1933 | [-2.7549, -1.0872] |
| waist | 60/60 | -5.4966 | 5.8316 | [-6.7782, -4.2610] |

These are existing T90 MHR/MHR results for 60 people, all overlapping the primary cohort. Canonical-only disagreement is not a four-representation preservation result. Compatible saved released/fitted LBFGSB girths for the full 60 were unavailable; no NICP source measurements were substituted. Fresh Y extents of immutable meshes support a full four-value height comparison for 60/60: mean Δ_abs 2.8153, 95% CI [1.8116, 3.8320]. Other complementary source-to-MHR girth effects remain unavailable. The full source-source/fitted/canonical geometry comparisons still use all 60 people.

All 60 LBFGSB canonical archives preserve identity/morphology and match pinned T90 articulation, but their facial expression controls differ from fitted archives. This is retained historical evidence; E4 does not rewrite those files. Canonical neck and head effects therefore include expression-neutralisation differences. Historical hip selection and neck procedures also differ, so larger companion disagreement cannot be attributed solely to the LBFGSB algorithm. No joint inference treating the two cohorts as independent was performed.

## 9. Ablations and sensitivity analyses

| Site | Proxy-inclusive n / mean Δ_abs | Ambiguity-excluded n / mean Δ_abs | Released-to-T90 n / mean Δ_abs (exploratory) |
|---|---|---|---|
| height | 150 / 0.5000 | 150 / 0.5000 | 150 / 0.1361 |
| abdomen | 149 / -0.1288 | 149 / -0.1288 | 149 / 0.0293 |
| waist | 149 / -0.7940 | 0 / unavailable | 149 / -3.0497 |
| hip | 150 / 0.2886 | 150 / 0.2886 | 150 / 0.4732 |
| neck | 100 / -0.2450 | 100 / -0.2450 | 100 / -0.5824 |
| chest | 1 / 0.8441 | 1 / 0.8441 | 1 / 0.1477 |

Ambiguity-excluded removes a measurement if its current or historical state is SITE_AMBIGUOUS or a waist fallback was applied. Proxy-inclusive retains finite geometric engineering measurements, including flagged proxies; it never restores invalid rings or fills missing values. Geometric invalidity overrides inherited PROXY_VALID labels. All observations remain in the evidence even when absent from a statistic. Differences between these subsets can reflect selection, not an improved method. The released-to-T90 column changes pose and is exploratory. `six-contrast-statistics.csv` retains the original six contrasts separately, with explicit E4 signs. Alternative fitting candidates remain intact and no canonical preference is changed. Older measurement revisions are lineage evidence rather than additional people or interchangeable validated protocols.

## 10. Failures, missingness and limitations

Height and hip are complete at 150/150; abdomen and waist at 149/150; neck at 100/150; chest at 1/150 for the primary released/fitted four-value analysis. The site-specific exclusions are retained even when they occur in different people. Missingness is representation- and pose-dependent. `E4-T6-validity.csv` reports available and ambiguity-excluded counts, geometric and proxy flags, protocol/pose states and per-reason failures for each branch/state/site. Numeric coverage does not make a site anatomically valid. Chest supports a case-level result only in the main contrast, even where canonical or companion chest values are more numerous.

The original physical unit convention remains unconfirmed. Engineering cm derives from stored source coordinates and the documented native conversion, without fitted rescaling. Tailor measurements have unresolved unit and protocol compatibility and are not independent physical accuracy references here. Source localisation uses fit-derived correspondence, inducing dependence. Common MHR restrictions can suppress disagreement while both models move away from source fits. Pose differences, conditional scale/rig controls, expression neutralisation in historical LBFGSB, finite surface sampling, LOD differences, missing difficult rings and cohort selection all constrain interpretation. High-error cases are retained. No claims about physiology, body fat, clinical girth, pure topology causality, provider-wide independence or cross-dataset generalisation are made. Scientific margins and anatomical acceptance remain unapproved.

## 11. Discussion

H4.1: the saved native reconstructions show nonzero cross-path morphology and measurement differences, supporting digital representation/fitting-path sensitivity within this cohort. H4.2: effects vary by site, with positive primary mean changes at height/hip and negative at abdomen; waist and neck mean directions remain uncertain. These are site-specific paired observations, not an unmodelled test of independent sites. H4.3: both suppression and amplification occur; the intervals support amplification at height/hip and suppression at abdomen. There is no justified claim of uniform improvement or equivalence. H4.4: the rank associations above evaluate the proposed relationship; they can show substantial associations and still leave local variation unexplained. This observational evidence does not isolate reconstruction quality from source size, pose and measurement placement, so a causal or complete explanatory claim remains inconclusive.

For the SomatoAnthro manuscript, E4 contributes a paired four-representation estimand, a reproducible 150-person engineering comparison, an explicitly dependent 60-person fitting-path complement, uncertainty, geometric context and a detailed missingness analysis. It establishes how existing reconstruction pathways transform digital disagreements. It does not validate anatomical accuracy or claim that MHR improves reconstruction of the actual participants.
