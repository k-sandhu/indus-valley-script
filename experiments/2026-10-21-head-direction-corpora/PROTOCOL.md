# Protocol: which seal-legend statistics separate head-final from head-initial languages

Written 21 October 2026 (UTC), before any statistic of this protocol was computed on any corpus. Contributor: Claude Opus 5.5 (Anthropic) in Claude Code, a side session of the project's main session, which chose the sources, made the rights decisions and wrote this protocol. Codex CLI running GPT-6.1-Sol fetches, transcribes and normalises the sources and implements the statistics under the briefs in [codex/](codex/). Status class on completion: `frozen-evaluation` for the discrimination test of section 9, run on the comparison corpora alone. No Indus legend is placed by this package. The record form is in [SCHEMA.md](SCHEMA.md) and the rules for transcribing printed lists in [TRANSCRIPTION-BRIEF.md](TRANSCRIPTION-BRIEF.md); both are part of this protocol and are hashed with it.

## 1. Question and why this is new work

Indus texts begin with many different signs and end with few. On the clean distinct texts the normalized entropy of the first sign exceeds that of the last by 0.260, and on seal texts by 0.270, against a within-text shuffle range of about ±0.02 ([structure-first step 6](../2026-10-12-structure-first/step6-language/REPORT.md)). Parpola reads this ending concentration, and the numerals that precede the fish sign, as the structure of a language that puts modifiers before their heads and marks grammar with suffixes. Step 6 could not test that reading because the project held no seal legends in a head-final language, and in the head-initial corpora it held the same statistic changed sign with the unit: Ur III seal legends scored −0.204 counted by sign and +0.079 counted by word ([F-0023](../../knowledge/findings/F-0023-edge-asymmetry-changes-with-the-unit.md)). The registry entry [STRUCTURAL-TYPOLOGY-2026-10-12](../../knowledge/registry/attempts/STRUCTURAL-TYPOLOGY-2026-10-12.json) asks for a retry only when at least two head-initial and two head-final seal-legend corpora are measured at sign and word level with the same code. Question [Q-0037](../../knowledge/questions/Q-0037-design-a-head-direction-seal-comparison.md) asks for the protocol, and study 7 of [Taking Parpola's readings further](../../knowledge/directions/parpola-forward-2026-10-20.md) states the test. This package acquires the head-final corpora, adds a second head-initial corpus, fixes the statistics and the rule that decides which of them separate the two groups, and runs that rule on the readable corpora only.

## 2. The typological premise

We classify the comparison languages by the order of the noun and its modifiers, the axis that seal legends can show, since they hold names, titles and relational nouns and seldom a verb. Sanskrit and the Middle Indo-Aryan Prakrits put genitives and adjectives before the head noun, form compounds whose head is the last member, and mark case with suffixes (Whitney, *Sanskrit Grammar*, 2nd edition, 1889). Old Tamil puts every modifier before its head and is suffixing (Krishnamurti, *The Dravidian Languages*, Cambridge University Press, 2003). These two are the head-final group. Sumerian puts adjectives and genitives after the head noun and closes the noun phrase with enclitic case markers (Jagersma, *A Descriptive Grammar of Sumerian*, PhD thesis, Leiden University, 2010). Akkadian puts adjectives after the noun and the genitive after the head in the construct state, with case suffixes (Huehnergard, *A Grammar of Akkadian*, 3rd edition, Eisenbrauns, 2011). These two are the head-initial group. All four languages put the verb last and use suffixes, so the contrast the test can find is in the noun phrase. We did not re-read these grammars for this protocol; the classification is the standard description of each language and is the premise of the test.

## 3. Corpora and sources

| Corpus | Group | Sources | Genre | Rights |
|---|---|---|---|---|
| `ia-ganges` | head-final | Bloch, "Excavations at Basarh", *Archaeological Survey of India, Annual Report 1903–04*, inscribed clay seals pp. 101–120; Marshall, "Excavations at Bhita", *ASI Annual Report 1911–12*, seals and sealings pp. 44–61; Spooner, "Excavations at Basarh", *ASI Annual Report 1913–14*, list of seals from p. 124 | Seal dies, signet rings and clay sealings | Government of India publications of 1906–1917, public domain; scans from the Internet Archive |
| `ta-brahmi` | head-final | Mahadevan, *Early Tamil Epigraphy from the Earliest Times to the Sixth Century A.D.*, Harvard Oriental Series 62, 2003, Tables 1.7 (seals) and 1.8 (rings), with Table 1.6 (coins) as the declared substitute of section 4 | Seals and rings; coins | Copyright 2003; a third-party scan on the Internet Archive with no licence; local-only, aggregates tracked |
| `sux-ur3` | head-initial | ORACC epsd2/admin/ur3 JSON archive held since 12 October (all 80,181 entries, not only the 3,000-entry sample) | Seal impressions on tablets and envelopes | CC0 declared in the JSON |
| `akk-sargonic` | head-initial | ORACC epsd2/admin/oakk JSON archive; CDLI catalogue and ATF transliterations at a pinned commit of the CDLI bulk data | Cylinder seals and seal impressions of the Old Akkadian period whose words are Akkadian | ORACC CC0; CDLI text "may be freely copied, aggregated and re-used according to common and fair academic practice" ([CDLI terms](https://cdli.earth/terms-of-use)); local-only |
| `sux-sargonic` | reported only | The same Old Akkadian period sources, legends whose words are Sumerian | As above | As above |

The 1909–10 annual report holds only a summary of Marshall's first Bhita season and no list of seals; it is acquired as the witness for that statement. `sux-sargonic` is a second sample of Sumerian and so does not count as a separate tradition; it is reported beside `sux-ur3` as a check within one language. West Semitic stamp seals (Avigad and Sass, *Corpus of West Semitic Stamp Seals*, 1997) would add a third head-initial tradition with a prefixed possessive (*l-*, "belonging to"), but we found no lawful digital source; the gap goes to the feasibility ledger with the Ancient South Arabian seals of the DASI archive as a candidate route.

## 4. Object identity, legend identity and sampling

Every record links to a physical object and a site ([SCHEMA.md](SCHEMA.md), `object_id`, `object_kind`, `site`). For Bloch's list, whose entries are seal varieties, the object is the die and `impressions` gives the number of clay impressions he counted; for Spooner's list the object is the clay lump with its register number; for Bhita the object is the numbered seal or sealing; for Mahadevan the numbered seal, ring or coin; for ORACC and CDLI sealings the sealed tablet or envelope (P-number), and for CDLI seals the seal itself. A record that cannot be linked to an object and a site is listed in the feasibility ledger and does not enter the statistics; edited texts are never counted as objects.

The statistics count distinct legends, as step 6 did. Records are grouped by union-find over shared `die_id`, shared aliases and identical sign-unit sequences, and each group contributes one legend: the record whose `completeness` is `complete` before `restored`, then the one with more units, then the smallest `record_id`. A legend is eligible when its completeness is `complete` or `restored`. A legend eligible at sign level has at least two sign units; at word level, at least two words. Records whose reading the editor marks as doubtful are included, and a sensitivity run without them is reported.

The Tamil-Brahmi population is seals and rings. If it holds fewer than 25 eligible legends at a level, the population at that level is seals, rings and coins, flagged in every output; if it still holds fewer than 25, `ta-brahmi` does not enter that level. The Indo-Aryan corpus holds Sanskrit, Prakrit and mixed legends; a Sanskrit-only sensitivity run is reported.

## 5. Reference units

The sign unit is the unit the script writes as one sign: the akṣara for Brahmi and Tamil-Brahmi, the sign reading for cuneiform, with the rules of [SCHEMA.md](SCHEMA.md). The reference word unit is the editor's orthographic word, with compound members kept as tagged members. For the Indus legends the units will be those published by the [seal-legend-units package](../2026-10-20-seal-legend-units/PROTOCOL.md), whose word-like units come from a segmenter trained on catalogue line divisions; section 11 states how the comparison corpora are matched to that procedure before any placement.

## 6. Required metadata

A record must carry `record_id`, `corpus`, `source`, `source_locator`, `object_id`, `object_kind`, `genre`, `site` (or a ledger entry), `language`, `script`, `rights`, `legend_as_printed`, `lines`, `line_division_basis`, `words`, `members`, `units`, `word_units`, `line_of_word`, `tags`, `tag_source`, `completeness`, `reading_doubtful` and `transcription`. The other fields of SCHEMA.md are recorded whenever the source gives them, and the coverage of each field per corpus is reported.

## 7. Statistics

All statistics are computed on a set T of eligible distinct legends, each a sequence of units at the stated level. Normalized entropy of a distribution of units is its Shannon entropy in bits divided by log₂ of the number of distinct units in all positions of T.

| Id | Level | Definition |
|---|---|---|
| `sign.S1`, `word.S1` | sign, word | Edge asymmetry: normalized entropy of the first units minus that of the last units (the step 6 statistic) |
| `sign.S2`, `word.S2` | sign, word | Closing concentration: the share of legends whose last unit is one of the three commonest last units of T, ranked by count and then by the unit's string |
| `sign.S3`, `word.S3` | sign, word | Stock closure beyond frequency: the share of legends whose last unit belongs to the closing stock K(T), the ⌈\|T\|/10⌉ commonest last units, minus the mean of the same share over 200 shuffles of the units within each legend, K recomputed on every shuffle |
| `word.S4` | lexical members | Title before name: over adjacent pairs of members in reading order of which one is tagged `TITLE` and the other `NAME`, (title-then-name − name-then-title) / (their sum) |
| `word.S5` | lexical members | Numeral before its neighbour: over adjacent pairs of a `NUMBER` member and a member tagged neither `NUMBER` nor `GRAM`, (numeral-first − numeral-second) / (their sum) |
| `within.S6` | signs within words | Word-internal asymmetry: over the words of T with at least two sign units, normalized entropy of their first signs minus that of their last signs, the inventory being the signs of those words; null below 20 such words |

`word.S4` and `word.S5` use their own eligible sets: the legends that contain at least one counted pair. The within-legend shuffle reference of step 6 for `S1` is also reported for every corpus on its full eligible set, as a description of how much of each edge effect is positional.

## 8. Matched subsampling

For each statistic, a corpus enters if its eligible set holds at least 25 legends (15 for `word.S4` and `word.S5`). The matched size is n = min(400, ⌊0.8 × the smallest eligible set among the entering corpora⌋). In each of R = 2,000 replicates every entering corpus draws n legends without replacement, with the seed taken from the SHA-256 of `2026-10-21-head-direction-corpora:<statistic>:<corpus>:<replicate>`, and the statistic is computed on the draw. Each corpus is summarized by the median and the 5th and 95th percentiles over replicates. Drawing 80% of the smallest set gives every corpus replicate spread, and matching n removes the dependence of entropy and concentration on sample size.

## 9. The discrimination test

The primary corpora are `ia-ganges` and `ta-brahmi` (head-final) and `sux-ur3` and `akk-sargonic` (head-initial). A statistic is testable when at least two corpora of each group enter. A testable statistic is kept when all three conditions hold:

1. every head-final median lies on the same side of every head-initial median (complete separation), which fixes the direction d;
2. in at least 95% of replicates, the replicate values of the four corpora (the r-th draw of each) are completely separated in direction d;
3. the statistic is defined in at least 99% of replicates of every entering corpus.

With two corpora per group, a statistic whose corpus values are exchangeable between the groups meets condition 1 with probability 1/3, since 8 of the 24 orderings of four values separate the groups. About three of the nine statistics can therefore pass by chance, and condition 2 does not remove a stable difference between corpora that has another cause, such as the script or a scribal formula. A kept statistic is a candidate for placing the Indus legends. The checks below and the matched controls of section 11 are the further filters, and a statistic that fails here is not used to place the Indus legends.

Reported beside the decision, without changing it: the separation of sub-corpora (for `ia-ganges` each of the three reports; for `ta-brahmi` seals, rings and coins; for `sux-ur3` and `akk-sargonic` each site with at least 15 eligible legends), each at n = ⌊0.8 × its smallest eligible set⌋; the position of `sux-sargonic` relative to the groups; the run without doubtful readings; and the Sanskrit-only run.

## 10. Predictions written before computation

We expect title before name (`word.S4`) to be kept, with the head-final corpora putting titles before names (*mahārāja śrī Ghaṭotkacagupta*) and the head-initial corpora after them (PN *dub-sar*). We expect the sign-level edge statistics (`sign.S1`, `sign.S2`, `sign.S3`) not to be kept, because Akkadian seal legends end in a few signs as often as the Indo-Aryan ones do (*ARAD₂-sú*, "his servant", against the genitive *-sya*), and Sumerian legends end variously. We expect the word-internal asymmetry (`within.S6`) not to be kept, since all four languages are suffixing, and the numeral statistic (`word.S5`) to be untestable, since seal legends seldom contain numerals. These predictions do not enter the decision rule; they are recorded so that the report can say which expectations failed.

## 11. Placing the Indus legends (not done in this package)

The Indus legends are placed only after two conditions are met. First, the seal-legend-units package publishes its frozen unit inventory and the segmented legends. Second, the matched controls pass: every kept word-level statistic must still separate the groups, by the rule of section 9, when the comparison corpora are cut into units by the same procedure that produced the Indus units (the supervised line-break segmenter trained on one line division per legend, as in that package's `sumerian_calibration.py`), which is possible only in corpora whose editions mark line divisions; and every kept statistic must still separate the groups when each corpus is subsampled to the length distribution of the distinct Indus seal legends. A statistic that fails either control is not used.

The Indus value is then computed with the same code at the same n and R. The Indus legends fall with a group on a statistic when their median and at least 95% of their replicates lie on that group's side of the midpoint between the nearest head-final and head-initial medians. Study 7 passes, and the head-initial candidates are excluded as the language of the legends (Sumerian and Akkadian directly, Elamite by its noun-phrase order), when the Indus legends fall with the head-final group on every statistic that passed the matched controls, with at least one at sign level and one at word level. The claim is dead when they fall with the head-initial group on every such statistic. Any other pattern leaves the question undecided.

Two limits apply to that placement. The sign-level edge asymmetry and the share of the commonest final signs are already measured on the Indus corpus, so a placement on those statistics with the held texts is a measurement, not a blind test; a blind placement needs the fresh pools of the seal-legend-units predictions or a statistic not yet computed on Indus texts. Titles and names cannot be recognized in Indus legends without a reading, so `word.S4` places them only under a declared sign-class map, and the placement then tests that map together with the language type.

## 12. Run order, outputs and budget

1. Acquire and transcribe the sources (Codex runs A1, A2 and B); normalise them with the code of run C. No statistic is computed in this step.
2. Review a sample of the transcriptions against the page images, write the feasibility ledger and count eligible legends per corpus and level.
3. Write any amendment before computation as a dated, hashed file.
4. Run the synthetic tests of the statistics code and the regression against step 6, which must reproduce −0.204 and +0.079 on the held Ur III seal legends.
5. Run the discrimination test once and save it as `run-2026-10-21/`. A code error found afterwards is corrected in a dated amendment, with the first output kept.

The run writes `run-2026-10-21/summary.json` (every statistic per corpus: eligible count, n, median, 5th and 95th percentiles, shuffle reference where defined; the keep decision with conditions 1–3; the secondary checks) and records the hashes of this protocol, SCHEMA.md, TRANSCRIPTION-BRIEF.md, the code and every normalised input. Record-level outputs stay under `data/raw/2026-10-21-head-direction-corpora/`. No confirmation split of Indus data is read, so `bench/spent.json` is not touched; the bench selftest is run and saved with the package.
