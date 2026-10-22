# Proposed changes to C-0011 after P5

For maintainers to integrate into [C-0011](../../knowledge/conjectures/C-0011-proto-dravidian-min-fish-and-star.md). This study did not edit the card.

## Credence

The frozen rule of P5 leaves the credence at 0.20, because one entry outside 4876 qualifies (pass needs two, failure needs none). We propose that review lower it to 0.15, which the protocol allows. Add to `credence_history`:

```yaml
  - {date: 2026-10-21, value: 0.20, reason: "P5 unresolved under its frozen rule: one entry outside 4876 (4952, 'crocodile') has Kurukh and Malto b- for Tamil m-"}
  - {date: 2026-10-21, value: 0.15, reason: "Review of P5: Tamil m- gives northern m- in 83 of 88 comparisons and in all 6 before a long front vowel, Malto keeps mínu 'fish' apart from bínḍke 'star', and northern b- answers Tamil v- in 50 of 55; the northern star words fit viṇ 'sky'"}
```

and set `credence: 0.15`, with `experiments/2026-10-21-north-b-correspondence/REPORT.md` and `experiments/2026-10-21-north-b-correspondence/results-v1/results.json` added to `tests`.

## Predictions table, P5 status cell

> unresolved: 1 entry outside 4876 (4952); northern *m-* for Tamil *m-* 83 of 88, *b-* 2; before a long front vowel 6 of 6 *m-*

## Record entry

> 21 October 2026: [NORTH-B-CORRESPONDENCE-2026-10-21](../../experiments/2026-10-21-north-b-correspondence/REPORT.md) ran P5 under a protocol hashed at 18:41 UTC and code frozen at 18:57. Across DEDR, Kurukh and Malto answer Tamil *m-* with *m-* in 83 of 88 comparisons and with *b-* in two, both in entry 4952 "crocodile"; they answer Tamil *v-* with *b-* in 50 of 55. P5 is unresolved under its rule (one qualifying entry, two needed), which leaves the credence at 0.20. Review lowered it to 0.15: in the setting P5 names, a long front vowel after Tamil *m-*, all six northern reflexes keep *m-*, Malto among them has *mínu* "fish" beside *bínḍke* "star", and the only regular source of northern *b-* is the *v-* of *viṇ* "sky", whose Malto reflex *biṉye* has the star word's initial and vowel. With the northern star words assigned to *viṇ*, "star" in entry 4876 reaches the root at 0.34–0.47 and is carried outside South I by Gondi alone, so the fish–star homophone is a South Dravidian pun. A second implementation written from the protocol alone reproduced the outcome and every entry list and corrected one count (entry 4886 is doubtful in Kurukh). Verification tier: submitted.

## A new prediction

The report's boldest reading is that North Dravidian named the star after the sky. We propose adding it to the card as a prediction that can fail:

| ID | Prediction | Data | Pass rule | Effect on credence | Status |
|---|---|---|---|---|---|
| P6 | The Kurukh and Malto star words are derivatives of the northern sky word **wiṇ-* | Malto and Kurukh grammars and dictionaries independent of DEDR (Droese 1884, Mahapatra 1979, Hahn 1903, Grignard 1924) or fieldwork | A source segments *bínḍke* or *bīnkō* as a sky base *biṉ-*/*bīn-* with a productive suffix, or records a Kurukh base *bīn-* "sky, heaven" | Pass: lower to 0.10 (the homophone is South Dravidian only); a source that segments them as *bin-* "shine" with the *-kō* of Gondi *mīnkō* and no sky base: raise to 0.20 | prospective |
