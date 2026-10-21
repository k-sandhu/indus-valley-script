# Seal legends in head-final languages end in few signs, and so do Akkadian ones

Package of 21 October 2026 for [Q-0037](../../knowledge/questions/Q-0037-design-a-head-direction-seal-comparison.md) and study 7 of [Taking Parpola's readings further](../../knowledge/directions/parpola-forward-2026-10-20.md). Protocol [PROTOCOL.md](PROTOCOL.md), hashed before any statistic ([PROTOCOL.sha256](PROTOCOL.sha256)), with four amendments written and hashed before computation. Status class: `frozen-evaluation`. Contributors: Claude Opus 5.5 in Claude Code (design, review, prose) and Codex CLI with GPT-6.1-Sol (acquisition, transcription, normalisation, statistics code); see [README.md](README.md).

## Results

We built the first head-final seal-legend corpora the project holds and set them beside two head-initial ones, all in one record form that links every legend to an object and a site. The Indo-Aryan seals and sealings of Basarh and Bhita give 245 distinct eligible legends and Tamil-Brahmi seals, rings and coins 23. Ur III seal legends in Sumerian give 3,044, and Old Akkadian legends in Akkadian 11. The frozen discrimination test needs two corpora of each group with at least 25 legends. Only one of each qualifies, so the test could not keep or reject any statistic, and the declared second panel at a threshold of 20 cannot either, because the Akkadian corpus still falls short ([Amendment 4](AMENDMENT-4.md)). Placing the Indus legends therefore remains closed.

The corpora that did enter differ sharply. In Indo-Aryan legends the first sign is far more varied than the last: edge asymmetry is +0.250 at a matched size of 196 legends, against −0.219 for Ur III, with the two separated in every one of 2,000 replicate draws. The same holds for the share of legends closing in the three commonest final signs (0.628 against 0.204), for the excess of stock closings over a within-legend shuffle (+0.264 against −0.025), and inside words (+0.204 against −0.111). In the second panel the Tamil-Brahmi legends sit on the Indo-Aryan side of Ur III on all four, at +0.363, 0.889, +0.527 and +0.411. The one other head-initial language we measured breaks the pattern: the 11 Akkadian legends have an edge asymmetry of +0.134, above their within-legend shuffle range (−0.073 to +0.092). The Sumerian legends of the same Old Akkadian period stand at +0.020, inside theirs. As we predicted before computing, final-sign concentration follows the closing formula rather than the order of noun and modifier. In Sanskrit and Prakrit that formula is a genitive suffix (147 of 245 Indo-Aryan legends end in *-sya* or *-sa*), in Tamil a name suffix (15 of 23 end in *-ṉ*), and in Akkadian the possessive *-šu*, "his" (5 of 11 end in *ARAD₂-sú*, "his servant", or *DUMU-sú*, "his son"; counts made after the runs, [exploratory-closing-units.json](exploratory-closing-units.json)). An exploratory count made after the runs points to the order of title and name as the statistic that does track head direction. Indo-Aryan legends put the title first in 57 of 61 adjacent title–name pairs. Ur III legends put it second in 2,393 of 2,475, and the Akkadian legends in 10 of 15.

## 1. Corpora

| Corpus | Group | Sources | Records | Objects | Eligible legends, sign / word |
|---|---|---|---:|---:|---:|
| `ia-ganges` | head-final | Bloch 1903–04 and Spooner 1913–14 (Basarh), Marshall 1911–12 (Bhita) | 556 | 495 | 245 / 30 |
| `ta-brahmi` | head-final | Mahadevan 2003, Tables 1.6–1.8 | 31 | 31 | 23 / 7 |
| `sux-ur3` | head-initial | ORACC `epsd2/admin/ur3`, all entries | 31,512 | 31,220 | 3,044 / 3,026 |
| `akk-sargonic` | head-initial | ORACC `epsd2/admin/oakk`, CDLI | 89 | 89 | 11 / 10 |
| `sux-sargonic` | reported only | as above, Sumerian legends | 175 | 175 | 42 / 36 |

A legend is eligible when, after grouping by die, shared alias and identical sign sequence, it is complete or restored, belongs to an object with a site and has at least two units at the level. The Basarh and Bhita entries were transcribed from page images and checked against the coordinator's reading of fourteen entries on five pages; the editors' bracket conventions differ, and [Amendment 3](AMENDMENT-3.md) reads each as its editor meant it. The Ur III corpus reproduces the 522 seal records of the held sample exactly. The [feasibility ledger](FEASIBILITY.md) gives sources, hashes, rights, exclusions and gaps.

## 2. The frozen test

With the entry threshold of 25 legends, `ia-ganges` and `sux-ur3` enter at sign level, and `ia-ganges` (30 legends) and `sux-ur3` at word level; `ta-brahmi` (23) and `akk-sargonic` (11) do not. With 20, `ta-brahmi` enters at sign level and `akk-sargonic` still does not. The keep rule needs two corpora of each group, so every statistic is untestable in both runs: [run-2026-10-21/summary.json](run-2026-10-21/summary.json) and [run-2026-10-21-threshold-20/summary.json](run-2026-10-21-threshold-20/summary.json) report `testable: false` and keep nothing, the outcome Amendment 4 stated before the runs.

The Old Akkadian shortfall reflects the record rather than our selection. CDLI lists 62 Akkadian-language seals and 31 sealings of the period, and gives a provenience for 210 of its 777 Old Akkadian seal entries of any language. Most inscribed cylinder seals are museum acquisitions without findspot, and most excavated impressions have lost their first or last signs.

## 3. What the entering corpora show

These values describe the corpora; no statistic was kept or rejected on them. Medians and 5th–95th percentiles are over 2,000 matched draws.

| Statistic | `ia-ganges` (n = 196) | `sux-ur3` (n = 196) | Separated draws |
|---|---|---|---:|
| `sign.S1` edge asymmetry | +0.250 (+0.227, +0.275) | −0.219 (−0.259, −0.178) | 100% |
| `sign.S2` closing concentration | 0.628 (0.602, 0.648) | 0.204 (0.168, 0.250) | 100% |
| `sign.S3` stock closure beyond shuffle | +0.264 (+0.247, +0.283) | −0.025 (−0.074, +0.027) | 100% |
| `within.S6` word-internal asymmetry | +0.204 (+0.178, +0.231) | −0.111 (−0.134, −0.087) | 100% |

| Statistic, second panel (n = 18) | `ia-ganges` | `ta-brahmi` | `sux-ur3` | `sux-sargonic` |
|---|---|---|---|---|
| `sign.S1` | +0.230 (+0.101, +0.368) | +0.363 (+0.300, +0.434) | −0.136 (−0.250, −0.031) | +0.017 |
| `sign.S2` | 0.667 | 0.889 | 0.333 | 0.389 |
| `sign.S3` | +0.383 | +0.527 | −0.018 | +0.093 |
| `within.S6` | +0.202 | +0.411 | −0.100 | −0.009 |

On each full eligible set, the within-legend shuffle reference of step 6 places the observed edge asymmetry well outside chance for Indo-Aryan (+0.246 against −0.041 to +0.041), Tamil-Brahmi (+0.378 against −0.118 to +0.118), Ur III (−0.226 against −0.013 to +0.014) and Akkadian (+0.134 against −0.073 to +0.092), and inside it for the Sumerian legends of the Old Akkadian period (+0.020 against −0.053 to +0.054). Each Survey report separately (Bloch +0.125, Marshall +0.169, Spooner +0.412) lies above every Ur III site with at least 15 legends (from −0.191 at Girsu to +0.025 at Garšana). The run without doubtful readings and the run restricted to Sanskrit legends move no value across the other group's range.

At word level the head-final side is too thin to describe: the 30 Indo-Aryan legends with two or more words are mostly a title and a compound, and they give an edge asymmetry of −0.015 against +0.014 for Ur III. Titles follow names in Ur III legends (`word.S4` −0.934), and numerals almost never appear in seal legends (`word.S5` has 155 eligible Ur III legends and none on the head-final side).

## 4. The predictions written before computation

We predicted that title before name (`word.S4`) would be kept; it could not be tested, because only 9 Indo-Aryan legends and 1 Tamil-Brahmi legend have a title–name pair across two words. We predicted that the sign-level edge statistics would not be kept because Akkadian legends close in few signs; they could not be tested, but the 11 Akkadian legends show exactly that pattern (+0.134 beyond their shuffle range). We predicted that the word-internal asymmetry would not be kept because all four languages are suffixing; Ur III words in fact begin with fewer distinct signs than they end (−0.111), largely because of the divine determinative and common name elements, so the prediction's reason was wrong whatever a test would show. We predicted that the numeral statistic would be untestable, and it is.

## 5. Exploratory: the order of title and name

After the runs we counted adjacent title and name members over every eligible legend, including the single-compound legends that the word-level statistic cannot use ([exploratory-title-name-order.json](exploratory-title-name-order.json)). Indo-Aryan legends put the title first in 57 of 61 pairs (+0.87, 53 legends: *kulika-Harisya*, "of the guild-president Hari"; *mahārāja-śrī-Ghaṭotkacaguptasya*). Ur III legends put it second in 2,393 of 2,475 (−0.93), the Akkadian legends in 10 of 15 (−0.33, 9 legends) and the Sumerian legends of the Old Akkadian period in 34 of 46 (−0.48). Tamil-Brahmi has one pair. The tags come from our lexicons, the editors' translations and ORACC's parts of speech, and an untagged word in the CDLI legends counts as a name.

## 6. Placing the Indus legends

Two things must happen first. The keep rule must keep at least one statistic, which needs a second head-initial corpus and a Tamil-Brahmi corpus of at least 25 eligible legends each. Then the matched controls of protocol section 11 must pass: every kept word-level statistic must still separate the groups when the comparison legends are cut by the seal-legend-units segmenter trained on one line division per legend, and every kept statistic must survive subsampling to the length distribution of the Indus seal legends. The cuneiform corpora carry ATF lines for this control; the Indo-Aryan editions mark line divisions for only 30 records.

The head-initial languages would be excluded if the Indus legends fell on the head-final side of the boundary, in their median and in at least 95% of their draws, on every statistic that passed the controls, with at least one at sign level and one at word level. The claim would be dead if they fell on the head-initial side of every such statistic. The present results show which statistics are likely to pass. The sign-level edge statistics separate Indo-Aryan and Tamil from Ur III but probably not from Akkadian, and the Indus sign-level edge asymmetry is already measured, so a placement on it would be neither discriminating nor blind. Title-and-name order looks discriminating, but in Indus legends it needs a declared map of which signs or units are titles and which are names, and the placement then tests that map together with the language type.

## 7. The boldest reading and the test that would decide it

Final-sign concentration in seal legends marks a closing formula, not a head-final language. Sanskrit, Prakrit and Tamil legends end in a genitive or name suffix, and Akkadian legends in the possessive "his". Ur III legends, most of which end with the father's name after *dumu*, "son of" (1,701 of 3,044), do not. The Indus legends' concentration of final signs therefore says that they close with a formula, which the seal-legend-units package has shown directly. Their language type will be read from the order of title and name, where head-final legends put the title first and head-initial legends put it second.

The test is to enlarge the two short corpora and run the frozen protocol unchanged. We need at least 25 eligible Akkadian seal legends with a site (from the Tell Brak and Tell Mozan excavation reports, or the Old Assyrian seals of Kültepe) and at least 25 Tamil-Brahmi seals and rings (from the revised *Early Tamil Epigraphy* and later Karur and Keeladi finds), with the compound members of Indo-Aryan legends kept as word units. The reading predicts that `sign.S1`, `sign.S2` and `sign.S3` fail the keep rule because Akkadian sits with the head-final group, and that title before name is kept, with Indo-Aryan and Tamil positive and Sumerian and Akkadian negative. The reading is dead if the enlarged Akkadian corpus falls below the Ur III range on `sign.S1` at matched size, because then final-sign concentration separates the language types after all.
