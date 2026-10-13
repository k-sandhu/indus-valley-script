# Class grammar research package

Read [REPORT.md](REPORT.md) for outcomes, class inventories and functional hypotheses. [PROTOCOL.md](PROTOCOL.md) fixes the primary run. [POST-OUTCOME-PROTOCOL.md](POST-OUTCOME-PROTOCOL.md) and [AMENDMENT-V3.md](AMENDMENT-V3.md) keep the later backoff development separate. [FUTURE-PREDICTIONS.md](FUTURE-PREDICTIONS.md) and [carry-forward.json](carry-forward.json) define the next-data commitments.

Manual commands from the repository root, using Python with NumPy and SciPy:

```powershell
C:/Python313/python.exe -B experiments/2026-10-11-two-approaches/grammar/analyze.py --run new-primary-run
C:/Python313/python.exe -B experiments/2026-10-11-two-approaches/grammar/verify.py --run new-primary-run
C:/Python313/python.exe -B experiments/2026-10-11-two-approaches/grammar/predict.py --length 5 --prefix 817,002 --top 5
```

The first command fits the declared primary grammar, five nested folds and six synthetic controls. It refuses an existing output name. `mixture.py` takes `--run` and `--primary`, preserves the earlier endpoint and writes the post-outcome class mixture. The matched-control script follows the documented run-v1/run-v2 paths; a new reproduction should copy it into a fresh dated package with explicit source pins rather than replace the completed endpoint.

`grammar.py` provides training-only alphabets, full-register grouping, positional and Markov models, the learned grammar, normalized prefix prediction and posterior/Viterbi descriptions. The grammar and comparator constructors accept lists of dictionaries with `seq` tuples, so other corpora can be evaluated through a separately declared caller and grouping protocol. `predict.py` loads the frozen full-data class arrays and rebuilds the pinned comparator counts for an assumed length and a supplied prefix. It uses no future target argument.

The input corpus and fitted dictionaries are local-only. A Git checkout can inspect protocols, source locators, code, aggregates and verification results; refitting requires the pinned observational derivative described in [sources.json](sources.json). Per-text sequences, predictions, model arrays and fold assignments live in `data/raw/2026-10-11-two-approaches/grammar/`. Synthetic roles in the controls are invented interpretations of a shared generator.

The JSON field `GRAMMAR_minus_MARKOV` stores a **log-probability gain**, equal to Markov loss minus grammar loss. In mixture summaries `GRAMMAR` denotes the combined predictor; each results file records the label mapping. The [report table](REPORT.md) labels these comparisons directly in terms of loss.

There is no CI/CD, deployment or recurring execution component.
