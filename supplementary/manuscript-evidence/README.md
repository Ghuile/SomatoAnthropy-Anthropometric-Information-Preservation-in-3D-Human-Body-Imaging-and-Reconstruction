# SomatoAnthropy supplementary manuscript evidence

These files accompany the Sensors manuscript *SomatoAnthropy: Anthropometric Information Preservation in 3D Human-Body Imaging and Reconstruction*. They are also distributed as **Supplementary Data S1**. They make the source-package evidence cited in the manuscript available directly to readers.

- evidence/: seventeen participant-free files with fixed T90 articulation coordinates, native control mappings and authored zero-width bounds, saved development/rank summaries, canonical P-side fallback contrasts, aggregate articulation diagnostics, extent-agreement arithmetic and template provenance.
- figures/waist/: saved Figure 3 rendering source, GLB-reading helper, stored generated-surface contours/profiles and figure provenance. These illustrations are outside the evaluation cohorts.
- FILE_MANIFEST.json: file sizes and SHA-256 hashes. No fitting, bootstrap or scientific estimation is required to inspect these files.

## Claim-to-file guide

| Manuscript claim or specification | File |
| --- | --- |
| Exact T90 transfer and native control permissions, Supplement S1 | evidence/t90_reference_130.csv, evidence/t90_reference_130.json, evidence/t90_reference_sparse16.csv, evidence/native_control_bounds.csv, evidence/native_control_sparse_mappings.csv, evidence/native_controls_9_and_zero_domains.json, evidence/specification_manifest.json |
| Four-person saved development comparisons and rank coefficients, Supplement S1/S9 | evidence/development_*.csv, evidence/development_and_rank_manifest.json, evidence/height_rank_correlations.csv |
| Non-fallback waist contrasts and exact denominators, main 4.5/Supplement S2 | evidence/waist_fallback_strata.json |
| Hip/spine/knee aggregate associations, main 4.2/Supplement S8 | evidence/articulation_associations.json |
| Lin concordance and descriptive Bland-Altman limits, main 4.1/Supplement S10 | evidence/extent_agreement.json |
| Figure 3 saved rendering inputs/source | figures/waist/render_waist_figure.py, figures/waist/mesh_io.py, figures/waist/waist_illustration_data.json, figures/waist/waist_figure_provenance.json |
| Figure S1 saved template provenance | evidence/template_control_provenance.json |

The saved Figure 3 renderer requires Python, NumPy, Pillow and the original Windows Arial fonts. It does not fit or remeasure a body. Its two required GLBs are already in the public Hugging Face companion, under meshes/synthetic_demo_001.glb and meshes/synthetic_demo_002.glb. Preserve their hashes listed in the stored illustration inputs. From an arbitrary staging root, place those meshes at publication/somatoanthropy-huggingface-companion/meshes/, then call:

    python <path-to-this-directory>/figures/waist/render_waist_figure.py --repo <staging-root>

The original rendering source is preserved apart from line-ending normalisation in the GitHub copies; each distribution retains a manifest matching its actual file bytes. No mesh or conditioning record is added here. No new render or model execution was performed for this release.

The original unredacted report hashes differ from the public abridged copies. docs/evidence_versions.json at the repository root maps original_sha256 to each public sha256; original report hashes remain historical provenance pins. These exports do not make restricted participant analyses or their bootstrap inputs available.

Project-owned rendering code is covered by the repository MIT licence; project-owned documentation and aggregate evidence by CC BY 4.0. Native MHR model metadata and referenced model assets retain the upstream MHR Apache-2.0 terms and notices; this release grants no rights to third-party participant datasets. Dependent source proxies are not anatomical truth. No participant ledgers, source conditioning values, fitted parameter archives or model binaries are included.
