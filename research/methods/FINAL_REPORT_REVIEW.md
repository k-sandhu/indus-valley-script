# Final quantitative report review

Reviewed the 18-page report `output/pdf/indus_script_research_report.pdf` against saved result JSON, including the 1,000 accepted uniqueness-conditioned nested shuffles completed at 02:57 UTC. This was a bounded read-only arithmetic and interpretation review; no models were refitted.

## Verdict

The reported main structural gains, confidence intervals, permutation counts and probabilities match the saved endpoints at the displayed rounding. The main corpus counts, second-annotator candidate-event results, known-slot restoration, cross-site restoration, historical and design-matched gap recovery, metadata and paired-surface tests, substitution transfer, calibration examples, and both font-image evaluations also match their result files.

The report keeps the important distinctions: candidate-set event likelihood is not fine-glyph accuracy; model mass is not calibrated archaeological confidence; bootstrap intervals condition on the chosen corpus, grouping and fitted procedure; significance of total substitution transfer is not significance of each selected pair; a post-reference geometry repair is a development diagnostic. Negative gap-count results and the failed frozen font acquisition pipeline remain visible. None of these statistical results supplies sounds, meanings or an independent decipherment.

## Material corrections identified and resolved

1. The previous draft incorrectly said that `audit_numerical_equalities.py` executed 35 coefficient sensitivities. The actual separate `numerical_count_delta.py` evaluates three hypothetical first-side stroke counts, two/three/four. Parent confirmed the refreshed draft removes the false count and names the separate script.
2. The previous reproduction table rendered the executable filename as `evaluate_font_fresh 20.py`. Parent confirmed that prose spacing now protects file paths and the refreshed PDF contains `src/evaluate_font_fresh20.py` literally.

## Final spot checks

Known-slot model mass 0.492 versus observed correctness 0.384, and 0.896 versus 0.838, agree with the saved calibration bins. The highest gap bin is 0.936 model mass versus 0.494 correctness. Microcontext permutation probabilities are 0.0560 (primary), 0.0609 (merged repeated-text variant), 0.0634 (unique variant), and 0.0864 (unique merged variant); these support the report's cautious interpretation.

The 1,000 accepted uniqueness-conditioned nested-null endpoint has 6,569 proposals, 0 exceedances, p = 1/1001, observed gain 0.8483578853 bits, null mean 0.0070936302 bits, and null central 95% range [-0.0065489334, 0.0213552291]. The full regrouped primary nested null has 0/1,000 exceedances and the same Monte Carlo resolution. Exact discrete p-values should retain that finite simulation interpretation.

The numerical equality audit has exactly four positive integer solutions under its stated integer restrictions: (L,S,v) = (4,20,36), (6,8,10), (10,8,6), (36,20,4). Restricting L to 8..13 or 8..18 selects (10,8,6), conditional on the quantity equalities, place assignments and range assumptions. The source and physical-identity qualifications were reviewed separately and remain material.

Reviewed by methods agent; completed 2026-10-02, approximately 03:08 UTC. No additional material quantitative correction remains from this review.
