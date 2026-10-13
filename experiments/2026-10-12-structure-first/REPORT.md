# Structure before meaning: results of steps 1–6

12 October 2026. This program carried out the six-step plan in [knowledge/directions/structure-first-2026-10-12.md](../../knowledge/directions/structure-first-2026-10-12.md) under the [protocol](PROTOCOL.md) recorded before any outcome. It used only material already in the repository: the pinned Lipi corpus, the Lipi glyph font, the Mayig sign schema and the Sumerian, Akkadian, Egyptian and Linear B editions acquired on 12 October. An independent [verification](verification/VERIFICATION.md) reproduced the headline numbers, and an adversarial [review](review/REVIEW.md) led to the corrections recorded in the [responses](review/RESPONSE.md). No sound value, meaning or language is assigned.

## Results

**Sign families (step 1).** Grouping Wells codes into graphic families improves held-out prediction of rare codes beyond 200 random groupings of the same sizes (0.0219 bits per sign, p = 0.005; for unseen signs the loss falls from 14.60 to 14.19 bits). Random contiguous cuts of the Wells number line recover about three quarters of that gain (0.0164 on average, none reaching 0.0219), because the Wells catalogue already orders signs by graphic class. The Parpola-level and Mahadevan-level groupings also pass and predict unseen signs better than the families (13.93 bits). Grouping by added elements across bases does not pass. Both coders were instances of the same model working from code-ordered sheets. [Step 1](step1-signs/REPORT.md).

**Images and texts (step 2).** On bas-relief and incised tablets from Harappa, recurring texts stay with one image class and a text's image is predicted from other text types better than chance (24.8% against a 21.5% majority; 57.4% against 48.1%). On copper tablets, recurring texts stay with one image class, as Parpola (2008) observed, but held-out prediction fails. Copper sign groups specific to an image class appear on seals showing the same animal 3 times against 3.01 expected (p = 0.62); the test could detect a fivefold enrichment. [Step 2](step2-image-text/REPORT.md).

**Line divisions and alternation (step 3).** Where the catalogue marks a line division, lines recur elsewhere as units more often than windows crossing the division (23 faces against 4 under the conservative line order, 42 ties; p = 0.0003), and the chosen segmenter places a boundary at 76 of 76 divisions against 37% of other positions. The alternation statistic decides nothing at this scale. [Step 3](step3-segmentation/REPORT.md).

**Stroke numerals (step 4).** Stroke values take fewer values next to a given sign than Ur III counts take before a given commodity (3.61 against 4.53–5.15) and have a more dominant value (0.606 against 0.407–0.450); the contrast holds under unit-aware, rarefied and bias-corrected comparisons. The preceding sign carries more information about the value than the following sign. Taking the following sign as the item, code 520 after three tall strokes (38 of 41) and code 585 after seven strokes (16 of 17) are near-fixed across several sites; taking the preceding sign, the text-opening signs 861, 817 and 820 before two short strokes are. [Step 4](step4-numerals/REPORT.md).

**Rehearsal (step 5).** At Indus scale, the best unsupervised segmenter averages boundary F1 0.531 across four readable cohorts against 0.485 for a boundary everywhere; on Ur III seal legends branching entropy reaches 0.692 against 0.557. The alternation statistic is 0.056–0.069 on the true words of all four writing systems and does not separate them. [Step 5](step5-rehearsal/REPORT.md).

**Structural profile (step 6).** Indus texts begin with many different signs and end with few (asymmetry +0.260, shuffle range ±0.018; +0.149 without the 35.2% of texts ending in 740). In the comparison corpora the statistic changes sign with unit and genre, so it is descriptive, and the frozen rule leaves every candidate language tied. [Step 6](step6-language/REPORT.md).

## The hypothesis ledger against the frozen predictions

| Step | H-LANG language | H-NAME names and titles | H-ADMIN administrative code | H-EMBLEM identity labels |
|---|---|---|---|---|
| 1: bases and modifiers predict context | Not met: modifiers failed | No prediction stated | Not met: modifiers failed | Modifier prediction met; base prediction ("weakly or not at all") not given a threshold, observed strong |
| 2: image pairing and transfer to seals | Either outcome allowed | Not met: no transfer at the detectable level | Met: pairing within genre, weak or failed held-out prediction, no transfer | Not met: no transfer at the detectable level |
| 4: numeral values per item | Accounting part not met | Partly met: near-fixed items, but not one value per item | Not met: values more fixed than Ur III counts | Partly met, as for H-NAME |

Every description fails at least one of its frozen predictions. The results describe the corpus more than they choose among these four: graphic families that carry contextual information, image–text pairing that is specific to genre, recurring units respected by catalogued line divisions, a small closing sign class, and stroke groups that are partly fixed to neighbouring signs. Steps 3, 5 and 6 and the line-division result had no per-hypothesis prediction and are descriptive.

## Prior work

The graphic grouping of signs organizes the sign lists of Wells, Mahadevan (1977) and Parpola (1994). The copper image–text tie is Parpola's (1994; 2008). Recurring segments were described by Koskenniemi (1981), Mahadevan (1977) and Yadav and colleagues (2010); positional concentration of finals by Mahadevan (1977) and Yadav and colleagues (2010); fixed numeral combinations by Mahadevan (1977) and Parpola (1994). The nonlinguistic descriptions in the ledger follow Farmer, Sproat and Witzel (2004) and Sproat (2014); the entropy argument for a linguistic system is Rao and colleagues' (2009). What this program adds is held-out and permutation measurements of these properties, a calibration of the methods on readable scripts at Indus scale, and preserved failures.

## What changes next

1. Recode the sign families from sheets in shuffled order without counts, with a human coder, and check the low-agreement families and the twelve-stroke grid on CISI 1 photographs.
2. Compare seals and sealings from one excavated deposit, where the same issuer is expected on both, in place of the cross-genre count of step 2.
3. Train and score segmentation against catalogued line divisions, enlarged with multi-line tablets and with sign spacing measured on photographs.
4. Analyse numeral combinations in both directions, stratified by site and period, and test whether the two strokes after the opening signs behave like a number at all.
5. Measure the edge asymmetry at sign and word level on at least two head-initial and two head-final seal-legend corpora (for example Ur III and Old Akkadian seals against early Tamil-Brahmi and Prakrit seals and sealings) before using it for language comparison.
6. Leave unsupervised Kober-style analysis and dictionary fitting aside until boundary evidence exists.

## Status and evidence

Frozen evaluations: step 1 `run-2026-10-12` (adopted layer and run order corrected by [amendment](step1-signs/AMENDMENT-2026-10-12.md)); step 2 `run-2026-10-12-v3`; step 3 `run-linebreaks-2026-10-12-v3` and `run-alternation-2026-10-12`; step 4 `run-2026-10-12`; step 5 `run-segmentation-2026-10-12`; step 6 `run-2026-10-12` (amended before computation). Exploratory: the step 4 heterogeneity and two-stroke analyses, and every review rerun cited in the step reports. Earlier runs stay in place beside their amendments. Raw segmentations, line-division face tables, glyph sheets, review reruns and the map generator output are kept locally under `data/raw/2026-10-12-structure-first/`.
