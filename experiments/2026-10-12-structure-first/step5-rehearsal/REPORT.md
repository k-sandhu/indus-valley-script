# Step 5: unsupervised segmentation at Indus scale, rehearsed on readable scripts

The rehearsal ran the step 3 segmenters on Sumerian, Egyptian and Akkadian records with word boundaries hidden, at the size and length distribution of the Indus corpus, and scored them against the editions' word divisions. Averaged over the four cohorts, the best segmenter places boundaries only a little better than cutting between every pair of signs. On Ur III seal legends, the cohort closest in genre to Indus seals, branching entropy does clearly better. The alternation statistic planned for step 3 barely separates the four writing systems even on their true words. Endpoint: [run-segmentation-2026-10-12](run-segmentation-2026-10-12/summary.json). The numeral rehearsal is reported with step 4.

## Cohorts

All 309 distinct Ur III seal legends with complete word units (mean 10.95 signs); 1,859 Sumerian administrative lines matched to the IVS length distribution (mean 4.59 signs, mean gold word 1.62 signs); 940 Egyptian glyph sentences and 1,223 Akkadian letter lines, matched as far as their length ranges allow. The Dirichlet-process segmenter ran 2,000 annealed sweeps. Linear B, the script on which Kober's method was developed, was named in the plan but left out: the acquired sample has 269 lines.

## Segmentation

| Cohort | Branching entropy | Greedy n-gram | Dirichlet process | Boundary everywhere |
|---|---:|---:|---:|---:|
| Ur III seal legends | 0.692 | 0.439 | 0.604 | 0.557 |
| Sumerian lines | 0.340 | 0.606 | 0.691 | 0.675 |
| Egyptian glyph sentences | 0.325 | 0.387 | 0.396 | 0.350 |
| Akkadian letter lines | 0.368 | 0.411 | 0.433 | 0.358 |

Values are boundary F1. The Dirichlet-process segmenter has the highest mean (0.531, against 0.461 for greedy matching and 0.431 for branching entropy) and was fixed as the step 3 segmenter before Indus segments were examined; its mean margin over the everywhere-boundary placement (0.485) is 0.046. On the seal legends, branching entropy reaches boundary F1 0.692 and exact-word F1 0.448, against 0.557 and 0.187 for a boundary everywhere. Exact-word F1 for the Dirichlet process is 0.30, 0.49, 0.20 and 0.26 in the four cohorts.

## Alternation

On the editions' own words, the share of stems occurring with at least two different final signs is 0.056 (seal legends), 0.064 (Sumerian lines), 0.069 (Egyptian) and 0.061 (Akkadian), although the four writing systems mark morphology in different ways, from Akkadian syllabic case endings to Egyptian word-final determinatives. On Dirichlet-process segments the rates fall to 0.021, 0.031, 0.011 and 0.015, that is, 38%, 48%, 16% and 25% of the gold rates.

## What the rehearsal decides

The alternation statistic does not separate the known systems even with perfect segmentation, so under the protocol it is descriptive for IVS, and the step 6 amendment replaced segment-internal statistics with whole-text ones. Segmentation quality depends on genre and method: averaged over cohorts it is weak, while on seal legends branching entropy recovers a useful share of word boundaries. A segmentation claim for the Indus texts therefore needs a check against boundary evidence such as the catalogued line divisions in step 3. The same applies to frequent-n-gram segmentations of the Indus corpus, such as that of Yadav and colleagues (2010): this rehearsal suggests how far an unsupervised segmentation can differ from true word boundaries at this scale.
