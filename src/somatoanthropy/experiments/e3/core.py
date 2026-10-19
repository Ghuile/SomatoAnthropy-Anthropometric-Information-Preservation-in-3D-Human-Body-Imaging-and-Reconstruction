"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from collections import Counter

import numpy as np

VERSION = "E3-SAVED-FIT-v1"
PROTOCOL = "E3-DFAUST-ATLAS-INDEXED-v1"
SITES = ("height", "waist", "abdomen", "hip", "chest", "neck")
SEED = 4182026


def validate_panel(rows):
    counts = Counter((r["subject_uid"] for r in rows))
    if len(rows) != 60 or len(counts) != 10 or set(counts.values()) != {6}:
        raise ValueError("TEN_SUBJECTS_SIX_OBSERVATIONS_REQUIRED")
    for key in ("observation_uid", "fit_uid", "body_uid", "selection_id"):
        if len({r[key] for r in rows}) != 60:
            raise ValueError("DUPLICATE_PANEL_LINK:" + key)
    if any((type(r["frame"]) is not int or r["frame"] < 0 for r in rows)):
        raise ValueError("ZERO_BASED_FRAME_INDEX_REQUIRED")


def dispersion(values):
    x = np.asarray(values, float)
    if not np.isfinite(x).all():
        raise ValueError("FINITE_DISPERSION_VALUES_REQUIRED")
    d = dict(
        n=len(x), median=None, sd=None, range=None, mad=None, pairwise_median=None, cv_percent=None
    )
    if len(x):
        d.update(median=float(np.median(x)), mad=float(np.median(np.abs(x - np.median(x)))))
    if len(x) > 1:
        pairs = np.abs(x[:, None] - x)[np.triu_indices(len(x), 1)]
        d.update(
            sd=float(x.std(ddof=1)),
            range=float(np.ptp(x)),
            pairwise_median=float(np.median(pairs)),
            cv_percent=float(x.std(ddof=1) / x.mean() * 100) if (x > 0).all() else None,
        )
    return d


def indexed_difference(a, b):
    a, b = (np.asarray(a, float), np.asarray(b, float))
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 3 or (not len(a)):
        raise ValueError("MATCHED_INDEXED_VERTICES_REQUIRED")
    delta = np.linalg.norm(a - b, axis=1) * 100
    if not np.isfinite(delta).all():
        raise ValueError("FINITE_GEOMETRY_REQUIRED")
    return dict(
        rms_cm=float(np.sqrt(np.mean(delta**2))),
        median_cm=float(np.median(delta)),
        p95_cm=float(np.quantile(delta, 0.95)),
    )


def local_plane(point, normal, root):
    p, n, r = map(lambda x: np.asarray(x, float), (point, normal, root))
    if any((x.shape != (3,) or not np.isfinite(x).all() for x in (p, n, r))):
        raise ValueError("FINITE_PLANE_FRAME_REQUIRED")
    if np.linalg.norm(n) == 0:
        raise ValueError("NONZERO_NORMAL_REQUIRED")
    return (p - r, n / np.linalg.norm(n))


def reference_site(rows):
    """Selection label only; the F01 evaluation is excluded from this ablation."""
    return min(rows, key=lambda r: r["selection_id"])


def angular_distance(a, b):
    """Shortest periodic difference of a named scalar revolute control (radians)."""
    return float(abs(np.arctan2(np.sin(a - b), np.cos(a - b))))


def cluster_association(groups, *, seed=SEED, replicates=2000):
    """Within-subject centred Pearson descriptor; resample whole subjects.

    Each cluster retains all eligible observations. No independent-row p-value.
    Constant clusters remain in coverage; unidentifiable draws are counted.
    """
    contributions, n = ([], 0)
    for _, x, y in groups:
        x, y = (np.asarray(x, float), np.asarray(y, float))
        if x.shape != y.shape or not np.isfinite([x, y]).all():
            raise ValueError("FINITE_PAIRED_ASSOCIATION_REQUIRED")
        if len(x) < 2:
            continue
        n += len(x)
        x, y = (x - x.mean(), y - y.mean())
        contributions.append([x @ x, y @ y, x @ y])
    a = np.asarray(contributions).reshape(-1, 3)

    def ratio(s):
        den = np.sqrt(s[..., 0] * s[..., 1])
        return np.divide(s[..., 2], den, out=np.full_like(den, np.nan), where=den > 1e-20)

    value = ratio(a.sum(0))
    ci, valid = (None, 0)
    if len(a) >= 2:
        rng = np.random.default_rng(seed)
        sums = a[rng.integers(0, len(a), (replicates, len(a)))].sum(1)
        draws = ratio(sums)
        valid = int(np.isfinite(draws).sum())
        if valid:
            ci = np.quantile(draws[np.isfinite(draws)], [0.025, 0.975]).tolist()
    return dict(
        subjects=len(a),
        observations=n,
        within_subject_r=float(value) if np.isfinite(value) else None,
        cluster_ci95=ci,
        identified_bootstrap_draws=valid,
        replicates=replicates,
        seed=seed,
        association_method="within-subject centred Pearson; whole-participant percentile bootstrap",
    )
