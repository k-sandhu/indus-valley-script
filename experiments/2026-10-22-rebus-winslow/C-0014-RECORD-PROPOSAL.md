# Proposed update to C-0014 from REBUS-WINSLOW-2026-10-22

Maintainers own the card. These are the changes this package proposes for [C-0014](../../knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md), applying the effect on credence that the card fixed for P2 before the test.

## Record line

- 2026-10-22. P2 failed under its frozen rule in Winslow's dictionary of 1862 ([REBUS-WINSLOW-2026-10-22](REPORT.md)): Winslow has no two-member compound beginning with *muruku* (the *Tamil Lexicon* has 7), so replacement words matched on its productivity have no compounds and none of 2,500 random pairs shares a member (rate 0.0, threshold above 0.20). Credence 0.55 → 0.45 by the card's rule. Neither *Muruka-vēḷ* nor *veṇ-mīṉ* is a Winslow entry, so the *veḷ* interlock does not exist there; two of Parpola's five links hold (*vaṭa-mīṉ*, *aṟu-mīṉ*) and random words reproduce both in 3.9% of draws. Post-outcome, with pools matched to the same compound-set sizes (7 and 29), random pairs share a member in 14.0% of cases in Winslow and 16.6% in the Lexicon.

## Front matter

```yaml
credence: 0.45
credence_history:
  - {date: 2026-10-21, value: 0.55, reason: "..."}   # unchanged
  - {date: 2026-10-22, value: 0.45, reason: "P2 failed in Winslow 1862 (REBUS-WINSLOW-2026-10-22): no compound of muruku is an entry, so the frozen chance rate is 0 against a threshold of 0.20; the card fixed -0.10 for a failure"}
tests: ["experiments/2026-10-21-rebus-base-rate/REPORT.md (retrospective prediction P3 passed; P1 and P2 untested)", "experiments/2026-10-22-rebus-winslow/REPORT.md (P2 failed)"]
```

## Prediction table

P2 status: "failed (Winslow 1862: rate 0.0; no compound of *muruku* is an entry, so the matched pool has no compounds)".

The failure falsifies P2 as written, which assumed that both anchor words have compounds in any large Tamil dictionary. The claim of the card is better served by a prediction about the rate per compound, which this study can no longer test prospectively because its post-outcome analysis already looked at it. We propose adding it for a third dictionary:

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P4 | In a third Tamil dictionary with compounds, random replacement pairs with pools matched to 7 first-member and 29 second-member compounds share a member at a rate within a factor of 1.5 of the *Tamil Lexicon*'s rate for the same targets (16.6%) | Kadirvelu Pillai's dictionary on DSAL, parsed and checked against the *Tamil Lexicon* before the run | ratio between 0.67 and 1.5 under T0s, pools of 50 | pass: +0.05; fail: −0.05 | untested (prospective) |

## Why it might be true (addition)

In Winslow's dictionary of 1862 the *veḷ* interlock has neither of its compounds, and Skanda's name formed on *vēḷ* is *cevvēḷ*. At equal compound-set sizes random words interlock at nearly the same rate in Winslow and in the Lexicon (14.0% and 16.6%; [exploratory.json](exploratory-v1/exploratory.json) `#/X3_equal_set_sizes`), so the chance of an interlock is fixed by how many compounds a dictionary records for the two words.
