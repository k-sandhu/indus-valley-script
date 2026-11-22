# Quantitative chance calibration of Dravidian rebus interlocks in the Indus script

Complete working manuscript, 22 November 2026, prepared with AI research and writing assistance. Author names, affiliations, and a submission venue have not been assigned.

## Abstract

Asko Parpola's Dravidian hypothesis for the Indus script rests on interlocking rebus readings: signs identified pictorially receive Old Tamil words whose homophones form attested two-member compounds when the signs appear together in inscriptions. Critics have long argued qualitatively that rebus flexibility allows chance fits in any large lexicon, yet no published study has measured how often Parpola's specific interlocks arise for matched random words, how strongly they depend on the reference dictionary, or how his word assignments perform on sign pairs he did not select. We calibrate every stage of this argument quantitatively. First, across five lexical corpora, single homophones between picturable nouns and name-suitable meanings occur more often in the *Dravidian Etymological Dictionary* (2.31% of evaluable pairs) than in Turner's Indo-Aryan dictionary (1.50%) or the Sumerian ePSD2 (0.45%). Second, in the Madras *Tamil Lexicon* (56,154 two-member compounds), the shared-member search behind Parpola's *veḷ* reading (*Muruka-vēḷ* and *veṇ-mīṉ*) succeeds for 30.5% of matched random noun pairs under his stated tolerance (52.8% under his practised tolerance; 28.8% after repairing the Sangam frequency proxy), and his own anchor pair yields an irrelevant accidental interlock in *puḷi* ("sour"). By contrast, the full conjunction of the four 2010 interlocks that hold in the *Tamil Lexicon* arises in only 0.44% of random replacements (0.40% with exact written-form frequency matching), raising the odds of the reading by up to a factor of about 230 if only those five templates were examined. Third, in Miron Winslow's 1862 Tamil dictionary, *muruku* forms zero two-member compounds under both raw guarded parsing (18,421 compounds) and *Tamil Lexicon*-assisted parsing (25,653 compounds); neither *Muruka-vēḷ* nor *veṇ-mīṉ* is an entry, and the surviving two-link network arises in 3.85% of random draws (raw guarded) or 7.17% (Lexicon-assisted). Fourth, phylogenetic reconstruction and a dictionary-wide sound-correspondence count across the *Dravidian Etymological Dictionary* show that northern Dravidian star words (*bīnkō*, *bínḍke*) begin with the regular reflex of Tamil *v-* (50 of 55 entries) rather than Tamil *m-* (2 of 88, 0 of 6 before long front vowels), confining the bare *mīn* "fish / star" homophone primarily to South Dravidian. Fifth, on 38 recurring Indus sign pairs that Parpola never published, his Dravidian words yield 9 *Tamil Lexicon* compounds against 5.19 expected across 10,000 sign-level dependent random keys after repairing the Sangam prefix-counting defect and removing the silent *aṟu*-to-*aṟṟu* fallback (ratio 1.73, 95% bootstrap interval 0.84 to 2.60, p = 0.1037; productivity-only ratio 1.74, p = 0.0821), whereas his 12 published pairs succeed 7 times against 1.51 expected (ratio 4.64, p = 0.0011). Finally, a pre-frozen Sanskrit cross-language control assigns standard Sanskrit nouns to Parpola's 16 concrete pictures and scores the exact same 38 blind pairs in Cologne Monier-Williams (101,164 two-member compounds): Sanskrit achieves 6 hits against 1.31 expected on a single-word map (ratio 4.59, p = 0.0020) and 8 hits against 2.04 expected when matching Parpola's exact number of alternative forms per sign (ratio 3.93, p = 0.0005), while scoring only 1 or 2 of 12 on Parpola's published pairs. Basic-vocabulary picture compounding and tolerant lexical matching therefore generate 2x to 4.6x excesses over productivity-matched random nouns without any Dravidian linguistic specificity.

## 1. Introduction

Among linguistic proposals for the undeciphered Indus script (c. 2600–1900 BCE), Asko Parpola's Dravidian rebus framework is the most detailed and sustained (Parpola 1994, 1997, 2005, 2008, 2009, 2010). Rather than assigning arbitrary phonetic values to signs, Parpola identifies concrete objects depicted by signs, takes their reconstructed Proto-Dravidian or Old Tamil words, and transfers those words by homophony to abstract meanings appropriate for personal names, titles, and divine epithets. The central pillar is the plain fish sign, read through the Tamil homophony of *mīṉ* ("fish") and *mīṉ* ("star"). Because single puns are easy to criticize, Parpola builds his evidential case on interlocking compounds: when two concrete signs recur adjacent to one another in Indus inscriptions, their proposed Dravidian words combine into attested Old Tamil or *Tamil Lexicon* compounds, such as *aṟu-mīṉ* ("six stars", Pleiades), *eḻu-mīṉ* ("seven stars", Ursa Major), *vaṭa-mīṉ* ("north star", via *vaṭam* "banyan fig"), and the cross-linked pair *Muruka-vēḷ* / *veṇ-mīṉ* ("white star", Venus), which supplies the reading *veḷ* for the two-long-strokes sign (Parpola 2010).

Critics of rebus decipherments have long argued that homophone freedom and large multi-dialect dictionaries make apparent interlocks easy to construct by chance. Farmer, Sproat, and Witzel (2004, pp. 20 and 34) state that rebus procedures allow "half-convincing pseudo-decipherments" of any sign inventory into any language, without measuring a chance rate. In adjacent statistical work on phonetic keys, Raghavendra (2026) demonstrates on a constructed emblem system that loose dictionary coverage fails to distinguish language from non-language, and our own key-calibration study (Paper 006) shows that a published Sanskrit consonant-skeleton key sits only 1.2 to 2.4 standard deviations above rearrangements of its own values while a correct synthetic key stands 27 to 72 standard deviations clear. Public computational work has also begun testing chance baselines for Tamil compounds (Daniel Bourdeau's Cyphersolver repository, inspected at commit `1c736459`, 1 October 2026). What has been missing is a controlled, reproducible calibration of Parpola's exact rebus procedure across four empirical axes: (1) how often his individual interlocks and his full 2010 network occur for matched random Tamil words, (2) whether those interlocks survive in an independent nineteenth-century Tamil dictionary, (3) whether his word assignments predict compound formation on recurring Indus sign pairs he never published, and (4) whether an unrelated language's standard nouns for the exact same concrete pictures achieve a comparable compound rate on those unselected sign pairs.

This manuscript brings together six dated computational studies and a dedicated repair package (21 October to 22 November 2026). All shared assumptions, lexical tolerances, and protocol histories are collected in Section 2 and in [methods.md](methods.md). We retain every frozen endpoint unchanged, including both results that favor Parpola's case (the 0.44% chance rate of his four-link network in the *Tamil Lexicon*) and earlier implementation defects discovered during audit (the Sangam prefix-counting proxy and phonological fallback, both repaired in Section 5). We then report the deciding Sanskrit cross-language control (Section 6) and a pre-submission checklist for Dravidianist and Sanskritist review (Section 8).

## 2. Data, lexical rules, and shared assumptions

Every analysis in this paper evaluates lexical and statistical properties of published word assignments and corpora; none assigns authenticated phonetic values or translations to Indus signs.

### 2.1 Lexical and inscription sources

The inscription pairs come from the Lipi digital export of the Indus corpus (5,680 catalogued faces), accessed through the repository's shared discovery-and-confirmation split loader (`bench.shots`, split `d1d1b920`). Because the 1994 edition of Parpola's *Deciphering the Indus Script* was not held with clear rights, the 16 concrete sign identifications were extracted from five openly accessible papers that restate his 1994 readings: Parpola (1997, 2005, 2008, 2009, 2010). Sign codes in the Interactive Corpus of Indus Texts (ICIT) numbering were fixed directly from the 45 Corpus of Indus Seals and Inscriptions (CISI) objects Parpola cites by catalogue number, plus the printed glyph of the "bull's head" (the "jar" sign, ICIT 740) in Parpola (1997).

Six dictionaries and wordlists supply the lexical tests:

1. **Madras *Tamil Lexicon*** (University of Madras, 1924–1936; Digital Dictionaries of South Asia [DSAL] edition): 4,400 query pages, 117,803 parsed entries, and 56,154 two-member compounds.
2. **Winslow's Tamil dictionary** (Miron Winslow, 1862; DSAL edition): 978 pages and 69,310 parsed entries. We evaluate both the initial 22 October extraction (18,426 two-member compounds) and the 24 October re-extraction, which keeps raw Winslow boundaries after a grammatical guard (`winslow_guarded_members`, 18,421 two-member compounds) strictly separate from *Tamil Lexicon*-assisted boundaries (`members`, 25,653 two-member compounds).
3. ***Dravidian Etymological Dictionary*** (DEDR; Burrow and Emeneau, 1984; DSAL edition): 514 pages and 5,623 cognate entries.
4. **Cross-linguistic homophone lexicons**: Turner's *Comparative Dictionary of the Indo-Aryan Languages* (CDIAL, DSAL edition, 15,418 entries), the Electronic Pennsylvania Sumerian Dictionary (ePSD2 from Oracc, 7,875 readable common lemmas), Rau's (2019) Munda cognate sets (112 Santali, Mundari, or Ho lexemes), and Backstrom and Radloff's (1992) Burushaski wordlist via Lexibank (204 concepts).
5. **Monier-Williams Sanskrit-English Dictionary** (Monier-Williams, 1899; Cologne `csl-orig` `mw.txt`, SLP1 encoding): 286,525 `<L>` blocks, from which our primary parser extracts 101,164 unique two-member `<e>3` compounds (87,281 via explicit em-dash `—`, 13,606 via vowel-coalescence `<srs/>`, and 277 via `—˚` plus `<srs/>`) and 35,694 deduplicated simplex nominal candidates (`<e>1`/`<e>2`).
6. **Sangam corpus and concept lists**: 17 Project Madurai Old Tamil HTML texts (162,436 Tamil letter-and-mark tokens via `lexical_inputs.tamil_tokens`; 162,399 raw-block tokens), Concepticon 3.4.0, and the Brysbaert concreteness norms in NoRaRe 1.1 (yielding 751 concrete picturable concepts and 436 name-suitable meanings).

### 2.2 Formalizing Parpola's homophone and compound tolerances

Parpola (2010, pp. 14–28) accepts homophones that agree when vowel length and consonant gemination vary, requires attestation across at least two Dravidian subgroups, and permits Old Tamil or *Tamil Lexicon* compounds. We encode two tolerances:

- **Stated tolerance (`T0s`)**: vowel length and gemination are collapsed (merge step `L`), together with standard first-member compound sandhi reversal (*veṇ-* from *veḷ*, *vaṭa-* from *vaṭam*, *muruka-* from *murukaṉ*). For cross-linguistic single-homophone comparisons, additional phonetic mergers are applied only to languages whose per-segment collision probability falls below Tamil's under `T0` (0.076); Old Indo-Aryan (0.119) and Sumerian (0.081) already exceed Tamil and need no extra merges.
- **Practised tolerance (`T1s`)**: adds the stem truncation Parpola uses in practice, dropping a final *-m* after a vowel and then a final vowel whenever at least two segments remain (*vaṭam* ~ *vaṭa*, *veḷ* ~ *veḷi*, *muruku* ~ *muruka-*).

In the compound index (`Compounds`), two-member entries are anchored by their `T1s` stems so that morphological variants of an anchor word (*muruku* / *murukaṉ*) enter the same compound set, while the partner member is checked under `T0s` (primary) or `T1s` (sensitivity). The exact same `T0s`, `T1s`, and anchor-indexing architecture is applied symmetrically to Monier-Williams Sanskrit compounds in Section 6, paired with general Sanskrit compound-boundary sandhi reversal (*-n* truncation as in *sapta-* from *saptan*, visarga/*-s* sandhi, final stop voicing and retroflex assimilation as in *ṣaṭ-/*ṣaḍ-/*ṣaṇ-* from *ṣaṣ*, and *yaṇ* glide sandhi as in *dvy-* from *dvi*).

### 2.3 Replacement pools and dependent random keys

To measure chance rates without penalizing rare or unproductive words, each real Tamil word is replaced by the nearest `K = 50` native one-member nouns (attested in DEDR under `T0s`, excluding verbs and starred loans) in standardized Euclidean distance on log-transformed compounding productivity and Sangam frequency (with sensitivities `K = 25`, `K = 100`, and productivity-only matching without Sangam frequency). Because multiple Indus sign pairs share the same high-frequency signs (notably `BULLHEAD`, `TWOLONG`, `TWO`, and `FISH`), evaluating the 38 blind templates requires **sign-level dependent random keys**: in each of 10,000 draws, every sign receives one consistent replacement word per alternative form across all templates where that sign appears, whether as first or second member. In Section 5 we report both unified sign-level keys and the slot-keyed compatibility draws of the 22 October run.

## 3. Linguistic background: antiquity of the *mīn* "fish / star" homophone

Before calibrating compound interlocks, we checked whether the foundational pun *mīn* ("fish") ~ *mīn* ("star") reconstructs to Proto-Dravidian at the Mature Harappan horizon. Kolipakam and colleagues (2018) date the root of their Bayesian maximum clade credibility (MCC) Dravidian tree to 4,433 years BP (c. 2400 BCE). Coding 16 senses of 9 words needed by Parpola's readings across the 20 tip languages of that tree from DEDR, we reconstructed ancestral states under symmetric maximum-likelihood Markov (Mk1) models and parsimony (`2026-10-21-dravidian-root-meanings`).

In DEDR, "fish" (*mīṉ*, entry 4885) reconstructs to the Proto-Dravidian root with probability 1.000. "Star" sits in a separate entry, 4876 (*miṉ* "to flash, glitter"), attested with a star sense in South I (Tamil, Malayalam, Kota, Toda, Kannada), Gondi (South II), and Kurukh (*bīnkō*) and Malto (*bínḍke*) in North Dravidian. On the MCC tree, the star sense in entry 4876 reaches the root with Mk1 probability 0.524 (95% posterior-tree range 0.498 to 0.561; 89% above 0.5) and the North Dravidian node with probability 0.681, while parsimony places "star" absent at the root (requiring four changes). Restricting the coding to star words that actually share the bare *mīn* form needed for the homophone drops the root probability to 0.412 and the North node to 0.220. Across the 14 testable meanings Parpola needs, 7 exceed root probability 0.5 against a reference mean of 0.54 drawn from unproposed glosses of the same entries (p = 1/10,001), confirming that Parpola selected broadly attested roots (chiefly numerals, "white", and "shine") rather than idiosyncratic glosses.

A sharper phonological test targets the northern star witnesses. Kurukh *bīnkō* and Malto *bínḍke* both begin with *b-*, and DEDR closes entry 4876 with a cross-reference to entry 5396, Tamil *viṇ* "sky" (Malto *biṉye*). Kolichala (2016) argued on the INDOLOGY list that DEDR 4876 and 4885 are unrelated and linked the northern forms to *viṇ*, and Kobayashi (2020) notes that Kurukh *b-* regularly reflects Proto-Dravidian `*w-`. To quantify this correspondence exhaustively, we counted every DEDR entry having a Tamil initial *m-* or *v-* alongside a Kurukh or Malto reflex (`2026-10-21-north-b-correspondence`, 63 Tamil *m-* entries and 44 Tamil *v-* entries).

| Tamil initial (DEDR) | Northern *m-* | Northern *b-* | Northern *v-* | Other (corrected) |
|---|---:|---:|---:|---:|
| *m-* (excluding entry 4876) | **83** | **2** | 0 | 3 |
| *m-* before long front vowel (*ī, ē*) | **6** | **0** | 0 | 0 |
| *v-* | **2** | **50** | 0 | 3 |

Northern *b-* answers Tamil *v-* in 50 of 55 undoubted language units, whereas Tamil *m-* answers northern *m-* in 83 of 88 units. Outside entry 4876, only one entry in the entire dictionary shows Kurukh and Malto *b-* for Tamil *m-*: entry 4952 "crocodile" (Tamil *mutalai*, short back vowel, no nasal, compared by DEDR with Sanskrit *mācala-* / *musali-*). In the exact phonological setting of *mīn* (Tamil *m-* before a long front vowel), all 6 northern reflexes keep *m-*, including Malto *mínu* "fish" (4885). Malto thus keeps "fish" (*mínu*) and "star" (*bínḍke*) apart by their initial consonants, while its star word matches its sky word (*biṉye*, 5396). Removing the Kurukh and Malto star forms from entry 4876 lowers the Mk1 root probability of "star" to between 0.344 (coded absent) and 0.472 (coded missing); Gondi *mīnkō* still links South II to South I, leaving the bare fish–star homophone primarily a South Dravidian phenomenon.

## 4. Chance base rates of single homophones and the 2010 interlock network

### 4.1 Single-homophone base rates across lexicons

Testing 751 picturable noun concepts against 436 name-suitable meanings (`2026-10-21-rebus-base-rate`) shows that Dravidian supplies single homophones more readily than the other full dictionaries tested (Table 2).

| Lexicon | Attested lexemes | Picture / name concepts found | Rate, all words (95% CI) | One word per concept | Random-lexeme form collision | Rate under T1s |
|---|---:|---|---:|---:|---:|---:|
| Dravidian, DEDR (Tamil-headed) | 3,633 | 509 / 331 | **2.31%** (1.95–2.69) | 0.27% | 2.5 × 10⁻⁴ | 4.88% |
| Dravidian, DEDR word level | 11,102 | 410 / 227 | 0.29% (0.20–0.38) | 0.03% | 1.3 × 10⁻⁴ | |
| Indo-Aryan, CDIAL (OIA headwords) | 7,414 | 563 / 346 | **1.50%** (1.24–1.79) | 0.07% | 3.6 × 10⁻⁵ | 1.71% |
| Sumerian, ePSD2 | 5,843 | 374 / 177 | **0.45%** (0.32–0.61) | 0.12% | 2.1 × 10⁻⁴ | 0.68% |
| Munda, Rau (2019) | 112 | 20 / 9 | 0 / 180 pairs | 0 | 1.6 × 10⁻³ | |
| Burushaski, Backstrom (1992) | 204 | 65 / 40 | 1 / 2,600 pairs | 1 | 2.9 × 10⁻⁴ | |

The DEDR rate (2.31%) is 2.37 times the median of Indo-Aryan and Sumerian, driven by two structural factors. First, Tamil lexemes are short, so two random Tamil words collide seven times as often as two Old Indo-Aryan headwords. Second, drawing meanings from any cognate in a DEDR entry raises the rate eightfold over restricting each Tamil word to its own gloss (0.29%). Even controlling for synonym count (one word per concept), Dravidian still ranks highest (0.27% vs. 0.12% in Sumerian and 0.07% in Indo-Aryan). A single Dravidian homophone therefore carries less evidential weight than an equivalent match in Indo-Aryan or Sumerian.

### 4.2 Individual interlocks versus the four-link conjunction

We encoded all five interlocks of Parpola (2010) in the Madras *Tamil Lexicon* (Table 3). Four hold for his words: I1 *veḷ* (*Muruka-vēḷ* and *veṇ-mīṉ*), I2 banyan (*vaṭa-mīṉ*, *peru-mīṉ*), I4 numerals 3, 6, and 7 (*mu-m-mīṉ*, *aṟu-mīṉ*, *eḻu-mīṉ*), and I5 spindle (*katir-k-kaṭavuḷ*). I3 (*Muruka-p-piḷḷai*, drawn by Parpola from modern Jaffna names) is absent from the Lexicon.

| Interlock | Holds in *Tamil Lexicon* | Chance rate, 21 Oct (T0s / T1s) | Repaired exact-freq rate (T0s / T1s) | Productivity-only rate (T0s / T1s) | Max odds factor (T0s) |
|---|---|---|---|---|---:|
| I1 *Muruka-vēḷ* / *veṇ-mīṉ* (both replaced, K=50) | yes (*veḷ*, *puḷi*) | **30.5%** / 52.8% | **28.8%** / 48.9% | **33.7%** / 61.4% | 3.5 |
| I1 restricted to semantic subset sizes (2 and 55, post-outcome) | yes (with manual gloss fix) | 7.8% / 16.6% | | | 12.8 |
| I2 banyan ~ first member of X-*mīṉ* (random head) | yes (*vaṭa-mīṉ*, *peru-mīṉ*) | 25.1% / 40.9% (42.7% with *mīṉ*) | | | 4.0 |
| I3 squirrel ~ second member of *muruku*-X | no | 4.8% / 9.2% | | | |
| I4 numerals 3, 6, 7 with *mīṉ* (at least one / all three) | all three | 36% / 0 of 50 | | | 2.8 (for one) |
| I5 spindle ~ first member of X-*kaṭavuḷ* (random word) | yes (*katir-k-kaṭavuḷ*) | 10.8% / 21.1% (7.8% with *kaṭavuḷ*) | | | 9.2 |
| **Network I1 + I2 + I4 + I5 together (10,000 draws)** | **yes** | **0.44%** / 2.2% | **0.40%** / 2.17% | **0.62%** / 2.69% | **227–250** |

Two sharply contrasting facts emerge, and both belong in the record:

1. **Individual rebus links are cheap, and the *veḷ* interlock fails its kill criterion.** In the *Tamil Lexicon*, 7 two-member compounds begin with *muruku* and 82 end in *mīṉ*. Replacing both anchors with matched native nouns yields a shared member in 30.5% of 2,500 pairs (95% bootstrap interval 25.2% to 36.2%; 40.3% at K = 25; 28.7% at K = 100; 52.8% under `T1s`), far above our pre-registered 20% kill threshold. Repairing the Sangam frequency proxy moves the rate only slightly, to 28.8% (22.8% to 35.2%), and productivity-only matching gives 33.7%. Parpola's own anchor pair even generates a second, accidental interlock in *puḷi* ("sour"): *murukkam-puḷi* ("citric acid") and *puḷi-mīṉ* ("fish soured with tamarind"). Even when we emulate Parpola's narrower semantic filtering after the fact by restricting replacement compound sets to sizes 2 and 55 (adding *muruka-vēḷ*, whose Lexicon gloss is only a cross-reference), random pairs still interlock in 7.8% of draws (`T0s`) and 16.6% (`T1s`), limiting *veḷ* to an odds factor of at most 13. Moreover, an exploratory check of numerals 1 to 10 with *mīṉ* finds star compounds only for 3, 5, 6, and 7 (none for "two"), yet two strokes precede the fish sign in 77 of 102 confirmation seals in our fish-context study (`2026-10-20-fish-context`). Parpola removes that mismatch by reading two long strokes as *veḷ* ("white star"), the very reading whose lexical interlock fails here.
2. **The four-link conjunction is genuinely rare if no other templates were tried.** Under `T0s`, all four surviving links hold together in only **0.44%** of 10,000 random replacements (95% CI 0.33% to 0.59%; **0.40%** with exact written-form frequency matching, CI 0.29% to 0.54%; **0.62%** productivity-only), passing the pre-registered 1% threshold and yielding a maximum odds factor of 227 to 250. Under the practised tolerance `T1s`, the rate rises to 2.2% (2.17% repaired), failing the 1% bar. Crucially, the network's rarity comes entirely from multiplying four moderate per-link rates (mean ~0.21): as a simple multiplicity calculation shows, four successes exceed 5% chance once roughly 8 templates have been tried and exceed 50% around 17 templates. That calculation describes a selection mechanism rather than reconstructing Parpola's historical search, and it points directly to the empirical test in Section 5: evaluating Parpola's own word assignments on recurring Indus sign pairs he never published.

## 5. Blind-template tests: input repairs and cross-dictionary sensitivity

### 5.1 Original blind-template run and the input defects discovered in audit

In `2026-10-22-rebus-blind-templates`, we extracted all recurring ordered adjacent pairs of Parpola's 16 identified signs across both halves of split `d1d1b920` (appearing in at least two distinct inscription components) and removed his 12 published pairs (`P01`–`P12`) plus pairs already examined on 21 October. This yielded 38 unselected adjacent pairs (`T01`–`T38`) and 24 gapped pairs (`G01`–`G24`), frozen by hash before any *Tamil Lexicon* compound lookup.

In the original 22 October run, Parpola's Tamil words formed attested *Tamil Lexicon* compounds for **9 of 38 blind pairs** (23.7%, Wilson CI 13.0% to 39.2%) against **4.97 expected** for slot-matched random nouns (ratio **1.81**, 95% bootstrap CI 0.93 to 2.72; 6.7% of 10,000 slot-keyed random keys reached 9 hits). By contrast, his 12 published pairs succeeded 7 times against 1.15 expected (ratio 6.11, CI 2.84 to 11.70; 58.3% vs. 23.7%, one-sided Fisher p = 0.032). The gapped shared-member search (shape S, the template behind *veḷ*) proved uninformative on blind pairs: 22 of 24 succeeded for Parpola's words and 19.79 of 24 (82%) for random nouns (ratio 1.11).

Subsequent audit (`2026-10-22-reading-eval-readiness`) identified two concrete defects in that scorer's lexical inputs:

1. **Prefix-counting frequency proxy.** Stripping trailing vowel marks reduced monosyllabic words such as *kā* (`கா`) and *ā* (`ஆ`) to single letters (`க`, `ஆ`), counting every Sangam token beginning with that letter. For *kā*, the old proxy counted **22,287** tokens where the same Sangam stream contains **9** exact written-form tokens; for *ā*, it counted **4,458** instead of **24**. Prefix and exact counts differed for 23 of the 24 proposed forms, affecting the `BULLHEAD` and `YOKE` templates that supplied five of the nine blind hits.
2. **Silent phonological fallback.** Because *aṟu* has no exact one-member record in the parsed *Tamil Lexicon* table, the old lookup fell back to a length- and gemination-free index and silently substituted *aṟṟu* (prefix count 53, exact count 8).
3. **Independent slot draws.** The original joint random-key loop drew separate replacement words for `(sign, first)` and `(sign, second)` rather than assigning each sign one consistent replacement word across all 38 templates.

### 5.2 Repaired Tamil blind-template rerun

In `2026-11-22-rebus-repaired`, we replaced the frequency proxy and lookup with `lexical_inputs.py` (exact NFC written-form token counting across all 162,436 Tamil letter-and-mark tokens and zero phonological fallback), matched unresolved *aṟu* on compounding productivity alone (plus a sensitivity using the direct exact Sangam count of `அறு`, 23), added a productivity-only matching mode removing Sangam frequency altogether, and ran 10,000 **sign-level unified random keys** alongside slot-keyed compatibility draws (Table 4).

| Madras *Tamil Lexicon* specification | Templates | Hits | Expected (sign-joint) | Ratio (sign-joint) | Bootstrap 95% CI | Random-key p (sign-joint) | Slot-joint ratio (p) |
|---|---:|---:|---:|---:|---|---:|---|
| Original 22 Oct (prefix proxy, fallback, slot-keyed) | 38 | 9 | (4.97 marg.) | (1.81 marg.) | 0.93–2.72 | | 1.81 (0.067) |
| **Repaired: exact freq + prod (primary, T0s, K=50)** | **38** | **9** | **5.19** | **1.73** | **0.84–2.60** | **0.1037** | **1.84 (0.0704)** |
| Repaired: exact freq + prod (direct *aṟu* count = 23) | 38 | 9 | 5.12 | 1.76 | 0.87–2.67 | 0.0965 | 1.86 (0.0601) |
| **Repaired: productivity-only (no Sangam freq, T0s, K=50)** | **38** | **9** | **5.18** | **1.74** | **0.92–2.62** | **0.0821** | **1.65 (0.0837)** |
| Repaired: practised tolerance T1s (exact freq + prod) | 38 | 11 | 6.68 | 1.65 | 0.91–2.34 | 0.0943 | 1.80 (0.0491) |
| Repaired: pools K=25 / K=100 (exact freq + prod) | 38 | 9 | 5.69 / 4.15 | 1.58 / 2.17 | 0.79–2.36 / 1.07–3.31 | 0.1320 / 0.0474 | 1.58 / 2.42 |
| Repaired: first member only (direction a) | 38 | 8 | 3.64 | 2.20 | 1.00–3.47 | 0.0474 | 2.34 (0.0321) |
| Repaired: without *mīṉ* and *muruku* (unexposed 26) | 26 | 8 | 4.37 | 1.83 | 0.91–2.78 | 0.0891 | 1.89 (0.0683) |
| Repaired: without `BULLHEAD` | 26 | 4 | 2.61 | 1.53 | 0.38–2.87 | 0.2815 | 1.53 (0.2694) |
| Repaired: gapped shared-member (shape S) | 24 | 22 | 19.30 | 1.14 | 1.04–1.26 | 0.1412 | 1.15 (0.1061) |
| Repaired: Parpola's published pairs (exact freq + prod) | 12 | 7 | 1.51 | **4.64** | 2.25–7.88 | **0.0011** | 5.10 (0.0002) |
| Repaired: Parpola's published pairs (productivity-only) | 12 | 7 | 1.47 | **4.77** | 2.31–8.84 | **0.0001** | 4.71 (0.0003) |

Repairing the lexical inputs preserves the substantive result and slightly weakens the statistical separation on blind pairs. Under exact written-form frequency matching with unified sign-level random keys, the ratio moves from 1.81 to **1.73** (leave-one-out range 1.60 to 1.88) and the random-key probability rises from 0.067 to **0.1037** (more than one in ten random keys matches or exceeds Parpola's 9 hits). Removing Sangam frequency altogether gives nearly the same figures (ratio **1.74**, p = **0.0821**). Five of the nine blind hits (`T01` *veḷ-ḷ-āṉai* "white elephant", `T05` *nīr-āvi* "steam", `T11` *āṉai-k-kā*, `T29` *aṟu-v-ā-*, `T36` *kaṇ-ṇ-āvi* "evil eye") come from `BULLHEAD` (*ā*, *āṉ*, *āvu*) via stem-anchored homophony with unrelated words (*āṉai* "elephant", *āvi* "vapour"); removing `BULLHEAD` drops the blind ratio to **1.53** (4 of 26, p = 0.2815). The contrast with Parpola's 12 published pairs remains sharp: 7 of 12 succeed against 1.51 expected (ratio 4.64, p = 0.0011).

### 5.3 Cross-dictionary sensitivity: Winslow (1862), raw guarded versus Lexicon-assisted

In `2026-10-22-rebus-winslow`, testing the 2010 interlocks in Miron Winslow's 1862 dictionary (18,426 initially parsed two-member compounds) failed prediction P2 of conjecture C-0014 for a revealing reason: Winslow records **zero** two-member compounds beginning with *muruku* (against 7 in the *Tamil Lexicon*) and 29 ending in *mīṉ* (against 82). Neither *Muruka-vēḷ* nor *veṇ-mīṉ* is an entry (Winslow names Skanda *cevvēḷ* with *cem* "red"). Consequently, matched replacements for *muruku* also had zero first-member compounds, yielding an I1 null rate of 0.0% rather than above 20%. At matched compound-set sizes (7 and 29 compounds, post-outcome), Winslow and the *Tamil Lexicon* produced nearly identical chance rates (14.0% vs. 16.6%).

The 24 October re-extraction (`2026-10-24-lexical-extraction-extension`) audited all 69,310 Winslow entries and separated **raw Winslow guarded boundaries** (`winslow_guarded_members`, 18,421 compounds, which removes false splits like Persian *jamīṉ* "land" parsed as *ja-mīṉ* while borrowing zero boundaries from the *Tamil Lexicon*) from **Lexicon-assisted boundaries** (`members`, 25,653 compounds, incorporating *Tamil Lexicon* splits where exact Tamil headwords align uniquely). Scoring both layers separately in `2026-11-22-rebus-repaired` confirms that cross-dictionary dependence does not alter the conclusion (Table 5).

| Winslow (1862) layer and test | Matching | Templates | Hits | Expected (sign-joint) | Ratio (sign-joint) | Bootstrap 95% CI | Random-key p |
|---|---|---:|---:|---:|---:|---|---:|
| **Raw guarded (18,421 compounds; independent)**: blind T0s | Exact freq + prod | 38 | 6 | 2.67 | 2.25 | 0.79–3.79 | 0.0683 |
| Raw guarded: blind T0s | Productivity-only | 38 | 6 | 2.39 | 2.51 | 0.98–4.13 | 0.0443 |
| Raw guarded: blind without `BULLHEAD` | Exact freq + prod | 26 | 1 | 1.41 | **0.71** | 0.00–2.31 | **0.7269** |
| Raw guarded: published pairs | Exact freq + prod | 12 | 3 | 0.66 | 4.52 | 1.04–9.08 | 0.0328 |
| **Lexicon-assisted (25,653 compounds; dependent)**: blind T0s | Exact freq + prod | 38 | 7 | 3.19 | 2.20 | 0.91–3.49 | 0.0588 |
| Lexicon-assisted: blind T0s | Productivity-only | 38 | 7 | 2.81 | 2.49 | 1.06–3.90 | 0.0323 |
| Lexicon-assisted: blind without `BULLHEAD` | Exact freq + prod | 26 | 2 | 1.66 | **1.20** | 0.00–2.96 | **0.4837** |
| Lexicon-assisted: published pairs | Exact freq + prod | 12 | 3 | 0.84 | 3.57 | 0.89–7.12 | 0.0560 |

Two results stand out across both Winslow layers. First, `A(muruku)` remains 0 even after *Tamil Lexicon* boundary alignment (`B(mīṉ)` moves from 28 raw guarded to 39 assisted); only two of Parpola's five 2010 links (`I2` *vaṭa-mīṉ* and `I4` *aṟu-mīṉ*) hold, and random replacements reproduce both together in **3.85%** of draws under raw guarded boundaries (2.33% productivity-only) and **7.17%** under Lexicon-assisted boundaries (5.85% productivity-only). Second, on the 38 blind pairs, Winslow's apparent ratios (2.25 raw guarded, 2.20 Lexicon-assisted) are almost entirely driven by `BULLHEAD`: 5 of the 6 raw-guarded hits involve `BULLHEAD` (*āvu*/*āṉ*), and across the remaining 26 blind pairs raw Winslow yields just 1 hit against 1.41 expected (ratio 0.71, p = 0.7269).

## 6. Deciding Sanskrit cross-language control

The repaired Tamil blind-template test leaves a modest, statistically non-significant excess on unselected pairs (ratio 1.73, p = 0.1037; Winslow raw guarded 2.25, p = 0.0683). Two explanations compete for an excess near 1.7 to 2.2: either Parpola's words capture a weak Dravidian signal in unselected Indus sign pairs, or basic concrete picture nouns (small numerals, eyes, cattle, water, yokes) naturally combine with one another in any compound-rich dictionary more often than random nouns matched only on marginal compounding productivity.

To decide between these explanations, we ran a pre-frozen Sanskrit cross-language control on the **exact same 38 blind Indus sign pairs and 12 published pairs** (`2026-11-22-rebus-repaired`, Experiment B). Before inspecting any Monier-Williams `<e>3` compound, we froze two standard Sanskrit noun and numeral maps for Parpola's 16 concrete pictures (verifying only `<e>1` and `<e>2` simplex headword spelling presence):

- **Primary single-word map (16 words)**: `FISH` *matsya* (avoiding the Dravidian loan *mīna*), `ONE` *eka*, `TWO` *dvi*, `SIX` *ṣaṣ*, `SEVEN` *saptan*, `FIG` *vaṭa*, `SPINDLE` *tarku*, `CIRCLES` *valaya*, `SQUIRREL` *kalandaka*, `TWOLONG` *rekhā* ("line, stroke"), `CRAB` *karkaṭa*, `EYE` *akṣi*, `WATER` *jala*, `HINDLEG` *pāda*, `BULLHEAD` *go*, and `YOKE` *yuga*.
- **Multiplicity-matched map (24 words, matching Parpola's exact alternative-form counts per sign)**: adds *ekaka* (`ONE`), *dvā* (`TWO`), *romaśī* (`SQUIRREL`), *jaṅghā* (`HINDLEG`), *vṛṣa* and *ukṣan* (`BULLHEAD`), and *dhur* and *vīvadha* (`YOKE`).
- **Pre-frozen `TWOLONG` gloss sensitivity (`antara`)**: replaces *rekhā* ("line, stroke") with *antara* ("interval, space between", translating Parpola's pictorial reading *veḷi* of the two long strokes) on both maps.

Scoring these maps in Cologne Monier-Williams (101,164 two-member `<e>3` compounds, 35,694 simplex nominal candidates) under the exact same `T0s`/`T1s` tolerances, symmetric Sanskrit compound sandhi reversal, productivity matching (`K = 50`), and 10,000 sign-level dependent random keys produces a decisive result (Table 6).

| Sanskrit map and test (Monier-Williams) | Templates | Hits | Expected (sign-joint) | Ratio (sign-joint) | Bootstrap 95% CI | Random-key p (sign-joint) | Slot-joint ratio (p) |
|---|---:|---:|---:|---:|---|---:|---|
| **Primary single-word (`rekhā`): blind T0s, K=50** | **38** | **6** | **1.31** | **4.59** | **1.78–8.94** | **0.0020** | **3.09 (0.0104)** |
| Primary single-word: blind T1s, K=50 | 38 | 6 | 1.44 | 4.15 | 1.70–8.20 | 0.0038 | 2.87 (0.0117) |
| Primary single-word: blind K=25 / K=100 | 38 | 6 | 1.66 / 1.05 | 3.61 / 5.73 | 1.33–7.48 / 2.04–10.65 | 0.0041 / 0.0008 | 2.74 / 3.73 |
| Primary single-word: without `BULLHEAD` | 26 | 5 | 1.01 | 4.94 | 1.56–11.98 | 0.0031 | 3.17 (0.0125) |
| Primary single-word: Parpola's published pairs | 12 | 1 | 0.49 | 2.04 | 0.00–3.00 | 0.4205 | 1.66 (0.5094) |
| **Multiplicity-matched (24 words, `rekhā`): blind T0s, K=50** | **38** | **8** | **2.04** | **3.93** | **1.75–7.28** | **0.0005** | **2.67 (0.0032)** |
| Multiplicity-matched: blind T1s, K=50 | 38 | 8 | 2.23 | 3.58 | 1.64–6.66 | 0.0012 | 2.53 (0.0054) |
| Multiplicity-matched: without `BULLHEAD` | 26 | 5 | 1.38 | 3.62 | 1.01–8.71 | 0.0090 | 2.25 (0.0410) |
| Multiplicity-matched: Parpola's published pairs | 12 | 2 | 0.56 | 3.59 | 0.00–6.39 | 0.0876 | 2.89 (0.1247) |
| Sensitivity `TWOLONG=antara` (single / mult.): blind T0s | 38 | 7 / 9 | 2.04 / 2.90 | **3.43 / 3.11** | 1.35–6.36 / 1.51–5.36 | **0.0054 / 0.0013** | 2.40 / 2.19 |
| Sensitivity MW + hyphenated `<e>3` (single / mult.) | 38 | 6 / 8 | 1.28 / 2.05 | **4.69 / 3.91** | 1.75–8.98 / 1.79–7.18 | **0.0022 / 0.0004** | 3.17 / 2.67 |

Across every pre-frozen specification, standard Sanskrit nouns for Parpola's 16 pictures achieve **3.11 to 4.69 times** the productivity-matched random-key compound rate on the 38 blind pairs (`p = 0.0004` to `0.0054`), exceeding the repaired Tamil blind-pair ratio (**1.73**, `p = 0.1037`) by a factor of two or more. Even without `BULLHEAD`, Sanskrit holds ratios of **4.94** (5 of 26, `p = 0.0031`) and **3.62** (5 of 26, `p = 0.0090`).

Inspecting the actual Sanskrit hits explains the mechanism transparently. Five of the six primary hits are literal semantic combinations of basic concrete concepts and numerals: `T09` (*dvi-ṣaṣ* "twice six"), `T11` (*go-yuga* "yoke of oxen"), `T13` (*dvi-saptan* "twice seven"), `T14` (*dvy-akṣa* "two-eyed", the direct parallel of Tamil *iru-kaṇ*), and `T32` (*jala-rekhā* "line on water"). The sixth, `T21` (*matsya-jāla* "fish-net" for *matsya* + *jala* "water"), is a vowel-length homophone coincidence identical in structure to Tamil *veḷ-ḷ-āṉai* ("white elephant" for *veḷ* + *āṉ* "cow"). The multiplicity-matched map adds `T12` (*sapta-vṛṣa* "seven bulls") and `T29` (*ṣaḍ-vṛṣa* "six bulls"); the *antara* sensitivity adds `T03` (*dvy-antara*) and `T27` (*ekāntara*). Meanwhile, on Parpola's 12 published pairs, Sanskrit produces only 1 hit (`P05` *jalākṣī* / *jālākṣa*) on the primary map and 2 hits (`P05`, `P12` *eka-vṛṣa*) on the multiplicity-matched map, confirming that the published set was selectively curated for Tamil matches (7 of 12, ratio 4.64) rather than general picture combinability.

Under the pre-frozen decision criterion in `experiments/2026-11-22-rebus-repaired/PROTOCOL.md` (`ratio_Sanskrit >= 1.5` or `ratio_Tamil / ratio_Sanskrit <= 1.25`), the Sanskrit control confirms conjecture C-0014 in full (`ratio_Tamil / ratio_Sanskrit` = 0.38 to 0.56). Crucially, this does not mean the Indus script encodes Sanskrit; rather, it demonstrates a general methodological bias in productivity-matched dictionary nulls. Matching random replacement nouns only on their marginal compound counts ignores **mutual semantic combinability**: core concrete nouns and small numerals combine with each other in every lexicon far more frequently than arbitrary dictionary headwords of equal marginal productivity. Any blind-template compound test that uses productivity-matched random nouns without a cross-language control will misread basic-vocabulary combinability as language-specific signal.

## 7. Discussion

Taken together, our six measurements separate what Parpola's rebus argument can and cannot establish.

First, **single homophones and isolated interlocks carry weak evidential force in Dravidian**. Single picture-to-name homophones arise in 2.31% of DEDR pairs (higher than Indo-Aryan at 1.50% and Sumerian at 0.45%), and the shared-member *veḷ* search succeeds for 28.8% to 33.7% of matched random Tamil noun pairs (48.9% to 61.4% under practised tolerance), even generating an irrelevant *puḷi* interlock on Parpola's own anchor words. Neither compound behind *veḷ* appears as an entry in Winslow's 1862 dictionary, regardless of whether raw guarded or *Tamil Lexicon*-assisted boundaries are used.

Second, **the four-link 2010 network remains the strongest lexical exhibit in the *Tamil Lexicon*, yet its weight depends entirely on unrecorded search multiplicity**. Its 0.44% chance rate (0.40% after frequency repair) yields a maximum odds factor near 230–250 only if no other sign pairs were examined and discarded. Our blind-template comparison measures that selection gap directly: Parpola's 12 published pairs succeed at 58.3% (ratio 4.64, p = 0.0011), whereas 38 unselected recurring pairs built from his exact same 16 sign identifications succeed at 23.7% (ratio 1.73, p = 0.1037).

Third, **the Sanskrit cross-language control closes the residual ambiguity of the blind-template test**. A modest blind-pair excess near 1.7x in Tamil cannot be attributed to Dravidian linguistic fit when standard Sanskrit nouns for the exact same 16 concrete pictures score 3.11x to 4.59x (p = 0.0005 to 0.0054) on the exact same 38 pairs in Monier-Williams. Both ratios show that core picture vocabulary combines densely inside large historical dictionaries, and that vowel-length-free, stem-anchored matching adds accidental homophone matches in any language.

Fourth, **external historical-linguistic constraints narrow the foundational *mīn* pun**. Across DEDR, Kurukh and Malto *b-* answers Tamil *v-* in 50 of 55 units and never answers Tamil *m-* before a long front vowel (0 of 6), separating Malto *mínu* "fish" from *bínḍke* "star" and linking the northern star words to *viṇ* "sky". While Gondi *mīnkō* preserves a South II star witness, the bare homophone *mīn* "fish / star" reconstructs mainly to South Dravidian.

Several limitations define the scope of this working manuscript. The 16 sign identifications come from five accessible Parpola papers (1997–2010) rather than his complete 1994 book, which remains outside our rights-cleared archive. All *Tamil Lexicon*, Winslow, and Monier-Williams compounds were extracted programmatically and have not yet undergone stratified specialist adjudication of compound boundaries, loan status, or individual senses. Finally, the Sangam written-form counts cover unsegmented HTML streams including editorial headers and do not estimate inflected lemma frequencies.

## 8. Pre-submission checklist for specialist review

Before submitting this manuscript for peer review, independent Dravidianist and Sanskritist checks are required on five concrete items:

1. **Parpola (1994) complete sign inventory and ICIT crosswalk.** Acquire a rights-cleared copy of *Deciphering the Indus Script* (1994), check every concrete picture sign omitted here (including the spear and *kaḷam* signs that lacked CISI numbers in the five later papers), and have an Indus epigraphist verify every sign-to-ICIT mapping.
2. **Dravidianist audit of Tamil compound boundaries and senses.** Independently adjudicate a stratified sample of accepted and rejected two-member compounds in the Madras *Tamil Lexicon* and in raw guarded Winslow (`winslow_guarded_members`), checking increment formations (`-am-`, such as *murukkampū* and *murukkañcettal*), loanword markings, and whether individual blind-template hits (*mīṉ-koḷḷi*, *aṟu-v-ā-*, *veḷ-ḷ-āṉai*, *oru-vēḷai*) represent genuine Old Tamil compounds versus late lexicographical entries.
3. **Old Tamil corpus attestation check.** Replace nineteenth- and twentieth-century encyclopaedic dictionaries with a clean, line-addressable Sangam poetic corpus (stripped of front matter and editorial apparatus) to test whether Parpola's interlocking compounds appear in early Tamil texts more often than matched chance-interlock compounds.
4. **Sanskritist audit of Monier-Williams compound parsing and picture mappings.** Independently review the 16-sign Sanskrit control mappings (*matsya*, *vaṭa*, *valaya*, *rekhā* / *antara*, *kalandaka* / *romaśī*, *go* / *vṛṣa* / *ukṣan*, *yuga* / *dhur* / *vīvadha*), check the `<srs/>` and `—˚` compound-boundary parser on a stratified sample of Monier-Williams `<e>3` entries, and verify whether restricting Monier-Williams to Vedic and early Classical attestations (excluding lexicographical `L.` entries) alters the 3.1x–4.6x Sanskrit blind-pair excess.
5. **North Dravidian morphology check outside DEDR.** Consult Droese (1884), Mahapatra (1979), Hahn (1903), and Grignard (1924) directly to determine whether Malto *bínḍke* and Kurukh *bīnkō* segment morphologically from a *biṉ-* / *bīn-* "sky" base or continue an irregular *b-* reflex of `*mīn-k-`.

## References

- Backstrom, Peter C., and Carla F. Radloff (1992). *Languages of Northern Areas* (Burushaski wordlists via Lexibank `backstromnorthernpakistan-v1.1`).
- Bourdeau, Daniel (2026). Cyphersolver Indus page (`github.com/dbourdeau/cyphersolver`, commit `1c73645947deba694cb82d42dba967319e8df5a5`, 1 October 2026).
- Burrow, T., and M. B. Emeneau (1984). *A Dravidian Etymological Dictionary* (2nd ed.). Oxford: Clarendon Press (Digital Dictionaries of South Asia edition).
- Electronic Pennsylvania Sumerian Dictionary (ePSD2). Oracc open glossary.
- Farmer, Steve, Richard Sproat, and Michael Witzel (2004). "The collapse of the Indus-script thesis: the myth of a literate Harappan civilization." *Electronic Journal of Vedic Studies* 11(2): 19–57.
- Kobayashi, Masato (2020). *Journal of the American Oriental Society* 140(2) (on Kurukh *b-* reflecting Proto-Dravidian `*w-`).
- Kolichala, Suresh (2016). INDOLOGY list message, January 2016 (`list.indology.info/pipermail/indology/2016-January/042593.html`).
- Kolipakam, Vishnupriya, Fiona M. Jordan, Michael Dunn, Simon J. Greenhill, Remco Bouckaert, Russell D. Gray, and Annemarie Verkerk (2018). "A Bayesian phylogenetic study of the Dravidian language family." *Royal Society Open Science* 5: 171504.
- Monier-Williams, Monier (1899). *A Sanskrit-English Dictionary*. Oxford: Clarendon Press (Cologne Digital Sanskrit Lexicon `mw.txt`).
- Parpola, Asko (1994). *Deciphering the Indus Script*. Cambridge: Cambridge University Press.
- Parpola, Asko (1997). "Dravidian and the Indus script: On the interpretation of some pivotal signs." *Studia Orientalia* 82: 167–192.
- Parpola, Asko (2005). "Study of the Indus script." *Transactions of the International Conference of Eastern Studies* 50: 28–66.
- Parpola, Asko (2008). "Is the Indus script indeed not a writing system?" In *Airāvati: Felicitation volume in honour of Iravatham Mahadevan*, pp. 111–131.
- Parpola, Asko (2009). "'Hind leg' + 'fish': towards further understanding of the Indus script." *Scripta* 1: 37–76.
- Parpola, Asko (2010). *A Dravidian solution to the Indus script problem*. Chennai: World Classical Tamil Conference.
- Raghavendra (2026). arXiv:2608.02999 (lexical coverage and grouped-split evaluation of decipherment keys).
- Rau, Felix (2019). *Proto-Munda cognate sets* (`pMunda_cognate_set_2019-08-29.csv`).
- Turner, R. L. (1962–1966). *A Comparative Dictionary of the Indo-Aryan Languages* (CDIAL). London: Oxford University Press (DSAL edition).
- University of Madras (1924–1936). *Tamil Lexicon*. Madras: University of Madras (DSAL edition).
- Winslow, Miron (1862). *A comprehensive Tamil and English dictionary of high and low Tamil*. Madras: P. R. Hunt (DSAL edition).
