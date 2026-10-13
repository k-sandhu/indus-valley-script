# Shot A retrospective

12–13 October 2026. This records the approaches, problems, fixes and outcomes of the shot as they can be seen in its files and logs.

## Approach

The shot began from the conjecture in [SHOT.md](SHOT.md): graded offices, seal size marking the grade, closing signs naming it, opening signs individualising the holder, and identical legends cut to one size. Exploration used only the discovery half. A shared module ([seal_table.py](seal_table.py)) fixed the population rules, and a second ([rank_lib.py](rank_lib.py)) held every statistic and null, so the discovery outputs, the rehearsals and the confirmation script all ran the same code. Seal size was the log of face area, residualised on seal type, site class and text length; every permutation moved labels only within those cells, and each component of the frozen split contributed one seal.

The exploration tried the last sign, the last two signs, the X-740 formula, the first sign and the first two signs as units; scanned every sign by position; looked for discrete size grades, numeral effects, find-area effects, motif, boss and the catalogue's unicorn and cult-object variant codes; and inspected ten seal photographs to see what the variant codes depict. Each step wrote a JSON output, listed in [EXPLORATION.md](EXPLORATION.md).

## Problems and fixes

The first unit tests showed a strong closing-sign effect that vanished when only common signs were kept. A sign-by-position scan and a list of the seals behind the effect located it in four rare last signs. To test whether that was a selection artefact, the discovery seals were split in half 300 times, with the lexicon built on one half and tested on the other ([power_split.py](power_split.py)). The high signs held up out of sample and the low ones did not, so the conjecture was cut down to one marked upper grade before freezing.

The same rehearsal showed that the full grade lexicon passed its own frozen calibration test at chance rate on half-size samples. A simulation on resampled discovery seals ([power_sim.py](power_sim.py)) then gave expected pass rates for each prediction at plausible effect sizes, and those rates went into [PREDICTIONS.md](PREDICTIONS.md) so the coordinator could judge the predictions' power before freezing.

Two locality statistics, the same-site share of pairs pooled over pairs and averaged over units, ranked opening and closing units in opposite orders because one is dominated by the 227 seals ending in 740 and the other by units of two or three seals. The frozen test used a z-scored mutual information instead, judged against each unit's own null. The difference was not significant on discovery (p = 0.11), and on the confirmation half it reversed.

The contrast statistic could return an undefined value when a group was empty; a guard returning "untestable" was added before freezing. The confirmation script checks the lexicon's SHA-256 against the value written in PREDICTIONS.md and refuses to overwrite a frozen result.

The first run of the independent verification ([verify.py](verify.py)) read the confirmation half and then failed to serialise a numpy boolean. It was fixed and rerun; the failed attempt is the second entry in `confirmation-access.jsonl`, which holds four reads in all: the scored run, the failed and the successful verification, and the exploratory breakdown.

## Order of review

Shot B froze and read the confirmation half first. The coordinator reviewed this shot's draft after Shot B's outcome was known, did not pass that outcome on, and changed nothing ([coordinator amendment](../AMENDMENT-2026-10-13-coordinator.md)). This shot's agent did not read Shot B's directory or outputs.

## Outcome

On the confirmation half, P4 (the four-sign closing set marks larger seals, +0.35, p = 0.021) and P1a (last signs carry size, ratio 1.81, p = 0.0074) passed; P1b, P1c, P2 and P3 failed, P3 in the reverse direction; the auxiliary P5 passed. The kill condition was not met and the credence rose from 0.12 to 0.21 under the frozen rules. The independent recomputation agreed on every checked quantity. The post-outcome breakdown ([amendment](AMENDMENT-2026-10-13-post-outcome.md), exploratory) found the P4 pass carried mainly by sign 820, with 679 not repeating.

## What to do differently

The split-half rehearsal and the power simulation were the most useful steps: they showed before freezing which predictions had a fair chance and which did not. They should be run before drafting predictions, not after. Predictions resting on a handful of rare signs need material from outside the split; the prospective predictions on seals published after this export, and a photographic check of where the closing signs sit on the face, are the next tests.
