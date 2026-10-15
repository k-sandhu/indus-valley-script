# Original analysis code (frozen)

This directory holds the analysis scripts of the first investigation and, in `six_hour/`, the code of the six-hour continuation recorded in [experiments/2026-10-02-six-hour/](../experiments/2026-10-02-six-hour/). Its files were last changed on 2 October 2026. Recorded hashes, papers and registry entries refer to them, so they stay unmodified. Several entry points write to default output directories and can overwrite frozen results: read [REPRODUCING.md](../REPRODUCING.md) and give a fresh output location before rerunning one.

New reusable code goes in [bench/](../bench/) for shared evaluation or [tools/](../tools/) for repository operation. New outputs go in a new dated package, `experiments/YYYY-MM-DD-short-slug/`.
