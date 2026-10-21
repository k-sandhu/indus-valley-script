# Protocol: seal legends and stratigraphic height at Mohenjo-daro

Package `2026-10-20-mohenjo-daro-stratigraphy`, written 20 October 2026 before the confirmation read. It tests conjecture [C-0006](../../knowledge/conjectures/C-0006-closing-stock-fixed-from-lowest-levels.md) with the two-stage design of the [conjecture shots](../2026-10-12-conjecture-shots/DESIGN.md) and its [seven later rules](../2026-10-12-conjecture-shots/REVIEW-RESPONSE.md#rules-for-the-next-shots). The predictions themselves are in [PREDICTIONS.md](PREDICTIONS.md).

## Question

Does the content of Mohenjo-daro seal legends change with the height at which the seals were found? The conjecture says that the closing stock (the final signs and two-sign closing formulae) stayed fixed from the lowest excavated levels upward, while opening signs, sign variants and legend length drifted.

## Data

The heights come from the excavators' own seal tables, joined to the local objects on 13 October ([join package](../2026-10-13-mackay-marshall-tables/README.md); values from Nitin Stephen Koshy's transcriptions, CC BY 4.0). Mackay 1938 prints each seal's level in feet against the DK datum, a fixed point in his DK-G excavation, or against the SD bench mark 2.2 ft above it. Marshall 1931 prints depth below the modern surface for seals from areas HR, VS, DK, C, E, D, SD, L, B, BJ, DM, A and F. Legends come from `data/normalized/lipi_observed_faces.jsonl` (hash `1220f559…`). [build_inputs.py](build_inputs.py) writes one row per joined object with one legend, chosen as the longest complete text without unknown signs or blanks; its counts and hashes are in [inputs/inputs-summary.json](inputs/inputs-summary.json), and the rows themselves, which carry sign sequences, stay local under `data/raw/2026-10-20-mohenjo-daro-stratigraphy/`.

A legend counts for the opening or closing position when it is complete, written on one line and readable at that position, and for length when it is complete. Legends of a single sign are left out of the position tests, where the opening and closing sign would be the same sign. Identical complete legends from the same stratum are merged at their median height so that a set of copies counts once.

## Partition

Discovery is Mackay's DK-area seals under the DK datum (625 seals with a level). Confirmation is every seal joined to Marshall's table that has a numeric depth (440 seals before the stratum rule). The excavators used different datums and dug different parts of the city, so the split by excavator gives two populations whose heights were never compared with each other and a confirmation population whose relation between legend and depth no earlier package has computed. Mackay's seals were not split for confirmation because a random half of DK-G would share a single trench, datum and building sequence with its other half.

The bench shots loader enforces the freeze. Its input for this package is the Marshall file alone; it closes families over CISI aliases and identical texts and assigns components at random to two halves. Both halves are confirmation material, and [confirm.py](confirm.py) reads the confirmation half (which the loader refuses before every registered prediction is frozen) and then the other half, after the freeze, and scores the pooled population once. The access log records both reads. The two loader halves are also scored separately as a split-half replication, which reports but does not decide.

## Height within a stratum

Depth below the modern surface is comparable only within an excavated section, since the surface itself rose and fell across the mound. Each Marshall seal is therefore ranked against the other seals of its stratum: Marshall's area letter together with the export's section (HR-A, HR-B, VS-A, DK-B, DK-C, DK-E and so on) where that cell holds at least 15 seals with a depth, and otherwise the rest of the area pooled under its letter. Strata with fewer than five seals are dropped. The rank is scaled to u between 0 (deepest) and 1 (highest), with tied depths sharing their average rank. The thirds used below are u < 1/3 and u ≥ 2/3. Mackay's seals form one stratum because one datum covers them. Ranking by Marshall's area letter alone is a pre-declared sensitivity analysis.

Every null distribution permutes u among the analysed legends within strata. This keeps each stratum's set of depths and breaks only the pairing of legends with depths, so a test asks whether legends sit at different heights within the same excavated section.

## Residual and intrusive objects

Seals were carried, kept and lost, and the excavators recorded where they were lost. A residual seal is older than the layer it lies in; an intrusive seal reached a lower layer through a pit, well or later foundation. Neither excavator's table marks either case, and Mackay's loci name no pits or wells for these seals.

The two errors bear differently on the claim. Residual seals move old legends up the sequence and blur a drift without creating one; they cannot remove a closing sign from the bottom. Intrusive seals can place late legends low. The protocol answers both. Drift tests are one-sided and their power is stated after a quarter and a half of the seals in each stratum exchange heights at random, which is how residual and intrusive finds degrade a real drift. Statements about the bottom of the sequence (P1, P2) are shares over the bottom third, never the presence or absence of a sign at the single deepest point, and they must survive deleting any of the most influential legends, so one intrusive seal cannot carry them. The contrast P5 compares opening and closing signs on the same legends, which carry the same displacement.

## The water table

The earliest deposits at Mohenjo-daro lie below the present water table. Mackay's deep digging in DK-G reached −30.5 ft against the datum, but only 82 of his 625 seals lie below −18 ft and five below −24 ft; Marshall's seals lie between 1 and 18 ft below the surface, half of them between 2.75 and 5.5 ft and only eight deeper than 10 ft. "The lowest levels" therefore means the bottom of each excavated sequence, not the founding of the city. Using ranks within strata lets every section contribute its own lowest seals in proportion to its size, rather than letting the few deep soundings decide the result. Tests use thirds of height, which hold about a hundred legends each in the confirmation population. Absence of a rare sign from a small deep sample is never read as a late arrival.

## Freshness and the spending ledger

[bench/spent.json](../../bench/spent.json) records two splits of the full Lipi input, the October 12 split and the bench round-1 split, both spent for `seal_size`, `site` and `motif`. Neither records level, depth or stratigraphy, and no earlier package computed a relation between legends and depth at Mohenjo-daro (searched 20 October: the seal-text identity review used excavation area, not depth, and the chronology package used Harappa periods). This package declares one new statistic family, `stratigraphic_level`. Earlier corpus-wide aggregates that include these seals (closing-class size, sign frequencies, seal size by motif, locality of duplicates) are not counted as confirmation here.

The loader runs with a package ledger, [shots/spent-ledger.json](shots/), which starts as a copy of `bench/spent.json`; we leave the shared ledger to the maintainer and propose the entry to add in [DATA-UPDATE.md](DATA-UPDATE.md). Once read, both the Marshall and the Mackay populations are spent for `stratigraphic_level`: Mackay's as the discovery population, Marshall's as the confirmation population.

## Examined before the freeze

From Marshall's population we looked only at what the design needed: area and section counts of seals with a depth, the depth values printed in the join table (in feet and inches, with 33 blank, 7 surface and one "B.P." entry), object types, and the numbers of seals whose legend is usable for length (333), opening and closing (317). No Marshall legend was tabulated against depth. Everything else in [EXPLORATION.md](EXPLORATION.md) was computed on Mackay's seals.

## Procedure

1. Build the inputs ([build_inputs.py](build_inputs.py)).
2. Explore Mackay's seals and derive the frozen parameters ([explore_mackay.py](explore_mackay.py) → [discovery-v2/](discovery-v2/)).
3. Estimate planted-effect power at the shape of Marshall's strata ([power.py](power.py) → [discovery-v2/power.json](discovery-v2/power.json)).
4. Create the loader split on the Marshall file, register the shot, freeze PREDICTIONS.json with the scorer, statistics module, protocol, frozen parameters and crosswalk as artifacts ([bench/](bench/), [shots/](shots/)).
5. Run [confirm.py](confirm.py) once; record the outcome, the credence change and the review in [REPORT.md](REPORT.md).
