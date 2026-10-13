# Step 4: stroke values are more tied to neighbouring signs than Ur III counts are

Indus stroke groups take fewer different values next to a given sign than Ur III administrative numerals take before a given commodity, and a sign's commonest value is more dominant. The contrast holds under every value definition and sampling repair tried. Which signs look fixed depends on whether the counted item is taken to be the next sign or the previous one, and the frozen analysis assumed the next. Short and tall strokes occur next to different signs. Endpoints: [run-2026-10-12](run-2026-10-12/summary.json) and the labelled post-outcome exploration [run-2026-10-12-explore](run-2026-10-12-explore/summary.json); the unit-aware, rarefied, net-information and preceding-item sensitivities were computed in the [review](../review/REVIEW.md) and are post-outcome.

## Prior work

Mahadevan's 1977 concordance tabulates the combinations of stroke numerals with other signs, and Parpola (1994) discusses stroke groups bound to particular signs as fixed expressions, such as the stroke-and-fish groups he read as asterisms. This step measures how fixed those combinations are against an administrative counting corpus.

## Population, comparison and assumptions

Numeral tokens are codes in coder 1's short-stroke and tall-stroke families that carry a stroke count, in the 1,859 distinct clean texts. In the frozen analysis the item is the next sign in reading order, a numeral followed by another numeral is skipped, and the value is the stroke count; this gives 1,265 tokens and 56 items with at least five tokens. Ur III tablets supply the comparison: the item is the next word after a numeral token, and the value is the digit *n* of the token `n(unit)`. That definition drops the unit, so ten (`1(u)`), sixty (`1(geš₂)`) and a capacity measure (`1(barig)`) all count as 1, and it keeps only the last token of a compound number: 865 of the 3,421 Ur III pairs have a unit other than *diš* and 780 are the last token of a compound. Ur III is subsampled 200 times to 1,265 tokens. The comparison sets seal and tablet texts against administrative accounts; a mark on an object that records a standard allotment, rank or capacity would also show one value per item.

## Results

| Measure | IVS | Ur III at IVS size, mean (95% range) |
|---|---:|---:|
| Distinct values per qualifying item | 3.61 | 4.80 (4.53–5.15) |
| Share of the commonest value, token-weighted | 0.606 | 0.429 (0.407–0.450) |
| Mutual information over value entropy | 0.457 | 0.318 (0.298–0.336) |

The IVS value and the next sign share 1.07 bits of mutual information against a permutation mean of 0.61 (p = 0.0001). The 201 Linear B commodity–number pairs, too few to subsample to IVS size, give 6.0 values per item across 12 items, a top share of 0.308 and an information ratio of 0.499.

**Sensitivities (post-outcome).** With values that distinguish the IVS stroke family and the Ur III unit, IVS has 4.50 values per item against 6.09–7.05 for Ur III, a top share of 0.551 against 0.357–0.405, and an information ratio of 0.524 against 0.447–0.484. Rarefied to five tokens per item, IVS shows 2.73 values against 3.26–3.56 and a top share of 0.608 against 0.453–0.510. The plug-in information ratio is biased at these sizes; net of its permutation mean it is 0.197 for IVS against 0.059–0.096 for Ur III, and 0.090 for Linear B. Removing every value-2 token leaves 691 tokens and the same direction (3.46 values per item, top share 0.562). Sixteen of the 56 IVS items have a commonest value with at least 80% of tokens, against 2–8 of about 43 in Ur III subsamples.

**Which side is the item.** The step 6 calibration test, repeated in review with family-aware IVS values and unit-aware Ur III values, detects the Ur III number-before-commodity order (the following word carries more information about the value) and finds the reverse for IVS: the preceding sign carries more information about a stroke value (excess 0.819 bits against 0.691 for the following sign). With the preceding sign as the item, the information ratio net of permutation is 0.221, and the most fixed combinations are the text-opening signs 861, 817 and 820 followed by two short strokes (98%, 92% and 77%). With the next sign as the item, the most fixed are code 520 after three tall strokes (38 of 41) and code 585 after seven strokes (16 of 17); these occur in 38 distinct texts from five named sites and 16 texts from four sites respectively, so they are not one production series. The fish 220, jar 740, 390, 405 and the U-shaped 700 each take five to eight values as next items.

The overall value counts are 196 (one), 574 (two), 248 (three), 67, 47, 33, 59 (seven), 6, 4, 1 (ten) and 28 for the twelve-stroke arrangement. Seven outnumbers six and twelve outnumbers each of eight to eleven.

Short and tall strokes occur before different signs (Jensen–Shannon divergence 0.42 bits, p = 0.0001). Short strokes most often precede 390, 220, 240, 235 and 803; tall strokes precede 220, the text end, 740, 520 and 700.

## What the result decides

The protocol predicted that counting would look like Ur III and lexical numerals would show one dominant value per item. IVS stroke values are measurably more tied to their neighbours than Ur III counts, in both directions, while several signs still take many values. This places the Indus combinations between the two predictions and closer to fixed expressions than administrative counting is, with the caveat that the comparison spans different genres. The list of near-fixed combinations, in both directions, gives specific targets: whether the two strokes after the opening signs are a number at all, whether seven and twelve concentrate on particular items across sites and periods, and whether the twelve-stroke grid is a number or a single sign, which needs photographs.
