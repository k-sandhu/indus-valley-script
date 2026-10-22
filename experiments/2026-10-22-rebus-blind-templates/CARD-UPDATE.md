# Proposed update to C-0014

For maintainers to fold into [knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md](../../knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md). This package does not edit the card.

## Credence

The frozen joint rule of [PREDICTIONS.json](PREDICTIONS.json) sets the credence to 0.8 when P1 passes, and P1 passed. We propose recording 0.8 as the rule's value and 0.7 as the reviewed credence. The blind ratio, 1.81, lies just under the threshold of 2, two sensitivities put it above 2 (pools of 100: 2.35; picture word as first member only: 2.42), and its interval reaches 2.72. The selection half of the claim gained more than the rule credits: Parpola's published pairs succeed at 58% against 24% for his blind pairs.

```yaml
credence: 0.7
credence_history:
  - {date: 2026-10-22, value: 0.8, reason: "Frozen rule of REBUS-BLIND-TEMPLATES-2026-10-22: P1 passed, ratio 1.81 (95% 0.93-2.72) on 38 blind sign pairs"}
  - {date: 2026-10-22, value: 0.7, reason: "Review: the pass is narrow and two sensitivities exceed 2, while the published pairs succeed at 2.5 times the blind rate"}
```

## Prediction table

P1 status: `passed (prospective): 9 of 38 blind pairs against 4.97 expected, ratio 1.81 (0.93-2.72); Parpola's published pairs 7 of 12 against 1.15, ratio 6.1`.

Proposed new prediction, the test that separates the remaining excess from the procedure:

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P4 | The 38 blind sign pairs, given Sanskrit words for Parpola's pictures and scored against the compounds of Monier-Williams (Cologne edition) with matched random Sanskrit words, show a ratio of hit rates within a factor of 1.5 of the Tamil ratio (1.81) | Cologne Monier-Williams; templates-v1.json of REBUS-BLIND-TEMPLATES-2026-10-22 | Sanskrit ratio between 1.2 and 2.7 | pass: +0.1; Sanskrit ratio below 1.2 with the Tamil ratio unchanged: -0.25 | untested (prospective) |

## Record line

- 2026-10-22. [REBUS-BLIND-TEMPLATES-2026-10-22](../../experiments/2026-10-22-rebus-blind-templates/REPORT.md) ran P1 on 38 Indus sign pairs Parpola never published, frozen with his identifications from his 1997–2010 papers before any Tamil compound was looked up. His words formed an attested *Tamil Lexicon* compound for 9 pairs against 4.97 expected for matched random words, a ratio of 1.81 (95% interval 0.93–2.72), so P1 passed (threshold 2; kill at 3). Most hits pair his word with an unrelated homophone (*veḷ-ḷ-āṉai* 'white elephant' for *āṉ* 'cow', *oru-vēḷai* 'once' for *veḷ*); *iru-kaṇ* 'two eyes' is the one apt reading. His twelve published pairs succeed seven times against 1.15 expected (ratio 6.1), a rate he would reach by trying about 28 pairs. Credence 0.8 by the frozen rule, 0.7 after review.
