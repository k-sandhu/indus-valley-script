# Two approaches developed on 11 October 2026

Start with the [integrated findings and theory](REPORT.md). The program extends grammar induction and competing administrative functions through new code, preserved primary failures, exploratory controls and adversarial review.

| Package | Outcome and reusable record |
|---|---|
| [Literature](literature/LANDSCAPE.md) | 20 sources, 22 anchored recommendations; [source ledger](literature/sources.json) and [recommendations](literature/recommendations.json) |
| [Learned grammar](grammar/REPORT.md) | Standalone grammar loses to Markov; exploratory class mixture adds 0.0557 bits per token over a matched position mixture; [future predictions](grammar/FUTURE-PREDICTIONS.md) |
| [Whole-object administrative records](administrative/REPORT.md) | Recurring bundles remain under a face-role control; sign-pair maxima do not pass its adjusted threshold |
| [Adversarial review](review/REVIEW.md) | Independent score/allocation reconstruction and an exact prototype-selection counterexample; [response](REVIEW-RESPONSE.md) |
| [Proposed typed record](HYPOTHESIS-NOTE.md) | Pre-result theory, followed by the [token life-cycle synthesis](REPORT.md#a-proposed-record-and-token-life-cycle) |
| [External anchors](ANCHORS.md) | Exact synthetic example of contextual information and copied-witness dependence |

## Manual reproduction

Python 3.13, NumPy and SciPy were used. The empirical packages require the pinned local `data/normalized/lipi_observed_faces.jsonl`, the clean sequence derivative, and saved fitted arrays or a fresh fit. The package reports each required hash. A Git checkout can read protocols, outputs and source records and run the synthetic examples; it does not include unresolved-rights corpora or downloaded witnesses. Package-specific commands are in [grammar/README.md](grammar/README.md) and [administrative/README.md](administrative/README.md).

From the repository root, choose new output versions rather than replacing an endpoint:

```powershell
python -B experiments/2026-10-11-two-approaches/contextual_anchors.py --out anchors-v2
python -B experiments/2026-10-11-two-approaches/verify_program.py --out verification-program-v2.json
python -B experiments/2026-10-11-two-approaches/independent_grammar_checks.py --out coordinator-checks/grammar-v3.json
python -B experiments/2026-10-11-two-approaches/independent_mixture_checks.py --out coordinator-checks/mixtures-v2.json
```

The scripts refuse to replace saved outputs. Their `--out` paths are relative to this package. Replaying a checker verifies the same endpoint rather than supplying a new empirical observation. [Coordinator checks](coordinator-checks/), [review checks](review/), [program integrity](verification-program-v1.json).

The [initial protocol](PROTOCOL.md), [baseline hashes](baseline-v1.json), package amendments and [retrospective](../../knowledge/retrospectives/2026-10-11-two-approaches.md) preserve the development sequence. Files are maintained locally; this program adds no CI/CD, deployment or recurring automation.
