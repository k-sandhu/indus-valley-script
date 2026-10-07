# Final polish for package F from the coordinator

A second Sonnet review is in `experiments/2026-10-06-field-recommendations/REVIEW-2.md`, with row checks in `review-2/`. It found 54 of 59 rows supported and 5 partly supported, and lists nine remaining fixes. Apply them without rebuilding the package, add a dated amendment to `PROTOCOL.md`, and keep `first-pass/` unchanged:

1. Revise F03 and F04 against the captions (the review's `review-2/caption-check.csv` gives the passages): F04 reports findings rather than a request, and F03's sample-size control is the coordinator's gloss; state each as what the speaker said and move any analytic gloss into a separate note. Re-rank the action list so that rank 5 no longer rests on F04 and F24 alone.
2. Correct F24: the footnote applies the Near Eastern second-hand seal problem to symbols on Indus seals.
3. Give the action ranking explicit scores or criteria, and do not place rows your feasibility field marks Limited (F58, F59) in a higher rank without saying why.
4. Replace repeated comparison passages with distinct opened sources where they exist, and add per-row `shared_or_disputed` and `n_independent_sources` fields that count author groups rather than papers (Wells and Fuls collaborated; Rao 2009 and Yadav 2013 share an author).
5. Store a short verbatim anchor of fewer than 15 words for each row.
6. Fix F10's nonexistent paragraph citation and the 68 strings where words are fused to numbers.
7. Reword or drop F53 and F55.
8. In `REPORT.md`, remove the corrective sentences the review lists and keep the lecture caveat in one place.
9. Align the nine rows whose `REPORT.md` heading differs from their theme, and cite F26, F47 and F50 or explain why not.

Update `README.md`, `RETROSPECTIVE.md` and `registry-entry.json` and rerun the checks. Keep disk use small.
