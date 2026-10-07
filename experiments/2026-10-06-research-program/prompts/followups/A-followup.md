# Follow-up for package A from the coordinator

A Sonnet review is in `experiments/2026-10-06-modern-restoration/REVIEW.md`, with scripts and aggregate outputs in `review/`. It reproduced every headline number, confirmed the extra-text exclusion and inner-fold selection, and found no leakage. Keep all existing endpoints unchanged, add a dated amendment to `PROTOCOL.md`, and make these corrections:

1. **The cross-fold links.** State their source and size: the review finds that 16 identical one- or two-sign texts on faces of different objects create all of the 144–159 links per fold, joining 192 benchmark strings (748 queries, 9.3%); with links limited to texts of three or more signs, none remain. Report the effect estimate: removing the linked training strings lowers top-one on those queries by 8.0 points for first order, 9.0 for second order and 5.9 for MKN, about −0.75 and −0.84 points on the whole benchmark for first and second order, with model order and paired differences moving by at most 0.3 points. Also report the near-duplicate result (31.9% of strings have a training string one sign edit away; removing those neighbours costs about 1.5–2.3 points). Name the claim this bears on: Paper 001's component-held-out independence. Use the review's files in `review/` as the evidence and cite them.
2. **What extra text does.** Say in words that the extra-text loss gain (about −0.30 bits for MKN) comes 72–94% from 251 targets outside the training alphabet and that top-one accuracy does not move.
3. **Calibration.** Drop the reading of calibration cost from frequency-stratum ECE, since those strata are defined by the outcome.
4. **Errata.** Add dated errata for the Kneser–Ney attribution (Yadav et al. 2010 used Witten–Bell smoothing with Katz backoff; modified Kneser–Ney is from Rao et al. 2009) and for the amendment timing (all ten n-gram cells existed by 00:16:07, before the 00:18:07 amendment).
5. **Reproducibility.** Record the plotting packages in `environment.json` and keep `figures/learning-curves.png` and `plot-requirements.txt` in the package directory; the coordinator will add a repository exception so they are tracked.
6. Fix the prose items the review lists.

Update `README.md`, `REPORT.md`, `RETROSPECTIVE.md` and `registry-entry.json`. Do not retrain models; disk space is limited (about 6 GB free).
