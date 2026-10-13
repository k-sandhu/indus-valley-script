# Shot A: rank is written twice on Indus seals

This shot tested the conjecture that Indus seals were issued in grades, with the grade marked both by the size of the seal and by the closing signs of its legend ([SHOT.md](SHOT.md), card [C-0001](../../../knowledge/conjectures/C-0001-rank-written-twice.md)). It followed the two-stage design of the [conjecture shots](../DESIGN.md): free exploration of the discovery half, predictions frozen with their hashes, then one scored run on the confirmation half.

On the confirmation half, legends ending in 001, 595, 679 or 820 sat on larger seals than legends of the same type, site class and length: the 11 such seals average +0.35 in residual log face area against −0.01 for the other 571 (p = 0.021). Last signs as a whole carried size information beyond type, site and length (between-sign ratio 1.81, p = 0.0074). The frozen grade order of the full closing-sign lexicon did not clear its rearrangement test (r = 0.117, p = 0.060), closing signs did not explain more size than opening signs (p = 0.32), identical legends were not significantly closer in size than matched seals (p = 0.10), and the site prediction reversed: closing formulae, not opening signs, were the site-specific end. The kill condition was not met, and under the frozen rules the conjecture's credence rose from 0.12 to 0.21. An independent recomputation agreed on P1a, P4 and the kill decision. The full account is in REPORT.md, placed by the coordinator.

The coordinator reviewed the draft predictions after Shot B had read the confirmation half and changed nothing ([coordinator amendment](../AMENDMENT-2026-10-13-coordinator.md)).

## Files

| File | Content |
|---|---|
| [EXPLORATION.md](EXPLORATION.md) | Discovery-half exploration, steps E1–E14, and the two revisions of the conjecture |
| [PREDICTIONS.md](PREDICTIONS.md), [PREDICTIONS.sha256](PREDICTIONS.sha256) | Frozen predictions; hashes of the predictions, lexicon and scoring code |
| [discovery/](discovery/) | Discovery outputs; [lexicon.json](discovery/lexicon.json) is the frozen grade lexicon |
| [confirmation/results.json](confirmation/results.json) | The frozen confirmation outcome |
| [verification.json](verification.json) | Independent recomputation of P1a, P4 and the kill decision |
| [AMENDMENT-2026-10-13-post-outcome.md](AMENDMENT-2026-10-13-post-outcome.md), [post-outcome-exploratory.json](confirmation/post-outcome-exploratory.json) | Exploratory breakdowns after the outcome |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Approaches, problems, fixes and outcomes |
| [registry-entry.json](registry-entry.json) | Proposed registry entry |
| `confirmation-access.jsonl` | Log of every read of the confirmation half |

Code: [seal_table.py](seal_table.py) (population rules), [rank_lib.py](rank_lib.py) (statistics and nulls), [explore.py](explore.py), [power_split.py](power_split.py), [power_sim.py](power_sim.py), [confirm.py](confirm.py), [verify.py](verify.py) (independent of confirm.py and rank_lib.py), [post_outcome.py](post_outcome.py). Files listing full legends stay local under `data/raw/2026-10-12-conjecture-shots/shot-a-rank/`.

## Rerunning

From the repository root, with the pinned faces file and the local split in place:

```
python experiments/2026-10-12-conjecture-shots/shot-a-rank/explore.py
python experiments/2026-10-12-conjecture-shots/shot-a-rank/power_split.py
python experiments/2026-10-12-conjecture-shots/shot-a-rank/power_sim.py
python experiments/2026-10-12-conjecture-shots/shot-a-rank/confirm.py --dry-run-discovery
python experiments/2026-10-12-conjecture-shots/shot-a-rank/verify.py
python experiments/2026-10-12-conjecture-shots/shot-a-rank/post_outcome.py
```

`confirm.py` without a flag refuses to run while `confirmation/results.json` exists; the frozen outcome is not recomputed in place. `verify.py` and `post_outcome.py` read the confirmation half through the logged loader, and each run appends to `confirmation-access.jsonl`. `explore.py` rewrites the discovery outputs, including `lexicon.json`; its four runs during exploration produced the same lexicon hash each time, and after any rerun the lexicon must still match the hash in `PREDICTIONS.sha256`.
