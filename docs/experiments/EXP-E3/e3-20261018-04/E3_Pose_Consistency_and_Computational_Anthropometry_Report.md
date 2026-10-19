# E3 — Pose Consistency and Computational Anthropometry

Participant-free abridged register report, released 19 October 2026. Scientific method and aggregate-result excerpts retain the original wording and historical interpretation. Private execution records, participant/case material, image galleries and internal publication planning are omitted. This is not the original byte stream. See the register for both SHA-256 values and the aggregate manifest for machine-readable results.

## Objective and hypotheses

We investigate independent identity recovery, common-articulation surface consistency, digital anthropometric repeatability and site stability as distinct phenomena. H3.1 asks whether canonical measurements are similar; H3.2 concerns original pose; H3.3 recovered identity variation; H3.4 measurement-site sensitivity; H3.5 regional sensitivity; H3.6 fitting residuals. No numerical equivalence margin is imposed. The within-person median is a repeatability reference, never physical truth. This is cross-pose repeated-observation analysis, not continuous motion tracking.

## E0, E2, E4 and independent E2-1

## Population, source sequences and geometry inventory

Ten dataset-local subject identifiers each link six observations to six distinct parameter/fit/body states. There are 60 distinct native parameter hashes. Ten previously fitted observations were reused and fifty fits were executed by the historical study; E3 creates no fits. The source subject/sequence/zero-based-frame mapping is checked with the existing identity namespace. All 60 canonical LOD0 meshes, original-pose LOD1 meshes, native controls and both raw source HDF5 containers are present and hash-pinned. Exact paths, source frame digests, source container hashes, transforms and fit configurations remain in the private panel. E3-T1 provides the sanitized inventory. No identity catalogue or new split was created.

The six observations are drawn from different sequences and are not treated as consecutive time points. Canonical bodies have 73,639 vertices and 147,274 identical ordered faces. Original-pose fits have 18,439 vertices: their LOD1 topology is never compared directly by index with LOD0. Actual design figure shows real saved source views and canonical bodies. Source thumbnails retain historical per-frame cameras; canonical galleries use identical metric cameras.

## Source registration, units and original fitting fidelity

## Native identity, morphology and canonical transfer verification

Every source state is finite float32 with shapes 1×45 identity, 1×204 model and 1×72 expression, and matches the fitted generation input exactly. Canonical controls 0–129 match the pinned T90 articulation exactly. Each observation's identity, expression and morphology controls 130–203 are preserved, without replacement by a participant mean/shared identity. Generation artifacts bind the original parameter SHA-256; historical independent LOD0 replay process IDs differ from generation IDs and replay residuals are zero. E3 verifies saved evidence and exact controls; it does not claim a fresh native forward. Original correctives are enabled. Shape-driven knee rotation is preserved.

FIT07 actually optimized morphology controls; NOMO restrictions cannot be assumed to apply. Median participant pairwise morphology norm is **1.119 coefficient units**. Facial expressions are zero by the original fitting policy, so zero expression dispersion is constrained behavior, not unconstrained recovery success. E3-T6 and `coefficient-dispersion.csv` preserve the actual parameter groups.

## Canonical geometry repeatability

The primary estimator takes the median of 15 pairwise indexed RMS distances within each person and then the cohort median. In the saved floor frame it is **2.031 engineering cm**, 95% participant-bootstrap interval [1.6813081046139722, 2.2345845435921285]. After subtracting each body's arithmetic vertex centroid, it is **1.498 cm**, interval [1.295130898813281, 1.8084655791964515]. No rotation, uniform scaling or non-uniform rescaling is applied. Centroid removal is a transparent vertex-density-dependent translation diagnostic, not an anatomical alignment.

Translation-normalised torso and pelvis medians are **0.829** and **1.147 cm**. E3-T2 includes all regions; `geometry-pairs.csv` retains pairwise RMS, median and P95 indexed displacement for both frames. Height, width, depth, floor shifts and native skeletal segment lengths are separate descriptors. Official skin-weight masks define engineering regions. The spine0/1 abdomen proxy is not anatomically validated. The within-person mean mesh is a dispersion reference, not independent truth. Gallery selects the lower-median rank 5/10 and largest rank 10/10 by centered RMS, using identical cameras. Regional figure displays actual vertex dispersion.

## Historical anthropometric baseline

## Common-method anthropometric repeatability

Frozen protocol `E3-DFAUST-ATLAS-INDEXED-v1` independently remeasures the saved LOD0 meshes. Waist is the midpoint of atlas lower-thorax/upper-pelvis surface candidates, with the spine-based normal; it is not a certified rib/iliac midpoint. Abdomen is the mapped umbilicus section, chest the mean anterior atlas feature level, hip posterior A in the existing gluteal search slab, and neck the existing shoulder-free profile minimum. Height is max(Y)−min(Y), not stature. No NOMO NICP source adapter is applied. All six common sites yield 60/60 valid geometric values; anatomically qualified measurements remain zero. Raw surface perimeter and convex outside-tape perimeter remain separate. The following table uses raw contours consistently for circumferences; units are engineering cm.

| Site | Valid | Median within SD | Median range | Median pairwise absolute difference | Range 95% cluster CI |
|---|---:|---:|---:|---:|---|
| height | 60/60 | 0.814 | 2.164 | 0.896 | [1.572390079498291, 2.394803464412689] |
| waist | 60/60 | 1.027 | 2.973 | 0.943 | [1.6174889652806996, 4.914634520040963] |
| abdomen | 60/60 | 1.155 | 3.094 | 1.035 | [2.1582008432682187, 4.95799725139269] |
| hip | 60/60 | 1.048 | 2.708 | 0.991 | [2.206228477624279, 4.59231785065279] |
| chest | 60/60 | 1.993 | 5.231 | 2.185 | [3.972520684000898, 6.459382931017856] |
| neck | 60/60 | 0.493 | 1.212 | 0.496 | [0.7898997272367012, 1.9899561118355962] |

E3-T3 and `participant-repeatability.csv` retain participant SD, range, median, MAD, pairwise absolute differences, valid n and relative CV, as well as complete-six versus available-case cohort summaries. Mean/SD and quantiles of participant statistics supplement medians. Repeatability figure uses points rather than temporal trajectories. Better coverage under a different engineering definition does not establish better anatomy.

## Measurement-site, fallback and contour stability

Planes are expressed relative to each body's own canonical root; normals are normalized and retained. A global floor-height difference is not an anatomical site difference. E3-T4 and `measurement-planes.csv` retain root-local positions, plane ranges/orientations, branches, selected landmarks and fallback frequency. Historical trunk planes are horizontal; atlas waist/neck can be oblique. Anatomical waist/rib/iliac landmark correspondence remains unavailable.

Fixed-site sensitivity chooses F01 lexicographically without looking at outcomes, transfers its common plane minus root to the other five bodies without rescaling, and excludes F01 from evaluation. This is a geometric diagnostic, not trustworthy anatomical correspondence. The common-site comparator uses exactly those same five observations:

| site | common_observations | fixed_observations | common_median_five_range_cm | fixed_median_five_range_cm |
| --- | --- | --- | --- | --- |
| waist | 50 | 50 | 2.4156 | 2.275 |
| abdomen | 50 | 50 | 3.0935 | 1.8406 |
| hip | 50 | 50 | 2.5491 | 2.2477 |
| chest | 50 | 50 | 4.8445 | 5.4497 |
| neck | 50 | 50 | 0.99429 | 1.6945 |

These are descriptive cohort medians, not fractions of variance caused by site movement. A fixed plane can increase variability or leave the plausible site. No improvement is guaranteed by construction, and no certified anatomical Method C is claimed. The original 60 observations remain the primary panel.

## Original pose, fitting quality and associations

Saved hash-bound source checks provide geometric knee/elbow flexion, arm elevation, trunk tilt and hip/shoulder twist proxies. These are measured source descriptors, not filename inferences. Native knee/elbow descriptors use shortest periodic differences of named scalar controls from T90. They are not arbitrary sums of Euler angles or full SO(3) joint distances. Full joint geodesics would require additional qualified joint transforms and are not invented. Contact/overlap screens do not measure penetration depth or verified physical self-contact.

Outcome is absolute measurement deviation from that participant's site/method median. Both variables are centered within participant; 2,000 whole-participant bootstrap draws retain each cluster. No independent-row p-value treats 60 observations as 60 people. The estimator weights clusters by their within-cluster sums of squares; this dependence is explicit, and it is descriptive rather than causal.

| Site | Predictor | Within-subject r | 95% cluster CI | Subjects / observations |
|---|---|---:|---|---|
| waist | source_knee_max_degrees | 0.103 | [-0.19241356741797266, 0.4359577149145213] | 10 / 60 |
| waist | fit_rms_cm | 0.123 | [-0.2767287394688677, 0.4444410436864855] | 10 / 60 |
| waist | identity_deviation_norm | 0.327 | [0.018731026295810124, 0.665716534841139] | 10 / 60 |
| waist | plane_deviation_cm | 0.133 | [-0.11274226213540797, 0.3572906764709759] | 10 / 60 |
| hip | source_knee_max_degrees | 0.040 | [-0.15404922403768054, 0.2679944495018105] | 10 / 60 |
| hip | fit_rms_cm | 0.284 | [-0.1004458743170421, 0.5613163634845364] | 10 / 60 |
| hip | identity_deviation_norm | 0.202 | [0.0186443612074955, 0.5731502397523537] | 10 / 60 |
| hip | plane_deviation_cm | 0.471 | [-0.16679831850250715, 0.6992394961458952] | 10 / 60 |
| chest | source_knee_max_degrees | -0.058 | [-0.34779552489921545, 0.29712008951059815] | 10 / 60 |
| chest | fit_rms_cm | -0.076 | [-0.3491750865437133, 0.2159410918978748] | 10 / 60 |
| chest | identity_deviation_norm | 0.375 | [0.01852358772300691, 0.6416672337285461] | 10 / 60 |
| chest | plane_deviation_cm | 0.006 | [-0.2848183219730108, 0.2908697563215844] | 10 / 60 |

## Recovered identity variation

Median participant pairwise identity norm is **6.538 coefficient units**, 95% cluster interval [5.289825071566548, 7.386950154592512]. Within-person RMS about subject means is **4.431**, versus **9.018** RMS dispersion of subject means about the cohort mean. These different finite-sample averages are descriptive dispersions, not biological identity distances or formal variance components. Rig morphology is independently recovered and varies; expression is constrained at zero. Per-control variation, native model-joint segment lengths and identity figure support the diagnosis.

The following explicitly outcome-selected examples compare empirical upper/lower quartiles of coefficient distance over 150 within-person pairs. They illustrate sensitivity, not an acceptance threshold or independent confirmation:

Different coefficient states can thus share a circumference, and smaller coefficient differences can coexist with larger circumference differences. No averaged identity or fixed-identity forward was used. Attribution to individual identity/rig controls requires a separate controlled experiment.

## Baselines, ablations, statistics and missingness

The participant is the independent sampling unit. Sample SD uses n−1; n<2 gives unavailable dispersion. Every participant supplies one statistic per cohort estimand. Seed 4182026, deterministic per-estimand seed derivation and 2,000 participant draws are recorded. Intervals are unadjusted exploratory percentile intervals conditional on a selected convenience panel. Only ten clusters make uncertainty unstable. A complex mixed model, ICC and equivalence test are not forced onto this design. Descriptive within/between identity dispersions do not replace an identifiable anthropometric variance-component model.

E3-T8 records selected denominators, missing/invalid values, ambiguity, absent methods and intentional F01 exclusions. Missing source containers, fitted/canonical geometry and parameter states: zero. Qualified independent landmarks and physical ground-truth anthropometry are unavailable for every participant. Inter-sequence velocities, acquisition times, full joint geodesics and physical contact severity remain unknown. No circumference was imputed and no difficult frame was replaced.

## Threats to validity and scientific interpretation

Registration uncertainty, actual pose-dependent deformation, articulation/optimization errors and independently recovered morphology are confounded. Canonicalization changes articulation and correctives but preserves recovered shape. There is no isolated experimental manipulation of source pose, certified neutral body or validated physical scale. Official native regions and atlas attachments are engineering proxies, not independent anatomy. Closed topology, contact screens and closed contours do not qualify closed-volume geometry or anatomical correctness. Global residuals do not establish regional fidelity. Selected repeated poses do not create new independent subjects. Source HDF5 bytes are independently SHA-256 checked, but raw frame extraction was not rerun in the Windows analysis runtime; source-frame digests and geometric pose proxies are linked through saved source checks. There is no physiology/body-fat model or claim.

For SomatoAnthro, E3 supplies a participant-clustered baseline distinguishing independent native recovery, canonical geometry, engineering circumference repeatability and site stability. It supports a careful computational-metrology contribution, not population-level pose invariance, clinical anthropometry or physiological accuracy. Negative/inconclusive findings are retained.
