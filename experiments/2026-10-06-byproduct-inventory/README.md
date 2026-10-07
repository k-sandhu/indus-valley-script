# Inventory of research outside decipherment

The corrected package contains **26 records**, with **25 assessed candidates** and a held rank-6 pointer to the unfinished evidence-census package. All **112 registry entries** have one primary checklist home; **24 records carry entries**. Original status wording and multi-topic cross-links are retained in [inventory.json](inventory.json). Current assessment text uses no B1/B2 figures.

The amended top five are the chart resource, context audit, CISI scan notice, combined numerical-premise/capacity audit and cross-catalogue join audit. The [report](REPORT.md) groups candidates by field. Inventory `rank` numbers preserve review references; `priority_position` and `recommended_priority_order` give the amended recommendation. Rank 6 is excluded.

The final chart has **16 ambiguous lower-code labels among 687 cells**, read by AI models without expert certification. The context audit finds **1,444 rows/1,163 provisional families** with its specified joint fields. CISI's **862 scan pages form 431 identical image-list pairs**. The numerical audit has **four positive-integer solutions in (L,S,v) order**, with **8≤L≤13** selecting (10,8,6); the companion capacity fit is **40.3531914893617 L/stroke** over three selected published vessels, with zero eligible independent held-out vessels. The plate audit has **17 compatible/seven discrepant objects among 24 source-complete cases**, judged by AI models. Exact evidence and limits are beside the claims in the report and inventory.

[REVIEW.md](REVIEW.md) confirmed 142 of 146 first-pass values and found stale figures, unsupported mappings and publication judgments. [first-pass/](first-pass/) preserves the nine original top-level files, including the review. New records cover CISI scan repetition, cross-catalogue joins and the completed October 2 dataset landscape. The Susa 25:1:2 reconstruction, 40.4 L capacity audit and newer Harappa module/count analysis are incorporated into existing records. [RETROSPECTIVE.md](RETROSPECTIVE.md) records problems and fixes.

Run from the repository root:

```powershell
python experiments/2026-10-06-byproduct-inventory/apply_review_corrections.py
python experiments/2026-10-06-byproduct-inventory/audit_coverage.py
python experiments/2026-10-06-byproduct-inventory/verify_corrections.py
python tools/review_prose.py --path experiments/2026-10-06-byproduct-inventory --no-write
```

The rebuilding script reads the preserved inventory/source records and saved endpoints, then rewrites only this package's current inventory and source records. The checker writes [correction-checks.json](correction-checks.json). No earlier analysis is rerun. The original sweep indexed titles/openings for 206 files and read relevant reports/outputs; it did not read every document in full. This correction adds standalone audit notes missed by that sweep. Subject searches and failed opens are in `sources.json` and the local raw correction log; exact novelty remains partial or unchecked where stated.
