# Step 1: graphic families improve prediction of rare signs, and most of the gain is already in the Wells order

Grouping the Wells codes into graphic families improves held-out prediction of rare codes beyond random groupings of the same sizes. Random contiguous cuts of the Wells number line recover about three quarters of that gain, because the Wells catalogue already arranges signs by graphic class; the hand-coded families add about 0.005 bits per sign beyond those cuts. The published Parpola-level and Mahadevan-level groupings also pass and predict unseen signs better than the families. Grouping signs by added elements across different bases does not pass. The endpoint is [run-2026-10-12](run-2026-10-12/summary.json); the [amendment](AMENDMENT-2026-10-12.md) records the adoption rule, the run order and the post-outcome comparisons, which were computed in the [review](../review/REVIEW.md).

## Coding and agreement

Both coders are instances of Claude Opus 5.5: the session running this program, and an agent it launched with only the glyph sheets and the vocabulary. The sheets show the Lipi font's renderings of the catalogue drawings in Wells code order, 48 to a sheet, each labelled with its code and token counts. The first coder coded all 722 font codes as a base family plus modifiers from a fourteen-term vocabulary, with stroke counts for numerals ([sign_components_v1.tsv](sign_components_v1.tsv)); the second produced [components_coder2.tsv](second-coder/components_coder2.tsv) and [notes](second-coder/NOTES.md). Over the 577 codes attested in the clean frame, the adjusted Rand index between the family partitions is 0.884, and 0.975 with codes weighted by tokens. The families follow the Wells order closely: 479 of 576 adjacent attested codes share a coder-1 family, and the two coders agree on where to cut between adjacent codes with kappa 0.79. Because both coders are the same model working from the same ordered sheets, the agreement measures consistency of the procedure and not independence of human judgement. Modifier agreement (Cohen's kappa): enclosure 0.93, dots 0.88, yoke 0.80, inner marks 0.75, doubling 0.75, cap 0.74, hold 0.61, hatch 0.60, pole 0.60, side 0.58, bar 0.58, crossing lines 0.56, top 0.54, stylistic variant 0.38.

## Inventories

| Inventory | Types | Occurring once | At most twice | Top 30 token share | Entropy (bits) |
|---|---:|---:|---:|---:|---:|
| W, Wells code | 577 | 37.1% | 52.5% | 57.8% | 6.92 |
| V, identical base, modifiers and count | 310 | 24.5% | 33.9% | 64.0% | 6.42 |
| P, Mayig (Parpola-level) class | 444 | 35.6% | 48.2% | 62.3% | 6.62 |
| M, Mahadevan number | 438 | 35.8% | 47.9% | 62.3% | 6.61 |
| B, base family (coder 1) | 78 | 6.4% | 10.3% | 91.3% | 4.68 |

The largest families are the human figure (57 attested codes, 614 tokens), the oval or lens (43 codes, 760 tokens), the U-shape (41 codes, 381 tokens), the short-stroke numerals (26 codes, 960 tokens), the diamond (23 codes), the fish (21 codes, 810 tokens) and the bracket (20 codes).

## Primary test

Every model predicts the original Wells code. The interpolated Kneser–Ney bigram baseline gives 5.893 bits per sign over 8,535 held-out signs in five grouped folds; a unigram gives 7.058. Interpolating the baseline with the class model helps by itself: with every code in its own class the gain is 0.0029 bits, so the table also gives gains net of that identity partition. The random-partition null includes the same effect.

| Grouping | Groups (vocabulary) | Gain (bits/sign) | Net of identity partition | Random 95th percentile | p (200 partitions) | Passes |
|---|---:|---:|---:|---:|---:|---|
| Base family, coder 1 | 85 | 0.0219 | 0.0190 | 0.0061 | 0.005 | yes |
| Base family, coder 2 | 63 | 0.0222 | 0.0193 | 0.0069 | 0.005 | yes |
| V | 359 | 0.0052 | 0.0023 | 0.0019 | 0.005 | yes |
| P | 555 | 0.0046 | 0.0017 | 0.0021 | 0.005 | yes |
| M | 551 | 0.0043 | 0.0014 | 0.0024 | 0.005 | yes |
| Modifier signature across bases | 271 | 0.0035 | 0.0006 | 0.0044 | 0.114 | no |

The gain is concentrated in rare signs. For held-out signs never seen in training, loss falls from 14.60 bits to 14.19 with coder 1's families, 14.22 with coder 2's, 13.93 with the P grouping and 13.94 with M. For signs seen once or twice the families give 11.29 against 11.44; signs seen ten or more times do not change (4.847 to 4.859).

**Post-outcome comparisons (review).** One hundred random partitions made by placing 85 cuts on the Wells number line, with no visual judgement, gain 0.0164 bits on average (5th–95th percentile 0.0124–0.0197, maximum 0.0212). All exceed the frozen null's 95th percentile and none reaches the coder-1 gain of 0.0219. Splitting the numeral families into single codes leaves the family gain at 0.0231; rebuilding folds so that one-substitution near-copies cannot cross them gives 0.0265; adding the end symbol gives 0.0222. One component of 206 linked texts puts 537 texts in fold 0 against 312–344 in the others.

## Modifiers

Modifiers are productive: inner marks occur on 24 bases (121 codes, 1,199 tokens), side elements on 25, doubling on 24, hatching on 23, top elements and enclosure on 15 each, a cap on 11. Pooled into modifier signatures, they do not improve prediction beyond random groupings (net gain 0.0006 bits). Tested one at a time after the outcome, none of nine modifiers passes (p from 0.14 to 0.93). With the coarse vocabulary and its moderate agreement, this shows that no modifier class, as coded, carries a context effect detectable at this corpus size.

## What the result decides

The protocol predicted that H-LANG and H-ADMIN would pass both the base and the modifier tests, and that H-EMBLEM would pass the base test weakly or not at all and fail the modifier test. Both H-LANG and H-ADMIN failed their modifier prediction. H-EMBLEM's base prediction was not given a threshold in advance, so the strong base result weakens it only informally. None of the four predictions matched the observed pattern as stated.

Under the protocol's coarsest-grouping rule, coder 2's families are the adopted feature layer (see the amendment). The result supports what Wells built into his catalogue order and what Mahadevan (1977) and Parpola (1994) built into their sign lists: graphically related codes occur in related contexts. Its contribution is a held-out measurement of that information, with the catalogue order as a comparator. The concurrent [allograph study](../../2026-10-12-published-claim-tests/allographs/REPORT.md) finds by substitution and neighbour divergence that Yajnadevam's graphic variant groups share contexts.

A further coding round should use sheets in shuffled order without counts, include a human coder, and check the low-agreement families (hatched creatures, bent bands, outline chevrons) on CISI 1 photographs.
