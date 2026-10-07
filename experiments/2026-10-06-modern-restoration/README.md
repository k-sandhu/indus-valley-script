# Modern restoration benchmark comparison

Status: Exploratory. Completed 7 October 2026 from a protocol written on 6 October before fitting.

Modified Kneser–Ney restores 39.7178% of 8,009 known slots with 4.581891 bucket bits, compared with 34.5861% / 5.119435 bits for first order and 37.2706% / 5.247171 bits for second order. The highest primary top-one is 41.1662% (`ensemble/extra1/loss`); the lowest native loss is 4.347675 bits (`ensemble/extra1/loss`). [Results and paired intervals](aggregate-results.json), `models`; [report](REPORT.md).

All saved masks, targets, artifacts, groups and folds match. Extra text adds 501–506 distinct strings and 1,419–1,427 tokens per fold after complete transitive exclusion. The wider export also links 144–159 existing benchmark training strings per fold to test strings; the original matched folds remain fixed. [Benchmark audit](benchmark-audit.json), [extra graph audit](extra-graph-audit.json).

The completed stages cover orders 2–5, two GRU configurations, two transformer configurations, three neural seeds, joint metadata conditioning, both text regimes, log-probability ensembles, secondary accuracy selection and 25/50/75/100% learning curves. [Curve results](learning-curves.json), [accuracy figure](figures/learning-curves.svg), [training diagnostics](training-diagnostics.json), [internal verification](verification.json). [Frozen carry-forward recipe](frozen-model/manifest.json), selected using inner outcomes, retains local counts/weights for a future fresh population. Its [refined loader checks](frozen-inference-v2-verification.json) verify fixed-batch hidden replacement; the [dated amendment](VERIFICATION-AMENDMENT-2026-10-07.md) records the first mixed-batch comparison.

## Reproduce from the repository root

The original normalized corpora and saved query audits must be present locally. Model fitting used Python 3.13.5, NumPy 2.5.3 and CUDA PyTorch 2.14.1+cu126 in the provided RTX 4070 environment. Plotting dependencies were added to the same environment. Pypdf from the system Python is needed only to repeat literature extraction. [Fitting environment](environment.json).

```powershell
$modernPython = 'C:/Users/sandh/.venvs/indus-ml/Scripts/python.exe'
& $modernPython -B experiments/2026-10-06-modern-restoration/run_all.py --run reviewer-2026-10-07
```

Choose a new run label. Fits can resume completed stage records; completed aggregate endpoints refuse replacement. `run_all.py` repeats all fitting, selection, curves, summaries and mathematical checks. It preserves the existing carry-forward model unless explicitly invoked with `--freeze`, which refuses an existing frozen record. The one-off `finish_when_ready.py` only continued this active run; no recurring automation exists.

To review existing predictions without retraining:

```powershell
& $modernPython -B experiments/2026-10-06-modern-restoration/data.py --output experiments/2026-10-06-modern-restoration/reviewer-benchmark-audit.json
& $modernPython -B experiments/2026-10-06-modern-restoration/audit_extra.py --output reviewer-extra-graph-audit.json --witness-name reviewer-extra-graph-witnesses.json
& $modernPython -B experiments/2026-10-06-modern-restoration/verify.py --run main --output reviewer-verification.json
& $modernPython -B experiments/2026-10-06-modern-restoration/summarize.py --run main --output reviewer-aggregate-results.json
& $modernPython -B experiments/2026-10-06-modern-restoration/summarize.py --run main --curves --output reviewer-learning-curves.json
& $modernPython -B experiments/2026-10-06-modern-restoration/verify_frozen.py --prefix reviewer-frozen-inference
& $modernPython -B experiments/2026-10-06-modern-restoration/inventory.py --verify
python -X utf8 -B tools/review_prose.py --path experiments/2026-10-06-modern-restoration --no-write
```

Inner count-of-count grids and training histories are under `main/`; raw probability matrices, per-query audits and weights are under `data/raw/2026-10-06-modern-restoration/main/`. Individual inner-seed arrays were removed after their complete means and seed records were audited, freeing 2,039,403,915 bytes. All outer predictions and checkpoints remain. There are three inner folds per outer fold. [Protocol](PROTOCOL.md), [dated auxiliary-loss amendment](AMENDMENT-2026-10-07.md), [disk recovery](RECOVERY-2026-10-07.md), [precedents](RELATED-WORK.md), [source access record](sources.json), [retrospective](RETROSPECTIVE.md), [proposed registry entry](registry-entry.json), and [complete path/hash inventory](file-manifest.json) provide the research record.

The accuracy figure uses Matplotlib 3.11.2, installed with `pip --no-cache-dir` in the authorized CUDA environment. Its added dependencies are pinned in [plot-requirements.txt](plot-requirements.txt), recorded in the local installation log and included in the path inventory. Re-render it with `& $modernPython -B experiments/2026-10-06-modern-restoration/plot_curves.py --prefix reviewer-learning-curves`.

The 45-epoch transformer cap, source transcription quality, full-register dependency links and future-population performance remain limitations. Published restoration percentages use different candidate-set and span definitions; see the source comparisons before ranking them against this benchmark.
