# Shot B predictions

Written 12 October 2026 from the discovery half only and frozen the same day, before the confirmation half was read; the SHA-256 of this file is in `PREDICTIONS.sha256`. The gloss map scored here is [GLOSS-MAP.json](GLOSS-MAP.json), frozen with SHA-256 `7d1f810caebf800e6512f0e4df446c0e1fc329e69e212161ee8a5605941dc348`. The reading behind it is in [READING.md](READING.md) and the construction record in [EXPLORATION.md](EXPLORATION.md). The script that implements every rule below is [confirm.py](confirm.py).

## What is tested

The working reading assigns each of the 118 signs with at least ten discovery tokens to one of seven classes: numeral (NUM), link (LINK), affiliation (AFF), personal-name element (NAME), commodity or unit (COMM), office or role (TITLE) and closing determinative (DET). Three attributes follow from the class: `official` (AFF, TITLE, and the institutional determinatives 400 and 621), `locality` (local for NAME and COMM, pan for the rest) and `stock` (for NAME and COMM signs whose discovery tokens lie mostly on Harappa moulded or incised tablets, `H`, or on copper tablets, `MD`). If the classes describe what the signs say, they predict where seals carrying them were found, how large those seals are, which animal they show and in which period they were made. None of these variables was loaded while the map was built. The test asks whether the map predicts them better than rearrangements of its own labels among signs of similar frequency and position.

## Data, units and per-sign effects

These definitions apply to every prediction.

The data are the confirmation-half faces returned by `shots_common.load_half("confirmation", shot_dir)`. Faces are grouped into object families. A family's signs are the union of its known signs (code 000 excluded); its text length is that of its longest face; its subtype is S for `SEAL:S`, R for `SEAL:R` and other for every other seal type; its site, field animal, period and material are the most common non-missing value among its faces. The field animal is the part of `symbol` before the first colon, with `Bull1` read as the unicorn. Values `""`, `-`, `None`, `?`, `NA`, `N/A`, `none` and `unknown` count as missing. Seal area is `horizontal(mm)` × `vertical(mm)` when both are plain positive numbers. A seal is a family whose object type begins with `SEAL`.

Linked objects stay together. Families are merged within their split component: for a categorical variable the unit is a (component, value) pair whose sign set is the union over its families, so identical texts at one site count once; for size the unit is the component, carrying the mean log₂ area of its measured families, its longest text length capped at 12, and its modal subtype. A family with a missing value drops out of that variable only.

For each mapped sign present in at least 8 units of a population (5 for P4), the script computes one effect size:

- **Site concentration**: over seal site units, sites with at least 20 units are separate categories and the rest are pooled. With the sign's site counts *o*, its unit count *n* and the background site shares *p*, the effect is (G − E₀[G]) / 2n, where G = 2 Σ *o* ln(*o*/*np*) and E₀[G] is the mean of G over 2,000 multinomial draws of *n* units from *p*. This is a bias-corrected Kullback–Leibler concentration in nats per unit.
- **Size residual**: log₂ area is regressed by least squares on subtype indicators and indicators of text length 1 to 12 over all seal size units; the effect is the mean residual of the units carrying the sign.
- **Unicorn excess**: over square-seal (subtype S) units with a recorded animal, the sign's unicorn share minus the overall unicorn share.
- **Harappa excess**: over seal site units at Harappa or Mohenjo-daro, the sign's Harappa share minus the overall Harappa share.
- **Period concentration**: as site concentration, over seal units with a recorded `period`, with values of fewer than 10 units pooled. It is computed only if there are at least 100 such units and at least two values with 10 or more units; otherwise P5 is reported as not computable.

## Predictions

Each prediction is a difference between two class groups of the per-sign effects, computed over the signs eligible for that effect. The predicted direction is that the actual map's difference lies above the mean of its rearrangements. P1 and P2 form the primary test; P3, P4 and P5 are tested individually.

| ID | Implication of the reading | Statistic T | Population | Direction |
|---|---|---|---|---|
| P1 | Personal names and the commodities of local offices belong to one city; institution names, titles, links, determinatives and numerals are shared across cities | mean site concentration of local signs (NAME, COMM) minus mean of pan signs (NUM, LINK, AFF, TITLE, DET) | confirmation seal site units | above rearrangements |
| P2 | Legends of office holders and great households are cut on larger seals than private legends of the same length and shape | mean size residual of official signs minus mean of all other signs | confirmation seal size units | above rearrangements |
| P3 | The unicorn is the emblem of the shared administration, so official legends carry it more often and private names carry the other animals | mean unicorn excess of official signs minus mean of NAME signs | confirmation square-seal units with a recorded animal | above rearrangements |
| P4 | The vocabulary of Harappa's tablet series names Harappa's own goods and people, and the vocabulary of Mohenjo-daro's copper tablets names Mohenjo-daro's | mean Harappa excess of H-stock signs minus mean of MD-stock signs | confirmation seal units at Harappa or Mohenjo-daro | above rearrangements |
| P5 | Personal names follow fashions that change with time; institutional and grammatical vocabulary persists | mean period concentration of NAME signs minus mean of pan signs | confirmation seal units with a recorded period | above rearrangements |

## Rearrangement null

The null keeps every per-sign effect and every object fixed and moves the gloss records. Signs are placed in cells by two bands recorded in the map. Frequency band: discovery tokens 10–19, 20–39, 40–99 or 100 and more. Position band, over distinct intact single-line discovery texts of two or more signs: final if at least 40% of the sign's tokens are text-final, otherwise initial if at least 30% are text-initial, otherwise medial. The twelve cells hold 2 to 19 signs (listed in `GLOSS-MAP.json` under each sign's `band`). One rearrangement permutes the complete records (class, gloss, official, locality, stock) among the signs of each cell independently. The script draws 10,000 rearrangements with NumPy's `default_rng(20261012)` and recomputes T₁ to T₅ for each.

## Primary test and pass rule

Each component is standardised by its own rearrangement distribution: z_k = (T_k − mean_k) / sd_k. The primary score is **S = z₁ + z₂**, the standardised site-concentration contrast (P1) plus the standardised size contrast (P2), and the same sum is formed for every rearrangement. **The map passes if S exceeds the 95th percentile of the rearranged scores.** The report gives S, its percentile among the rearranged scores, its one-sided permutation p, and its distance from the rearrangement mean in standard deviations of the rearranged scores. A component is not computable if its actual statistic is undefined or if more than half of the rearrangements leave one of its groups without eligible signs; rearrangements that leave a group empty contribute z = 0 for that component.

P1 and P2 form the primary score because they follow most directly from the class structure: the distinction between local and shared vocabulary, and between official and private legends, is what the map adds to frequency and position. The draft summed all five components; the coordinator's review changed the primary score to P1 and P2 before freezing. In the planted dry run, real P1 and P2 effects still failed when the sum also carried P3, which the 6 October finding that seal texts do not predict the unicorn makes nearly certain to be null, and P5, which may not be computable. The stock labels of P4 were derived from object types that stand in for city, so P4 tests city vocabulary rather than the glosses.

**Individual predictions.** P3, P4 and P5 are preregistered separately. Each passes if its one-sided rearrangement p is below 0.05, and each is reported in full with T, its rearrangement mean and standard deviation, z, p and the number of eligible signs in each group. P1 and P2 are reported the same way. For reference only, the sum of all five standardised components is also reported; it has no pass rule.

**Sensitivity.** The primary test is repeated with the numeral records held fixed, so that only non-numeral records are permuted. It does not change the pass rule.

**Power.** With random withheld fields attached to the discovery half ([synthetic_dryrun_null.json](discovery/synthetic_dryrun_null.json)), S stands 0.78 standard deviations below its rearrangement mean. With planted effects ([synthetic_dryrun_planted.json](discovery/synthetic_dryrun_planted.json)), in which texts with name signs lean towards one of three sites and official legends get 25% larger linear dimensions, z₁ = 1.06, z₂ = 3.56 and S stands 3.13 standard deviations above its rearrangements, at the 100th percentile, and passes. Over eight further random synthetic datasets with 300 rearrangements each ([synthetic_seed_check.json](discovery/synthetic_seed_check.json)), S ranged from −1.71 to +2.03 standard deviations and one dataset of eight passed, at the 98th percentile.

## Secondary checks

These give the numeral, determinative and commodity classes their own object predictions. Each is reported individually and none enters S.

- **S1, commodities on cheap media.** Commodity records belong to the token and labelling genres, which use fired clay and faience more than carved steatite. Over all confirmation families with a recorded material, a family's steatite indicator (material containing "steat") minus the steatite share of its object group (seal, moulded tablet, incised tablet, copper tablet, pottery, sealing, other) is averaged within components; over signs present in at least 8 such components, T = mean residual of non-COMM signs minus mean of COMM signs, compared with the same 10,000-rearrangement procedure. Predicted: above the rearrangement mean, one-sided p < 0.05.
- **S2, the body and the man.** A legend ending 740-400 names an office as an institution and one ending 740-090 an individual holder, so the first is cut on larger seals. Size residuals (the P2 model) of seal components with a text ending 740-400 against those with a text ending 740-090, one-sided Mann–Whitney, computed if both groups are non-empty; predicted p < 0.05.
- **S3, numbered shares as grades.** In seal legends ending in a stroke numeral followed by 390, 405 or 407, the numeral counts the holder's shares; larger holdings go with larger seals. Spearman correlation between the stroke count (002 excluded) and the size residual over such seal components, computed if there are at least 8; predicted ρ > 0 with one-sided p < 0.05.

## Effect on credence and kill condition

The credence of [C-0002](../../../knowledge/conjectures/C-0002-working-reading.md) at freezing is 0.10. If the primary test passes, it rises to 0.30 and the map becomes the reference against which later meaning maps are rearranged. If the primary test fails with a positive distance, it falls to 0.06. Each of P3 and P5 that passes adds 0.03 and a passing P4 adds 0.01, since P4 tests city vocabulary; a failure of P3, P4 or P5 leaves the credence set by the primary test unchanged. The secondary checks S1 to S3 do not move the credence.

**Kill condition.** The conjecture is dead if the primary test fails and either the distance of S from the rearrangement mean is zero or below, or P1 and P2 both fall below their rearrangement means. A dead result means that the class structure built from sign behaviour and pictures carries no information about the objects beyond what frequency and position already carry.

## Prospective predictions

These concern texts and contexts that no part of this project has examined. They are scored when such material is published, independently of the confirmation result.

1. Among newly published seal legends of three or more signs, 18% to 32% open with an affiliation formula: 817, 861 or 820 followed by 002, or 920 or 692 followed by 060. (Discovery: 151 of 591, 25.5%.)
2. In newly published texts on any object that contain a stroke numeral other than 002 and one of 390, 405 or 407, a numeral stands directly before a sheaf sign in at least 55% of texts. (Discovery: 51 of 78 distinct intact texts, 65%.)
3. New Harappa moulded or incised tablets with sign 700 carry a stroke numeral plus 700, and nothing else, on at least 80% of intact faces (discovery: 203 of 237), and on any new tablet series texts ending 740-400 outnumber texts ending 740-090, while on new seals the reverse holds.
4. In an excavated deposit that holds both seals and sealings, seals with an official legend (an AFF or TITLE sign, or a final 400) have more matching sealings per seal than seals with name-only legends.
5. If an Indus office legend is ever found with a translation (a bilingual seal or a cuneiform caption naming an Indus official), the jar sign 740 corresponds to a word for a steward or storekeeper, and a legend's final 090 to a word for a person.

## What was known before writing

The withheld variables were never loaded for either half. These aggregate facts were already known from reading and are listed because they bear on the predictions. From [what-12-october-established.md](../../../knowledge/directions/what-12-october-established.md) and the README: identical seal texts share the field animal only on unicorn seals; the 65 recurring seal texts are placed at Mohenjo-daro as freely as chance would place them, and some duplicates at smaller sites stay local; most sealings carrying a seal text match seals from other cities; ten Lothal sealings with an elephant carry the text of a Mohenjo-daro fragment recorded with a unicorn; round Gulf-type seals use unusual sign orders. From `knowledge/WORKING-MODEL.md`, opened during the search for prior proposals before it was clear that it summarises the earlier size and motif outputs: 77% of known square-seal motifs are unicorns; 88 of 89 concordant identical-text pairs are unicorn pairs; unicorn seals are no more uniform in size than others; seal texts do not predict unicorn against other animals (from the 6 October sign-context-and-seals package); larger seals carry longer legends, 1.16 positions per doubling of area; 41 of the 65 recurring texts occur at more than one site. From the corpus summary and the split summary: corpus-wide face counts by site (Harappa 2,717, Mohenjo-daro 1,923, Dholavira 238 and so on) and the first rows of the split's face counts by half, site and object type. From the October 11 catalogue data: the site counts of sign 740, seen once before the statistics block was excluded. From the seal-text identity code (not its outputs): the unicorn is coded `Bull1` in `symbol`. While looking up CISI numbers for the ten quoted texts, the site prefixes of up to three discovery objects per quoted text, including three Banawali seals reading 817-002. From general archaeology: Harappa's moulded and incised tablets and Mohenjo-daro's copper tablets are city-specific genres, which P4 uses. P3 runs against the earlier finding that texts do not predict the unicorn; it is kept because the reading implies it.

## Dry runs before freezing

`python confirm.py --synthetic` runs the full procedure on the discovery half with randomly generated site, animal, size, period and material values, so the code path was exercised without reading any withheld value; `--plant` adds the planted effects described under Power. Before the coordinator's review the five-component sum on the planted data stood 1.31 standard deviations above its rearrangements and failed; that figure is what led to the change of primary score.
