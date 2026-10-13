# Amendment before step 6 measurements

Recorded 12 October 2026 after the step 5 segmentation rehearsal and before any step 6 statistic was computed.

The rehearsal showed that, at Indus scale, the best unsupervised segmenter recovers word boundaries only slightly better than placing a boundary between every pair of signs (mean boundary F1 0.531 against 0.485), and that alternation counted on predicted segments falls far below the gold-word rate in every readable corpus. Under the protocol's step 5 rule, segment-based statistics are therefore reported for IVS as descriptive only. Two changes follow.

1. **Whole-text asymmetry replaces segment-internal affix asymmetry as the primary profile statistic.** For each corpus, the normalized entropy of text-initial units minus that of text-final units, computed on distinct texts at the sign level, with a within-text shuffle reference. The segment-internal version is still computed on the step 3 segments and labelled descriptive.
2. **Numeral order is tested directly and calibrated.** For each corpus with numerals, the mutual information between a numeral's value and the following unit is compared with that for the preceding unit, each against 2,000 value permutations. Ur III accounts write the numeral before the commodity and Linear B writes it after the logogram, so the two calibrate the direction of the test. For IVS this also checks the reading-order normalization: if numerals are written before what they count, the following sign should carry more information about the value.

The decision rule is unchanged. A candidate language is disfavoured only by a statistic that separates known head-initial from head-final seal legends. The acquired corpora contain head-initial seal legends (Sumerian, Akkadian) and no head-final ones, so the rule is expected to leave the South Asian candidates tied; the report states this rather than inferring from one-sided comparisons.
