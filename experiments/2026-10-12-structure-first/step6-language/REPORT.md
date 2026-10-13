# Step 6: a descriptive structural profile; the frozen rule leaves every candidate tied

Indus inscriptions begin with many different signs and end with few. The asymmetry is large, and it remains after the texts ending in the commonest final sign are removed. In the readable comparison corpora the same statistic changes sign with the unit (sign or word) and with the genre, so it does not track head direction there and is descriptive for IVS. Under the frozen rule no candidate language is disfavoured. The endpoint is [run-2026-10-12](run-2026-10-12/summary.json), computed after the [pre-run amendment](AMENDMENT-2026-10-12.md); the [typology table](typology.json) was written before any step 6 statistic, from memory of the cited grammars, and has not been checked against them. Checks marked as review come from the [review](../review/REVIEW.md) and are post-outcome.

## Prior work

The concentration of a few signs at the ends of Indus texts appears in Mahadevan's 1977 positional tables, where the "jar" sign is the commonest terminal, and in Yadav and colleagues' (2010) analysis of text beginners and enders. This step measures it with a within-text shuffle reference and sets it beside readable seal and record corpora.

## Edge asymmetry

Normalized entropy of the first unit minus that of the last unit, over distinct texts of at least two units. The reference shuffles units within each text. The Indus reading direction is the catalogue's: the clean frame contains only texts the catalogue marks right to left, and which end is final follows that judgement.

| Corpus | Unit | Texts | Initial | Final | Asymmetry | Shuffle 95% range |
|---|---|---:|---:|---:|---:|---|
| IVS, clean distinct texts | sign | 1,859 | 0.768 | 0.508 | +0.260 | −0.017 to 0.018 |
| IVS, seal texts only | sign | 1,312 | 0.755 | 0.486 | +0.270 | −0.021 to 0.020 |
| Ur III seal legends | sign | 309 | 0.503 | 0.707 | −0.204 | −0.039 to 0.041 |
| Ur III seal legends | word | 308 | 0.861 | 0.782 | +0.079 | −0.064 to 0.062 |
| Egyptian glyph sentences | sign | 1,696 | 0.670 | 0.626 | +0.044 | −0.017 to 0.018 |
| Egyptian glyph sentences | word | 1,301 | 0.721 | 0.828 | −0.107 | −0.018 to 0.018 |
| Ur III tablets | sign | 1,067 | 0.550 | 0.545 | +0.005 | −0.017 to 0.017 |
| Ur III tablets | word | 1,065 | 0.517 | 0.521 | −0.004 | −0.018 to 0.017 |

In IVS, 35.2% of clean texts end in the "jar" sign 740 and the three commonest finals cover 51.8%. Removing the texts that end in 740 leaves an asymmetry of +0.149 (review), so the concentration does not rest on one sign. The Ur III sign-level value reflects how personal names are spelled: 78 of the 309 legends begin with *ur* and 58 with *lu₂*, the first elements of names of the Ur-DN and Lu₂-DN type, and only 30 begin with the divine determinative, whose removal moves the value from −0.204 to −0.182 (review). At word level the Ur III legends have the same sign as IVS. Sumerian and Egyptian, both of which place genitives after the noun, take both signs of the statistic depending on the unit, so in this material its sign follows unit and genre rather than head direction. The three Akkadian seals in the sample are too few to measure.

## Other measures

Profile item (iv), segment length, is reported in step 3: Dirichlet-process segments average 1.39 signs. The twenty Indus signs with the most diverse neighbours relative to their frequency sit slightly before the middle of texts (mean position 0.435 against 0.521 for all eligible tokens); the Ur III word-level comparison rests on four eligible words and is not interpreted. The numeral-order test, as frozen, detected Linear B's commodity-then-number order but not Ur III's number-then-commodity order; the review traced that failure to the Ur III value definition, which drops units, and with units kept the test detects Ur III's order (following 0.735 against preceding 0.514 bits). For IVS, the preceding sign carries more information about a stroke value than the following sign in both versions. Because the working definition changed after the outcome, this remains descriptive; step 4 reports what it implies for the numeral items.

## Typology and decision

The South Asian candidates in the [typology table](typology.json) (Proto-Dravidian, Old Indo-Aryan, Munda, Burushaski) place genitives and adjectives before the noun and mark case with suffixes, and Elamite, Sumerian and Akkadian place genitives and adjectives after the noun, as recalled from the cited grammars. The frozen rule disfavours a candidate only through a statistic that separates known head-initial from known head-final seal legends. The acquired corpora contain no head-final seal legends, and the one statistic measured changes sign with unit and genre within the head-initial corpora, so no candidate is disfavoured and all remain tied.

For this statistic to inform the rule, it needs to be measured at sign and word level on at least two head-initial and two head-final seal-legend corpora, for example Ur III and Old Akkadian seals against early Tamil-Brahmi and Prakrit seals and sealings, and to separate them consistently.
