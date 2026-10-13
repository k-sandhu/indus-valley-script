# Two conjecture shots: design

Recorded 12 October 2026 before any outcome of either shot was computed. The user asked the project to state bolder ideas and to take one or two shots at the script before the public-repository work. Before writing, the only counts examined were object-type totals, the component sizes produced by candidate closure rules and the face counts of the final split by half, site and object type.

## Method

Each shot states a conjecture at full strength and then tests it once. The corpus is divided into a discovery half and a confirmation half. A shot explores the discovery half without restriction: it may try any idea, refine its conjecture after seeing results and build whatever lexicon, grammar or model the data suggest. No multiplicity correction applies there, and everything found there is exploratory.

When exploration ends, the shot writes `PREDICTIONS.md`: each prediction, its statistic, its null, its pass rule and what passing or failing does to the conjecture's credence. The file's SHA-256 goes into `PREDICTIONS.sha256`. Only then can `shots_common.load_half("confirmation", shot_dir)` read the other half, and every read is logged in that shot's `confirmation-access.jsonl`. Each prediction is scored by its own rule and every result is reported, passed or failed. A later change to a prediction is a dated amendment, and the frozen outcome stays as the shot's result.

A conjecture enters the evidence record only through predictions that pass on the confirmation half, or through a prospective prediction about material not yet examined. Failed predictions lower its credence in its card under `knowledge/conjectures/`; a dead conjecture stays there with its record.

## Split

`shots_common.py` closes object families over CISI aliases and over identical complete texts: texts of three or more signs for every object type, and two-sign texts among seals. Two-sign texts on Harappa tablets are not joined, because they chain multi-faced tablets into a single 500-family component; identical two-sign tablet texts can therefore fall in both halves. Each component goes to a half by the parity of SHA-256 of the seed `2026-10-12-conjecture-shots` and the component's smallest family identifier. The result is 2,349 discovery and 2,346 confirmation families in 4,104 components; the largest component has 40 families. Face counts by half, site and object type are in [split-summary.json](split-summary.json). The assignment itself lists object identifiers and stays local in `data/raw/2026-10-12-conjecture-shots/split.json`, hash recorded in the summary.

The confirmation half is fresh only for the statistics these shots define. Earlier packages computed corpus-wide aggregates that include it: the unicorn share and motif concentration, size dispersion by motif, the relation of seal area to text length, the locality of duplicate seal texts, the small closing class, image–text pairing on tablets and the fixity of stroke values. Each shot lists the earlier results it builds on and does not count their reproduction as confirmation.

## Calibration of meaning maps

A shot that assigns functions or glosses to signs tests them as the key-calibration memo tests sound keys. The score of the proposed map on the confirmation half is compared with the scores of rearrangements of the same labels among signs of similar frequency and position. A map is informative only if it stands clear of its own rearrangements; the shot reports how many standard deviations above the rearrangement mean it falls.

## Records and writing

Each shot owns its subdirectory and its conjecture card. Tracked files hold code, protocols, gloss maps, aggregate statistics and object identifiers. Files that list full sign sequences of acquired texts stay under `data/raw/2026-10-12-conjecture-shots/`. Conjectures are written as plain claims with one credence number; the uncertainty belongs in that number and in the predictions, not in qualifying phrases. Follow `knowledge/editorial/WRITING.md`: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument.
