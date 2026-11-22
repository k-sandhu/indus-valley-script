# REBUS-REPAIRED-2026-11-22: repaired Tamil blind-template calibration, re-extracted Winslow sensitivity, and Sanskrit cross-language control

Date: 22 November 2026. Addresses GitHub Issue #18 (Q-0039). Protocol written before execution in [PROTOCOL.md](PROTOCOL.md). All earlier frozen endpoints remain unchanged, and no new Indus confirmation cohort was read.

## Results

Two findings settle the open questions from the October 2026 rebus studies.

First, repairing the Tamil lexical inputs leaves the blind-template outcome essentially unchanged and slightly weakens its statistical separation from chance. Replacing the Sangam prefix-count proxy (*kā* 22,287 to 9 exact tokens; *ā* 4,458 to 24) and removing the silent phonological fallback (*aṟu* to *aṟṟu*) gives 9 attested *Tamil Lexicon* compounds among Asko Parpola's 38 unpublished sign pairs against 5.19 expected across 10,000 sign-level dependent random keys (ratio 1.73; marginal expected 5.13, ratio 1.75, 95% bootstrap interval 0.84 to 2.60; exact random-key probability p = 0.1037; [tamil_repaired.json](results-v1/tamil_repaired.json)). Removing Sangam frequency entirely and matching solely on compounding productivity gives nearly the same numbers (expected 5.18, ratio 1.74, p = 0.0821). Under the legacy slot-keyed draw scheme of 22 October, the repaired ratio is 1.84 (p = 0.0704), compared with the original 1.81 (p = 0.067). Repairing the frequency proxy also leaves the 21 October base-rate conclusions intact: the *veḷ* interlock (I1) arises in 28.8% of random replacement pairs under exact written-form frequency matching (33.7% productivity-only), well above the 20% kill line, while the four-link conjunction holds in 0.40% of draws (0.62% productivity-only).

Second, the Sanskrit cross-language control decides conjecture [C-0014](../../knowledge/conjectures/C-0014-parpola-interlocks-measure-the-lexicon.md) against Dravidian lexical specificity on unselected sign pairs. When Parpola's 16 concrete pictures are mapped to their standard Sanskrit nouns and numerals before any compound lookup and scored on the exact same 38 blind Indus sign pairs in Cologne Monier-Williams (101,164 extracted two-member compounds), the single-word Sanskrit map yields 6 attested compounds against 1.31 expected from 10,000 sign-level random keys, a ratio of 4.59 (95% bootstrap interval 1.78 to 8.94, p = 0.0020; [sanskrit_control.json](results-v1/sanskrit_control.json)). Matching Parpola's exact number of alternative forms per sign (24 Sanskrit words across the 16 signs) yields 8 hits against 2.04 expected, a ratio of 3.93 (1.75 to 7.28, p = 0.0005). Replacing *rekhā* ("line, stroke") with *antara* ("space between, interval", translating Parpola's pictorial *veḷi* reading of the two long strokes) gives ratios of 3.43 (7 hits, p = 0.0054) and 3.11 (9 hits, p = 0.0013). On the 12 sign pairs Parpola published, by contrast, Sanskrit produces only 1 hit (single-word map, ratio 2.04, p = 0.4205) or 2 hits (multiplicity-matched map, ratio 3.59, p = 0.0876), whereas Parpola's Tamil words hit 7 of 12 (ratio 4.64, p = 0.0011).

This comparison satisfies the pre-frozen decision criterion of [PROTOCOL.md](PROTOCOL.md) Section 3.3 (`ratio_Sanskrit >= 1.5`, with `ratio_Tamil / ratio_Sanskrit` between 0.38 and 0.56). A blind-pair ratio near 1.7 to 2.5 does not discriminate Dravidian from an unrelated Indo-Aryan lexical control. Basic concrete nouns and numerals (two, six, seven, eye, cow, yoke, water) combine with one another far more often than random dictionary nouns matched only on marginal compounding productivity, and vowel-length-free matching adds accidental homophone hits in both languages (*matsya-jāla* "fish-net" for fish plus water in Sanskrit, alongside *veḷ-ḷ-āṉai* "white elephant" for two long strokes plus bull's head in Tamil).

## Experiment A1: Repaired Madras Tamil Lexicon rerun

We reused the frozen 38 blind pairs (`T01`–`T38`), 24 gapped pairs (`G01`–`G24`), and 12 published pairs (`P01`–`P12`) from `experiments/2026-10-22-rebus-blind-templates/templates-v1.json`, together with the 56,154 two-member compounds of the Madras *Tamil Lexicon* and the 17 Project Madurai Sangam files. Exact written-form tokenization through `lexical_inputs.tamil_tokens` yields 162,436 Tamil letter-and-mark tokens (37 more splits than the earlier raw-block regex's 162,399 because Tamil numeral symbols in `U+0B80`–`U+0BFF` separate tokens, while exact written-form counts for every Parpola word are unchanged: *kā* = 9, *ā* = 24, *aṟu* = 23, *aṟṟu* = 8). Strict lookup through `lexical_inputs.Lexicon.resolve` finds exact one-member records for 23 of the 24 proposed Tamil forms and zero exact one-member records for *aṟu*. Unresolved *aṟu* is matched on compounding productivity alone in the primary exact-frequency run; a declared sensitivity assigns it the direct Sangam written-form count of `அறு` (23) while keeping its missing Lexicon status visible.

| Mode and template set | Templates | Parpola hits | Expected hits (sign-joint) | Ratio (sign-joint) | Bootstrap 95% CI | Random-key p (sign-joint) | Slot-joint ratio (p) |
|---|---:|---:|---:|---:|---|---:|---|
| Exact freq + prod: primary blind (T0s, K=50) | 38 | 9 | 5.19 | 1.73 | 0.84–2.60 | 0.1037 | 1.84 (0.0704) |
| Exact freq + prod (direct *aṟu* count): blind (T0s, K=50) | 38 | 9 | 5.12 | 1.76 | 0.87–2.67 | 0.0965 | 1.86 (0.0601) |
| Productivity-only: primary blind (T0s, K=50) | 38 | 9 | 5.18 | 1.74 | 0.92–2.62 | 0.0821 | 1.65 (0.0837) |
| Exact freq + prod: practised tolerance T1s (K=50) | 38 | 11 | 6.68 | 1.65 | 0.91–2.34 | 0.0943 | 1.80 (0.0491) |
| Exact freq + prod: pools K=25 | 38 | 9 | 5.69 | 1.58 | 0.79–2.36 | 0.1320 | 1.58 (0.1223) |
| Exact freq + prod: pools K=100 | 38 | 9 | 4.15 | 2.17 | 1.07–3.31 | 0.0474 | 2.42 (0.0206) |
| Exact freq + prod: first member only (direction a) | 38 | 8 | 3.64 | 2.20 | 1.00–3.47 | 0.0474 | 2.34 (0.0321) |
| Exact freq + prod: without *mīṉ* and *muruku* | 26 | 8 | 4.37 | 1.83 | 0.91–2.78 | 0.0891 | 1.89 (0.0683) |
| Exact freq + prod: without `BULLHEAD` | 26 | 4 | 2.61 | 1.53 | 0.38–2.87 | 0.2815 | 1.53 (0.2694) |
| Exact freq + prod: gapped shared-member (shape S) | 24 | 22 | 19.30 | 1.14 | 1.04–1.26 | 0.1412 | 1.15 (0.1061) |
| Exact freq + prod: Parpola's published pairs | 12 | 7 | 1.51 | 4.64 | 2.25–7.88 | 0.0011 | 5.10 (0.0002) |
| Productivity-only: Parpola's published pairs | 12 | 7 | 1.47 | 4.77 | 2.31–8.84 | 0.0001 | 4.71 (0.0003) |

All bootstrap intervals are computed over templates from marginal expected rates (5.13 for exact freq + prod, marginal ratio 1.75, leave-one-out 1.60 to 1.88; 5.16 for productivity-only, marginal ratio 1.74, leave-one-out 1.59 to 1.91). Unifying each sign into one consistent replacement word across first and second positions increases the variance of random-key hit counts compared with independent slot draws, raising the random-key probability from 0.0704 (slot-keyed) to 0.1037 (sign-level).

Recomputing the 21 October base-rate searches with exact written-form counts confirms that the prefix-count defect did not drive those findings either. Under `exact_freq_prod` (`T0s`, `K = 50`), the *veḷ* interlock (I1) occurs in 28.8% of 2,500 replacement pairs (95% bootstrap interval 22.8% to 35.2%; 48.9% under `T1s`), and the four-link conjunction (`I1`, `I2`, `I4`, `I5`) holds in 0.40% of 10,000 draws (95% Wilson interval 0.29% to 0.54%; 2.17% under `T1s`). Under `prod_only`, I1 occurs in 33.7% of pairs (61.4% under `T1s`) and the four-link network in 0.62% of draws (2.69% under `T1s`).

## Experiment A2: Re-extracted Winslow sensitivity

We evaluated the 24 October re-extracted Winslow table (`data/raw/2026-10-24-lexical-extraction-extension/run-v1/winslow-entries.jsonl`, 69,310 records) under two strictly separated boundary layers: raw Winslow guarded boundaries (`winslow_guarded_members`, 18,421 two-member compounds, independent of the *Tamil Lexicon*) and *Tamil Lexicon*-assisted boundaries (`members`, 25,653 two-member compounds, a cross-dictionary-dependent sensitivity that cannot be treated as independent cross-dictionary agreement).

| Winslow boundary layer and test | Matching | Templates | Hits | Expected (sign-joint) | Ratio (sign-joint) | Bootstrap 95% CI | Random-key p |
|---|---|---:|---:|---:|---:|---|---:|
| Raw guarded (18,421 compounds): blind T0s | Exact freq + prod | 38 | 6 | 2.67 | 2.25 | 0.79–3.79 | 0.0683 |
| Raw guarded: blind T0s | Productivity-only | 38 | 6 | 2.39 | 2.51 | 0.98–4.13 | 0.0443 |
| Raw guarded: blind without `BULLHEAD` | Exact freq + prod | 26 | 1 | 1.41 | 0.71 | 0.00–2.31 | 0.7269 |
| Raw guarded: published pairs | Exact freq + prod | 12 | 3 | 0.66 | 4.52 | 1.04–9.08 | 0.0328 |
| Lexicon-assisted (25,653 compounds): blind T0s | Exact freq + prod | 38 | 7 | 3.19 | 2.20 | 0.91–3.49 | 0.0588 |
| Lexicon-assisted: blind T0s | Productivity-only | 38 | 7 | 2.81 | 2.49 | 1.06–3.90 | 0.0323 |
| Lexicon-assisted: blind without `BULLHEAD` | Exact freq + prod | 26 | 2 | 1.66 | 1.20 | 0.00–2.96 | 0.4837 |
| Lexicon-assisted: published pairs | Exact freq + prod | 12 | 3 | 0.84 | 3.57 | 0.89–7.12 | 0.0560 |

Two patterns stand out in [winslow_reextracted.json](results-v1/winslow_reextracted.json). First, nearly every blind hit in Winslow belongs to `BULLHEAD` (*āvu*/*āṉ*): five of the six raw-guarded hits (`T01`, `T05`, `T11`, `T29`, `T36`) and five of the seven Lexicon-assisted hits use `BULLHEAD`, while the remaining 26 blind pairs yield only 1 hit in raw Winslow (ratio 0.71, p = 0.7269) and 2 hits in Lexicon-assisted Winslow (ratio 1.20, p = 0.4837). Second, on the 2010 base-rate network, `A(muruku)` remains 0 in both boundary layers (the grammatical guard removes the false *ja-mīṉ* split of *jamīṉ*, reducing raw `B(mīṉ)` from 29 to 28, while Lexicon-assisted boundaries raise `B(mīṉ)` to 39 and `B(kaṭavuḷ)` to 5). In both layers, only two of Parpola's five interlocks (`I2` *vaṭa-mīṉ* and `I4` *aṟu-mīṉ*) hold, the I1 null rate remains 0.0%, and random words match both surviving links in 3.85% of draws under raw guarded boundaries (2.33% productivity-only) and 7.17% under Lexicon-assisted boundaries (5.85% productivity-only).

## Experiment B: Sanskrit cross-language control

From Cologne Monier-Williams (`mw.txt`, 286,525 `<L>` blocks, 112,183 main `<e>3` compound entries), the primary parser extracts 101,164 unique two-member compounds (87,281 via explicit em-dash `—`, 13,606 via vowel-coalescence `<srs/>`, and 277 via `—˚` plus `<srs/>`) and 35,694 deduplicated simplex nominal candidates (`<e>1`/`<e>2`). Adding nominal hyphenated `<e>3` entries without derivative suffixes adds 6,216 compounds (107,380 total) and barely moves any ratio.

| Sanskrit map and test | Templates | Hits | Expected (sign-joint) | Ratio (sign-joint) | Bootstrap 95% CI | Random-key p (sign-joint) | Slot-joint ratio (p) |
|---|---:|---:|---:|---:|---|---:|---|
| Primary single-word (`rekhā`): blind T0s, K=50 | 38 | 6 | 1.31 | 4.59 | 1.78–8.94 | 0.0020 | 3.09 (0.0104) |
| Primary single-word: blind T1s, K=50 | 38 | 6 | 1.44 | 4.15 | 1.70–8.20 | 0.0038 | 2.87 (0.0117) |
| Primary single-word: blind K=25 / K=100 | 38 | 6 | 1.66 / 1.05 | 3.61 / 5.73 | 1.33–7.48 / 2.04–10.65 | 0.0041 / 0.0008 | 2.74 / 3.73 |
| Primary single-word: without `BULLHEAD` | 26 | 5 | 1.01 | 4.94 | 1.56–11.98 | 0.0031 | 3.17 (0.0125) |
| Primary single-word: published pairs (T0s, K=50) | 12 | 1 | 0.49 | 2.04 | 0.00–3.00 | 0.4205 | 1.66 (0.5094) |
| Multiplicity-matched (24 words, `rekhā`): blind T0s, K=50 | 38 | 8 | 2.04 | 3.93 | 1.75–7.28 | 0.0005 | 2.67 (0.0032) |
| Multiplicity-matched: blind T1s, K=50 | 38 | 8 | 2.23 | 3.58 | 1.64–6.66 | 0.0012 | 2.53 (0.0054) |
| Multiplicity-matched: without `BULLHEAD` | 26 | 5 | 1.38 | 3.62 | 1.01–8.71 | 0.0090 | 2.25 (0.0410) |
| Multiplicity-matched: published pairs (T0s, K=50) | 12 | 2 | 0.56 | 3.59 | 0.00–6.39 | 0.0876 | 2.89 (0.1247) |
| Sensitivity `TWOLONG=antara` (single-word): blind T0s | 38 | 7 | 2.04 | 3.43 | 1.35–6.36 | 0.0054 | 2.40 (0.0158) |
| Sensitivity `TWOLONG=antara` (multiplicity-matched): blind T0s | 38 | 9 | 2.90 | 3.11 | 1.51–5.36 | 0.0013 | 2.19 (0.0095) |
| Sensitivity MW + hyphenated `<e>3` (single / mult.): blind T0s | 38 | 6 / 8 | 1.28 / 2.05 | 4.69 / 3.91 | 1.75–8.98 / 1.79–7.18 | 0.0022 / 0.0004 | 3.17 / 2.67 |

Inspection of the local compound detail file (`data/raw/2026-11-22-rebus-repaired/results-v1/sanskrit-control-detail.json`) shows why Sanskrit achieves 3.1 to 4.6 times the random-key rate on these 38 sign pairs. Five of the six primary hits are literal semantic combinations of basic concrete words and numerals: `T09` (*dvi-ṣaṣ* "twice six"), `T11` (*go-yuga* "yoke of oxen"), `T13` (*dvi-saptan* "twice seven"), `T14` (*dvy-akṣa* "two-eyed"), and `T32` (*jala-rekhā* "line on water"). The sixth, `T21` (*matsya-jāla* "fish-net" for fish plus *jala* "water"), is a vowel-length homophone match of the same kind that produces Tamil hits such as *veḷ-ḷ-āṉai* ("white elephant" for *veḷ* plus *āṉ* "cow"). The multiplicity-matched map adds two numeral-plus-bull compounds, `T12` (*sapta-vṛṣa*) and `T29` (*ṣaḍ-vṛṣa*), and the *antara* sensitivity adds `T03` (*dvy-antara*) and `T27` (*ekāntara*). On the 12 published pairs, Sanskrit hits only `P05` (*jalākṣī* / *jālākṣa*) and, in the multiplicity-matched map, `P12` (*eka-vṛṣa*).

Two methodological observations follow from comparing the Tamil and Sanskrit controls. First, matching random words on marginal compounding productivity alone does not control for **mutual semantic combinability**: basic vocabulary items (small numerals, cattle, eyes, water, yokes) form compounds with each other at several times the rate of random dictionary nouns that happen to have similar total compound counts with unrelated words. Second, because *Compounds* anchors lookups on `T1s` stems before checking `T0s` forms, both Tamil (*āṉ* matching *-āṉai*, *veḷ* matching *-vēḷai*) and Sanskrit (*akṣi* matching *-akṣa*, *dvi* sharing the *T1s* stem `dv` with *dvā*) gain hits through stem truncation and vowel-length collapse. Even excluding the single vowel-length coincidence (*matsya-jāla*), Sanskrit still yields five literal compounds out of 38 blind pairs (ratio 3.8 against 1.31 expected). Neither the Tamil ratio (1.73) nor the Sanskrit ratio (3.11–4.59) is evidence for the language of the Indus script; rather, the Sanskrit result proves that a 2x–4.6x blind-pair ratio arises naturally from basic-vocabulary compounding under this scoring procedure.

## Verification

An independent verification script ([verify.py](code/verify.py)), written without importing `run_tamil_repaired.py`, `run_sanskrit_control.py`, or `lexical_inputs.py`, passed all five checks ([verification-v1.json](verification-v1.json)):

1. Exact Sangam counts: 162,436 letter-and-mark tokens (162,399 raw-block tokens), *kā* = 9, *ā* = 24, *aṟu* = 23, *aṟṟu* = 8.
2. Madras *Tamil Lexicon*: 0 exact one-member records for *aṟu*, 56,154 two-member compounds, 9 blind hits, 7 published hits.
3. Re-extracted Winslow: 18,421 raw-guarded compounds (6 blind hits, 3 published hits, *jamīṉ* suppressed) and 25,653 Lexicon-assisted compounds (7 blind hits, 3 published hits).
4. Monier-Williams: all six unit checks on `—˚ + <srs/>`, `<srs/>`, and Sanskrit sandhi reversal pass; 101,164 two-member compounds reproduced exactly; blind and published hit counts reproduced for all four Sanskrit mappings.
5. Synthetic joint-key calibration: a planted key scores ratio 4.98 (p = 0.0) with sign-level variance exceeding independent-template variance (3.02 vs. 2.72); 20 unplanted keys average ratio 1.28 and reject below 0.05 in 5% of cases.

## Commands and outputs

Run from repository root with Python 3.13 and NumPy 2.2.6:

```text
python experiments/2026-11-22-rebus-repaired/code/run_tamil_repaired.py
python experiments/2026-11-22-rebus-repaired/code/run_sanskrit_control.py
python experiments/2026-11-22-rebus-repaired/code/verify.py
```

Tracked outputs: [PROTOCOL.md](PROTOCOL.md), [results-v1/tamil_repaired.json](results-v1/tamil_repaired.json), [results-v1/winslow_reextracted.json](results-v1/winslow_reextracted.json), [results-v1/sanskrit_control.json](results-v1/sanskrit_control.json), [verification-v1.json](verification-v1.json). Local detail files on `D:\projects\indus_valley_script\data\raw\2026-11-22-rebus-repaired\results-v1\` (reached via `data/raw/2026-11-22-rebus-repaired/results-v1/`): `tamil-repaired-detail.json`, `winslow-reextracted-detail.json`, `sanskrit-control-detail.json`.

## Boldest reading and the test that decides it

Conjecture C-0014 holds in full for the blind-template test: Parpola's interlocking Dravidian readings measure the density of the Madras *Tamil Lexicon*, the basic-vocabulary combinability of concrete picture nouns, and post-hoc pair selection rather than Dravidian lexical specificity of the Indus script. Repairing the Tamil frequency proxy and lookup fallback leaves the blind-pair ratio at 1.73 (p = 0.1037 under sign-level dependent keys), while standard Sanskrit words for the exact same 16 concrete pictures reach ratios of 3.11 to 4.59 (p = 0.0005 to 0.0054) on the same 38 unpublished pairs. Parpola's 12 published pairs show the opposite asymmetry (7 of 12 in Tamil, ratio 4.64, against 1 or 2 of 12 in Sanskrit), reflecting selection of sign pairs for Tamil compound matches.

The test that would still separate genuine Dravidian rebus structure from basic-vocabulary compounding requires two changes together: expanding the sign inventory to Parpola's full 1994 concrete-picture list (after specialist sign-code adjudication) and replacing productivity-matched random dictionary nouns with **domain-matched basic-vocabulary controls** across at least three candidate language families (Dravidian, Indo-Aryan, and Sumerian or Munda), scoring only compounds attested in early literary corpora (such as the Sangam corpus and Vedic texts) rather than nineteenth- and twentieth-century encyclopaedic lexicons. If Dravidian outperforms every control language on an enlarged blind inventory using early-corpus attestations and exact sense-reviewed compounds, rebus evidence would become discriminating; if non-Dravidian control languages continue to match or exceed Dravidian, lexical compound interlocks cannot identify the language of the Indus script.
