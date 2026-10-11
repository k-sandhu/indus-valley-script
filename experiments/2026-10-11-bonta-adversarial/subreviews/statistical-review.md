# Statistical computation review, October 11, 2026

The main position counts, shuffle expectations, saved permutation probabilities, BH adjustments, family counts and maximum-statistic values reproduce from the frozen inputs. One site-enumeration bug omits 29 code/site summaries across 24 codes. It changes no pooled result or shortlisted ranking. The maximum statistic can also use analytic conditional moments to remove a small avoidable asymmetry in its Monte Carlo normalization.

This review read `analyze.py`, `robustness.py`, `hypotheses.py`, the run-v2 diagnostic JSONs and `REPORT.md`. It recalculated counts from the pinned clean-face input and reused the saved 5,000 permutation count arrays. It did not generate new permutations, edit code or alter frozen outputs. This document is the only path owned and written by this reviewer.

## Site enumeration needs correction

In [analyze.py](../analyze.py#L81), lines 81–85 obtain the list of sites from one representative record per distinct string, then build each site's frame using every record. A site disappears if all its strings are duplicated at sites with an earlier representative record ID. The representative-site counts have their stated meaning; they should not determine which sites receive a sensitivity calculation.

Keep `sites` for `representative_site_counts`, and replace `for site in sites:` with `for site in sorted({r['site'] for r in rs}):`. Here `rs` already contains every clean face bearing the code. Preserve the existing set comprehension for the site's distinct-string frame. A string shared by two sites should enter each site's separate sensitivity; site totals therefore need not sum to the pooled unique-text count.

The missing summaries are:

| Wells code | Omitted site or sites |
|---|---|
| W003 | Nausharo |
| W004 | Banawali |
| W017 | Rupar |
| W033 | Rajanpur |
| W061 | Banawali, Kalibangan, Lakhanjo-daro |
| W255 | Rajanpur |
| W390 | Banawali, Nausharo |
| W400 | Rajanpur |
| W422 | Dholavira |
| W436 | Rajanpur |
| W463 | Chanhu-daro |
| W482 | Chanhu-daro |
| W495 | Kalibangan |
| W503 | Chanhu-daro |
| W520 | Kanmer |
| W531 | Kalibangan |
| W585 | Rupar |
| W690 | Rajanpur |
| W700 | Chanhu-daro, Rajanpur, Unknown |
| W740 | Rajanpur |
| W776 | Kalibangan |
| W803 | Banawali |
| W817 | Banawali |
| W840 | Kalibangan |

Only W400 is shortlisted. Its missing Rajanpur summary is one token, one final occurrence and shuffle expectation 0.200. The Harappa and Mohenjo-daro values remain unchanged. A new diagnostic amendment can reconstruct all site frames from `data/normalized/lipi_clean_rtl_singleline.jsonl`, copy the original pooled results, and record the previous and corrected site sets. The input hash recorded in run-v2 is `9e539daef4d5a7efbe3c5f34b73e14058eec1c5e888c749bc2eafb0f08084ba8`. No position permutations need to be rerun.

## Maximum-statistic normalization and deterministic cells

[robustness.py](../robustness.py#L21), lines 21–28 estimate each null mean and standard deviation from the saved permutations. Each shuffled count contributes to its own estimated normalizer, while the observed count does not. Consequently, the usual plus-one rank expression is not exactly permutation-symmetric. This is a small calibration qualification for these results, rather than an observed ranking failure.

The null moments are available analytically. For one text of length L containing n copies of a code, write p = n/L. The expected counts are p, (L−2)p and p. Initial and final variances are p(1−p); medial variance is 2(L−2)p(1−p)/(L−1). Add these means and variances across the distinct texts under the declared independent within-text shuffle reference. Standardize both observed and saved shuffled counts with those fixed moments, then take the common maximum as before. This uses the existing arrays and requires no new random draws.

I applied this arithmetic as a sensitivity without saving or replacing an endpoint. W142's medial maximum-statistic value changes from 0.478104 to 0.461108. The shortlisted closing-sign values remain at 1/5,001, except W161, which remains 8/5,001. W130 remains 1.0. The numerical-marker results for W001, W002 and W060 also remain at 1/5,001. Thus the distinction between structural carrier/closing signals and W142's pictorial evidence survives this normalization change.

Zero null variance is handled coherently for this dataset. All 437 zero-variance code/slot cells in the full 713-code array have exactly zero analytic variance; none is merely unsampled in 5,000 draws. Every corresponding observed count equals its deterministic null mean. Of the 1,788 previously new code/slot comparisons, 400 are deterministic and 1,388 enter the maximum with nonzero variance. Omitting the deterministic cells is appropriate. [REPORT.md](../REPORT.md#L28) should state the 1,388 active comparisons explicitly when describing the standardized maximum. The 1,788 count remains correct for the BH adjustment.

## Checks that passed

The input has 2,930 faces, 2,469 families and 1,859 distinct strings. All 1,859 strings in this particular clean frame have length at least two. Every observed code exists in the 713-code index. The permutation arrays preserve each code's total in every draw; their largest saved cell is 553, comfortably within the signed 16-bit storage range.

Independent count arithmetic matched every observed position and rounded expectation in `position-audit.json`. Recomputed tail counts and BH arithmetic matched the saved probabilities and the count of 40 codes with at least one q below 0.05. All selected maximum-statistic values reproduced from the saved arrays. The deterministic longest-face-per-family reconstruction matched all family sensitivities; this is a reweighting, and the report correctly retains shared-mould and production-tradition limitations.

The seven rows of the report's closing-sign table match the diagnostics. W154/W156 have four exact substitution templates, W151/W161 have two, W400/W151 have two and W400/W527 have one. W400 follows W740 in 73 adjacent positions, as stated in `hypotheses.py`. The three lexical rows agree on motivating-family count, alternatives, selected-residual coverage and empty literal intersections. W154 and W158 each occur once per relevant distinct string and never co-occur in one of those strings; the stated Fisher table and its 0.006246759 value are correct. Its post-selection and archaeological-dependence scope remains necessary.

The report does not convert ordering probabilities into probabilities of Sanskrit meanings. BH values summarize the selected ordering tests; the common maximum addresses selection across the declared code/slot family under the global shuffle reference. Neither procedure resolves the untested semantic mapping, language assumption or archaeological independence.
