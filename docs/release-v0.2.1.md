# Corrected software and data release v0.2.1

The v0.2.0 downloadable ZIP contains exactly the 257 tracked files at commit
`5c1553ba02de1ba511c5d2165c3918b09c7b7b9b`. Its SHA-256 is
`e91a3883359b43795f9ea351878d89c106d24c23ed23ed9e4c795bc81708a77e`.
The tag was subsequently observed at `c0cd2154d5761999774a4c7fa797545fc261937c`.
Thus the tag and attached ZIP identify different snapshots. The archive and tag
are retained without further retargeting; v0.2.0 is superseded by v0.2.1.
The machine-readable comparison is in `v0.2.0-provenance-audit.json`.

The corrected software starts from green commit
`4118cb42594c7c76de67f59d1881385c740b9065`, then updates release metadata and
the companion package builder. The new tag is created only after the exact
release commit passes both Python CI jobs. Its software ZIP is generated with
`git archive` from that commit, and every archived file is compared with the
tagged tree. The published release receipt records the full software commit,
CI run, source archive and SHA-256.

The matching Hugging Face package is additive, under `releases/v0.2.1/`.
It contains the 47 canonical aggregate tables, six CSV exports, existing approved
illustrations, the 23 approved supplementary manuscript-evidence files, licence
notices, invented examples and provenance. `SOURCE.json` pins the exact software
commit and source manifest hash; `MANIFEST.sha256` covers the package bytes.
The full dataset commit and data tag `v0.2.1` are recorded in the external
release receipt after upload. This avoids circular self-references between the
software commit, its generated package and the subsequent dataset commit.

No participant records, private ledgers, source conditioning values, meshes,
model binaries or private correspondence are added. The supplementary rendering
scripts and saved generated-surface profiles retain their documented limitations;
the two illustration meshes remain separate existing assets. Scientific results
and manuscript sources are unchanged by this release preparation.

Project-owned code is MIT; project-owned documentation and aggregates are
CC BY 4.0. Upstream MHR and other notices retain their scope. Zenodo archival
remains deferred and no registered DOI is asserted.
