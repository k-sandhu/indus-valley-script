# Seal-legend units trained on catalogue line divisions, with frozen predictions for unread seals

Package of 20 October 2026, answering question cards [Q-0027](../../knowledge/questions/Q-0027-audit-catalogue-line-division-locators.md) and [Q-0028](../../knowledge/questions/Q-0028-train-segmentation-on-observed-divisions.md) and preparing the target set that day: to show, on seals no analysis has read, that a seal legend joins a variable opening to a closing formula from a small shared stock. Contributor: Claude Opus 5.5 (Anthropic) in Claude Code, a side session of the project's main session, with five Claude Opus 5.5 subagents (three plate readers, one independent segmenter, all with written briefs). Protocol [PROTOCOL.md](PROTOCOL.md), hashed before any scoring ([PROTOCOL.sha256](PROTOCOL.sha256)); [Amendment 1](AMENDMENT-1.md) was written before the held set was read, and [Amendment 2](AMENDMENT-2.md) after that read and before the predictions were frozen. Status class: `frozen-evaluation` for the segmenter; the predictions in [PREDICTIONS.md](PREDICTIONS.md) are frozen and wait for their data.

## Results

A segmenter trained only on where the catalogue breaks a legend across lines finds those breaks on faces it has not seen. On the 33 faces whose line order we verified on the plates, it cuts at 79.4% of the held-out divisions while cutting 7.7% of the other positions, a margin over cutting everywhere of J = 0.718 (95% interval 0.586–0.838, resampling groups of related objects). The Dirichlet-process segmenter, the project's saved method, reaches 0.348 on the same faces, greedy n-gram matching 0.340 and branching entropy 0.117. Both rules fixed in advance pass: the margin of at least 0.25 with a lower bound above 0.10, and the improvement over the Dirichlet process (+0.370, interval 0.227–0.512). Moving each face's divisions to random positions and refitting gives a mean J of 0.010 and a largest value of 0.222 in 200 trials. The same model trained on one line division per Ur III seal legend, and given no word divisions, beats cutting everywhere on held-out word divisions by the pre-stated margin (boundary F1 0.618 against 0.557) with 91% of its cuts correct.

The plate audit settles how the catalogue's line divisions should be read. On 75 faces with photographs, 65 divisions are confirmed and none is contradicted. The first segment of the Lipi visual code is the lower line on 55 faces and the upper line on 8, because the export's visual code reverses the catalogue's reading order as a whole; the export's reading-order field already puts the line read first at the front.

From the trained model we froze a unit inventory and a closing stock of 49 formulae, with rules that an independent agent, who saw only the rules and the lists, applied to 171 held legends with complete agreement (Cohen's kappa 1.00). On those held legends, which played no part in building the stock, 76% close with a stock formula, against 21% when each legend's signs are shuffled; their final sign pairs recur elsewhere more often than their initial pairs (79% against 60%), and only 17% of their openings occur anywhere else in the corpus. On divided seals the line break follows the closing formula: the longer line, read alone, ends in a stock formula on 36 of 58 distinct legends, against 22% if the break fell anywhere else. Four predictions about the absent CISI 3.1 seal numbers and post-catalogue finds are hashed with their power.

## 1. The plate audit (Q-0027)

The catalogue marks a division on 118 faces of the Lipi export. Of these, 43 have no plate crop: 32 carry CISI 3 numbers, whose volumes the project does not hold, and 11 have no CISI number. Three readers, each given 25 faces and a [brief](plate-audit/BRIEF.md) that kept them away from the analysis, counted the signs in each group of the 75 others and placed the code's segments on the face. Their verdicts are in [audit-table.csv](plate-audit/audit-table.csv) and summarized in [audit-summary.json](plate-audit/audit-summary.json).

| Verdict | Faces |
|---|---:|
| Legible in full / in part / not legible | 51 / 21 / 3 |
| Division confirmed / unclear / contradicted | 65 / 10 / 0 |
| Code's first segment: lower line / upper line / left, right or field / undetermined | 55 / 8 / 4 / 8 |
| Layout: wrapped second line / separate group / other | 57 / 7 / 11 |
| Confidence high / medium / low | 17 / 33 / 25 |

A division counts as confirmed when the face shows the code's groups of signs with counts that match within one sign. The pattern in the segment order has a simple cause. The export's `signs_reading_rtl` field, which earlier packages used as reading order, is the exact reversal of its visual code, so the visual code lists the line read first at the end. Read top line first, the reversed order fits 43 of the 46 faces placed with high or medium confidence. On the other three (H-60, H-97, K-16) the catalogue reads the lower line first, and on H-60 that order gives a canonical legend, 820-002 … 740-621, which suggests the editors chose the reading order from the text. One reader noted single signs set apart below the main line or in the field (621 on M-882 and M-1186, 790 on M-748 and M-1202, 930 on M-1005 and M-1101), and another found the order of signs within a line doubtful on L-5 and H-98.

Of the 75 faces the segmenter could use (no unreadable sign, no damaged edge, not boustrophedon), 33 received a plate order, 30 of them the reversed code order. The readers also confirmed the identities that the image index had given to four crops named only by volume and page, and found a duplicated impression file and a misnamed crop; these are listed for the data manifest in [DATA-UPDATE.md](DATA-UPDATE.md).

## 2. Training and scoring the segmenter (Q-0028)

The model treats a scribe's line break as a choice among the positions of a legend. Each position gets a unit score from eleven corpus statistics, among them the branching entropy rise in both directions, how often the sign before the cut ends texts and the sign after it begins them, and how often the stretch before the cut ends texts. Each statistic is computed with the scored legend's whole group of related objects (aliases, identical texts, other faces of the object) removed. A separate layout term absorbs where lines tend to end and is dropped when the model segments. It cuts wherever the unit score exceeds a threshold chosen on the training faces to maximize recall at divisions minus the cut rate elsewhere. Faces were split into five folds by groups of related objects; every face was scored by a model that never saw it or its relatives.

A division shows where a boundary must fall and says nothing about the other positions, so precision cannot be measured on Indus texts. The statistic is therefore J, recall at the divisions minus the cut rate at other positions. Cutting everywhere, cutting nowhere and cutting at random all score zero.

| Reference set | Faces | Line-trained model | Layout only | Branching entropy | Greedy n-gram | Dirichlet process |
|---|---:|---:|---:|---:|---:|---:|
| Plate order (primary) | 33 | **0.718** (0.586–0.838) | −0.006 | 0.117 | 0.340 | 0.348 |
| Catalogue reading order | 75 | 0.627 (0.523–0.724) | 0.021 | 0.106 | 0.321 | 0.361 |
| Visual code order | 75 | 0.267 (0.158–0.381) | 0.005 | −0.122 | 0.390 | 0.265 |
| Worse order for each method | 75 | 0.128 (0.038–0.226) | −0.103 | −0.212 | 0.293 | 0.230 |

On the primary set the model finds 27 of 34 divisions, cuts 18.9% of all positions and ranks the division above a given other position in 88% of pairs within a face. Greedy matching and the Dirichlet process find nearly every division (94% and 97%) by cutting at 60% and 62% of the other positions. The model depends on reading order. In the visual code's order, which is the wrong order for most faces, it falls to 0.267, and when each face takes whichever order is worse for the method, greedy matching leads. The protocol keeps that worse-order set as a guard against crediting a junction that the wrong order creates; it was the fallback for a primary set under 25 faces and was not needed. By layout, the 30 wrapped faces score J = 0.79, and the model found none of the divisions on the three faces whose second group stands apart in the picture field. Every number comes from `python -m bench segmentation` on reference and prediction files written by [run_cv.py](run_cv.py) ([cv-summary.json](run-2026-10-20/cv-summary.json), [bench outputs](run-2026-10-20/bench/)); the permutation control is [label-permutation.json](run-2026-10-20/label-permutation.json), added after the protocol.

## 3. Calibration on a readable script

Ur III seal legends are the readable genre closest to Indus seals, and their editions mark both lines and words: 309 distinct legends, 1,187 word divisions, of which 718 are line divisions. We trained the same model in each fold on exactly one line division from each of 75 training legends, the scale of the Indus training set, and scored the held-out legends against their word divisions ([sumerian_calibration.py](sumerian_calibration.py), [sumerian-summary.json](run-2026-10-20/sumerian-summary.json)).

| Method | Boundary precision | Recall | F1 | J at line divisions |
|---|---:|---:|---:|---:|
| Line-trained, 75 labels | 0.908 | 0.468 | **0.618** | 0.683 |
| Line-trained, all line divisions | 0.799 | 0.586 | 0.676 | 0.737 |
| Branching entropy | 0.635 | 0.761 | 0.692 | 0.332 |
| Dirichlet process | 0.588 | 0.622 | 0.604 | 0.276 |
| Greedy n-gram | 0.422 | 0.458 | 0.439 | 0.097 |
| Cut everywhere | 0.386 | 1.000 | 0.557 | 0 |

The calibration passes its rule (margin 0.061 against the required 0.05), and it says what the Indus J means. A model that scores about 0.7 on line divisions makes cuts that are right nine times in ten but finds only half the word boundaries; branching entropy, poor at line divisions, finds more words. The threshold learned from line divisions keeps the strongest boundary of a text and little else.

## 4. The inventory and its amendment

The protocol's inventory rule (version 1) applied that threshold to the 1,687 texts of the build corpus. It cut 4.5% of positions, and its closing stock held one formula that closed 9 of 994 seal legends ([FROZEN-v1.json](FROZEN-v1.json)). [Amendment 1](AMENDMENT-1.md) kept the model and the rules and changed one step: each legend is also cut at its highest-scoring position, the place the model would break the line, and the closing stock is every stretch of one to four signs after that position that closes seal legends in at least three unrelated groups of objects. Version 2 cuts 29% of positions (mean unit 2.2 signs), holds 225 units of two to six signs, and its stock has 49 formulae: 13 of one sign, 27 of two, 9 of three ([FROZEN-v2.json](FROZEN-v2.json)). The commonest, by the number of unrelated groups they close, are 400 (22), 090 (16), 176-740 (10), 621 (9), 679 (8), 220-520 and 923-740 (7 each), and 151, 760-740, 820 and 840-032-740 (6 each). The inventory and stock list Lipi-derived sign sequences and stay local; their hashes are in FROZEN-v2.json.

[RULES-v2.md](RULES-v2.md) states the segmentation for a reader with the two lists. The closing formula is the longest final stretch of one to four signs that is in the stock, and the opening before it is cut into the fewest inventory units. The rules define the closing by the stock alone, so they and the model's own junction agree on the closing of only 35% of held legends; the rules cut 74% of held positions because most openings contain no inventory unit ([agreement-v2-junction.json](run-2026-10-20/agreement-v2-junction.json)). The predictions use the rules.

## 5. Agreement between independent segmentations

The held set H is the 171 seal legends of three or more signs in 15% of the groups of related objects, set aside by hash before the inventory was built. A separate agent received [a brief](AGREEMENT-BRIEF.md), RULES-v2.md, the two lists and the H legends, wrote its own program from the rule text and segmented every legend. Its cuts and closing formulas match our implementation on all 776 positions and all 171 legends (kappa 1.00; [agreement-v2.json](run-2026-10-20/agreement-v2.json)), well above the operational standard of kappa 0.80 and 90% identical closings. The agent named one reading the rules force: the closing is fixed before the opening is cut, so on 47 legends a closing splits an inventory unit (a four-sign legend whose last two signs are a closing formula is cut into its first pair and that formula; the codes are in the local held-set record). That is how the rules are meant, and it is now recorded. The `rules_sha256` field of both agreement outputs holds the hash of RULES.md (version 1) through a slip in the script, since corrected; the agent used RULES-v2.md, whose hash is in FROZEN-v2.json and PREDICTIONS.sha256.

## 6. Where scribes broke the line

The known divided faces show what the second line holds. Read top line first, the joined legend ends in a stock formula on only 6 of 32 two-line faces with a plate order, against 76% of single-line legends. The top line read alone ends in one on 21, and the second line has one to three signs on 28. Over all 58 distinct divided seal legends in the catalogue's reading order, the longer line ends in a stock formula on 36 (62%); with the break moved to each other position of the same legend the rate is 22%. Three arrangements recur. Most often the long line ends in its closing formula and the short line adds one or two signs after it, as on M-79 (… 100-740 / 688), M-288 (… 740-090 / 820) and M-1202 (… 100-740 / 790). On some faces the short line is itself the closing formula, as on M-1112 (… / 220-585-740) and M-1129 (… / 544-740), and the break falls just before it. On others the short line is an opening: 820-002 begins 43 of the build corpus's seal legends and ends none, 820-060 and 692-060 behave alike, and on H-60 the catalogue reads the lower 820-002 first. In all three the break falls at one edge of the closing formula or of the opening. These divisions trained the model, so the figures are in-sample; [Amendment 2](AMENDMENT-2.md) moves divided legends into a prediction of their own for that reason, and that prediction (P4) tests only the commonest arrangement.

## 7. Prospective predictions

[PREDICTIONS.md](PREDICTIONS.md) states the claim at credence 0.6: a seal legend is a variable opening joined to a closing formula from a shared stock of about fifty, and a scribe who broke a legend across two lines broke it after the closing formula. It is scored separately on the absent CISI 3.1 seal numbers, about 50 single-line legends once the volume is acquired, and on post-catalogue finds.

| Prediction | Held-set value | Pass rule | Power at 50 legends |
|---|---|---|---|
| P1 stock closings | 0.760 (shuffled 0.207) | share ≥ lower 2.5% predictive bound (0.62 at 50) | 0.99 at H's rate, 0.50 at 0.15 lower; kill at ≤ 0.32 |
| P2 endings recur more than beginnings | 0.789 against 0.602 | one-sided McNemar p < 0.05 | 0.57 (0.78 at 80) |
| P3 openings are new | 0.171 known | share ≤ upper 97.5% bound (0.33 for 36 openings) | false pass 0.00 if openings were formulaic |
| P4 break after the closing (long shot) | 0.62 against 0.22 (in-sample) | share ≥ 0.5 and binomial p < 0.05, three or more legends | 0.25 at three legends, 0.60 at six |

The joint credence rule, the kill condition (fresh legends closing with the stock no more often than shuffled ones, in a pool of 20 or more) and the scorer are frozen in [PREDICTIONS.sha256](PREDICTIONS.sha256). [score_prospective.py](score_prospective.py) refuses to run if a hashed file changes and logs each read; run on the held set and the known divided seals it reproduces every calibration value. The statistic families for the ledger are in [spent-entry.json](spent-entry.json).

## Scope

The audit readers are AI models reading halftone crops of about 300 pixels; a quarter of their calls are low confidence, and only faces with CISI 1 and 2 photographs could be read. The primary set is 33 faces, 25 of them Mohenjo-daro seals, so the interval on J is wide and its sites are few. Line divisions label one boundary per legend, and the Ur III calibration shows that a model trained this way recovers about half the word boundaries of a known script; the version 2 inventory therefore describes strong boundaries, and the amendment that built it was chosen after version 1 was seen on the build corpus. The held set was read once, after Amendment 1 fixed the inventory; Amendment 2, written after that read, changed only how divided legends are scored, and the held set contains none. The closing stock includes common final signs (740, 400, 090, 520), so a fresh legend's stock closing partly reflects its last sign; the shuffle null measures that share. Mahadevan described the jar sign and its functional equivalents as a terminal class ("Terminal Ideograms in the Indus Script", in *Harappan Civilization: A Contemporary Perspective*, ed. G. L. Possehl, 1982, pp. 311–317), Koskenniemi's 1981 segmentation grouped the corpus into recurring sign sequences ([structure-first step 3](../2026-10-12-structure-first/step3-segmentation/REPORT.md)), and Yadav and colleagues found text endings more tightly constrained than beginnings ("Statistical Analysis of the Indus Script Using n-Grams", *PLoS ONE* 5(3): e9506, 2010). The line-trained segmenter, the plate-checked reading order and the frozen predictions are what this package adds; whether line divisions were used as segmentation evidence before has not been checked in Parpola (1994) or in Wells' publications. On the same day the [stratigraphy package](../2026-10-20-mohenjo-daro-stratigraphy/) found a twelve-sign closing stock closing about 73% of Mohenjo-daro legends at every excavated height, consistent with the 76% here from a different definition.

## Reproducing

From the repository root with Python 3.13, NumPy and SciPy, and the local inputs listed in [PROTOCOL.md](PROTOCOL.md), section 2:

```text
python -P experiments/2026-10-20-seal-legend-units/audit_summary.py --out <new dir>
python -P experiments/2026-10-20-seal-legend-units/sumerian_calibration.py --run <new run>
python -P experiments/2026-10-20-seal-legend-units/run_cv.py --run <new run>
python -P experiments/2026-10-20-seal-legend-units/label_permutation.py --run <new run> --perms 200
python -P experiments/2026-10-20-seal-legend-units/build_inventory.py --version <new>
python -P experiments/2026-10-20-seal-legend-units/build_inventory_v2.py --version <new>
python -P experiments/2026-10-20-seal-legend-units/agreement.py --version v2 --agent <agent file> --out <json>
python -P experiments/2026-10-20-seal-legend-units/calibrate.py --version v2 --out <json>
python -P experiments/2026-10-20-seal-legend-units/make_predictions.py --calibration <json> --out <json>
python -m bench selftest --out <json>
```

The bench selftest passed ([selftest.json](run-2026-10-20/selftest.json)). Reference and prediction files, the inventories, the held legends and the agent's output stay in `data/raw/2026-10-20-seal-legend-units/`.

## Boldest reading and the test that decides it

An Indus seal legend is written in two parts and sometimes a third. A variable opening names the holder; a closing formula from a stock of about fifty, half of them ending in the jar sign 740 and others standing alone as 400, 090, 621 or 679, names the office; and a short group such as 621, 790, 930 or 820 can follow in a slot of its own. When the legend did not fit on the top edge of the seal, the scribe ended the line at the closing formula and set the remainder below, so the catalogue's line divisions mark the joints of this structure. If this is right, the seals of CISI 3.1 that no analysis has read will close with the frozen stock about three times in four (at least 62% of 50 legends), their openings will be new, and every divided legend among them will break beside its closing formula. The decisive test is scoring P1 to P3 on those seals when the volume is acquired; a stock closing rate at or below 32% kills the claim.

Publication note, 21 October 2026: one complete four-sign code sequence was replaced by a description and two four-code excerpts were shortened to three codes before publication; the original report is preserved locally under `data/raw/2026-10-21-publication-screen/originals/`.
