# Protocol: REBUS-REPAIRED-2026-11-22

Date: 22 November 2026. Addresses GitHub Issue #18 (Q-0039) and the repairs specified in Section 7 of `experiments/2026-10-22-field-novelty-review/REPORT.md` and `experiments/2026-10-22-reading-eval-readiness/REPORT.md`.

This protocol is written before any repaired Tamil rerun, re-extracted Winslow scoring, or Monier-Williams compound lookup is executed. It reads no new Indus confirmation cohort: all templates are the frozen pairs of `experiments/2026-10-22-rebus-blind-templates/templates-v1.json` (SHA-256 `8ddc7d2a...`, 38 blind adjacent pairs, 24 gapped pairs, and 12 published pairs). Every earlier frozen endpoint remains untouched.

## 1. Purpose and design

The blind-template study of 22 October 2026 found 9 attested *Tamil Lexicon* compounds among 38 adjacent sign pairs not published by Asko Parpola, against 4.97 expected for matched random words (ratio 1.81, 95% bootstrap interval 0.93 to 2.72; 6.7% of random keys reached 9 hits). Three questions remained open:

1. **Frequency-proxy and fallback repair (Experiment A1).** The 22 October scorer counted every Sangam token beginning with a word's initial letter string after stripping vowel signs, inflating single-syllable words (*kā* 22,287 instead of 9 exact tokens; *ā* 4,458 instead of 24), and resolved *aṟu* to *aṟṟu* through a length- and gemination-free fallback. Does repairing these defects change the Tamil blind-template ratio or the joint random-key p-value?
2. **Re-extracted Winslow cross-dictionary test (Experiment A2).** The 24 October re-extraction (`data/raw/2026-10-24-lexical-extraction-extension/run-v1/winslow-entries.jsonl`) preserves raw Winslow boundaries after a grammatical guard (`winslow_guarded_members`, 18,421 two-member compounds) separately from Tamil Lexicon-assisted boundaries (`members`, 25,653 two-member compounds). How do the 38 blind pairs, 12 published pairs, and the 2010 interlock network behave on each boundary layer?
3. **Sanskrit cross-language control (Experiment B).** On the exact same 38 blind sign pairs and 12 published pairs, if Parpola's 16 concrete pictures receive their standard Sanskrit words instead of Tamil words and are scored in Monier-Williams against productivity-matched random Sanskrit words, do they produce a similar excess (~1.8x) or sit near 1.0? A Sanskrit ratio near the repaired Tamil ratio shows that the modest excess on blind pairs comes from basic picture vocabulary and compound-dictionary density, confirming conjecture C-0014 in full. A Sanskrit ratio near 1.0 while the repaired Tamil ratio stays well above 1.5 with low random-key probability would distinguish Dravidian lexical fit from general picture compounding.

## 2. Experiment A: Repaired Tamil and Winslow reruns

### 2.1 Inputs

- Frozen templates and 16-sign identifications: `experiments/2026-10-22-rebus-blind-templates/templates-v1.json` (38 blind pairs `T01`–`T38`, 24 gapped pairs `G01`–`G24`, 12 published pairs `P01`–`P12`).
- Madras *Tamil Lexicon*: `data/raw/2026-10-21-rebus-base-rate/derived-v1/tamil-lex-entries.jsonl` (117,803 records; 56,154 two-member compounds).
- *Dravidian Etymological Dictionary* (DEDR): `data/raw/2026-10-21-rebus-base-rate/derived-v1/dedr-entries.jsonl`.
- Sangam corpus: 17 Project Madurai HTML files in `data/raw/2026-10-21-rebus-base-rate/sources-v1/sangam/pmuni*.html` (162,399 Tamil tokens).
- Re-extracted Winslow dictionary: `data/raw/2026-10-24-lexical-extraction-extension/run-v1/winslow-entries.jsonl` (69,310 records).
- Exact lookup and written-form counter: `experiments/2026-10-22-reading-eval-readiness/code/lexical_inputs.py` (`FormCounts`, `tamil_tokens`, `Lexicon`, `form_key`, `roman_key`).

### 2.2 Repaired frequency counting and lexical lookup

1. Strip HTML tags from each Sangam file (`re.sub(r"<[^>]+>", " ", text)`) and tokenize with `lexical_inputs.tamil_tokens`, preserving Tamil vowel marks and NFC normalization. Count exact complete written-form occurrences with `FormCounts`.
2. Resolve every proposed Tamil word and every candidate replacement noun strictly through `lexical_inputs.Lexicon.resolve(word, counts)` with no phonological fallback.
   - Where one or more exact one-member entries match (`exact` or `ambiguous` homographs sharing the written form), use the sum of exact written-form counts across their distinct NFC Tamil headwords (`sum(form_counts.values())`), without choosing a sense.
   - Where no exact one-member entry exists (`missing`, which affects *aṟu* in the *Tamil Lexicon*), do not fall back to another headword (*aṟṟu*). In the primary frequency-matched pool, match unresolved words on compounding productivity alone so neither an arbitrary zero nor a substituted headword distorts their pool. As a declared sensitivity, also compute a variant using the exact Sangam written-form count of `அறு` directly while flagging the missing one-member Lexicon record.
3. Apply the same exact written-form counter to all native one-member noun replacement candidates (DEDR-attested under `T0s`, non-verb, non-starred, `pos == "n"`, deduplicated by T1 anchor stem as in `run_interlocks.py`).

### 2.3 Pool matching and dependent random-key draws

We run two matching rules across the Madras *Tamil Lexicon*:

- **Exact-frequency + productivity matching (`exact_freq_prod`, primary):** nearest `K = 50` candidates in standardized Euclidean distance on `(log1p(prod), log1p(freq))` for slot-specific pools, and on `(log1p(prod_first), log1p(prod_last), log1p(freq))` for unified sign-level pools.
- **Productivity-only matching (`prod_only`):** nearest `K = 50` candidates in standardized distance on `log1p(prod)` alone (slot-specific) or `(log1p(prod_first), log1p(prod_last))` (sign-level), removing Sangam frequency completely.

To preserve shared-sign dependencies across the 38 templates:

- **Sign-level joint random keys (primary null, 10,000 draws, seed `20261122`):** each of the 16 signs receives one replacement word per alternative form from its unified sign-level pool, and that same replacement word is used in every template where the sign appears, whether as first or second member.
- **Slot-keyed joint random keys (compatibility null, 10,000 draws):** matches the exact slot-keyed draw structure of `2026-10-22-rebus-blind-templates/code/run_templates.py` so the effect of repairing the frequency proxy is isolated cleanly from the move to unified sign-level keys.

For every pool specification we report: Parpola hits, exact/Monte Carlo marginal expected hits, joint-key mean expected hits, hit-rate ratio with 95% bootstrap interval over templates (2,000 resamples), leave-one-out min/max ratio, and exact random-key probability `P(joint_hits >= parpola_hits)`. Sensitivities: `K = 25`, `K = 100`, practised tolerance `T1s`, direction `a` (first member only), without *mīṉ* and *muruku* (26 templates), without `BULLHEAD` (26 templates), gapped shape S (24 templates), and published pairs (12 templates).

We also recompute the *veḷ* interlock (I1) and 4-link network null from `2026-10-21-rebus-base-rate` under exact written-form counts and productivity-only matching to confirm whether repairing the frequency proxy alters those base-rate figures.

### 2.4 Re-extracted Winslow sensitivity

We score the 38 blind pairs, 24 gapped pairs, 12 published pairs, and the 2010 I1/network searches on `winslow-entries.jsonl` under two strictly separated boundary fields:

1. **Raw Winslow guarded (`winslow_raw_guarded`):** compound members taken strictly from `winslow_guarded_members` (18,421 two-member compounds; zero boundaries borrowed from the *Tamil Lexicon*). This is the independent cross-dictionary test.
2. **Lexicon-assisted Winslow (`winslow_lexicon_assisted`):** compound members taken from `members` (25,653 two-member compounds, incorporating *Tamil Lexicon*-aligned boundaries where exact Tamil headwords uniquely match). This is reported solely as a boundary-recovery sensitivity and never counted as independent cross-dictionary agreement.

In both Winslow layers, candidate nouns are one-member non-verb, non-starred nouns attested in DEDR (`T0s`), with exact written-form Sangam counts and both `exact_freq_prod` and `prod_only` matching. Because Winslow's DSAL text encodes initial short *e* as ஏ, we record exact counts directly without silent substitution and treat `prod_only` as immune to that orthography quirk.

## 3. Experiment B: Deciding Sanskrit cross-language control

### 3.1 Frozen Sanskrit picture-to-word mapping

The following standard Sanskrit lexical nouns and numerals for Parpola's 16 concrete pictures are frozen here before any Monier-Williams compound lookup. Only `<e>1`/`<e>2` simplex headword spelling presence in `mw.txt` was verified prior to freezing; zero `<e>3` or `<e>4` compounds were inspected.

| Sign | Concrete picture | Tamil forms (n) | Primary map (1 word, IAST / SLP1) | Multiplicity-matched map (IAST / SLP1) |
|---|---|---|---|---|
| `FISH` | fish (plain) | *mīṉ* (1) | *matsya* (`matsya`) | *matsya* (`matsya`) |
| `ONE` | numeral one | *oru*, *oṉṟu* (2) | *eka* (`eka`) | *eka*, *ekaka* (`eka`, `ekaka`) |
| `TWO` | numeral two | *iru*, *iraṇṭu* (2) | *dvi* (`dvi`) | *dvi*, *dvā* (`dvi`, `dvA`) |
| `SIX` | numeral six | *aṟu* (1) | *ṣaṣ* (`zaz`) | *ṣaṣ* (`zaz`) |
| `SEVEN` | numeral seven | *eḻu* (1) | *saptan* (`saptan`) | *saptan* (`saptan`) |
| `FIG` | banyan fig tree | *vaṭam* (1) | *vaṭa* (`vawa`) | *vaṭa* (`vawa`) |
| `SPINDLE` | spindle | *katir* (1) | *tarku* (`tarku`) | *tarku* (`tarku`) |
| `CIRCLES` | intersecting circles (bangles, ear-rings) | *muruku* (1) | *valaya* (`valaya`) | *valaya* (`valaya`) |
| `SQUIRREL` | palm squirrel | *piḷḷai*, *aṇil* (2) | *kalandaka* (`kalandaka`) | *kalandaka*, *romaśī* (`kalandaka`, `romaSI`) |
| `TWOLONG` | two long vertical strokes | *veḷ* (1) | *rekhā* (`reKA`) | *rekhā* (`reKA`) |
| `CRAB` | crab | *kōḷ* (1) | *karkaṭa* (`karkawa`) | *karkaṭa* (`karkawa`) |
| `EYE` | eye | *kaṇ* (1) | *akṣi* (`akzi`) | *akṣi* (`akzi`) |
| `WATER` | water | *nīr* (1) | *jala* (`jala`) | *jala* (`jala`) |
| `HINDLEG` | hind leg of an ungulate | *tāḷ*, *tōḷ* (2) | *pāda* (`pAda`) | *pāda*, *jaṅghā* (`pAda`, `jaNGA`) |
| `BULLHEAD` | bull's head / cow | *ā*, *āṉ*, *āvu* (3) | *go* (`go`) | *go*, *vṛṣa*, *ukṣan* (`go`, `vfza`, `ukzan`) |
| `YOKE` | yoke-carrier | *kā*, *kāvu*, *kāvaṭi* (3) | *yuga* (`yuga`) | *yuga*, *dhur*, *vīvadha* (`yuga`, `Dur`, `vIvaDa`) |

Declared pre-frozen sensitivity **`twolong_antara`**: replaces *rekhā* ("stroke, line") with *antara* ("space between, interval", translating Parpola's pictorial reading *veḷi* of the two long strokes) on both the primary and multiplicity-matched maps.

We deliberately select *matsya* rather than *mīna* for `FISH` to avoid borrowing overlap with Tamil *mīṉ*. For `FIG`, *vaṭa* is the standard simplex Classical Sanskrit headword for the banyan (*Ficus indica*), whereas *nyagrodha* is analyzed by Monier-Williams as a compound (`nyac + rodha`).

### 3.2 Monier-Williams compound extraction and normalization

Source: Cologne Digital Sanskrit Lexicon `data/raw/2026-10-12-decipherment-claim-tests/mw/mw.txt` (SLP1 encoding, 286,525 `<L>` blocks).

1. **Two-member compounds:** scan all `<e>3` main compound entries (excluding sub-sense continuations `3A`/`3B`/`3C` and nested `<e>4` sub-compounds). Extract `(m1, m2)` as follows:
   - If the headword span `<s>...</s>` before `¦` contains `—˚` and `<srs/>`: remove `—˚` (print abbreviation inside the first member) and split at `<srs/>`.
   - Else if `<k2>` contains exactly one em-dash `—`: split `<k2>` on `—`. Strip accents (`/`, `^`, `\`), degree marks (`°`, `˚`), internal hyphens, and leading single-character sandhi connectors (`M-`, `m-`, `n-`, `r-`, `s-`) on `m2`.
   - Else if `<k2>` has no `—` and the headword span before `¦` contains exactly one `<srs/>`: split at `<srs/>` by reversing standard Sanskrit vowel coalescence (`A -> a+a`, `I -> i+i`, `U -> u+u`, `F -> f+f`, `e -> a+i`, `o -> a+u`, `E -> a+e`, `O -> a+o`, `ar -> a+f`), noting that under vowel-length-free normalization (`L`), every savarṇa/guṇa split (`A, I, U, e, o`) yields a unique normalized pair.
   - Deduplicate compounds by `(k1, m1, m2)` and require both cleaned members to have length at least 1.
   - As a sensitivity (`mw_plus_hyphen`), also include `<e>3` entries lacking `—` and `<srs/>` that have a single hyphen `-` in `<k2>` and are neither abstract suffixes (`tA`, `tva`, `maya`) nor `cvi`-verb entries (`<info verb=` or `√`).
2. **Simplex candidate pool:** unique `<k1>` headwords from `<e>1` and `<e>2` entries whose `<k2>` contains no `—`, with no `<info verb=` tag and at least one nominal gender code (`m`, `f`, or `n` in `<info lex="..."/>`), deduplicated by `T1s` anchor stem just as in the Tamil scorer.
3. **Symmetric Sanskrit normalization and sandhi:** convert SLP1 to IAST, segment with `rebus.seg_indic`, and apply the identical `rebus.normalise(..., ["L"])` (`T0s`, vowel length and gemination free — recalling from `2026-10-21-rebus-base-rate` that Old Indo-Aryan already exceeds Tamil's per-segment collision probability, so `T0s` requires only step `L`) and `rebus.stem` (`T1s`). Reverse general Sanskrit first-member compound sandhi symmetrically for every word (`skt_sandhi_bases`):
   - `-n` stem truncation: final `a`/`i` -> `+n` (`sapta-` < `saptan`, `rāja-` < `rājan`, `ukṣa-` < `ukṣan`).
   - `-s` stem visarga/sibilant sandhi: final `o` -> `as`, final `r` -> `s`, final `H`/`S`/`z` -> `s`.
   - Final stop voicing/retroflex/nasal assimilation: `w`/`q`/`R` -> `z`, `w`, `q`; `d` -> `t`, `g` -> `k`, `b` -> `p`, `j` -> `c`; `k`/`g` -> `c`; `M`/`n` -> `m`.
   - *Yaṇ* glide sandhi (Pāṇini 6.1.77): consonant + `y` -> consonant + `i` (`dvy-` < `dvi`), consonant + `v` -> consonant + `u`.
4. **Matching and null draws:** match each Sanskrit sign word to the nearest `K = 50` simplex candidates (with sensitivities `K = 25`, `K = 100`) on compounding productivity (`(log1p(prod_first), log1p(prod_last))` for unified sign-level pools and `log1p(prod)` for slot-specific pools). Score the exact same 38 blind pairs (`T01`–`T38`), 12 published pairs (`P01`–`P12`), and 24 gapped pairs (`G01`–`G24`) under `T0s` (primary) and `T1s` (sensitivity), with 10,000 sign-level dependent random-key draws (seed `20261122`).

### 3.3 Decision interpretation for C-0014

- **Primary comparison:** compare the Sanskrit blind-pair ratio (`T0s`, `K = 50`, sign-level joint keys) on the 38 blind pairs against the repaired Tamil blind-pair ratio (`T0s`, `K = 50`, exact written-form frequency + productivity and productivity-only).
- If the Sanskrit ratio on the 38 blind pairs is comparable to or exceeds the repaired Tamil ratio (specifically `ratio_Sanskrit >= 1.5` or `ratio_Tamil / ratio_Sanskrit <= 1.25`), the blind-pair excess is a property of basic picture nouns and compound-dictionary density rather than Dravidian specificity, supporting C-0014.
- If the repaired Tamil ratio remains >= 1.5 with `p_random_key < 0.05` while the Sanskrit ratio sits near 1.0 (`<= 1.2`) on both the primary and multiplicity-matched maps, that provides the first blind-pair evidence favoring Dravidian over Sanskrit on Parpola's 16 concrete pictures.

## 4. Verification plan

An independent script `code/verify.py` (without importing the main scorers) will verify:
1. Exact Sangam token totals (162,399) and exact counts for *kā* (9), *ā* (24), and unresolved *aṟu* (0 exact Lexicon one-member records).
2. Independent recomputation of Tamil compound counts, Parpola blind hits, replacement pools, and sign-level joint-key mean and p-value on a synthetic planted/unplanted benchmark and on the real tables.
3. Independent check of raw Winslow guarded vs Lexicon-assisted two-member compound counts (18,421 vs 25,653).
4. Independent check of Monier-Williams `<e>3` compound parsing (including `—`, `<srs/>`, and `—˚` + `<srs/>` cases), symmetric sandhi reversal, and a synthetic Sanskrit planted-key vs unplanted-key control.
