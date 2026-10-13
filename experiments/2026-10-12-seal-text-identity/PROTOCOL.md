# Do identical seal texts behave like personal names?

Recorded 12 October 2026 before any outcome in this directory was computed. Claude Opus 5.5 runs this package unattended at the user's request to continue pursuing new ideas. It owns `experiments/2026-10-12-seal-text-identity/` and `data/raw/2026-10-12-seal-text-identity/`. Before writing, the only counts examined were eligibility totals by object type, site, motif code, period label and length, and an earlier survey count that 84 complete texts of any object type occur at more than one site.

## Question

Many Indus seal texts recur on more than one seal. If seals carried personal names, as the H-NAME description in the [structure-first ledger](../2026-10-12-structure-first/REPORT.md) supposes, a text shared by two seals would usually belong to one person or family, and the two seals would usually come from the same city. If seals carried titles of offices, institutions, clans or commodity categories present across the civilization, identical texts would be spread among cities roughly in proportion to how many seals each city has yielded. The test is whether duplicates are local.

Three further measurements sharpen the comparison: whether identical texts recur more often than a sequence model of the corpus predicts (whole-text reuse), whether seals with identical texts also share the field motif (text and emblem bundled), and where sealings and tags carry texts found on seals elsewhere.

## Population

Faces from `data/normalized/lipi_observed_faces.jsonl` (Lipi commit `fc8813a5`) with object type beginning `SEAL`, complete, single line, without unknown signs, of length at least two, at a named South Asian site (sites outside South Asia, which Study B of the published-claim tests covered, and the label "Unknown" are excluded). One face per object family: when a family has several eligible faces, the face with the lowest record identifier. Text identity is the exact reading-order sequence of Wells/ICIT codes. Motif is the part of the `symbol` field before the first colon (so all unicorn variants are one motif); seals with motif `None`, `-` or empty are kept but treated as having no motif in S4.

## Statistics

**S1, locality (primary).** For each text carried by two or more seal objects, compute the share of its object pairs found at the same site; L is the mean of these shares over texts, so each shared text has weight one. The null permutes site labels among all eligible seal objects 10,000 times, keeping site totals and texts fixed. Report L, the null mean and 95% range, the one-sided p for locality (L above the null), and L divided by the null mean. Report L separately for texts of length 2, 3 and at least 4, and a pair-weighted version.

**S2, period sensitivity.** Repeat S1 restricted to Mohenjo-daro and Harappa seals, the two sites that supply most duplicates, with site as the label. Report the share of within-Mohenjo-daro duplicate pairs whose period labels (Early, Intermediate, Late) agree, against a within-site permutation of period labels, as a descriptive check of whether duplicates are contemporaneous.

**S3, whole-text reuse.** Fit an interpolated Kneser–Ney bigram model with start and end symbols to the distinct texts of all object types (deduplicated). For each length L, the expected number of identical pairs among the n_L eligible seals of that length, if each seal text were drawn independently from the model conditioned on length, is C(n_L, 2) times the sum over texts of length L of P(text | L)². Compute that sum exactly by dynamic programming over squared transition probabilities. Report observed and expected identical pairs by length and their ratio. Because the model is fitted to the corpus that contains these texts, it overstates their probabilities, so the expectation is an upper estimate and the ratio a lower estimate of reuse.

**S4, motif concordance.** Among pairs of seal objects with identical texts where both have a motif, the share with the same motif, against 10,000 permutations of motifs among motif-bearing eligible seals within site (so site composition is held). One-sided p for concordance.

**S5, sealings and tags (descriptive).** For faces of object type beginning `TAG` with complete legible texts, list every text that also occurs on an eligible seal, with the sites of both. Counts and record identifiers only.

## Predictions

| Description | S1 locality | S3 whole-text reuse | S4 motif concordance |
|---|---|---|---|
| Personal names (one owner per text) | L well above the null; long duplicates mostly same-site | Duplicates of long texts rare | Same owner's seals may share motif |
| Titles, offices or commodity categories across cities | L near the null | Reuse far above the model, also for long texts | No requirement |
| Clan or guild identities across cities | L near the null | Reuse above the model | Concordance above the null |

Decision rules: S1 supports locality if L exceeds the 97.5th percentile of its null; it supports pan-site distribution if L lies within the central 95% and the ratio L/null is below 1.25. S3 counts as whole-text reuse if observed identical pairs of length at least four exceed the model expectation tenfold. S4 counts as concordance if the same-motif share exceeds the 97.5th percentile of its null. These rules sort the results among the descriptions; none assigns a meaning.

## Writing and records

Follow `knowledge/editorial/WRITING.md`: maximize reader comprehension; explain the idea directly in connected prose; keep necessary shared assumptions together; avoid repeated corrective comparisons or warnings that interrupt the argument. Tracked outputs contain counts, identifiers and statistics; any file listing full sign sequences goes under `data/raw/2026-10-12-seal-text-identity/`. Amendments after outcomes are dated and leave earlier outputs in place. An independent verification and an adversarial review precede integration.
