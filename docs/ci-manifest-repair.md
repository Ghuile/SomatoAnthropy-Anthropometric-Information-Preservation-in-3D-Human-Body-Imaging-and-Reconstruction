# Manuscript evidence upload: CI repair

Commit `05f8e8fac023daa4a3fc8b8c55ac06e09c8e7859` added supplementary manuscript
evidence without updating the root content manifest. Both Python CI jobs stopped
earlier at 54 lint errors in its two figure scripts, so the history audit never ran.

The repair formats those scripts, replaces two assigned lambdas with equivalent
local functions, refreshes their supplementary checksums and includes the complete
tracked tree in the current root manifest. Scientific inputs and calculations are
unchanged. No render, fit or measurement is required for this maintenance change.

The original commit remains intact. Its exact complete tree (excluding its own
root manifest) is pinned in
`docs/historical-manifests/05f8e8fac023daa4a3fc8b8c55ac06e09c8e7859.sha256`.
The history verifier uses that receipt only for that exact commit, checking every
path and blob checksum and applying the same content scan. Other revisions must
still match their original manifests. This records the original omission without
silently accepting missing entries or rewriting the release tag.

The supplementary renderer remains an optional Windows/Pillow workflow requiring
the separately hosted generated illustration meshes. CI checks its syntax and
style; it does not claim to reproduce that optional illustration.
