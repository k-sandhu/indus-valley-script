# Shot A predictions

Written 12 October 2026 after exploring the discovery half only, and frozen on 13 October 2026 before this shot read the confirmation half; the hash of this file, of the lexicon and of confirm.py is in `PREDICTIONS.sha256`. The coordinator reviewed this draft on 13 October 2026, after another shot had read the confirmation half, and made no changes; see ../AMENDMENT-2026-10-13-coordinator.md.

## Conjecture as it enters confirmation

Indus seals were issued in at least two grades, and the upper grade is written twice: the seal is cut larger, and its legend closes with one of four signs, 001, 595, 679 or 820, often in the recurring closing pairs 740-679, 368-001, 420-595, 595-820 and 820-595. A seal whose legend closes this way has about 1.5 to 2 times the face area of a seal of the same type, site class and text length. No other closing sign marks size: the jar sign 740, the X-740 formulas and the other common closers carry no grade. Opening signs individualise the holder and are more local than closings. Seals with identical ordinary legends are not cut to a common size.

Credence before confirmation: 0.12 (starting value 0.25; [EXPLORATION.md](EXPLORATION.md) explains the revision).

## Shared definitions

All statistics are computed by [confirm.py](confirm.py) with functions in [rank_lib.py](rank_lib.py) and the population rules in [seal_table.py](seal_table.py). The same code produced the discovery values quoted below.

Each seal object family contributes one face: the face with the most sign positions, ties broken by the lowest record identifier. The size population is every family from the confirmation half whose object type is `SEAL:S` or `SEAL:R`, with positive `horizontal(mm)` and `vertical(mm)`, preservation `complete`, `slightly chipped`, `chipped` or the catalogue spelling `complsete`, and a text that is completely observed, single-line, free of unknown signs and at least two signs long. For every prediction except P2, each component of the frozen split contributes one seal, the family with the smallest identifier (shorter identifiers first); seals with identical legends of two or more signs always share a component, so each duplicated legend counts once.

Size is ln(horizontal mm) + ln(vertical mm). Residual size is that value minus the fit of an ordinary least-squares model on the confirmation population with seal type, site class (Mohenjo-daro, Harappa, Dholavira, Lothal, Chanhu-daro, Kalibangan, other) and length class (2, 3, …, 8, 9 or more) as factors. Permutation strata are the cells of type × site class × length class; labels move only within a stratum, so each null keeps the type, site and length composition of every label. Every permutation null uses 9,999 draws with seed 20261013, every test is one-sided, and a prediction passes when its p < 0.05. The closing unit is the last sign in reading order; the closing formula is the last two signs when the last is 740 and otherwise the last sign; the opening unit is the first sign.

The frozen grade lexicon is [discovery/lexicon.json](discovery/lexicon.json), lexicon.json SHA-256: `c4b96e20792ffe50186c3eb2c5e59abb2c9999ef6f043d4fc1c772df9df1b887`. It holds a grade score for each last sign and each first sign seen at least three times in the discovery population: the sum of its seals' residuals divided by (n + 3). confirm.py refuses to run if the file's hash differs.

P1a, P1b and P4 all draw on the same few seals that end in the high set. They are three readings of one pattern, not three independent confirmations, and the credence rules below are set with that in mind. A simulation on resampled discovery seals gives their expected pass rates ([power-sim.json](discovery/power-sim.json)). With no grade effect, each passes in 2–5% of 200 trials. If the high set's true effect equals its held-out rehearsal value of +0.36 in log area, P4 passes in 82% of trials, P1b in 51%, P1a in 27% and P1c in 25%; at the in-sample value of +0.66 the rates are 100%, 88%, 78% and 67%. The simulation assumes the confirmation half has about as many high-set seals as the discovery half (median 18 per trial).

## Predictions

### P1a. Closing signs carry size beyond type, site and length

Population: the size population, one seal per component. Statistic: the between-sign sum of squares of residual size, Σ n·(mean residual)², over last signs that occur on at least three seals, divided by its mean under the null. Null: last signs permuted within strata. Pass: p < 0.05. Discovery value: ratio 2.14, p = 0.001 ([unit-size-tests.json](discovery/unit-size-tests.json), `tests`, unit `last`, `min_n` 3). Effect on credence: pass +0.03, fail −0.03.

### P1b. The grade order of closing signs reappears

Population: seals of the size population whose last sign has a score in `closing_scores_last` (28 signs). Statistic: Pearson r between each seal's frozen score and its confirmation residual. Null: the frozen scores rearranged among the 28 signs within bins of discovery frequency (3–4, 5–9, 10–29, 30 or more seals), 9,999 rearrangements; this asks whether the particular signs graded high or low in discovery keep their places, compared with signs of similar frequency given the same scores. Pass: r > 0 and p < 0.05. The seal-level permutation p for the same r is reported beside it. The discovery half cannot score its own lexicon. Effect on credence: pass +0.03, fail −0.02.

### P1c. Closing signs explain more size variation than opening signs

Population: the size population, one seal per component. Statistic: the P1a ratio for last signs minus the same ratio for first signs, both over signs with at least three seals. Null: whole texts permuted within strata, so first and last sign move together. Dividing each sum by its own null mean corrects for opening signs having more distinct units and a different spread of frequencies. Pass: p < 0.05. Discovery value: 2.13 against 1.15, difference 0.98, p = 0.005 ([unit-size-tests.json](discovery/unit-size-tests.json), `closing_minus_opening`, first row). Effect on credence: pass +0.02, fail −0.01.

### P2. Identical legends are closer in size than matched seals

Population: every seal of the size population (no reduction to components) whose exact text is shared by at least one other seal in it. Statistic: mean |difference in size| over all pairs of seals with the same text. Null: for each pair, one member chosen at random is replaced by a random seal of the same type, length and site class from a different component, 9,999 draws. Pass: observed mean below the null with p < 0.05; untestable with fewer than ten usable pairs. Discovery value: 0.568 against 0.592, p = 0.31 ([identical-legends.json](discovery/identical-legends.json), `test`). The revised conjecture expects a failure here; a pass would restore the original claim that a shared legend fixes the size. Effect on credence: pass +0.04, fail 0.

### P3. Opening signs are more specific to site than closing formulae

Population: confirmation families of type `SEAL:S` or `SEAL:R` with a clean text of at least two signs and a named site (not `Unknown`), one per component; dimensions are not required. Statistic: z(MI first sign; site) − z(MI closing formula; site), each z measured against its own null distribution of mutual information, so each unit is judged against the chance level set by its own frequency spectrum and entropy. Null: site labels shuffled within seal type; the same 9,999 shuffles serve both units and give the null of the difference. Pass: p < 0.05. Discovery value: z = 2.54 for first signs, 0.88 for closing formulae, difference 1.66, p = 0.11 ([site-specificity.json](discovery/site-specificity.json), first row). Effect on credence: pass +0.02, fail −0.01.

### P4. Legends closing in 001, 595, 679 or 820 sit on larger seals

Population: the size population, one seal per component. Statistic: mean residual of seals whose last sign is 001, 595, 679 or 820 minus the mean residual of all other seals. Null: last signs permuted within strata. Pass: p < 0.05; untestable if fewer than five seals end in the set. Discovery value: +0.68 (18 seals at +0.66, 572 at −0.02), p = 0.0002; dropping any one of the four signs leaves p ≤ 0.0005 ([high-closers.json](discovery/high-closers.json), `contrast_high_minus_rest`, `drop_one`). The set was chosen after looking: it is every last sign with a discovery score of at least 0.25, and the next sign scores 0.13. In 300 split-half rehearsals with the set chosen on one half of the discovery seals, its seals on the other half averaged +0.36, against −0.03 for the signs scored low and 0.00 for the rest ([power-split.json](discovery/power-split.json), `pooled_test_half_mean_residual`). Effect on credence: pass +0.10, fail −0.06.

### P5. Unicorn seals coded `Bull1:W` are larger (auxiliary)

Population: seals of the size population whose field animal is a unicorn (`symbol` beginning `Bull1`). Statistic: mean residual of the catalogue variant `Bull1:W` minus that of the other `Bull1` variants. Null: the W/other label permuted within strata among unicorn seals. Pass: p < 0.05, with at least five seals in each group. Discovery value: +0.41 (144 W seals at +0.26, 238 others at −0.14), p = 0.0002 ([iconography.json](discovery/iconography.json), `unicorn_W_vs_other`). In the photographs inspected the W seals show a broad loop over the unicorn's shoulder, and the W share rises smoothly from 3% below 18 mm to 95% above 40 mm, which fits an ornament carved when the face has room. This prediction records an image–size relation for the evidence record; it does not bear on the grade conjecture. Effect on credence: none.

## Kill condition

The conjecture is dead if P4 does not pass (failed or untestable) and P1a fails. That outcome means the confirmation half shows no size information in closing signs at all, either through the named set or through any other closing sign. Its card then moves to status dead with credence 0.02.

If P4 fails and P1a passes, closing signs carry size but not through the named set; the conjecture is weakened and the lexicon needs replacing by a new shot. If P4 passes and P1a fails, the named set stands but the general claim about closing units loses its wider support.

## Credence after confirmation

Start from 0.12 and add the stated amounts for each scored prediction; clip to the range 0.02–0.60. The kill condition overrides the sum. P5 does not enter.

## Prospective predictions

These concern material outside the Lipi export or not yet measured. They are scored when the material is examined, and are not part of the confirmation run.

1. Ten Lothal bale sealings, L-161 to L-170, carry the text of Mohenjo-daro seal M-895 (see the [seal-text identity report](../../2026-10-12-seal-text-identity/REPORT.md)). If the catalogue's last sign of that text is 001, 595, 679 or 820, the seal face impressed on the sealings measures more than 30 mm on a side. Otherwise the conjecture assigns it the ordinary grade, and the impressed face falls within the 10th–90th percentile range of four-sign square seals in the discovery half, 19.9 to 35.4 mm. Effect on credence: +0.03 if met, −0.03 if not.
2. In seals published after this export, or in a future concordance that adds seals absent from it, at least two thirds of complete square or rectangular seals whose legend ends in 001, 595, 679 or 820 are larger than the median seal of the same type and text length from the same site, judged once at least ten such seals are available. In the discovery half 16 of 18 such seals are (residual above zero; [high-closers.json](discovery/high-closers.json), `seals`). Effect on credence: +0.05 if met, −0.05 if not.
3. Inspection of photographs of the 18 discovery seals and of the high-set seals in the confirmation half shows the closing sign inside the text band at its end, as on H-1 and M-1. If on most of them the sign stands apart in the field, for example above the animal's back, the catalogue's final position reflects layout on large faces rather than a closing formula, and the conjecture loses its textual half.

## Commands

```
python experiments/2026-10-12-conjecture-shots/shot-a-rank/explore.py
python experiments/2026-10-12-conjecture-shots/shot-a-rank/confirm.py --dry-run-discovery
python experiments/2026-10-12-conjecture-shots/shot-a-rank/confirm.py     # after freezing
```
