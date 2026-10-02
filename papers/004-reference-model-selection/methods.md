# Method files and claim map

| Claim | Exact evidence | Status |
|---|---|---|
| Fresh 48-system, 384-condition slot/graph grid | [Protocol](../../experiments/2026-10-02-six-hour/slot-mapping/PROTOCOL.md), [main](../../experiments/2026-10-02-six-hour/slot-mapping/main/results.json), [generated worlds](../../experiments/2026-10-02-six-hour/slot-mapping/main/worlds.json) | Completed new-world comparison developed after the earlier graph result |
| Administrative 20-symbol recovery 55/96 versus 25/96 | [Summary and paired intervals](../../experiments/2026-10-02-six-hour/slot-mapping/review/summary.json) | Twelve systems, eight conditions each; system bootstrap |
| All linear optima checked, 23 tied conditions | [Review](../../experiments/2026-10-02-six-hour/slot-mapping/review/verification.json), [alternatives](../../experiments/2026-10-02-six-hour/slot-mapping/review/ties.json) | Independent scalar likelihoods and assignment dual bounds; declared floating tolerances |
| Reference-only model choice | [Selector protocol](../../experiments/2026-10-02-six-hour/reference-selector/PROTOCOL.md), [source snapshot](../../experiments/2026-10-02-six-hour/reference-selector/main/code_snapshot.py) | Fresh reference-only three-fold choice; no truth/family input to selector |
| 309/384 selected recoveries versus 310 supplied-family diagnostic | [Selector result](../../experiments/2026-10-02-six-hour/reference-selector/main/results.json), [independent report](../../experiments/2026-10-02-six-hour/reference-selector/review/REPORT.md) | 6,489 independent checks of all folds, choices, scores, dual bounds and truth comparisons |
| Eleven exact slot-tie conditions, 32 alternative witnesses | [Exact alternatives](../../experiments/2026-10-02-six-hour/reference-selector/review/additional-v1/exact-slot-alternatives.json) | Post-run mathematical diagnostic with prime-factor equality certificates |

The graph matcher uses [the preserved implementation](../../src/six_hour/graph_mapping.py). The slot model and review are [slot_mapping.py](../../src/six_hour/slot_mapping.py) and [review_slot_mapping.py](../../src/six_hour/review_slot_mapping.py). The reference selector is [reference_selector.py](../../src/six_hour/reference_selector.py), with exact executed helpers retained in its endpoint.

Run scripts from the root only into a new dated endpoint. The existing outputs should be inspected directly. Each main directory has immutable source and helper snapshots, protocol hashes and saved generated worlds. The [slot retrospective](../../experiments/2026-10-02-six-hour/slot-mapping/RETROSPECTIVE.md) records the preceding failure that suggested the new model.
