"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from somatoanthropy.experiments.e4.core import bootstrap, describe


def summary_stats(values, seed):
    if not values:
        return dict(
            subjects=0, median=None, median_ci95=None, mean=None, sd=None, q05=None, q95=None
        )
    d = describe(values)
    b = bootstrap(values, seed=seed, replicates=2000)
    return dict(
        subjects=len(values),
        median=d["median"],
        median_ci95=b["median_ci95"],
        mean=d["mean"],
        sd=d["sd"],
        q05=d["q05"],
        q95=d["q95"],
    )
