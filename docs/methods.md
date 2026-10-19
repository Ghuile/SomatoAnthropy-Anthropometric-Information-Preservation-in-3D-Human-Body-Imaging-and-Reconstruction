# Methods represented by the release

## Populations and dependency

The primary NOMO cohort has 150 people, two source pathways and four fitted/
canonical observations per person. Source-reference analyses use 149 complete
people (596 four-state or 298 canonical observations); common raw-contour
comparisons can use 148. The historical 60-person LBFGSB cohort overlaps NOMO.
E2-1 evaluates 12 people after four development people; E2-2 evaluates another
12 with the same four development people. D-FAUST has ten people with six
independently fitted observations each, from 54 sequences. The 150 within-person
pairs are dependent observations, not 150 independent people.

## Native reconstruction and the control intervention

The official MHR revision is `4998cec385b1aaa07abdefba71bfba2f83c7db32`.
Native controls are 45 identity, 204 rig/model and 72 expression parameters.
`reconstruction.py` loads the upstream model with pose correctives and checks
control names and LOD topology. Code/asset SHA-256 pins are in
`configs/model_hashes.json`; assets are obtained separately.

`geometry/mpii_mhr_fit01/fit.py` retains the original staged native optimiser:
area-sampled bidirectional cloud nearest-neighbour residuals, pseudo-Huber loss,
identity/pose priors, parameter bounds and resource/time limits. This fitting
objective is distinct from the triangle-distance evaluation below. Its resource
check requires Linux `/proc/meminfo`. It is an inspectable callable, not a batch
launcher for every dataset. Each historical family's saved initial state,
transforms and qualification records remain required.

`experiments/e2_1/optimizer.py` implements the matched 100-step B/C continuation
from the same saved state, 8,192 fixed samples, reset Adam moments, identical
objective and the lowest regularised pre-step objective. Nine permitted rig
indices are 139, 140, 141, 142, 143, 146, 149, 150 and 153. They act through local
rest-joint transforms rather than global uniform scaling. Their names, bounds,
groups, learning rates, priors, stages and seeds are frozen in
`configs/control_release.json`. E2-2 `policies`, `starting_controls` and
`fit_config` preserve the G1–G4 and prior comparisons. A is the historical fit,
B locks the nine controls, C releases them and D uses the quarter rig prior
(the code policy is R025). Development and held-out populations remain distinct.

`geometry/anthropometry/t90_remeasurement.py` transfers only rig entries 0:130
from the pinned T90 reference, retaining identity, morphology 130:204 and
expression. Native forward regeneration produces geometry; no mesh warp is
substituted. Historical HIT uses its saved neutral state. The historical NOMO
LBFGSB cohort has a documented expression-state exception; the release does not
rewrite its saved outputs to pretend it used the later protocol.

## Surface geometry and digital measurements

E1 uses 4,096 area-weighted samples in each direction and sample-to-opposite-
triangle distances for mean, RMS and P95. Saved transforms are applied without
post-hoc registration. The exact distance implementation is in
`geometry/mpii_mhr_fit01/metrics.py`; evaluation wrappers are in E1 and E2-1.
Regional definitions use the available frozen masks. E3/E4 indexed comparisons
require compatible topology. Centroid alignment is a translation-only diagnostic.
Lengths are engineering units whose physical interpretation depends on the
source family's calibration. Mesh vertical extent is not measured stature.

E2 `proxy_sites`, the indexed section engine, mapped anchors and NOMO metrology
retain raw contour and convex outside-tape functionals separately. Historical
waist, mapped umbilical abdomen, hip and atlas-midpoint proxies are distinct
measurement definitions. Invalid geometry, site ambiguity and unavailable
anatomical qualification remain explicit.

The frozen adaptive P selector and its state-dependent above-abdomen fallback
are retained; fallback does not silently become anatomical validity. WAIST's
`one` function combines these definitions with the official clad-body revision
`a2140a74555a6382e1712ec1a5d8dc939b59e655`. B1 is its 61%-height convex-hull waist;
B2 is a separate 63% comparator. B3_offset is the simple umbilical-plane offset
baseline. The offset baseline's favourable result and adverse UCSC finding are
retained; P is not universally superior.

## Repeated observations

`repeated.geometry_summary` computes 15 indexed comparisons per person, then a
person-level median and a cohort median with the original bootstrap.
`measurement_records` retains the original E3 computational loop for common,
historical and fixed-plane measurements. Its file reader and cache have been
replaced by explicit inputs. Fixed planes come from lexicographic F01, translated
through the root without scaling. F01 is excluded from fixed-plane evaluation.
`measurement_summary` preserves historical eligibility, matched held-out common
sites, at-least-two/complete-six subsets, sample SD and range before participant
bootstrap. The fixed-plane experiment tests engineering sensitivity, not proved
anatomical correspondence.

## Equation response and inference

E5/S1/S2 use `q(H,W) = -20 H/W`, with positive H and W in the same unit. Its zero
is arbitrary. Responses are equation percentage-point changes, not absolute
body-fat estimates. No missing age or sex is assigned.

E5 uses actual reconstructed height. S1 additionally controls source height or
reconstructed height and preserves the ordered height–waist compensation. S2 H1
uses reconstructed height, H2 each pathway's source height, and H3_strict the
qualified original SMPL-source anchor, not a substituted two-source median.
Relaxed H3 tolerances are separate sensitivity policies. Strict eligibility is
103 people; compatibility does not certify physical stature or anatomical pose.
The source-waist reference is MHR-mapped and dependent, not independent truth.

Original paired participant bootstrap seeds/draws are retained in each experiment
module. E4 retains its specified 98.75% family intervals; most other displays use
95%. E5 and S1 have different bootstrap settings and therefore different saved
intervals for the same actual-height mean; neither interval replaces the other.
Advantage signs follow their named contrast. S2 Pareto membership is descriptive
and conditional on objectives, eligibility and reference construction. The
149-person and strict 103-person frontiers must not be merged.
