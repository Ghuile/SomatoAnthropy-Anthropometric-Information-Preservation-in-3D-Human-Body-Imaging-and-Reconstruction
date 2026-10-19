# Attribution, licences and figure rights

Project-owned code, documentation and aggregate material are licensed under
CC BY 4.0. The lead author confirmed LSBU approval on 19 October 2026. See LICENSE
and NOTICE. External dependencies and source datasets retain their own terms.

| Dependency | Pinned revision / terms |
|---|---|
| [Meta MHR](https://github.com/facebookresearch/MHR) | `4998cec385b1aaa07abdefba71bfba2f83c7db32`; upstream Apache-2.0 code notice retained in `third_party/MHR-code-Apache-2.0.txt`; the inspected asset notice is separately retained in `MHR-assets-Apache-2.0.txt`. No upstream code tree or model binaries are redistributed. |
| [clad-body](https://github.com/datar-psa/clad-body) | `a2140a74555a6382e1712ec1a5d8dc939b59e655`; Apache-2.0 notice retained in `third_party/clad-body-Apache-2.0.txt`. Installed externally; exact inspected Python-file hashes are in configs. |
| NumPy, SciPy, trimesh, PyYAML, matplotlib, pytest, Ruff, PyTorch, h5py | Installed packages retain their upstream distribution notices. Exact relevant versions and the native-runtime distinction are documented in environment/. |

Dataset providers and source-model licences impose additional conditions; see
[datasets](datasets.md). MHR's software/model notices do not grant rights over
NOMO participants or source-derived images.

NOMO v3's [release record](https://zenodo.org/records/5172126) has a discrepancy
between the reported CC BY metadata and description restrictions on modification
and redistribution. No dataset redistribution or source-derived body-image
permission is inferred from it. Neither the original Figure 2(a) body renderings
nor Figure 2(b) residual maps is included or described as publication-cleared.

The released Figure 2 is a schematic and aggregate chart, consistent with the
current manuscript replacement. All six released illustrations are generated
from geometric-independent diagrams or cohort aggregates; none contains a
participant mesh, body rendering, residual-map panel or photograph. The separate
template mechanism illustration uses only the native zero-identity MHR template,
with the asset notice retained. Private correspondence and permission records
are excluded. GitHub visibility is controlled separately from the Zenodo archive.


The 0.2.0 [audit update](audit-update.md) supersedes prior unresolved project-licence and Figure 2 statements: project-owned release material is CC BY 4.0 with LSBU approval reported by the lead author. Current manuscript Figure 2 has no participant imagery. Dataset restrictions and excluded historical imagery remain unchanged.
