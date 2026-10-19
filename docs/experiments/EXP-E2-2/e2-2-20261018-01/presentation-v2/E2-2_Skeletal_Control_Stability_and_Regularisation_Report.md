# E2-2 Skeletal-Control Stability and Regularisation Report

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

## 1. Research question and hypotheses

Which verified native skeletal control groups contribute to useful reconstruction, and how sensitive are those effects to the prior, optimization samples and initial root pose? The six hypotheses concern group contribution, anatomical specificity, optimization stability, regularization trade-offs, new-identity replication within NOMO and practical parameter identifiability. Every numerical result below comes from saved NOMO bodies and completed native jobs; synthetic tests establish engineering invariants only.

## 2. Relationship to E2 and E2-1

E2 observed strong compression of canonical Y-extent variation when all morphology entries were zero. E2-1's matched nine-control release partly recovered variation and improved independent source surface errors, while increasing cross-path disagreement and leaving anatomical waist preservation unresolved. E2-2 reuses the four E2-1 development people and exactly compatible B/C results, then evaluates 12 different existing NOMO people. E0/E2/E4/E2-1 and E3 outputs remain protected and fingerprinted. A count of optimization jobs is not a count of new people or newly acquired scans.

## 3. Official native control semantics

## 4. Frozen control groups

G1: spine and neck length. G2: upper-leg, lower-leg and foot length. G3: upper-arm and forearm length. G4: shoulder and hip width. The groups partition all nine controls without overlap. Four group-only conditions and full-minus-G1/full-minus-G2 are tested. These are mapping-derived engineering groups; optimization interactions prevent additive attribution. See T2 for exact indices, mappings, domains and masks.

## 5. Original optimization configuration

The unchanged E2-1 optimizer continues the original saved identity/articulation/expression and external translation with fresh Adam moments. Both reference arms use 100 steps, 8192 fixed area samples, original seeds 20261018/20261019, original pseudo-Huber sampled-cloud reconstruction, identity/pose priors, clipping and bounds. Identity LR .015, pose .002, external translation .001, released controls .01; expression remains fixed. The best regularized pre-step state is retained. Independent evaluation uses 4096 area samples per direction and different deterministic evaluation seeds. No height-specific loss, arbitrary body scaling, post-hoc alignment or new metrology engine is introduced.

The skeletal prior is λΣ(all nine control²)/9, with λ₀=2×10⁻⁵. For a k-control group, the reused optimizer's mean over k entries receives coefficient λk/9, preserving the original nine-control denominator with excluded entries fixed to zero. This prevents group size from silently changing the penalty on active controls. Domain normalization is used in diagnostics only, not substituted into the objective.

## 6. Development population and compatible reuse

The four original development identities and both source pathways are retained, one person per original extent quartile. Sixteen E2-1 locked/full reference jobs are reused with exact source, initial parameter and translation checks, unchanged optimizer-code hashes, matching protocol/seeds and pinned model assets. No existing successful fit is repeated merely to populate a batch. New group, prior and repeat conditions use the same original starting state, rather than starting from E2-1's released solution.

## 7. Group-only results

Among group-only conditions, G2 has the lowest development aggregate independent surface mean (0.4041 engineering cm), while G2 has the lowest fitted-pose height MAE (1.758 cm). G2 raises canonical/source SD ratios from locked B's .186/.195 to .572/.511 (SMPL/CAESAR); G1 reaches .480/.441. G3 and G4 remain near locked height spread (.184/.192 and .189/.195). Full C reaches .642/.580. Thus leg/foot and axial freedom account for much of the tested height-spread effect, with full release retaining better aggregate fidelity. These are descriptive comparisons on four people and do not establish a unique biological mechanism. Figure 2 also shows group-specific measured native segment/width changes. Native segment/width descriptors, circumference errors, cross-path differences and bound contacts are retained in the condition records and companion tables.

## 8. Leave-one-group-out results

Full-minus-G1 and full-minus-G2 are compared with full C as well as locked B. Removing G1 raises aggregate development mean surface error from .351 to .376 engineering cm and fitted height MAE from 1.269 to 1.688 cm; removing G2 raises them to .390 and 2.352 cm. Their canonical SD ratios are .558/.514 and .500/.461, respectively. Both groups contribute within the full fit, while compensation by remaining degrees of freedom preserves part of the effect. T3, T7 and paired-effects.csv retain surface, height, region and measurement effects. A group-only effect demonstrates sufficiency under these conditions; leaving it out describes its contribution within the full optimization. Neither is a uniquely additive effect. A different local optimum or compensation by identity/pose can mediate the observed change. No further combinatorial subsets are searched.

## 9. Rig-prior sensitivity

The predefined λ multipliers .25, 1 and 4 use identical masks, original starts, samples, budgets and all non-rig objective weights. Figure 3 and T4 jointly show independent surface fidelity, individual height error, SD ratio, cross-path RMS, circumference error and bound contact. Reduced parameter norm or fewer bound contacts is not treated as better anatomy by itself. The exact development comparison used to select a candidate is:

| policy | control_count | multiplier | surface_cm | fitted_height_mae_cm | circumference_mae_cm | cross_path_rms_cm | bound_fraction | dominated | worst_fractional_rank | mean_fractional_rank |
|---|---|---|---|---|---|---|---|---|---|---|
| C | 9 | 1 | 0.3508 | 1.269 | 0.7761 | 0.7599 | 0 | 1 | 1 | 0.4722 |
| G1 | 2 | 1 | 0.4227 | 2.452 | 1.327 | 0.4505 | 0 | 0 | 0.8889 | 0.6389 |
| G2 | 3 | 1 | 0.4041 | 1.758 | 0.7825 | 0.5302 | 0 | 0 | 0.6667 | 0.5278 |
| G3 | 2 | 1 | 0.4353 | 3.763 | 1.081 | 0.3319 | 0 | 0 | 1 | 0.6389 |
| G4 | 2 | 1 | 0.4363 | 3.748 | 1.2 | 0.2726 | 0.125 | 0 | 1 | 0.7222 |
| noG1 | 7 | 1 | 0.3758 | 1.688 | 0.7084 | 0.6991 | 0 | 0 | 0.8889 | 0.4907 |
| noG2 | 6 | 1 | 0.3901 | 2.352 | 1.431 | 0.5542 | 0 | 0 | 1 | 0.6389 |
| R025 | 9 | 0.25 | 0.3479 | 1.252 | 0.7607 | 0.6532 | 0 | 0 | 0.6667 | 0.3611 |
| R4 | 9 | 4 | 0.3578 | 1.407 | 0.8783 | 0.6665 | 0 | 1 | 0.7778 | 0.5093 |

## 10. Sampling-seed stability

One alternative fixed source/target seed pair, 20261028/20261029, is tested for matched B/C on all four development people and B/C/D on the predetermined four-person held-out subset. These are sampling repeats, not new independent people. The original and alternative samples are shared within every matched policy comparison.

| partition | condition | metric | n | mean | q95 | ci95 |
|---|---|---|---|---|---|---|
| development | B | geometry_error_delta_cm | 4 | -8.319e-07 | 0.003611 | [-0.002841, 0.002839] |
| development | B | normalized_control_l2 | 4 | 0 | 0 | [0, 0] |
| development | B | canonical_repeat_vertex_rms_cm | 4 | 0.08476 | 0.1203 | [0.06457, 0.1139] |
| development | C | geometry_error_delta_cm | 4 | 0.001098 | 0.006842 | [-0.004282, 0.006435] |
| development | C | normalized_control_l2 | 4 | 0.282 | 0.4029 | [0.1938, 0.3812] |
| development | C | canonical_repeat_vertex_rms_cm | 4 | 0.5702 | 1.072 | [0.2865, 0.9502] |
| heldout | B | geometry_error_delta_cm | 4 | -0.003358 | 0.002501 | [-0.008618, 0.002045] |
| heldout | B | normalized_control_l2 | 4 | 0 | 0 | [0, 0] |
| heldout | B | canonical_repeat_vertex_rms_cm | 4 | 0.06917 | 0.08017 | [0.0584, 0.07993] |
| heldout | C | geometry_error_delta_cm | 4 | -0.002475 | 0.001574 | [-0.004374, 0.0008733] |
| heldout | C | normalized_control_l2 | 4 | 0.09828 | 0.1291 | [0.07383, 0.1233] |
| heldout | C | canonical_repeat_vertex_rms_cm | 4 | 0.4051 | 0.5669 | [0.3006, 0.5432] |
| heldout | D | geometry_error_delta_cm | 4 | -0.0003595 | 0.005149 | [-0.005786, 0.004318] |
| heldout | D | normalized_control_l2 | 4 | 0.1134 | 0.1417 | [0.09038, 0.1361] |
| heldout | D | canonical_repeat_vertex_rms_cm | 4 | 0.4085 | 0.5608 | [0.3069, 0.5334] |

This limited two-realization comparison describes repeat sensitivity under the tested schedule; it does not estimate a general convergence distribution. Individual records retain source-agreement deltas, fitted and canonical vertex RMS, parameter movement, height/contour changes, bound contact and cross-path results for each repetition.

## 11. Initialization sensitivity

A separate development-only perturbation changes the original allowed root rotations by +.01, −.01 and +.005 radians for X/Y/Z, clamped to the original authored fitting bounds. Identity, expression, morphology and original external translation are unchanged; B and C receive the same perturbed start. The root-pose perturbation is small and does not introduce a global scale. The original sampling seed pair is retained. The established sampler derives target faces from the shared initial surface, so any initialization-dependent sampling difference is recorded rather than hidden. This is a narrow root-pose diagnostic, not a test of every identity/shape initialization.

| condition | metric | n | mean | q95 | ci95 |
|---|---|---|---|---|---|
| B | geometry_error_delta_cm | 4 | -9.187e-05 | 0.0003813 | [-0.0004378, 0.0002589] |
| B | normalized_control_l2 | 4 | 0 | 0 | [0, 0] |
| B | canonical_repeat_vertex_rms_cm | 4 | 0.01362 | 0.02292 | [0.008978, 0.02124] |
| C | geometry_error_delta_cm | 4 | -0.0004379 | 0.00297 | [-0.002115, 0.002316] |
| C | normalized_control_l2 | 4 | 0.04149 | 0.05805 | [0.02569, 0.05578] |
| C | canonical_repeat_vertex_rms_cm | 4 | 0.1424 | 0.2125 | [0.07597, 0.2017] |

Actual fingerprint audit: 16/16 pose-perturbation repeats changed the target face-index sample, while retaining the source cloud and barycentric random draws. Thus this estimates the response to the initialization procedure **including its target-area sampling effect**; it does not isolate solver-basin dependence with an identical target cloud. No additional fitting was launched to conceal that limitation. Full equality/difference flags are retained in repeat-sampling-audit.csv.

## 12. Development-only candidate decision and freeze

Selected policy: **R025**, controls `["scale_spine_length", "scale_neck_length", "scale_shoulder_width", "scale_uparms", "scale_lowarms", "scale_hip_width", "scale_uplegs", "scale_lowlegs", "scale_foot_length"]`, λ multiplier **0.25**. The frozen rule was declared before development fitting: Development only: Pareto minimization of independent global surface mean, fitted height MAE, mean fixed-plane waist/abdomen/hip MAE, canonical cross-path vertex RMS, any-bound fraction and circumference missingness. Among nondominated policies, minimize worst fractional rank, then mean fractional rank, then control count, then prefer lambda multiplier nearest 1, then policy ID. SD ratio and repeat sensitivity are descriptive, not selection targets. No universal quality margins. Incomplete native policies remain failures and are ineligible for the candidate.

All eligible complete native policies remain in the descriptive Pareto/rank table. Circumference missingness is a criterion so unavailable measurements cannot silently improve a candidate's score. Canonical height SD is displayed alongside source agreement but is not optimized as a selection target. Stability evidence is directly available for B/C only; alternative-policy stability is explicitly unresolved at selection, then examined on the held-out four-person sampling subset. The decision is an engineering compromise based on small-sample ranks, not a universal scientific threshold or a claim of statistical superiority.

The immutable candidate-freeze.json stores the selection time, exact development evidence hashes, original configuration hash and selection-source snapshot, with zero held-out attempts and no inspected E2-2 held-out outcomes. Subsequent held-out results do not retune this decision. If D equals C, the logical D condition is an alias and no redundant fit is run.

## 13. New held-out selection

The 12 people come from the original 150-person NOMO cohort, excluding all 16 E2-1 participants. Three are selected per original source-extent quartile, using mean two-path original extent for quartile placement. Within each quartile, one person is sampled from each tertile of the original SMPL-NICP source-fit surface error using seed 20261022. SMPL's original metric is available for all 150; CAESAR's saved metric is absent for 50, so incompatible metrics are not mixed. The middle error-tertile selection in each quartile defines the four-person additional-seed subset. Original source/fit eligibility, hashes and linkage are verified before execution; no replacement follows a poor result. This is identity-level held-out evaluation within the existing NOMO ecosystem, not external population validation.

## 14. Held-out source reconstruction

SMPL-NICP, C-B: mean surface-error change -0.1191 [95% paired bootstrap interval [-0.1413, -0.09566]; n=12] engineering cm.

SMPL-NICP, D-C: mean surface-error change -0.003082 [95% paired bootstrap interval [-0.006176, -0.0001413]; n=12] engineering cm.

SMPL-NICP, D-B: mean surface-error change -0.1222 [95% paired bootstrap interval [-0.1446, -0.1008]; n=12] engineering cm.

CAESAR-NICP, C-B: mean surface-error change -0.1156 [95% paired bootstrap interval [-0.1398, -0.09276]; n=12] engineering cm.

CAESAR-NICP, D-C: mean surface-error change -0.003619 [95% paired bootstrap interval [-0.006815, -0.0005098]; n=12] engineering cm.

CAESAR-NICP, D-B: mean surface-error change -0.1192 [95% paired bootstrap interval [-0.1422, -0.09847]; n=12] engineering cm.

Mean, median, RMS, P95, both directions and torso/pelvis/upper-leg/lower-leg/arm/head-neck/foot/hand diagnostics are retained. Source samples and evaluation configuration are common across policies for each branch; target sampling uses common random seeds with the actual area probabilities of each surface. Evaluation distances go to exact opposite indexed triangles and are separate from the optimization's sampled-cloud nearest neighbors. Positive-area masks are policy-defined; original buffers and existing native topology defects are retained. Region labels use official dominant joints, an official pelvis mask and fixed historical source-label transfer, not independently annotated source anatomy.

## 15. Height and morphological variability

| pathway | condition | source_sd_cm | canonical_sd_cm | sd_ratio | canonical_mae_cm | fitted_mae_cm | surface_mean_cm |
|---|---|---|---|---|---|---|---|
| SMPL-NICP | historical | 9.287 | 1.668 | 0.1797 | 6.815 | 4.397 | 0.4704 |
| SMPL-NICP | B | 9.287 | 1.688 | 0.1818 | 6.854 | 4.192 | 0.4631 |
| SMPL-NICP | C | 9.287 | 5.373 | 0.5786 | 3.174 | 1.843 | 0.344 |
| SMPL-NICP | D | 9.287 | 5.433 | 0.585 | 3.141 | 1.8 | 0.3409 |
| CAESAR-NICP | historical | 9.313 | 1.729 | 0.1857 | 6.853 | 4.46 | 0.4791 |
| CAESAR-NICP | B | 9.313 | 1.724 | 0.1851 | 6.859 | 4.307 | 0.4706 |
| CAESAR-NICP | C | 9.313 | 5.302 | 0.5693 | 3.401 | 2.028 | 0.355 |
| CAESAR-NICP | D | 9.313 | 5.361 | 0.5756 | 3.348 | 1.989 | 0.3514 |

T7 separates fitted and canonical states and supplies bias, MAE/RMSE, SD/IQR/range, SD ratio, regression slope and Pearson/Spearman correlations on identical participant subsets. Source extent is unchanged. Canonicalization uses the exact pinned T90 articulation, preserving identity, expression and all indices 130:204, followed by the existing floor translation. Pose/correctives and head-envelope geometry affect extent. No scalp/hair separation, observed clinical stature or unique source skeletal dimensions are inferred. Increased spread must be considered with individual error and source reconstruction.

## 16. Anthropometric measurements

SMPL-NICP, waist, D−C fixed-source-plane absolute-error change: -0.0108 [95% paired bootstrap interval [-0.0428, 0.02006]; n=12] engineering cm.

SMPL-NICP, abdomen, D−C fixed-source-plane absolute-error change: -0.008616 [95% paired bootstrap interval [-0.05173, 0.03464]; n=12] engineering cm.

SMPL-NICP, hip, D−C fixed-source-plane absolute-error change: 0.01099 [95% paired bootstrap interval [-0.01168, 0.03546]; n=12] engineering cm.

CAESAR-NICP, waist, D−C fixed-source-plane absolute-error change: -0.02351 [95% paired bootstrap interval [-0.07451, 0.0257]; n=12] engineering cm.

CAESAR-NICP, abdomen, D−C fixed-source-plane absolute-error change: -0.02313 [95% paired bootstrap interval [-0.07249, 0.02688]; n=12] engineering cm.

CAESAR-NICP, hip, D−C fixed-source-plane absolute-error change: 0.003012 [95% paired bootstrap interval [-0.01744, 0.028]; n=12] engineering cm.

All source-plane coordinates remain fixed across policies. Abdomen is the mapped-umbilicus reference; historical waist is the saved adaptive or fallback site. The fallback is +0.005 engineering m above that mapped reference, not a verified rib/iliac midpoint. The same E2 IndexedSections, atlas attachments and hip landmark procedure are reused. Waist/abdomen/chest use raw contour and hip/neck use their recorded tape quantity. Neck/chest remain supplementary where eligible. The separate E2 midpoint/surface-proxy panel is retained with its own coverage and failures; no historical flags are retroactively reclassified. A valid fixed contour is not proof of anatomical waist accuracy, and fallback use alone is not anatomical failure. T8 and individual-anthropometry.csv retain bias, MAE/RMSE, median/P95 absolute errors, source/target failure reasons, fallback counts and missingness.

All 12 people per pathway support the fixed-source-plane waist/abdomen/hip comparisons. Source historical waist fallback is used for 6/12 SMPL and 12/12 CAESAR cases. In contrast, the separate E2 midpoint waist proxy supports 9/12 SMPL and 0/12 CAESAR cases. Full C reduces mean fixed-plane absolute errors relative to B by .251/.354 cm at waist, .269/.387 cm at abdomen and .118/.118 cm at hip; all six exploratory intervals include zero. D adds small waist/abdomen reductions and small hip increases relative to C, also with intervals including zero. These findings do not establish improved anatomical waist preservation. Unsupported proxy sites remain missing and are not pooled with fixed-plane results.

## 17. Cross-path consistency

C-B, canonical corresponding-vertex RMS change: 0.4808 [95% paired bootstrap interval [0.3506, 0.6331]; n=12] engineering cm.

D-C, canonical corresponding-vertex RMS change: 0.02775 [95% paired bootstrap interval [-0.009422, 0.06883]; n=12] engineering cm.

D-B, canonical corresponding-vertex RMS change: 0.5086 [95% paired bootstrap interval [0.3683, 0.6619]; n=12] engineering cm.

Mean canonical corresponding-vertex RMS across the 12 people is B 0.1057, C 0.5866 and D 0.6143 engineering cm. The selected weaker prior does not reduce cross-path disagreement on this held-out cohort.

Corresponding-index mean/median/RMS/P95 and regional distances compare the two canonical native bodies per person in fixed T90/floor coordinates, including any residual placement effect. Height and eligible canonical proxy circumference differences, plus all nine parameter differences, remain in T9. Greater freedom may legitimately preserve disagreement already present in the original source bodies. Therefore smaller cross-path distance is not rewarded in isolation from fidelity. Seed-repeat changes help distinguish source-dependent fitting from optimization instability, without establishing physical anatomical truth.

## 18. Parameter movement and identifiability

Every condition preserves starting/final controls, native parameter checksums, allowed masks, gradients, loss components and update histories. Normalized movement uses authored domain width; actual resulting skeletal dimensions are measured independently of control magnitude. Figure 9 includes raw full/candidate values and explicit bound contacts; repeat parameter/geometry differences are in T5 and identifiability.csv. Distinct parameter states with small geometry differences are evidence of practical ambiguity under these repeats, not proof of a mathematical null space or unique physiological interpretation. Descriptive repeated-path correlations are labelled as such and receive no independent-job significance claim.

## 19. Bounds and geometric plausibility

Held-out primary fits with any authored-bound contact, out of 24 branches per policy: `{"B": 0, "C": 14, "D": 15}`. Bound contact is a diagnostic, not automatic scientific failure. Regional errors, left/right segment asymmetry, widths, lengths, cranial envelope and finite/watertight/winding/duplicate/zero-area observations remain available. Complete self-intersection and anatomical plausibility qualification has not been performed. Representative shortest/median/tallest held-out source cases are selected reproducibly for the actual-mesh gallery; failures receive an explicit missing label instead of fabricated geometry.

## 20. Failures and missingness

Actual execution counts: `{"candidate_aliases": 0, "development_people": 4, "evaluated_condition_records": 240, "heldout_sampling_repeat_people": 4, "new_attempts": 192, "new_completed": 192, "new_failures": 0, "new_heldout_people": 12, "new_regenerated": 192, "reused_E2_1_reference_jobs": 16}`. Logical reused references and candidate aliases are separate from new optimization attempts. All failed or interrupted attempts remain recorded; no unsuccessful fit is restarted with new hyperparameters, and completed fits are reused. An interrupted optimizer may resume only its saved parameters, Adam moments, best state, iteration and matching fingerprints; interruption before a durable checkpoint remains a failure. Unsupported site comparisons remain missing rather than zero. No difficult person or high-error condition is dropped to improve aggregate results.

## 21. Statistical uncertainty and nesting

The independent unit is the person. Pathways are paired and seeds/initializations are repeated fitting outcomes. Primary contrasts C−B, D−C and D−B use matched individual differences within each pathway and 2000 deterministic participant bootstrap replicates. SD ratios resample source/B/C or source/C/D vectors jointly. Cross-path contrasts have one observation per person. Repeat summaries first average eligible paired pathways within each person, then bootstrap people; jobs are not independently resampled. Development n=4, held-out n=12 and repeat-subset n=4 remain separate. Intervals are exploratory unadjusted percentile intervals; neither significance nor a universal error margin is required. Small stratified convenience samples limit population inference.

## 22. Threats to validity

Physical calibration remains unconfirmed. Source mesh and NICP biases, model-derived site placement, fixed-plane pose sensitivity, transferred regional labels, warm-start dependence, limited 100-step budget, a single alternative sampling seed, root-only initialization perturbation, correlated controls and incomplete anatomy/mesh validation remain limitations. Rank-based candidate choice can be unstable on four people; the frozen held-out evaluation reports that risk rather than retroactively selecting a different candidate. Native replay, finite values, input hashes and tests establish engineering consistency, not scientific acceptance.

## 23. Scientific interpretation

SMPL-NICP: D−C surface mean -0.003082 cm; canonical SD ratio C→D 0.5786→0.585; canonical MAE C→D 3.174→3.141 cm. CAESAR-NICP: D−C surface mean -0.003619 cm; canonical SD ratio C→D 0.5693→0.5756; canonical MAE C→D 3.401→3.348 cm.

Group-only and leave-out interventions identify conditional algorithmic contributions under this optimizer, prior and initialization. They do not identify a unique biological decomposition. Sampling and pose-start repeats address local optimization sensitivity; stronger regularization can trade flexibility for consistency but is not intrinsically more anatomical. Whether each hypothesis is supported, contradicted or unresolved must be read against these measured effects and intervals. The new held-out cohort supplies a replication within NOMO and does not turn digital anthropometry into independent anatomical ground truth.

The hypothesis assessments are:

- **H2-2.1, group contribution: supported conditionally.** G2 and G1 retain much of the height-spread effect; excluding either worsens full-fit fidelity and height error. No reduced mask displaces the full nine-control family under the frozen joint selection rule.
- **H2-2.2, anatomical specificity: supported for native model dimensions; biological specificity unresolved.** Axial, limb and transverse controls change their mapped skeletal descriptors. Source regions and model joints supply engineering proxies, without observed participant bone lengths or anatomical correspondence ground truth.
- **H2-2.3, optimization stability: sampling sensitivity observed.** On the held-out four-person repeat subset, mean canonical repeat vertex RMS is .069 cm for B, .405 cm for C and .409 cm for D. Full-release results vary despite very small changes in mean source residual. Root-pose repeats also vary, but all 16 initialization repeats change target face samples, preventing a pure solver-basin interpretation.
- **H2-2.4, useful regularization compromise: unresolved broadly; the selected candidate does not improve the tested stability trade-off.** Development selected quarter-strength prior D, retaining all nine controls. Its held-out additional mean surface gain over C is only .031/.036 engineering mm (SMPL/CAESAR). Cross-path RMS increases by .028 cm (interval includes zero), bound contact rises from 14/24 to 15/24 branches, and sampling repeat RMS does not improve. The stronger development prior trades some fidelity and variance recovery for smaller cross-path disagreement relative to C, without establishing an overall superior policy or held-out stability benefit.
- **H2-2.5, held-out reproducibility: supported within this NOMO sample.** Full C lowers mean surface error by 1.191/1.156 engineering mm and canonical height MAE by 3.680/3.458 cm versus B on 12 people excluded from E2-1. D retains that main improvement. Canonical SD remains about 5.3–5.4 cm against source SD about 9.3 cm, so recovery is partial.
- **H2-2.6, identifiability: practical ambiguity observed; structural identifiability unresolved.** Held-out repeat domain-normalized control L2 averages .098 for C and .113 for D, alongside near-equal residual means and measurable shape differences. This shows weak constraint of the fitted state by the tested loss. It does not demonstrate exactly interchangeable parameter vectors, a mathematical null space or a unique physiological interpretation.

## 24. Implications for SomatoAnthro

Fitting-policy masks, prior definitions and full native controls should be versioned and retained with source/identity lineage, fitted/canonical states, repeat metadata, reconstruction errors and site coverage. Marginal height SD alone is insufficient for dataset acceptance. A smaller or more regularized mask can be a useful candidate only when its fidelity and measurement trade-offs are explicit. Geometry, anthropometry, visual plausibility and latent physiology remain separate evaluation targets. Dataset engineering can preserve paired source/fitted/canonical representations, expose repeat-derived uncertainty instead of treating one latent control vector as anatomical truth, and stratify qualification by reconstruction, site coverage and sensitivity. Future controlled sampling interventions can hold the target cloud fixed across initialization changes. These are engineering implications, without a newly authorized fitting campaign or biological causal explanation.

For a paper, E2-2 strengthens a methodological claim that native skeletal restrictions materially constrain recoverable geometry and variation, while release introduces sensitivity and source-dependent disagreement. It does not establish a validated physiological generator or a scientifically accepted replacement fitter. Retain the adverse candidate outcome and initialization-sampling coupling in any manuscript account.
