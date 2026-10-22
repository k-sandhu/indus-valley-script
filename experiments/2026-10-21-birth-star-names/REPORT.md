# Birth-star names: the calibration overturns the flatness prediction, and fresh seals will decide the closed class

We tested study 3 of the [Parpola direction note](../../knowledge/directions/parpola-forward-2026-10-20.md): the claim that the fish compounds on Indus seals are personal names taken from the birth asterism, so that they form a closed set of about 27 or 28 names used at nearly equal frequency. A known naming system gives the first result. Among 757 donor occurrences in Lüders's 1912 list of early Brāhmī inscriptions, names formed from asterisms are a closed class, but a strongly skewed one: Puṣya alone supplies 19 of the 42 strictly marked names. This real birth-star class is less evenly used than a matched sample of open name vocabulary, so the direction note's flatness prediction would fail on the system it was meant to describe. On the discovery half of a new split, the three predictions fail as the direction note wrote them. Fish runs without their stroke prefix are closed, have the Brāhmī class's profile at matched size, and keep the same dominant forms at four cities; runs of other sign families are as closed, and fish runs appear on five to six times as many legends as asterism names do among Brāhmī donors. We froze five predictions for seals no analysis has used, with a joint credence rule under which the claim dies if fresh fish runs fall outside the discovery inventory.

## Calibration on Lüders's list

We parsed the OCR text of two independent Internet Archive scans of the list ([sources and rights](SOURCES.md)), aligned their "gift of", "dedication of" and "erection of" clauses and took the donor named in each, with the Sanskrit equivalent that Lüders prints beside Prakrit names. Of 819 donor rows, 26 were duplicates left by clauses that only one scan aligned, and marker B judged 37 to be villages, committees, clan labels or OCR debris, leaving 757 personal donor occurrences after one co-donor was added. A [marking rule](MARKING-RULE.md), hashed before extraction, lists 25 asterism labels and their Sanskrit and Prakrit stems and flags seven stems with a common non-astral meaning. Marker A applied it by script and marker B, a separate agent that saw only the rule and the rows, applied it by reading. They agree on 814 of 819 rows (Cohen's kappa 0.97 for asterism against none, 0.94 for the strict label); a logged third pass settled the five disagreements ([resolve.py](resolve.py)).

| Statistic | Asterism names, strict | Asterism names, broad | Other name elements |
|---|---:|---:|---:|
| Occurrences | 42 | 57 | 697 |
| Share of personal donor occurrences (95% interval) | 5.5% (4.1–7.4%) | 7.5% (5.9–9.6%) | |
| Distinct types (of 25 asterism labels) | 12 | 16 | 467 |
| Chao1 | 17.0 | 21.0 | 2,282 |
| Commonest type and its share | Puṣya, 0.45 | Puṣya, 0.33 | "Buddha-", 0.03 |
| Normalised entropy H/ln S | 0.775 | 0.835 | 0.944 |
| Zipf slope | −1.10 | −1.05 | −0.44 |

Other name elements are first members of names after a second member such as -datta or -mitra and a hypocoristic suffix are removed, with OCR variants merged at 0.85 string similarity. Drawn 9,999 times at the asterism class's own size, they have a median of 39 types, normalised entropy 0.993 and a commonest-type share of 0.048; the asterism class lies outside all 9,999 draws on every statistic ([calibration](calibration-v1/calibration.json)). A birth-star class is therefore recognisable in a real name corpus at a few dozen occurrences, by closure and by one favoured member, not by evenness. A small sample of an open vocabulary consists mostly of names that occur once, so its normalised entropy approaches one; a closed class with a favourite stays well below. The moon spreads births evenly over the asterisms, but the donors' names are not spread evenly: Puṣya and its Prakrit forms (Pusa, Tisa, Posi) dominate, as the auspicious reputation of Puṣya in later Indian tradition would lead one to expect.

## Exploration on the discovery half

We created a split with seed `2026-10-21-birth-star-names` through the bench shots loader (2,372 discovery and 2,323 confirmation families) and read only its discovery half. The split inherits the spent fish families of the fish-context study, so every Indus number here is exploration. The discovery half holds 666 distinct clean seal legends, 257 with a fish sign. A fish compound is a maximal run of fish-family signs with the stroke group immediately before it (unit T1); it stands in name position when at least one sign follows it, since in the working model the last sign of a legend belongs to the title. There are 246 such compounds and 20 final ones ([results](discovery-v1/results.json)).

The direction note's three predictions fail as written. N1 asked for a Chao1 between 24 and 45; prefix-plus-run compounds have 60 types, 36 of them seen once, and Chao1 186. N2 asked for fish compounds more even than matched opening vocabulary; their normalised entropy is 0.817 against a median of 0.929, with a commonest-type share of 0.122 against 0.053. N3 asked for one modifier that distinguishes exactly three fish forms in pairs; in name position the forms are plain (80 occurrences), top-marked (73), capped (60), barred (46) and inner-marked (24), with a few rare ones, and no modifier pairs more than two bases. The calibration shows that N2 points the wrong way for any real birth-star class, so we retired it rather than refine it.

The stroke prefix carries most of the openness. Without it, fish runs (unit T0) have 33 types and Chao1 38.6, and their Good–Turing novelty, the expected share of new types in new data, is 0.041. Further checks, chosen after these results ([checks](discovery-v2/checks.json)), place that closure in context:

- Fish runs are not unusually closed for a sign family. At 246 runs the B790 family has 29 run types and Chao1 40 against 33 and 38.6 for fish; at 124 runs B090 has 30 types and Chao1 33.8 against 25 and 35.0 for fish; and the jar family B740 has 8 run types in 143 occurrences.
- At the Brāhmī sample size of 57, fish runs have 17 types, normalised entropy 0.821 and a commonest-type share of 0.246, inside the 95% ranges of bootstrap samples from the broad Brāhmī class (0.754–0.907 and 0.211–0.456). Against the strict class the top share falls below its range (0.310–0.595).
- The four commonest runs (plain, top-marked, capped, barred) cover 66% of runs at Mohenjo-daro, 62% at Harappa, 75% at Lothal and 71% at Dholavira.
- The run type is independent of the sign that follows it (mutual information 0.098 nats, permutation p = 0.36 over 246 runs). An earlier unversioned run of the same test with another seed gave 0.35.
- 35.6% of seal legends (95% interval 32.0–39.3%) carry a fish run in name position, five to six times the Brāhmī share of asterism names (5.5–7.5%).

The prefixes show a pattern of their own. The long pair of strokes stands before the plain fish in 26 of its 27 occurrences, and three short strokes stand before the plain fish in all five, while the short pair spreads over seven fish forms (60 occurrences). Parpola reads the long pair as a separate word, *veḷ*, joined to the plain fish as "white star", and three strokes with the fish as Mṛgaśiras; the discovery half agrees that these two prefixes belong to the plain fish and the short pair does not. We did not test this.

## What was frozen

Before freezing we simulated the refined rules at 40, 60, 100 and 150 fresh runs ([power](power-v2/power-broad.json)). A first design bootstrapped the 57 Brāhmī names up to the fresh sample size; since 57 names miss the asterisms not yet seen, it rejected even the claim's own model as the sample grew ([power-v1](power-v1/)), and we replaced it by subsampling the fish runs down to the Brāhmī size. The [freeze notes](FREEZE-NOTES.md) record this and every other choice made after a result was seen.

The [frozen predictions](PREDICTIONS.json), the [scorer](score_fresh.py), its [library](birthstar.py), the [reference data](frozen-reference.json), the protocol, the marking rule, the freeze notes, the discovery inventory, the calibration output and the sign coding were frozen through `python -m bench shots --action freeze` at 03:36 UTC on 21 October ([freeze record](freeze-v1.json), [hashes](PREDICTIONS.sha256)). The confirmation half of the split was never read ([access log](round.access.jsonl)).

| ID | Prediction on fresh seals | Pass rule | Discovery value | Pass probability if the discovery profile holds, 40–150 runs |
|---|---|---|---|---|
| P1 | Direction note N1 on prefix-plus-run compounds | Chao1 24–45, opening vocabulary above 45 in 95% of matched draws | Chao1 186, fails | |
| P2 | Fish runs stay inside the 33-type discovery inventory | At most 15% of runs of new types | Novelty 0.041 | 0.995–1.0 (open vocabulary: 0.0–0.02) |
| P3 | Fish runs have the Brāhmī asterism profile | Normalised entropy and top share inside the broad Brāhmī 95% ranges at n* = min(runs, 57) | Inside | 0.83–0.94 (site-specific profile: 0.02–0.22) |
| P4 | The four commonest discovery runs keep their share | 0.50–0.85 of fresh runs | 0.667 | 0.98–1.0 (site-specific: 0.01–0.08) |
| P5 | Direction note N3 | One modifier with exactly three balanced base pairs | Fails | |

One joint rule governs all five. Conjecture [C-0013](../../knowledge/conjectures/C-0013-fish-runs-are-birth-star-names.md) starts at 0.03. If P2 fails, it falls to 0.005 and the claim is dead; if P2 passes, it becomes 0.06 when P3 and P4 both pass, 0.03 when one passes and 0.01 when neither does; P1 and P5 add 0.04 only if both pass with P2. A pass weighs little because the frozen rules cannot separate the claim from a rival in which fish runs are an ordinary closed family of signs with the same profile; both predict that fresh seals look like the discovery half.

Scoring needs at least 40 fish runs in name position on seals the pinned corpus does not hold, about 110 fresh seal legends at the discovery rate. The 244 absent CISI 3.1 numbers between seals, tablets and sealings, the 73 such numbers in CISI 3.2 and the published post-catalogue seals, above all Dholavira's, are the expected sources ([scoring instructions](SCORING.md)).

## Boldest reading and the test that decides it

The boldest reading these results support is that the Harappans named people after their birth asterism and wrote that name as a run of fish signs: a closed list of about 30 to 40 star names built from five fish forms, in which the plain fish was the favourite, as Puṣya was among Brāhmī donors two thousand years later, while the stroke groups before a fish are separate words, the long pair and the three short strokes belonging to the plain fish alone. Fresh seals decide whether the list is closed. If more than 15% of their fish runs are of types not seen in the discovery half, the runs are an open vocabulary and the claim is dead. If they stay inside the list, keep the Brāhmī profile and keep their dominant forms at Dholavira and the other new sites, the claim survives at 0.06, and the decisive evidence must then come from something tied to birth: legends naming a holder and a parent, whose two fish runs should behave as independent draws from the same list.
