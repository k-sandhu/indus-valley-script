# Modern restoration benchmark comparison

Status: Exploratory. Completed 7 October 2026 from a protocol written on 6 October before fitting; interpretation corrected after the Sonnet review on 7 October.

Modified Kneser–Ney restores 39.7178% of 8,009 known slots with 4.581891 bucket bits, compared with 34.5861% / 5.119435 bits for first order and 37.2706% / 5.247171 bits for second order. The neural families alone do not beat MKN on top-one. Combining MKN and neural probabilities raises accuracy to 40.7916% without extra text and 41.1662% with it; the latter has the lowest native loss, 4.347675 bits. [Results](aggregate-results.json), `models`; [report](REPORT.md), Accuracy, probability loss and calibration.

Extra text adds 501-506 distinct strings and 1,419-1,427 tokens per fold after transitive exclusion. It gives no measurable top-one gain in any family: the point changes range from -0.1124 to +0.4870 percentage points, and every paired interval includes zero. MKN's common-alphabet loss falls by 0.2990 bits, with 94% of that gain coming from the 251 targets outside the original training alphabet. Across families those targets account for 72-94% of the loss gain; their top-one accuracy is unchanged. [Direct contrasts](aggregate-results.json), `direct_contrasts`; [review decomposition](review/extra-text-decomposition.json), `families`.

All saved masks, targets, artifacts, groups and folds match. The complete export reveals chains across the saved folds: 16 identical one- or two-sign texts on faces of different objects join 192 benchmark strings and 748 queries (9.3%) in six sets, yielding 144-159 linked training strings per fold. No links remain when identical-text edges require three signs. This bears on Paper 001's component-held-out independence. Removing linked training strings costs 8.02, 8.96 and 5.88 points on the touched queries for first order, second order and MKN, respectively; holding the other queries fixed implies whole-benchmark changes of -0.75, -0.84 and -0.55 points. Model ranking stays the same and paired differences move by at most 0.30 points. [Graph size](review/graph-links-summary.json), [graph rules](review/graph-rule-sensitivity.json), [reviewer effect estimates](review/link-respect-estimate.json), `models`.

A training string one sign edit away exists for 509/1,596 benchmark strings (31.9%), covering 2,016 queries. Removing those neighbours costs an estimated 1.47-2.32 points across the whole benchmark for the three n-gram models. Both dependency results are exploratory reviewer sensitivities with fixed hyperparameters; the saved endpoints remain unchanged. [Neighbour exposure](review/neighbor-exposure.json), [removal estimates](review/variant-respect-estimate.json), `models`.

The completed comparisons cover orders 2-5, two GRU configurations, two transformer configurations, three neural seeds, joint metadata conditioning, both text regimes, ensembles, secondary accuracy selection and four training sizes. All four learning curves still rise from 75% to 100% training, by 1.21-1.71 accuracy points. The report keeps training-budget and variant-coverage limitations beside that finding.

- [Learning curves](learning-curves.json) and [accuracy figure](figures/learning-curves.png).
- [Training diagnostics](training-diagnostics.json) and [internal verification](verification.json).
- [Frozen carry-forward recipe](frozen-model/manifest.json), selected using inner outcomes, with local counts and weights for a future fresh population.
- [Refined loader checks](frozen-inference-v2-verification.json) and [verification amendment](VERIFICATION-AMENDMENT-2026-10-07.md).

## Reproduce from the repository root

The normalized corpora and saved query audits must be present locally. Fitting used Python 3.13.5, NumPy 2.5.3 and CUDA PyTorch 2.14.1+cu126 in the RTX 4070 environment. Plotting dependencies were added to that environment and are now recorded in [environment.json](environment.json). Pypdf from the system Python is needed only for literature extraction.

```powershell
$modernPython = 'C:/Users/sandh/.venvs/indus-ml/Scripts/python.exe'
& $modernPython -B experiments/2026-10-06-modern-restoration/run_all.py --run reviewer-2026-10-07
```

Choose a new run label. Fits can resume completed stage records; completed aggregate endpoints refuse replacement. `run_all.py` repeats fitting, selection, curves, summaries and mathematical checks. It preserves the existing carry-forward model unless invoked with `--freeze`, which refuses an existing frozen record. The one-off `finish_when_ready.py` continued the original active run.

To review existing predictions without retraining:

```powershell
& $modernPython -B experiments/2026-10-06-modern-restoration/data.py --output experiments/2026-10-06-modern-restoration/reviewer-benchmark-audit.json
& $modernPython -B experiments/2026-10-06-modern-restoration/audit_extra.py --output reviewer-extra-graph-audit.json --witness-name reviewer-extra-graph-witnesses.json
& $modernPython -B experiments/2026-10-06-modern-restoration/verify.py --run main --output reviewer-verification.json
& $modernPython -B experiments/2026-10-06-modern-restoration/summarize.py --run main --output reviewer-aggregate-results.json
& $modernPython -B experiments/2026-10-06-modern-restoration/summarize.py --run main --curves --output reviewer-learning-curves.json
& $modernPython -B experiments/2026-10-06-modern-restoration/verify_frozen.py --prefix reviewer-frozen-inference
& $modernPython -B experiments/2026-10-06-modern-restoration/verify_followup.py
python -X utf8 -B tools/review_prose.py --path experiments/2026-10-06-modern-restoration --no-write
```

Inner grids and training histories are under `main/`; probability matrices, per-query audits and weights are under `data/raw/2026-10-06-modern-restoration/main/`. There are three inner folds per outer fold. Disk recovery removed 450 individual inner-seed arrays after auditing their complete means and seed records, freeing 2,039,403,915 bytes. All outer predictions and checkpoints remain.

- [Protocol](PROTOCOL.md), [original auxiliary-loss amendment](AMENDMENT-2026-10-07.md) and [dated review errata](ERRATA-2026-10-07.md).
- [Review](REVIEW.md), [precedents](RELATED-WORK.md) and [source access record](sources.json).
- [Disk recovery](RECOVERY-2026-10-07.md), [retrospective](RETROSPECTIVE.md) and [proposed registry entry](registry-entry.json).
- [Original path/hash inventory](file-manifest.json) and [review follow-up manifest](followup-2026-10-07.json). The original inventory describes the pre-review package; `verify_followup.py` checks its unchanged files and the amended files against their separate records.

The figure uses Matplotlib 3.11.2, installed with `pip --no-cache-dir` in the CUDA environment. Versions are pinned in [plot-requirements.txt](plot-requirements.txt). The PNG and requirements remain in this package for the coordinator's tracking exception. Re-render with `& $modernPython -B experiments/2026-10-06-modern-restoration/plot_curves.py --prefix reviewer-learning-curves`.

The reviewer reproduced every headline and confirmed selection and extra-text exclusion. Longer transformer training, source transcription quality and performance on a fresh population remain unverified. Published restoration percentages use different candidate-set and span definitions; [source comparisons](RELATED-WORK.md) give those definitions.
