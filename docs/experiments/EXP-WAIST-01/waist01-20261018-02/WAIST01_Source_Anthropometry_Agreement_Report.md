# EXP-WAIST-01 — source anthropometry agreement

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

## 1. Research objective

Test whether body-specific adaptive/fallback waist selection improves agreement with an explicitly named source reference over fixed-height selection. This is a saved-body measurement experiment. No body fitting, geometry generation, equation-derived body-fat calculation or scientific acceptance was performed.

## 2. Method definitions

P retains the existing lower-half mapped umbilicus-to-chest adaptive selector and its original fallback triggers. The fallback is mapped umbilicus +0.005 engineering metres. Saved original search profiles are replayed through `select_adaptive`; saved original planes/values remain linked and are checked with indexed contour extraction. For the 60 LBFGSB fitted bodies whose historical released waist was unavailable, this experiment executes the unchanged released-pose selector on the existing mesh; its source-reference gap remains unavailable. Supplementary cases are identified individually. Method table.

## 3. Pinned clad-body implementation

Saved LOD0 engineering metres are converted using the original upstream Y-up-cm helper on `vertices*100`, preserving float32 behaviour and floor alignment. Original geometry is untouched. The common engine uses original full-precision vertices. Both methods receive the same LOD0 body; no rest-pose model forward, LOD substitution or percentage tuning is used. This evaluates the upstream waist algorithm on our saved poses rather than its default generated elbow pose. Anatomical anterior-axis naming differs across documentation; the exact proper rotation `(x,-z,y)` is retained, and no front-facing anatomical equivalence is inferred from that naming.

## 4. Source measurement inventory

The numerical source endpoint is the **existing released-source engineering waist proxy**, where available. It depends on MHR-mapped source landmarks and our historical source selector. It is fixed for both competing measurements, but it is not independent superiority evidence. No MHR-selected plane was newly used to manufacture a reference. Other acquired source families lack an independently specified waist site in the admitted records and remain R4 for reference agreement. NHANES conditioning targets are excluded from validation. 3DPatBody is excluded under the revised request.

## 5. Cross-dataset selection

8 families were examined: DFAUST, FAUST, HBW, HIT, MPII, NHANES, NOMO, UCSC. There are 232 dataset-local participant identities and 852 saved body/pose observations. This is not a verified count of biologically independent donors across datasets. Inventory. MPII/UCSC CAESAR-derived donor overlap remains unresolved. D-FAUST contributes 60 observations from 10 people; it is never counted as 60 people. Static source families were capped at 20 identities using source-descriptor order statistics. The first available original FAUST observation per person was selected without method outcomes. Existing HIT historical neutral geometry is explicitly distinct from pinned T90.

## 6. Full NOMO analysis

All 150 linked NICP people are retained in both pathways. The source waist proxy is unavailable for one person, leaving 149 complete participants and 298 canonical branch comparisons (99.33% linked coverage). The 60 LBFGSB identities are a dependent supplementary representation cohort without an eligible historical released-source waist reference here. Canonical and saved fitted-pose results remain separate. Compact manuscript table; full NOMO summary; pathway and pose results. The primary linked-NICP canonical summary gives each complete person's two source pathways equal weight, then weights people equally. Missing one pathway prevents that person's inclusion in this linked summary.

End-to-end: 149 participant means (298 body pairs): P MAE 2.893, comparator MAE 3.543; P RMSE 3.912, comparator RMSE 4.792; mean advantage 0.649, median 0.145, percentile 95% CI [0.36489664711193354, 0.9227801581312939], all in engineering cm. This compares P raw perimeter against the official hull output and a raw source reference, so its functional mismatch is explicit.

The result is representation- and pose-dependent. CAESAR-NICP / canonical: A=0.032, 95% CI [-0.32333374203249315, 0.37813953491627916] (n=149). CAESAR-NICP / fitted: A=-1.532, 95% CI [-2.2664893059978795, -0.7985949418632999] (n=149). SMPL-NICP / canonical: A=1.266, 95% CI [0.8936306266613708, 1.6547102990654678] (n=149). SMPL-NICP / fitted: A=1.606, 95% CI [0.8706635060484367, 2.4050594536292653] (n=149). Therefore, the combined canonical advantage is not consistent independent replication across all pathways; the fitted CAESAR result is a clear contrary outcome.

## 7. Morphological challenge analysis

The frozen 48-person stress panel contains {'G4': 12, 'G2': 12, 'G3': 12, 'G1': 12}. Source geometry, within-family descriptors and pre-existing fallback flags were frozen before comparison outcomes. G1 uses typical within-family axial-envelope ranks; G4 enriches historical fallback and upper-envelope sensitivity. Independent anatomical torso/leg labels are unavailable: G2/G3 are explicitly labelled source axial-quantile surrogates, not confirmed short-/long-torso people. This limits the proposed anatomical stress hypothesis. Challenge results. Only 3/48 challenge people have an available source-proxy endpoint. G1/G3/G4 have one eligible NOMO person each; G2 has none. R4 families support method-difference descriptions, not a source-accuracy winner. These counts cannot establish a group-level morphological advantage; the G4 canonical NOMO illustration favours clad-body. Small subgroup counts and unavailable intervals remain visible.

## 8. Fallback analysis

Fallback and adaptive strata are retained separately. Fallback is neither automatically invalid nor anatomically certified. Fallback metrics; fallback-minus-adaptive contrast. A person may have different fallback states across reconstructions; the contrast resamples people jointly and recomputes both subgroup means. This is an observational subgroup association, not evidence that invoking fallback causes better accuracy.

## 9. Site-only comparison

Both planes are passed to the same indexed, torso-constrained extractor on the unchanged mesh. Raw and convex tape-envelope values remain distinct. Common raw perimeter: 149 participant means (298 body pairs): P MAE 2.893, comparator MAE 3.545; P RMSE 3.912, comparator RMSE 4.796; mean advantage 0.652, median 0.144, percentile 95% CI [0.3684894068354346, 0.925225231612537], all in engineering cm. Common tape-envelope: 149 participant means (298 body pairs): P MAE 2.923, comparator MAE 3.650; P RMSE 3.992, comparator RMSE 4.949; mean advantage 0.727, median 0.233, percentile 95% CI [0.44006699436295466, 1.0036785433063582], all in engineering cm. Each uses the corresponding same-functional source proxy where available. Ablations.

## 10. End-to-end comparison

The complete official B1 waist result remains separate from controlled extraction. P's original raw circumference is preserved with its original selector status and indexed audit residual. Any end-to-end difference can include site localisation, contour selection and raw-versus-hull functionals; it cannot be attributed entirely to plane location. The common-raw advantage 0.652 closely matches the end-to-end 0.649 under this estimand. B2 (63%), B3 (umbilicus), and B3_offset (umbilicus+0.005 m) are independently labelled sensitivities and are not tuned or attributed to clad-body.

Against the simple offset-only B3_offset baseline, P's paired advantage is -0.179 (95% CI [-0.37709408384028686, -0.0075870785841911014]); its MAE is 2.714 versus P 2.893. This contrary result provides no incremental support for the complete adaptive procedure over the simple offset on this reference; many cases tie because the fallback is identical. Against the independent 63% plane, A=0.164, CI [-0.09857289778737749, 0.44198469830030446], which includes zero. The result must not be generalized to every fixed-height percentage.

## 11. Source-reference error statistics

MAE, RMSE, signed bias, median and P95 absolute errors use the same complete pairs within each row. Paired advantage is `abs(B1-reference)-abs(P-reference)`. Error functionals are calculated per observation before participant averaging; median/P95 in linked summaries describe participant-mean absolute errors. Unavailable outcomes remain in denominators and missingness tables. Participant mean advantage is resampled with seed 18012601 and 2,000 bootstrap replicates. Complete statistics with metric intervals. Private paired records permit exact recomputation. `analysis-v2.json` corrects the linked coverage denominator to 150/300 and includes the explicit HIT historical-neutral descriptor analysis; initial `analysis.json` is preserved, and primary effect values, input references and cohort membership did not change.

## 12. Physical versus engineering evidence

## 15. Statistical uncertainty and cross-dataset synthesis

Intervals are descriptive percentile 95% participant-bootstrap intervals, without multiple-testing adjustment. NOMO pathways and D-FAUST observations are dependent. No pooled cross-dataset accuracy MAE is justified because the other families lack a common qualified reference. Subject-weighted and equally dataset-weighted **method differences** are saved in `analysis-v2.json`, with the interpretation separated from accuracy. Source morphology associations are descriptive; association table.

## 16. Scientific interpretation

Under the frozen linked-NICP canonical end-to-end estimand, P has a point estimate of **greater agreement with the named dependent source proxy**. The interval is above zero and supports greater agreement with this dependent source proxy. The exact effect and uncertainty above govern the claim. Site-only results and contrary cases determine whether that finding survives common functionals. This experiment does not establish a universal fixed-height failure mechanism, verified anatomical waist placement or physiological validity.

## 19. Limitations

Mapped umbilicus and atlas points are not palpable rib/iliac landmarks. Reference construction shares our source-selector correspondence. Source physical scale and tailor-site protocols remain unresolved. Original and canonical poses differ; LBFGSB also retains the previously documented expression confound. Mesh extent is not anatomical stature. Topology affects vertex-quantile descriptors. G2/G3 anatomical targets are unqualified. Cross-resource donor independence is unknown. Small enriched subgroups do not establish population-wide effects. No independent expert ratings or body-composition accuracy references were supplied. Saved inputs, historical negative results and unqualified cases remain preserved.
