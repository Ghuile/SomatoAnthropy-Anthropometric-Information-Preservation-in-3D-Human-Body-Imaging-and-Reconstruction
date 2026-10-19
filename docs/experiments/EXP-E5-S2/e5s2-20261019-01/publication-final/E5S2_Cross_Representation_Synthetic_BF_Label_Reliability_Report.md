# E5-S2 — Cross-Representation Synthetic BF Label Reliability

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

## 1. Executive scientific assessment

A simple umbilicus-offset policy offers the strongest tested NOMO balance of cross-path consistency and dependent source agreement. The adaptive method does not dominate: it retains more coordinate dispersion but has larger canonical disagreement. Official clad-body is the most consistent of the three primary methods across D-FAUST observations. These findings support conditional engineering choices and immediate manuscript drafting, with no further experiment programme.
|method|height_policy|consistency_people|cross_path_mae_pp|cross_path_ci95|source_people|coordinate_sd_pp|source_sd_ratio|reference_mae_pp|
|---|---|---|---|---|---|---|---|---|
|B1|H1|150|0.2380|[0.2032, 0.2803]|149|3.9640|0.8511|1.8372|
|B1|H2|150|0.2193|[0.1878, 0.2568]|149|3.8244|0.8211|1.5452|
|B1|H3_strict|103|0.1979|[0.1645, 0.2356]|103|4.0249|0.8672|1.2345|
|B3_offset|H1|150|0.2159|[0.1833, 0.2550]|149|4.6951|1.0081|2.0942|
|B3_offset|H2|150|0.2032|[0.1720, 0.2396]|149|4.3021|0.9237|1.1511|
|B3_offset|H3_strict|103|0.1772|[0.1456, 0.2118]|103|4.3182|0.9303|0.9992|
|P|H1|150|0.3297|[0.2179, 0.4670]|149|5.3557|1.1499|2.4118|
|P|H2|150|0.3093|[0.2051, 0.4368]|149|4.8346|1.0380|1.2734|
|P|H3_strict|103|0.3047|[0.1775, 0.4670]|103|4.7247|1.0179|1.1155|

## 2. Research questions and hypotheses

H1: method-dependent consistency; H2: consistency/source-agreement trade-off; H3: between-person dispersion sensitivity; H4: height-policy effects; H5: simple offset versus adaptive complexity; H6: pathway dependence. These are retrospective exploratory hypotheses, not independently preregistered tests. The policy set, numerical ladder, endpoint definitions and seed were frozen before the new outcomes. No waist thresholds were tuned.

## 3. Relationship to the complete prior programme

E0 supplies identity/asset provenance; E1 reconstruction and canonicalisation lineage; E2 anthropometric preservation; E2-1 and E2-2 morphology-permission interventions on dependent NOMO subsets; E3 repeated-observation consistency; E4 cross-representation sensitivity; WAIST supplies the actual frozen P/B1/offset and contour controls; E5 propagates these inputs through formulas; E5-S1 separates height control from waist agreement; RECON records dependence and scientific reconciliation. E5-S2 derives policy comparisons from these saved quantities. It does not generate new bodies or independent intervention participants. Cross-resource donor overlap remains unresolved.

## 4. Frozen evidence and reproducibility boundary

|experiment|version|revision|
|---|---|---|
|E0|e0-unified-20261018-01||
|E1|e1-20261018-02||
|E2|e2-20261018-01|report03|
|E2-1|e2-1-20261018-01||
|E2-2|e2-2-20261018-01|presentation-v2|
|E3|e3-20261018-04||
|E4|e4-20261018-03|report02|
|WAIST-01|waist01-20261018-02||
|RECON-01|recon-20261018-04||
|E5|e5-20261018-03||
|E5-S1|e5s1-20261018-01||

The private input-pins manifest protects every frozen file and inherited original mesh/model/parameter hashes. Repository HEAD, branch, dirty status, interpreter and package versions are in repository-initial.json. Historical and newly computed uncertainty intervals retain different seeds/estimands.

## 5. Formula response versus absolute BF

## 6. Cohorts and participant dependence

NOMO: 150 frozen dataset-local identities, two pathways (SMPL-NICP and CAESAR-NICP), two states (fitted and canonical), 600 linked bodies. Source-free canonical comparisons retain all 150 where inputs exist. The original dependent-reference complete cohort has 149 people / 596 body observations (298 canonical). Strict H3 has 103 source-height-eligible people, all with complete original reference measurements. D-FAUST: ten people, six independently fitted canonical observations each, 60 bodies. Frames, states, pathways and pairwise combinations are never counted as independent people. Coverage differs in common-contour controls and is tabulated without imputation.

## 7. Candidate waist measurements

P is the frozen adaptive lower-half selector with explicit mapped umbilicus +0.005 engineering metre fallback. B1 is actual official clad-body at 61% floor-aligned body height with its original convex-hull implementation, commit a2140a74555a6382e1712ec1a5d8dc939b59e655. B3_offset uses that umbilicus offset as a standalone raw-contour method. Supplementary B2 uses 63% raw contour and is not the official method. No anatomical correctness follows from a winning proxy endpoint.

## 8. Height policies

H1 uses each saved body's geometric Y extent. H2 uses its own pathway's frozen source Y extent for both fitted/canonical bodies. H3_strict preserves E5-S1's exact 1e−8 cm eligibility and original SMPL descriptor choice. Relaxed H3 thresholds use the symmetric median of the two source heights after numerical compatibility; the frozen source-formula reference is never re-anchored. No clinical stature is qualified.

## 9. Identity-height precision and eligibility

|policy|threshold_cm|eligible_people|anchor_construction|
|---|---|---|---|
|H3_strict|0.0000|103|original strict SMPL source|
|H3_t0.001|0.0010|104|symmetric two-path source median|
|H3_t0.01|0.0100|109|symmetric two-path source median|
|H3_t0.1|0.1000|138|symmetric two-path source median|
|H3_t0.25|0.2500|150|symmetric two-path source median|

The 47 strict mismatches span 0.0004–0.2338 engineering cm (median 0.0459). All 300 source OBJ files use six decimal metre Y coordinates (text step 0.0001 cm). The smallest mismatch exceeds ordinary double roundoff and the approximately 0.0002 cm discrepancy from two independently rounded extents of identical extrema. All recorded source-to-working linear parts are identity rotations with translations, which cannot explain extent differences. These are saved representation-extent disagreements; topology/extrema, released-pose and discretisation causes cannot be individually resolved from these records. Relaxed eligibility is numerical sensitivity, never proof of anatomical equality.

## 10. Canonical cross-representation variability

The principal endpoint is |q_SMPL−q_CAESAR| on each identity's two canonical bodies. Signed SMPL-minus-CAESAR bias, median, P90/P95, participant-bootstrap intervals and deterministic largest cases are in S2-T4 and its supplements.
|method|height_policy|people|mean|mean_ci95|median|p90|p95|signed_bias_pp|
|---|---|---|---|---|---|---|---|---|
|B1|H1|150|0.2380|[0.2032, 0.2803]|0.1687|0.4766|0.6010|0.0379|
|B1|H2|150|0.2193|[0.1878, 0.2568]|0.1561|0.4492|0.5358|0.0297|
|B1|H3_strict|103|0.1979|[0.1645, 0.2356]|0.1368|0.4187|0.5212|0.0672|
|B3_offset|H1|150|0.2159|[0.1833, 0.2550]|0.1582|0.4033|0.5432|-0.0270|
|B3_offset|H2|150|0.2032|[0.1720, 0.2396]|0.1468|0.3980|0.4990|-0.0337|
|B3_offset|H3_strict|103|0.1772|[0.1456, 0.2118]|0.1280|0.3805|0.4501|0.0050|
|P|H1|150|0.3297|[0.2179, 0.4670]|0.1560|0.4529|0.8202|-0.0120|
|P|H2|150|0.3093|[0.2051, 0.4368]|0.1532|0.4361|0.7734|-0.0201|
|P|H3_strict|103|0.3047|[0.1775, 0.4670]|0.1291|0.4276|0.6418|-0.0179|

## 11. Fitted-to-canonical sensitivity

These changes combine articulation transfer, pose correctives and measurement changes; they are not repeated independent observations. They remain separate from canonical cross-path disagreement.
|method|height_policy|pathway|people|mean|mean_ci95|signed_change_pp|
|---|---|---|---|---|---|---|
|B1|H1|CAESAR-NICP|150|1.1977|[0.9027, 1.5865]|-0.5704|
|B1|H1|SMPL-NICP|150|1.2419|[0.9247, 1.6564]|-0.5823|
|B1|H2|CAESAR-NICP|150|0.6330|[0.4973, 0.8082]|-0.1410|
|B1|H2|SMPL-NICP|150|0.6510|[0.5016, 0.8461]|-0.1462|
|B1|H3_strict|CAESAR-NICP|103|0.5504|[0.4040, 0.7667]|-0.0687|
|B1|H3_strict|SMPL-NICP|103|0.5597|[0.4051, 0.7871]|-0.0574|
|B3_offset|H1|CAESAR-NICP|150|1.6080|[1.3538, 1.9065]|-1.0800|
|B3_offset|H1|SMPL-NICP|150|1.6046|[1.3549, 1.8974]|-1.0686|
|B3_offset|H2|CAESAR-NICP|150|0.8334|[0.7202, 0.9515]|-0.6141|
|B3_offset|H2|SMPL-NICP|150|0.8149|[0.7041, 0.9289]|-0.5978|
|B3_offset|H3_strict|CAESAR-NICP|103|0.7328|[0.6253, 0.8475]|-0.4682|
|B3_offset|H3_strict|SMPL-NICP|103|0.7266|[0.6208, 0.8418]|-0.4502|
|P|H1|CAESAR-NICP|150|2.1293|[1.7963, 2.5164]|-0.0394|
|P|H1|SMPL-NICP|150|2.0337|[1.7200, 2.3915]|0.3168|
|P|H2|CAESAR-NICP|150|1.6633|[1.4139, 1.9258]|0.4144|
|P|H2|SMPL-NICP|150|1.6542|[1.3940, 1.9172]|0.7681|
|P|H3_strict|CAESAR-NICP|103|1.5070|[1.2369, 1.7847]|0.5723|
|P|H3_strict|SMPL-NICP|103|1.4145|[1.1610, 1.6823]|0.7198|

## 12. D-FAUST repeated observations

The historical E5 estimates and original intervals reproduce exactly; the newly derived 4,000-draw intervals use seed 51912601 and are labelled separately.
|method|mean_sd_pp|historical_ci95|
|---|---|---|
|P|0.6222|[0.5040, 0.7701]|
|B1|0.5135|[0.3726, 0.6555]|
|B3_offset|0.5666|[0.4683, 0.6777]|
|B2|0.5310|[0.3838, 0.7126]|

|method|metric|people|mean|mean_ci95|
|---|---|---|---|---|
|B1|sd_pp|10|0.5135|[0.3805, 0.6622]|
|B1|range_pp|10|1.3728|[1.0139, 1.8039]|
|B1|mad_pp|10|0.3040|[0.1912, 0.4206]|
|B1|mean_pairwise_absolute_pp|10|0.6027|[0.4438, 0.7812]|
|B2|sd_pp|10|0.5310|[0.3857, 0.7111]|
|B2|range_pp|10|1.3852|[1.0180, 1.8187]|
|B2|mad_pp|10|0.3390|[0.2185, 0.4920]|
|B2|mean_pairwise_absolute_pp|10|0.6234|[0.4487, 0.8415]|
|B3_offset|sd_pp|10|0.5666|[0.4706, 0.6783]|
|B3_offset|range_pp|10|1.4914|[1.2333, 1.7846]|
|B3_offset|mad_pp|10|0.3380|[0.2520, 0.4360]|
|B3_offset|mean_pairwise_absolute_pp|10|0.6682|[0.5559, 0.7989]|
|P|sd_pp|10|0.6222|[0.5002, 0.7712]|
|P|range_pp|10|1.6122|[1.3178, 1.9356]|
|P|mad_pp|10|0.4045|[0.2729, 0.5572]|
|P|mean_pairwise_absolute_pp|10|0.7323|[0.5813, 0.9159]|

All ten participant outcomes, six-observation SD/range/MAD and 15 dependent pair differences per person are saved. There is no qualified independent D-FAUST identity height. An observation-median height is only a descriptive counterfactual; it is never H2/H3. Differences combine registration, fitting, pose, recovered morphology and measurement-site variation.

## 13. Between-person response-coordinate diversity

The person coordinate is the mean of its two canonical pathway values. Sample SD, IQR, P5–P95 span, pathway rank agreement, source rank and paired SD-ratio intervals are reported. Larger SD is not automatically better: artefacts can inflate it.
|method|height_policy|people|sd|sd_ci95|iqr|p5_p95_range|source_sd|sd_ratio|sd_ratio_ci95|source_spearman|cross_path_spearman|
|---|---|---|---|---|---|---|---|---|---|---|---|
|B1|H1|149|3.9640|[3.4377, 4.4876]|5.0800|11.8737|4.6575|0.8511|[0.7742, 0.9672]|0.8907|0.9952|
|B1|H2|149|3.8244|[3.3335, 4.2802]|4.9968|12.0643|4.6575|0.8211|[0.7788, 0.8634]|0.9451|0.9959|
|B1|H3_strict|103|4.0249|[3.3836, 4.6138]|4.9268|12.9375|4.6416|0.8672|[0.8310, 0.9052]|0.9553|0.9965|
|B3_offset|H1|149|4.6951|[4.1273, 5.2489]|5.9412|14.8959|4.6575|1.0081|[0.9181, 1.1293]|0.8682|0.9978|
|B3_offset|H2|149|4.3021|[3.7866, 4.7779]|6.0224|13.8726|4.6575|0.9237|[0.8925, 0.9575]|0.9688|0.9960|
|B3_offset|H3_strict|103|4.3182|[3.6487, 4.9389]|5.5315|14.1167|4.6416|0.9303|[0.8980, 0.9678]|0.9758|0.9954|
|P|H1|149|5.3557|[4.6456, 6.0265]|6.4230|18.0579|4.6575|1.1499|[1.0235, 1.3019]|0.8694|0.9942|
|P|H2|149|4.8346|[4.2391, 5.3830]|6.6207|15.5997|4.6575|1.0380|[0.9795, 1.1045]|0.9613|0.9904|
|P|H3_strict|103|4.7247|[3.9786, 5.4207]|5.5726|15.1110|4.6416|1.0179|[0.9554, 1.0911]|0.9710|0.9889|

## 14. Source-to-MHR formula agreement

The comparison always retains the exact frozen source q(Hs,Ws) for the matching pathway and functional. This R3 source proxy depends on historical MHR-mapped source landmarks and measurement selection. It can structurally favour umbilicus methods. It is neither a physical waist nor independent physiological BF ground truth.
|method|height_policy|people|body_observations|mean|mean_ci95|
|---|---|---|---|---|---|
|B1|H1|149|596|1.5686|[1.3902, 1.7684]|
|B1|H2|149|596|1.5805|[1.3939, 1.7793]|
|B1|H3_strict|103|412|1.2734|[1.0885, 1.4643]|
|B3_offset|H1|149|596|1.6194|[1.4595, 1.7982]|
|B3_offset|H2|149|596|1.1794|[1.0533, 1.3105]|
|B3_offset|H3_strict|103|412|1.0164|[0.8812, 1.1520]|
|P|H1|149|596|2.2206|[1.9682, 2.4832]|
|P|H2|149|596|1.4408|[1.2925, 1.6042]|
|P|H3_strict|103|412|1.3315|[1.1570, 1.5078]|

## 15. Canonical dependent-reference agreement

The source-dependence limitation applies directly to every row below. Matching a proxy does not establish anatomical accuracy.
|method|height_policy|people|mean|mean_ci95|signed_bias_pp|
|---|---|---|---|---|---|
|B1|H1|149|1.8372|[1.6185, 2.0915]|-0.0085|
|B1|H2|149|1.5452|[1.3638, 1.7433]|1.0779|
|B1|H3_strict|103|1.2345|[1.0619, 1.4112]|0.7276|
|B3_offset|H1|149|2.0942|[1.8550, 2.3732]|-0.7954|
|B3_offset|H2|149|1.1511|[1.0358, 1.2722]|0.3381|
|B3_offset|H3_strict|103|0.9992|[0.8754, 1.1266]|0.2348|
|P|H1|149|2.4118|[2.0994, 2.7548]|-1.0984|
|P|H2|149|1.2734|[1.1290, 1.4317]|0.0577|
|P|H3_strict|103|1.1155|[0.9663, 1.2766]|0.0216|

## 16. Simple offset versus adaptive/fallback

Under H2 across the 149 people / 596 bodies, offset mean absolute drift is 1.179 pp (95% CI 1.053 to 1.310; n=149), compared with adaptive 1.441 pp (95% CI 1.293 to 1.604; n=149). Canonical cross-path disagreement is 0.203 pp (95% CI 0.172 to 0.240; n=150) versus adaptive 0.309 pp (95% CI 0.205 to 0.437; n=150). The simpler method remains preferable for these tested NOMO engineering endpoints, with dependent-reference qualification. P retains dispersion closer to the proxy spread under H2. Neither result establishes correct anatomical waist.

## 17. Official clad-body and pathway dependence

Official B1 is competitive on canonical consistency and has the smallest D-FAUST mean SD among primary methods. Pathway/state reference results follow, retaining all contrary outcomes.
|method|height_policy|stratum|people|mean|mean_ci95|
|---|---|---|---|---|---|
|B1|H1|CAESAR-NICP|149|1.2531|[1.0769, 1.4508]|
|B1|H1|SMPL-NICP|149|1.8841|[1.6308, 2.1583]|
|B1|H2|CAESAR-NICP|149|0.9580|[0.8105, 1.1159]|
|B1|H2|SMPL-NICP|149|2.2030|[1.9244, 2.5008]|
|B3_offset|H1|CAESAR-NICP|149|1.4530|[1.2786, 1.6426]|
|B3_offset|H1|SMPL-NICP|149|1.7858|[1.5683, 2.0147]|
|B3_offset|H2|CAESAR-NICP|149|0.6430|[0.5879, 0.7029]|
|B3_offset|H2|SMPL-NICP|149|1.7157|[1.4884, 1.9567]|
|P|H1|CAESAR-NICP|149|2.3444|[2.0464, 2.6533]|
|P|H1|SMPL-NICP|149|2.0968|[1.8425, 2.3702]|
|P|H2|CAESAR-NICP|149|1.3293|[1.1521, 1.5119]|
|P|H2|SMPL-NICP|149|1.5522|[1.3761, 1.7452]|

## 18. Height-anchor sensitivity

The ladder changes eligibility from 103 to 104, 109, 138 and 150. Comparing an unadjusted strict subset mean against a full-cohort mean confounds policy with cohort selection. Canonical, reference and diversity paired-contrast tables therefore intersect identities for every comparison. H2 already removes within-path fitted/canonical height changes while retaining the saved cross-path source difference. Relaxed H3 is sensitivity only; no BF outcome determined an anchor or threshold.

## 19. Height compensation and historical reversals

The original E5 actual-height P-minus-B1 advantage reproduces −0.6519785407196393 pp with historical CI [−0.8720514366604958, −0.4400866515006125]. In E5-S1, source-height control gives approximately +0.140 pp overall; body-height control approximately +0.150 pp. These do not establish overall controlled superiority. Fifty-two people changed preferred method. Clad-body's greater height–waist cancellation explains why actual-height proxy rankings need not match waist accuracy. These are reused historical results, not new independent confirmations.

## 20. Policy trade-offs, coverage and Pareto set

No scalar score is used. Descriptive point-estimate dominance minimises cross-path MAE, dependent canonical reference MAE and |log(canonical/source SD ratio)| on identical participants. The last objective is merely similarity to a dependent source distribution; maximising dispersion is not a goal. Coverage, protocol support and complexity remain separate. Strict/common and full/source-matched comparisons are separate. No interval-based statistical dominance is claimed.
|comparison_group|policy_id|people|cross_path_mae_pp|reference_mae_pp|sd_ratio|height_eligible_people|non_dominated|
|---|---|---|---|---|---|---|---|
|full_source_matched|B1/H1|149|0.2267|1.8372|0.8511|150|False|
|full_source_matched|B1/H2|149|0.2093|1.5452|0.8211|150|False|
|full_source_matched|B1/H3_t0.25|149|0.2093|1.5454|0.8211|150|False|
|full_source_matched|B3_offset/H1|149|0.2082|2.0942|1.0081|150|True|
|full_source_matched|B3_offset/H2|149|0.1960|1.1511|0.9237|150|True|
|full_source_matched|B3_offset/H3_t0.25|149|0.1966|1.1519|0.9237|150|False|
|full_source_matched|P/H1|149|0.3220|2.4118|1.1499|150|False|
|full_source_matched|P/H2|149|0.3021|1.2734|1.0380|150|True|
|full_source_matched|P/H3_t0.25|149|0.3028|1.2740|1.0380|150|False|
|strict_common|B1/H1|103|0.2140|1.7640|0.8983|150|False|
|strict_common|B1/H2|103|0.1979|1.2345|0.8672|150|False|
|strict_common|B1/H3_strict|103|0.1979|1.2345|0.8672|103|False|
|strict_common|B3_offset/H1|103|0.1886|2.0052|1.0093|150|True|
|strict_common|B3_offset/H2|103|0.1772|0.9992|0.9303|150|False|
|strict_common|B3_offset/H3_strict|103|0.1772|0.9992|0.9303|103|True|
|strict_common|P/H1|103|0.3221|2.2410|1.1223|150|False|
|strict_common|P/H2|103|0.3047|1.1155|1.0179|150|False|
|strict_common|P/H3_strict|103|0.3047|1.1155|1.0179|103|True|

Non-dominated policies: {"full_source_matched": ["B3_offset/H1", "B3_offset/H2", "P/H2"], "strict_common": ["B3_offset/H1", "B3_offset/H3_strict", "P/H3_strict"]}.

## 22. Statistical uncertainty and missingness

Sorted dataset-local identities are independent bootstrap clusters. All dependent pathways/states stay together; reference errors are averaged within person before resampling. NOMO primary endpoint uses one canonical pair/person. D-FAUST statistics use one outcome/person, never 60 frames or 150 pairs as independent units. There are 4,000 NumPy default_rng draws with seed 51912601. Intervals are unadjusted exploratory summaries across a declared family of waist-method and height-policy contrasts, not confirmatory multiplicity-controlled tests. Medians and tail quantiles use explicitly defined person outcomes. No missing measurement is imputed; no invalid q is clipped. Machine tables include exact coverage.

## 23. Physical, anatomical and reference limitations

Independent physiological BF, physical waist and clinical stature are absent. Digital Y extent and waist sites are off-protocol RFM inputs. Engineering scale is recorded but physical calibration is unqualified. NOMO source-release categories do not supply complete age/protocol eligibility and no demographic coding is invented. Source-pathway dependence, historical morphology restrictions, articulation/corrective geometry changes and unknown cross-resource donor overlap limit external validity. Numerical reproducibility and AI checks do not establish scientific acceptance or novelty.

## 24. Synthetic data implications

For an existing source population, retain the source-defined height as H2 and prefer a simple frozen offset waist when the objective is the demonstrated NOMO balance. Store source, canonical and observation-specific q alongside uncertainty. Newly generated identities have no observed source height: require explicit generator scale and a reproducible canonical body, then use the declared body extent or a generator-defined identity height as a new annotation convention without asserting the tested H2 advantage transfers.

## 25. Conditional measurement policy recommendation

Existing NOMO reconstructions: offset/H2 is a practical simple default for the measured engineering objective; retain P and B1 diagnostics. Strict H3 can support a shared source-height convention only on its eligible identities, with no stature claim. Relaxed H3 is reported as sensitivity and is not a production recommendation. Repeated D-FAUST reconstruction consistency alone favours B1 by mean SD. P's closer source-coordinate SD under H2 is a distinct possible objective, with larger inconsistency. There is no universal physiological winner.
