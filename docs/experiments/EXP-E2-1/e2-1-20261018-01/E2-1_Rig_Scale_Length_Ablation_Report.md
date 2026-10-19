# E2-1 Rig Scale/Length Ablation Report

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

## 1. Research question and motivation

Does allowing verified native skeletal length/width controls to move alter height compression and reconstruction fidelity under the existing NICP surface objective? The intervention is permission to optimize nine controls; its primary effect is Arm C minus Arm B. Releasing the selected controls increased canonical between-person extent variability and produced lower mean reconstruction errors relative to matched locked continuation. This is a bounded experimental result, not scientific acceptance of the resulting bodies.

## 2. E2 finding

Across the original primary 150, source vertical-extent SD was 10.784 cm for SMPL-NICP and 10.794 cm for CAESAR-NICP; canonical native SD was 1.863 and 1.854 cm. All 74 morphology entries 130:204 were zero. The same 60-person crossover retained source/canonical SD 10.069/10.087 cm in the historical LBFGSB pathway but 9.466/1.950 in NICP. These earlier comparisons describe geometry and association. E2-1 supplies a matched solver intervention. Original E0/E4/E2 evidence remains preserved and hashed.

## 3. Official native parameter semantics

These nine columns modify local rest-joint translations, including bilateral mappings; they are not uniform surface rescaling. There is no exposed whole-body/root scale in the 204 rig entries. Root translation and rotation are alignment/articulation. Flexible controls 130:135 include duplicate mappings and authored zero domains and remain fixed; eye offsets, hip height/depth, knee-knock, ankle-height, hand scale and finger offsets/lengths remain fixed. Some names containing “scale” therefore do not describe an admissible body-length intervention. T2 contains all 204 mappings in CSV and a focused manuscript subset; exact coefficients, authored limit weights and reasons are preserved in the private control manifest. Hard bounds use authored MinMax domains; the native limit-weight metadata is not silently reinterpreted as a clinical prior.

## 4. Original NICP restrictions

The pinned production NICP fitter optimized identity, its original named articulation subset and external translation, with neutral expression and morphology entries 130:204 fixed to zero. It used bidirectional area-sampled nearest-cloud pseudo-Huber reconstruction, identity and pose mean-square priors, Adam, bounds and gradient clipping. This experiment does not replace that qualified production implementation, alter MPII, or use an official SMPL conversion loss in place of the existing NICP objective. Copies do not renew other fitting allowances.

## 5. Frozen participant selection

The unit is a person. The mean original source Y extent across their two NICP pathways orders the frozen 150 primary people into four deterministic quartiles (`numpy.array_split`, tie-break by subject UID). Seed 20261018 selects two crossover and two non-crossover people per quartile, then one development person per quartile. There are 16 unique people, eight crossover, four development and 12 reserved evaluation. Both linked source representations remain together; this local experimental partition does not alter E0/E4 data splits. No replacement follows an observed fitting outcome. T1 uses public Case IDs; exact private source, fit and participant linkage is in experiment.json/selection.json.

## 6. Controlled arms

A is the saved historical state, reused without fitting. B and C start from identical original fitted identity, articulation, expression and explicit external translation. Both reset Adam moments, retain original identity/articulation permissions and receive the same 100-step fine-stage continuation. B fixes the nine selected controls; C releases them. The returned state is the minimum regularized pre-step objective among those 100 iterations. Historical A separates the effects of continuation from those of newly available parameter freedom; C−A is not the primary causal contrast.

## 8. Height variability results

Canonical variability is partially recovered, remaining about 59% of source SD in the reserved evaluation subset. Actual native environment: Python 3.12.12, PyTorch 2.8.0, NumPy 2.3.5, SciPy 1.18.1, PyMomentum 0.1.0; CPU execution, CUDA available=False. Exact platform/runtime paths and package metadata are retained in native-environment.json.

**SMPL-NICP:** source SD 10.02; historical A 1.887; locked B 1.873; released C 5.872 engineering cm. SD/source-SD ratios B→C: 0.1869→0.5861. Canonical height MAE B→C: 7.812→4.343 cm. Paired SD-ratio effect: 0.3991 (95% paired bootstrap interval [0.2111, 0.4868]; n=12). Paired height absolute-error change: -3.469 (95% paired bootstrap interval [-5.197, -1.713]; n=12) cm.

**CAESAR-NICP:** source SD 10.02; historical A 1.851; locked B 1.792; released C 5.879 engineering cm. SD/source-SD ratios B→C: 0.179→0.587. Canonical height MAE B→C: 7.863→4.333 cm. Paired SD-ratio effect: 0.4081 (95% paired bootstrap interval [0.2119, 0.4958]; n=12). Paired height absolute-error change: -3.53 (95% paired bootstrap interval [-5.194, -1.838]; n=12) cm.

T4 supplies SD, minimum/maximum, IQR, bias, MAE, RMSE, Pearson/Spearman correlation, regression slope and SD ratio separately for fitted/canonical states, each pathway, development/evaluation, and all-16 descriptive context. Increased spread is assessed alongside individual error. Source and canonical pose differ; this is global Y extent, not observed clinical stature. Figures 2–3 show every reserved participant.

## 9. Pose and skeletal diagnostics

The within-native canonical-minus-fitted extent is recorded per person and arm. Skeleton-derived thigh, shank, upper-arm, root-to-neck, neck-to-head, foot lengths and hip/shoulder widths are retained with vertical projections and left/right asymmetry. They describe the generated rig, not directly observed source bone lengths. T7 includes pose deltas and cranial-envelope descriptors. Full per-state dimensions are in private evaluation records. Pose parameter changes are retained, including pelvis/root, spine/neck, knees and feet where the original mask permits them. Correctives, articulation and local joint offsets can all change the envelope; overall extent change cannot be assigned wholly to femur, tibia or spine length. No scalp/skull/hair boundary is independently known; no hairstyle removal is claimed.

## 10. Independent geometric reconstruction

**SMPL-NICP:** C−B symmetric mean surface error -0.1188 (95% paired bootstrap interval [-0.1738, -0.07914]; n=12) engineering cm.

**CAESAR-NICP:** C−B symmetric mean surface error -0.1147 (95% paired bootstrap interval [-0.1679, -0.07852]; n=12) engineering cm.

The original source-to-working rigid transform, saved external translation and engineering unit convention are retained; no post-hoc fitted scale/alignment is applied. Evaluation uses native LOD0, 4096 deterministic independent area samples per direction and the established exact point-to-triangle engine. Source samples are byte-identical across A/B/C; target area-weighted sampling uses common random seeds, allowing area probabilities to follow each actual surface. This is distinct from optimization’s sampled-cloud loss. Mean/median/RMS/P95 and both directions are in T5, regional C−B effects in paired-effects.csv. Dominant-joint proxy regions cover torso, legs, arms, head/neck, hands and feet; source labels are transferred once from the historical fitted body. Those transferred labels are not independently annotated source anatomy. Zero-area faces are masked identically by policy; validity observations are retained, not used as arbitrary error gates.

## 11. Anthropometric preservation

SMPL-NICP, waist: paired absolute-error change -0.1147 (95% paired bootstrap interval [-0.4497, 0.2225]; n=12) cm.

SMPL-NICP, abdomen: paired absolute-error change -0.4848 (95% paired bootstrap interval [-0.9247, 0.009031]; n=12) cm.

SMPL-NICP, hip: paired absolute-error change -0.2993 (95% paired bootstrap interval [-0.6318, 0.04053]; n=12) cm.

CAESAR-NICP, waist: paired absolute-error change -0.4776 (95% paired bootstrap interval [-0.9349, 0.02555]; n=12) cm.

CAESAR-NICP, abdomen: paired absolute-error change -0.3928 (95% paired bootstrap interval [-0.8894, 0.1061]; n=12) cm.

CAESAR-NICP, hip: paired absolute-error change -0.3824 (95% paired bootstrap interval [-0.7567, -0.02068]; n=12) cm.

The primary broad-coverage engineering panel above holds each original source plane and circumference definition fixed in A/B/C: raw contour for waist/abdomen/chest, tape envelope for hip/neck. It is pose-sensitive and does not certify the plane’s anatomical site. The separate E2 midpoint/surface proxy panel re-extracts sites with the unchanged E2 IndexedSections, atlas attachments and hip landmark rule; fitted and canonical results remain separate. Missing source midpoint proxies, particularly CAESAR, are retained rather than silently replaced. Historical engineering quantities are supported diagnostics, not relabelled midpoint measurements. No plane is chosen by minimizing C’s error. T6 includes signed bias, MAE, RMSE, median/P95 absolute errors, valid coverage and missingness; individual records preserve source/target contour-failure reasons and raw/tape quantities.

Waist fallback selection method, anatomical evidence, contour validity and proxy status remain separate. The historical fallback is a mapped umbilicus offset, not a verified rib-to-iliac midpoint; use of fallback alone is not an anatomical failure. Historical fallback flags are retained in both arms. The fixed-source-plane panel introduces no target-driven fallback. Neck is an engineering contour where the source plane and eligible closed contour exist. Chest is exploratory only where valid. No new metrology engine or physical calibration is introduced.

## 12. Parameter movement and plausibility

All permitted controls are checked against actual native gradients and saved fitted states; locked and all other frozen entries remain bitwise unchanged. 9/32 completed released fits have at least one retained parameter at its authored bound. Bound contact is reported, not treated as scientific failure. The parameter heatmap includes development and evaluation, with all nine raw values and their relative authored magnitudes. Mesh finite status, winding, watertightness, duplicate/zero-area faces and asymmetry are recorded in T7. Existing native facial topology defects are not “repaired” or excluded by outcome. Self-intersections and anatomical plausibility have not been comprehensively validated; these diagnostics cannot establish clinical acceptability.

## 13. Pathway differences and cross-path consistency

SMPL-NICP and CAESAR-NICP remain separate paired analyses on the same people. The corresponding-index canonical native RMS in cross-path.csv quantifies changes in cross-path agreement with fixed T90 and floor translation; root placement remains part of that descriptor. Regional and circumference differences can move differently. Agreement between generated branches is distinct from accuracy against individual anatomy; correlated source/pipeline errors can also converge.

## 14. Historical LBFGSB context

Reserved cross-path canonical vertex RMS changed by 0.4756 (95% paired bootstrap interval [0.2823, 0.7211]; n=12) engineering cm (positive means greater disagreement). This is an observed trade-off despite lower source reconstruction errors.

The eight selected crossover people retain the existing LBFGSB source/canonical height evidence in LBFGSB-context.csv. Those bodies involve a different source and fitting pathway and are not an additional experimental arm. Neither this contextual crossover nor the earlier 60-person association identifies the effect of releasing controls under a common solver. Only C−B supplies that matched intervention estimate.

## 15. Statistical uncertainty

People, not source branches, poses or circumferences, are resampled. Each pathway uses the same participant indices for its B/C contrast; no 24-pathway observation count is reported as 24 independent evaluation people. For a variability contrast, source/B/C height vectors are resampled jointly and SD ratios recomputed, with constant-source bootstrap draws explicitly counted. Paired means use the existing E4 bootstrap. There are 2000 deterministic percentile replicates, unadjusted exploratory 95% intervals; no significance requirement or acceptance margin is imposed. Development (n=4/path) is separate from reserved evaluation (n=12/path). The all-16 summaries are descriptive only. Small convenience samples, non-normal errors and stratified selection limit population inference.

## 16. Failures and limitations

Counts: `{"attempted": 64, "complete_matched_branches": 32, "completed": 64, "development_people": 4, "evaluated_branches": 32, "evaluation_people": 12, "failed": 0, "regenerated": 64, "selected_branches": 32, "selected_people": 16}`. Failed/missing arms, unavailable contours and their reasons remain in versioned records; no high-error person is removed. Digital source units remain engineering cm with unconfirmed physical calibration. Source mesh, atlas, landmark and NICP shape errors, fixed-sample objective approximation, warm-start dependence, added rig prior, limited 100-step budget, correlated pathway inputs and incomplete anatomy validation remain limitations. Finite native geometry and exact participant/input matches are necessary numerical validity checks, not scientific quality approvals. Partial or adverse outcomes do not trigger recovery fits or a larger study.

## 17. Mechanistic interpretation

Releasing the selected controls increased canonical between-person extent variability and produced lower mean reconstruction errors relative to matched locked continuation. C−B estimates the effect of permitting these nine controls under this particular initialization, objective, regularization, bound set and finite optimization schedule. It can establish a modifiable restriction in that pipeline if useful variation and reconstruction change together. It does not isolate each control’s effect, identify the unique physiology or bone anatomy of a participant, prove optimal use of all native MHR capacity, or imply that the full historical NICP/LBFGSB difference is caused by this restriction. A/B differences diagnose continuation effects separately. Participant-specific worsening or regional trade-offs remain evidence rather than exclusions.

## 18. Implications for SomatoAnthro

Dataset engineering can preserve full native controls, expose an explicitly versioned fitting mask, retain fitted and canonical states, and maintain source-matched identity linkage and per-person error/coverage metadata. Shape diversity should be monitored jointly with source fidelity and measurement validity; marginal height spread alone must not become a selection target. The present experimental bodies are separate candidates and do not replace production, physiological labels or scientific qualification. Body composition and observed geometry remain distinct.
