# Timing and exact-space checks before the calibration study

Written October 2, 2026 before the pilot. The question is whether the manuscript's full-procedure conditional references produce the stated rejection rates when the null-generating law is known. This pilot selects a computational budget by timing, then a separate main protocol fixes the number of synthetic datasets and null draws.

The pilot uses forty three-sign records, eight codes and two equally sized metadata strata. Within each stratum, positions are independent categorical draws. Slot probabilities are rotations of [.20,.16,.14,.12,.11,.10,.09,.08]. The unique family conditions the entire draw on distinct complete strings. A physical-copy family draws twenty independent latent strings and copies each twice on a shared artifact; positions remain independent at the latent-object level.

Run three datasets per family, with nine fitted reference draws per dataset. For physical copies, compare record-wise column permutations with block-preserving column permutations of latent objects. Rebuild artifact/string groups, five outer folds and three inner folds on every corpus, using the unchanged nested selection grid 5/20/100/500/2000 and gain statistic. Preserve the original code snapshots. These small pilot counts estimate timing and feasibility, rather than rejection rates.

The exact check enumerates six labeled three-sign binary rows with three zeros and three ones in each column. There are `choose(6,3)^3 = 8,000` equally likely labeled tables. Count the distinct-row subset, derive each table's uniform probability and the probability after rejection conditioning. Check the shuffle sampler against this finite space, preserve cell margins and enumerate exact integer-adjacency-statistic p-values with ties included.

A separate four-latent-object binary example, copied twice, compares the block-preserving conditional space with ordinary record-column permutations. This makes the physical-copy assumption visible in a space small enough to count exactly.

Before selecting the main budget, verify source hashes, group recomputation, exact margin preservation, conditional rejection sampling, block consistency and plus-one exceedance counting. Record feasibility failures and their data rather than silently removing difficult datasets.
