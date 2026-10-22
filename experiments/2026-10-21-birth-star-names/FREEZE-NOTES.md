# Changes between the protocol and the freeze

Written on 21 October 2026 (UTC) before the freeze. The [protocol](PROTOCOL.md) and [marking rule](MARKING-RULE.md) were hashed at 01:36 UTC ([PROTOCOL.sha256.txt](PROTOCOL.sha256.txt)), before any donor name was extracted and before the split existed. Everything below was decided afterwards, with the outcome that prompted it.

## Calibration

The extractor ([extract_luders.py](extract_luders.py)) went through five trial runs before its output was fixed in `data/raw/2026-10-21-birth-star-names/luders-v1/`. The trials repaired entry-number detection (entries whose first line is a year, a longest rising chain of entry numbers allowing gaps of up to 80), replaced exact-string alignment of the two scans with a global alignment on text similarity, and added "Dedication of" and "Erection of" clauses and the rule that a clause opening with an object ("Gift of a pillar … by X") takes the donor after "by". No asterism mark had been made when these changes were made.

Marker A ([mark_a.py](mark_a.py)) was revised twice after its first output and before marker B's output was opened. Version 0 fell back to the Prakrit form even when Lüders's Sanskrit equivalent named a different word, against the rule; version 1 obeyed the rule strictly and so lost names whose Sanskrit equivalent the OCR had garbled; the final version accepts a Prakrit stem when both scans read the Prakrit name with that stem. All three outputs are kept (`marking-A-v0.csv`, `marking-A-v1.csv`, `marking-A.csv`). Two equivalents joined by "or" are marked ambiguous.

The resolution pass ([resolve.py](resolve.py)) settled five disagreements, removed 26 duplicate rows where the alignment had left one clause unpaired in each scan, excluded 37 rows that marker B judged not to be personal names, and added one co-donor that marker B found in a clause. Each decision is written into the script with its reason.

## Indus exploration

The discovery results ([discovery-v1](discovery-v1/results.json)) failed the direction note's predictions as written. Prefix-plus-run compounds (T1) have 60 types in 246 tokens and Chao1 186; no modifier distinguishes three bases; fish compounds are less even than matched opening vocabulary. Fish runs without their prefix (T0) have 33 types and Chao1 38.6.

The calibration then showed that a known birth-star class is also less even than matched open vocabulary, so N2 as written points the wrong way and is retired. The [discovery checks](discovery-v2/checks.json) were chosen after these two results: runs of other sign families are as closed as fish runs at matched size, the four commonest fish runs cover 62–75% of runs at each of the four best-represented sites, the fish-run type is independent of the following sign (permutation p = 0.35), and 35.6% of discovery seal legends carry a fish run in name position.

From these results we chose, after seeing them:

- T0 as the unit of the frozen closure, profile and stability predictions, keeping T1 for the literal N1;
- the broad Brahmi marking as the reference for P3, because Lüders equates the ambiguous stems with asterisms and the strict class is dominated by Puṣya to 45%; the strict comparison is reported without credence effect;
- comparison at n* = min(fresh runs, 57), subsampling the fish runs rather than bootstrapping the 57 Brahmi names upwards. The first power run ([power-v1](power-v1/)) bootstrapped the Brahmi names to the fresh sample size; because 57 names miss the unseen asterisms, that design rejected even the claim's own model as the sample grew. [power-v2](power-v2/) uses the matched-size design;
- a minimum of 40 fresh fish runs, at which the three refined rules pass together with probability 0.88 if the discovery profile holds.

The frozen rules cannot separate the claim from a rival in which fish runs are an ordinary closed family of signs with the same frequency profile; both predict that fresh data look like the discovery half. The joint credence rule therefore gives a pass little weight and a failure of closure decisive weight.

## Shared file

`python -m bench shots --action create` added the ledger entry `078aef2d…` to `bench/spent.json`, inheriting the fish families spent by the fish-context study. The shot never reads the confirmation half, so the entry records no read.
