# E1 — Geometric Fidelity and Reconstruction Decision Analysis

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

## 1. Executive scientific assessment

E1 evaluated 90 own-source/fitted-pose pairs from seven source families, using ten dataset-local people per family and three NOMO pathways for the same ten people. NHANES is kept separate. No global count of independent donors is asserted. The complete native-control audit contains 90 paired fitted/canonical states.

The frozen completed WAIST primary result is reproduced from participant records: 149 complete NOMO people; SomatoSynth3D MAE 2.893 versus clad-body 3.543 engineering cm, paired advantage 0.649 (95% CI [0.365, 0.923]), or 18.3% lower MAE against the declared dependent source proxy. This is neither independent anatomical superiority nor physiological accuracy.

## 2. Research question and hypotheses

How do source-specific reconstruction, native-control restrictions, articulation transfer and measurement-site decisions affect source-surface and digital-measurement preservation? Competing explanations include regional residuals, source/reference dependence, selected plane location, pose, control freedom and contour functional. None is assumed causal from observational correlations.

## 3. Relationship to previous experiments

Pinned inputs: E0 `e0-unified-20261018-01`; E2 `e2-20261018-01/report03`; E4 `e4-20261018-03/report02`; E2-1 `e2-1-20261018-01`; E2-2 `e2-2-20261018-01/presentation-v2`; E3 `e3-20261018-04`; RECON `recon-20261018-04`; WAIST `waist01-20261018-02`. Original metric records, controls, correction candidates and negative results are retained. E1 does not repeat those experiments.

## 4. Dataset and representation inventory

E1-T1 distinguishes full saved coverage, dataset-local people, source observations, eligible pairs and the bounded fresh panel. The population counts are dependent across pathways and resources. FIT03 includes historical SMPL-LBFGSB and SMPL-NICP; FIT04 is CAESAR-NICP. FIT09 is numerical conditioning only.

## 5. Source-to-MHR architecture

Released source → saved source-specific transform/correction → existing fitted native MHR → saved fitted-pose surface → pinned T90 or explicitly labelled historical neutral → declared computational metrology → E5 engineering handoff. Figure E1-1 locates the evidence supplied by each completed experiment.

## 6. Source-specific engineering corrections

The inventory reads existing FIT01–FIT09 implementations. MPII uses its actual 6449-point topology, saved axis conversion and fit translation; UCSC uses saved proper orientation and original/hardfeet/hybrid candidates; NOMO retains three source/fitting pathways; HIT retains its proper source-axis rotation; FAUST retains source-unit similarity frames; D-FAUST retains independent motion-frame fits; HBW retains the released SMPL-X exterior. These transforms are reused exactly, with no new alignment or scale optimisation.

## 7. Decision registry and evidence strength

E1-T2 contains 24 stable decisions with problems, rationale, exact code hashes, implementation references, evidence class, confounders and downstream relevance. Controlled fitting permissions, same-body measurement-method comparisons, matched historical pipeline changes and implementation-only decisions remain distinct. An implemented correction is not thereby scientifically validated.

## 8. Geometry methodology

Fresh protocol: 4,096 deterministic area-uniform samples in each direction; exact point-to-opposite-triangle distances using the existing conservative centroid/radius engine; independent per-pair seed derived from 18102601. Mean, median, RMS and pooled P95 are distinct. Positive-area triangles only; masked counts retained. Unoriented nearest-face normal agreement is descriptive. Global directional weights are equal. Regional samples are allocated by global area sampling, and regional pooled weights follow their reported directional counts.

Own source and fitted articulation are compared in their saved matching frame. Canonical T90 is never substituted as a source reconstruction target. Fresh LOD0 is used for MPII, UCSC, NOMO, HIT and HBW; only saved own-pose LOD1 is available here for FAUST and D-FAUST. The 0.02 numerical coverage radius is a descriptive engineering radius, not a scientific acceptance threshold. No silhouette result is manufactured.

## 9. Global reconstruction fidelity

The following values are participant means of each per-pair statistic, not pooled surface-sample distributions. Each row has ten people. Engineering-metre rows remain uncalibrated physically; FAUST and D-FAUST retain their separate source-unit conventions. Bootstrap intervals and directional statistics are in E1-T3.

| Dataset/pathway | Mean | RMS | P95 | Unit / LOD |
| --- | ---: | ---: | ---: | --- |
| DFAUST / saved_native | 0.004189 | 0.005656 | 0.011277 | DFAUST_source_units_conditional_m; LOD1 |
| FAUST / saved_native | 0.005533 | 0.007714 | 0.014313 | FAUST_source_units_physical_unconfirmed; LOD1 |
| HBW / saved_native | 0.003502 | 0.004797 | 0.009834 | engineering_m_HBW_model_linked; LOD0 |
| HIT / saved_native | 0.005400 | 0.008664 | 0.017839 | engineering_m_HIT_model_linked; LOD0 |
| MPII / saved_native | 0.004735 | 0.007778 | 0.013454 | engineering_m; LOD0 |
| NOMO / CAESAR-NICP | 0.004352 | 0.006561 | 0.012455 | engineering_m; LOD0 |
| NOMO / SMPL-LBFGSB | 0.003322 | 0.004589 | 0.009636 | engineering_m; LOD0 |
| NOMO / SMPL-NICP | 0.004257 | 0.006299 | 0.011947 | engineering_m; LOD0 |
| UCSC / saved_native | 0.008746 | 0.013500 | 0.030702 | engineering_m; LOD0 |

Historical E0 reports and 360 unique NOMO own-source body metrics recovered through E4 remain a separate evidence level with their original protocol. No cross-dataset pooled accuracy statistic is justified.

## 10. Regional geometry analysis

E1-T4 reports torso, thorax, abdomen, pelvis, head/neck, upper/lower limbs and feet where the LOD0 native-weight masks apply. Source samples inherit the label of the nearest fitted triangle; this is a fit-dependent engineering proxy, not independent source annotation. No MHR indices are applied directly to unrelated source topology. FAUST/D-FAUST regional source accuracy remains unavailable under this admitted protocol. E1-4 shows real sampled source-surface residuals.

## 11. Feet and lower-limb correction

UCSC original, hardfeet and current hybrid states are compared against the same source, with identical sample seeds and exact metrics. E1-T5 and private correction records retain global/foot errors, floors and extents, including increases. These are combined historical pipeline effects; controls and optimisation history prevent an isolated hardfeet causal claim. A floor translation cannot alter maximum-minus-minimum extent.

The current UCSC pipeline has a larger global mean discrepancy than the saved original by 0.355 engineering cm on average, participant CI [0.154, 0.568], n=10. Average foot-region RMS is 2.202 before versus 2.602 after. This contrary result prevents a blanket claim that the saved correction pipeline improved source-surface fidelity.

## 12. Head/neck and cranial-envelope reconstruction

E1-T7 and the head/feet diagnostics retain source/fitted extrema, vertex q99 envelope descriptors and native head/neck-region errors. Source hair, scalp and skull are not independently labelled. E2's approximately 3.2 engineering-cm mean extent discrepancy cannot be causally assigned to hairstyle using endpoint analysis. Neck/shoulder exclusion is a metrology correction, not proof of correct neck anatomy.

## 13. Pose alignment and normalisation

FAUST source and fitted comparison surfaces stay in original registered source units with the historical fitted similarity transform. D-FAUST retains independent observation fitting and the E3 six-frame-per-person panel. A rigid source-axis convention, a fitted global similarity and a native articulation change are separate operations. HIT historical neutral is explicitly distinguished from T90.

## 14. T90 implementation and parameter retention

Across the 90 audited pairs: identity preserved 90/90; morphology [130:204] preserved 90/90; expression preserved 80/90; exact pinned [0:130] articulation 80/90. The ten HIT states are historical neutral exceptions. The ten sampled historical LBFGSB states change expression; their geometric transition cannot be attributed to articulation alone. Native dimensions and pose-control differences are retained in E1-T6.

## 15. Torso reconstruction and surface consistency

Native torso/abdomen/pelvis residuals are linked to the exact subject, body, fit, source hash and measurement definition. Common articulation does not guarantee common recovered morphology: E3 and E4 document repeated-observation and cross-pathway canonical disagreement. Those estimands remain separate from source-fitted reconstruction error.

## 16. Waist and abdomen engineering

The original adaptive profile, ambiguity triggers and mapped umbilicus+0.005 m fallback are unchanged. The comparator is the actual clad-body MHR API at commit `a2140a74555a6382e1712ec1a5d8dc939b59e655`: floor-aligned 61% maximum Z after its original coordinate helper, fragment filtering and convex hull circumference. Its source hashes are verified; E1 does not execute that experiment again.

The common raw-contour comparison preserves the frozen 0.652 engineering-cm advantage, close to the end-to-end 0.649. This supports a site-related contribution under the tested dependent endpoint, but does not prove that all effects are due to plane location. The offset-only baseline has MAE 2.714 versus 2.893 and a paired adaptive advantage of -0.179, CI [-0.377, -0.008]. There is no incremental superiority evidence for the complete adaptive selector over this simpler baseline. The umbilical abdominal site is a mapped model feature, not independently observed anatomy.

## 17. Hip, neck and chest decisions

## 18. Fitting restrictions and representation flexibility

The nine verified skeletal controls concern spine, neck, shoulder width, upper/lower arms, hip width, upper/lower legs and feet. E1-T10 reproduces every existing participant-level intervention contrast, preserving development/validation/test and E2-1/E2-2 dependence. Released controls improve tested source fidelity and extent preservation while increasing pathway disagreement and sampling sensitivity. No intervention is rerun and no new general optimisation method is claimed.

## 19. Geometry versus anthropometric preservation

E1-T9 separates fresh regional-panel correlations from broader historical-E4 global-residual correlations, and separates fitted/canonical states and measurement protocols. Some intervals are broad or include zero. Geometry errors and circumference differences are related quantities with different supports; correlations cannot identify a causal error budget.

Broader original-metric evidence, CAESAR-NICP / height: source-fitted global residual versus absolute canonical digital difference has rho 0.867, CI [0.809, 0.906], n=150.
Broader original-metric evidence, CAESAR-NICP / hip: source-fitted global residual versus absolute canonical digital difference has rho 0.257, CI [0.098, 0.409], n=150.
Broader original-metric evidence, CAESAR-NICP / neck: source-fitted global residual versus absolute canonical digital difference has rho -0.052, CI [-0.259, 0.151], n=105.
Broader original-metric evidence, CAESAR-NICP / waist: source-fitted global residual versus absolute canonical digital difference has rho 0.083, CI [-0.077, 0.245], n=149.
Broader original-metric evidence, SMPL-NICP / height: source-fitted global residual versus absolute canonical digital difference has rho 0.848, CI [0.780, 0.893], n=150.
Broader original-metric evidence, SMPL-NICP / hip: source-fitted global residual versus absolute canonical digital difference has rho 0.296, CI [0.132, 0.448], n=150.
Broader original-metric evidence, SMPL-NICP / neck: source-fitted global residual versus absolute canonical digital difference has rho 0.017, CI [-0.184, 0.227], n=102.
Broader original-metric evidence, SMPL-NICP / waist: source-fitted global residual versus absolute canonical digital difference has rho 0.020, CI [-0.138, 0.171], n=149.

The prespecified canonical extent associations are strong in both NICP pathways, while the waist and neck intervals include zero. Hip associations are modest. These comparisons do not isolate morphology from pose, control restrictions or measurement-site dependence. The small fresh regional panel does not establish that regional residuals explain waist-method advantage better than global metrics.

For CAESAR-NICP, absolute plane separation versus common-raw waist advantage has Spearman rho -0.033, 95% CI [-0.220, 0.153], n=149. This is a new exploratory association, not a causal explanation.
For SMPL-NICP, absolute plane separation versus common-raw waist advantage has Spearman rho 0.283, 95% CI [0.096, 0.462], n=149. This is a new exploratory association, not a causal explanation.

The contrary method findings remain: fitted CAESAR-NICP favours clad-body (advantage -1.532, CI [-2.266, -0.799]); canonical CAESAR-NICP is inconclusive (0.032, CI [-0.323, 0.378]). Source representation, pose and selected planes matter to the estimand. Body-proportion surrogates are axial surface descriptors, not qualified anatomical torso/leg lengths.

## 21. Statistics and uncertainty

The independent unit is the verified dataset-local person. Source pathways, repeats and poses are aggregated within person for each explicitly defined estimand. Deterministic 2,000-replicate participant bootstraps use seed 18102601 with stable keyed seeds. Frozen WAIST intervals retain seed 18012601. Spearman intervals resample paired participants with tie-aware ranks. All new associations are exploratory without multiplicity adjustment. Intervals from dependent experiments are not averaged.

## 22. Source-reference and anatomical limitations

E1-T11 retains physical-unit uncertainty, source registration/model-fit error, unresolved donor overlap, missing regional/camera evidence, pose differences, morphology/expression confounding and unqualified landmarks. No numerical field is promoted to independently observed anatomy.

## 23. Implications for synthetic anthropometric datasets

The evidence supports an auditable reconstruction-to-metrology chain: high global fidelity does not by itself qualify a selected circumference or site; representation freedom, articulation and method choices require distinct evidence. The present data quantify their tested consequences and uncertainty, including contrary outcomes.

## 24. Body-fat-estimation relevance

Height, waist, abdominal, hip and neck digital discrepancies may influence future equation inputs. The dependence, dimensional qualification and site compatibility must accompany them. Reconstruction residuals, canonical changes, method differences and repeated observations are not additive independent stochastic error terms. No body-fat percentages or physiological improvements are calculated or inferred.
