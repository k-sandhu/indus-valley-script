# Indus weight metrology across sites and regions

The corrected Dholavira analysis gives **13.716 g, signal CV 1.591%** for 90 intact certain weights of 5–100 g, and **14.280 g, CV 5.777%** for 147 weights of 1.3–5 g. The pooled 14.003 g fit combines these distributions. Western compatibility counts fail the chance comparison and give **no evidence of Indus-standard weights in the western assemblages**. [Report](REPORT.md); [mass-band estimates](runs/2026-10-07-review-response-v4/mass-band-estimates.json), `fits`; [chance controls](runs/2026-10-07-review-response-v4/western-chance-baselines.json), `nulls`.

The final review response is **Exploratory**, because the model changes followed the [Sonnet review](REVIEW.md). Its computation is verified. The frozen `runs/2026-10-06-main/` endpoint and extraction v6 remain unchanged. The [dated protocol amendments](PROTOCOL.md) declare the new comparisons; [historical documents and code](history/2026-10-07-before-review-response/) preserve the earlier statements.

## What changed

The parser retains **2,058 entries**, including **938 Greater Indus** records. It fixes decimal-comma masses in cats. 1201 and 1730, clears **111** false grid fields, removes captions from **7** entries and captures cat. 593's numeric unit annotation. The explicit 430-object dimension screen has **13 flags before correction and 12 afterward**; the review's 413-object screen excludes 17 terracotta records, which add no flags. Cat. 1212 has a further printed inconsistency outside the box-shape gate. [Parser audit](runs/2026-10-07-review-response-v4/parser-audit.json), `changed_field_counts`, `dimension_screen_before`, `dimension_screen_after`; [report](REPORT.md).

The final run contains **45 site/model fits, 75 stratum fits, 1,600 bootstrap refits and 12 quantograms**. Two-unit, additional-fraction, absolute-error and small-mass-offset models all improve on the original pooled model. Their differences leave the physical cause unresolved. The main model comparisons have **0 optimizer failures**. [Completion](runs/2026-10-07-review-response-v4/completion.json); [model tests](runs/2026-10-07-review-response-v4/dholavira-model-tests.json).

With the old western rule, observed counts of **136 geometric / 18 close** compare with jitter-control means of **170.246 / 38.727**. With canonical 7.8, 8.4 and 9.4 g competitors and a 13.65 g reference, observed counts are **125 / 29**, against **148.716 / 38.5375**. The 29 close hits are 4.137% of 701 selected records (conditional Wilson interval 2.896–5.878%). Ascalone's Susa list and the overlap comparison are documented separately; cat. 220 is absent from the revised screen objects. [Compatibility](runs/2026-10-07-review-response-v4/western-compatibility.json); [Susa comparison](runs/2026-10-07-review-response-v4/ascalone-susa-comparison.json).

## Reproduce from the repository root

Python needs NumPy, SciPy, PyMuPDF and Pillow, already available in this environment. No installation is needed. The original source PDF remains at `data/raw/2026-10-02-connections-and-priority/regional-west/ascalone2022.pdf`. Scripts set writable library temporary paths under this package's local raw directory. New endpoints refuse existing output directories.

```powershell
python -B -X utf8 experiments/2026-10-06-weight-metrology/review_response.py --output experiments/2026-10-06-weight-metrology/runs/2026-10-07-reviewer-repeat --raw-output data/raw/2026-10-06-weight-metrology/2026-10-07-reviewer-repeat
python -B -X utf8 experiments/2026-10-06-weight-metrology/verify_review_response.py --run experiments/2026-10-06-weight-metrology/runs/2026-10-07-reviewer-repeat --output experiments/2026-10-06-weight-metrology/reviewer-repeat-verification.json
python -B -X utf8 experiments/2026-10-06-weight-metrology/verify.py --output experiments/2026-10-06-weight-metrology/reviewer-frozen-verification.json
python -B -X utf8 experiments/2026-10-06-weight-metrology/make_review_summaries.py --run experiments/2026-10-06-weight-metrology/runs/2026-10-07-reviewer-repeat --output experiments/2026-10-06-weight-metrology/summary-tables-reviewer-repeat
python tools/review_prose.py --path experiments/2026-10-06-weight-metrology --no-write
```

The completed run took **131.334 seconds**. The final verifier reproduced **2,058 rows**, independently checked **129 likelihoods**, **203 scalar quantogram points**, **6,309 western scores** and **9 null-summary frames**, and confirmed **20 unchanged frozen files**. [Verification](review-response-verification.json); [historical verification](review-response-frozen-verification.json). The completed v3 run is a Superseded witness: a section-boundary error duplicated two rows in its book-list aggregate. The recomputation reproduced **25 owned numerical files and 18 local derivatives** byte for byte, with model tests identical apart from that corrected source-list aggregate. [Comparison](review-response-reproduction.json). Two earlier partial attempts have Failed records. [Retrospective](RETROSPECTIVE.md).

## Files and source access

[Summary tables](summary-tables-review-response/manifest.json) point to the current endpoint. Older `summary-tables/`, top-level verification records and Gulf supplement remain historical witnesses. [Sources](sources.json) records exact titles, venues, access levels, corrected metadata and unrecovered originals. [Research log](review-response-research-log.json) records the new source recovery and failures. [Registry proposal](registry-entry.json) is local to this package; the shared registry was not edited.

All catalogue rows, source-selected lists, predictions, bootstrap draws, simulated counts and acquired source payloads remain under `data/raw/2026-10-06-weight-metrology/`. The [revision file inventory](REVIEW-RESPONSE-FILES.json) lists every new or modified file with hashes. The response adds only a small local working set; the existing PDF and renders were reused. See [REPORT.md](REPORT.md) for the required reweighing, rounding-resolution, wear, identity and excavation-context checks.
