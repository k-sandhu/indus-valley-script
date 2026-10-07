# Cross-script shape resemblance pilot

The amended pilot matches **30/42 Tamil Nadu bases to Indus, 24/42 to Ogham and 31/42 to Tifinagh** using segment and loop counts (R1). At a common reference size of 20, mean coverage is **53.70%, 57.14% and 65.11%**. The paired Tifinagh-minus-Indus difference is **11.41 percentage points**, with a central 95% subset interval of **[-9.52, 35.71]**. The Indus subset leads for 4–6 segment drawings: **14/15**, against **10/15 Ogham and 7/15 Tifinagh**. [Counts](run-v2/observed.json), `matched`, `complexity`; [size comparisons](run-v2/paired-size-comparisons.json), `version=v2`, `rule=R1`, `n=20`, `inventories`, `paired`.

**Coder reliability is a result.** The reviewer and original primary pass agree on complete descriptors for **52/113 drawings (46.02%)**, with orientation agreeing on **61/113 (53.98%)**. Removing orientation raises complete agreement to **88/113 (77.88%)**. The amended strict rule R3S uses integer counts plus symmetry and matches **4/42 Indus, 2/42 Ogham and 9/42 Tifinagh**. A consistently applied descriptor is a prerequisite for interpreting a resemblance rate. [Reliability](run-v2/inter-coder-reliability.json), `primary_reviewer_113`; [amended rules](PROTOCOL.md).

Status: **Exploratory**. Seven drawings were corrected after the October 7 review. [Run-v1](run-v1/manifest.json), its code, original inputs and the [review](REVIEW.md) remain unchanged. The original orientation-sensitive R3 remains diagnostic: v1/v2 counts are **4/4 Indus, 1/1 Ogham and 10/9 Tifinagh**. Across all nine query/reference combinations of the original primary, second-pass overlay and reviewer overlay, R3 ranges are **1–4, 0–1 and 8–10**. The overlays cover **19** and **113** readable drawings respectively, retaining primary rows elsewhere. [Version comparison](run-v2/v1-v2-comparison.json), `cells`; [sensitivity](run-v2/coding-sensitivity.json), `ranges`, `overlay_coverage`.

[REPORT.md](REPORT.md) gives the source audit, paired comparisons and limitations. The accessible 2025 PDF is a catalogued **8-page booklet**; a separate **145-page edition, ISBN 9788197784255**, remains unexamined. The source repair adds the exact The Week URL and the 2026 Volume I revisions. The calculation labelled Synthetic is within-inventory re-drawing; the requested generator of new random geometric marks **was not built**. [Sources](sources.json), `library-marc-2025`, `exotic-book-record`, `pti-theweek-2025`; [new observations](source-observations-v2.json).

## Repeat from the repository root

Python, NumPy, PyMuPDF, Pillow and requests were already installed. Computation requires local `coder-a.json`, `coder-b.json`, `indus-selection.json`, the corrected rows under `data/raw/2026-10-06-resemblance-baseline/amendment-20261007/`, and reviewer coding. Raw charts, coding rows, extracts and per-query matches stay local. A checkout without these inputs cannot reproduce manual coding.

```powershell
python experiments/2026-10-06-resemblance-baseline/analyze_v2.py --verify
python experiments/2026-10-06-resemblance-baseline/verify_package.py
python experiments/2026-10-06-resemblance-baseline/verify_v2.py
python experiments/2026-10-06-resemblance-baseline/analyze_v2.py --output reviewer-v2-01
python experiments/2026-10-06-resemblance-baseline/prepare_inputs.py --directory reviewer-sheets-03
python tools/review_prose.py --path experiments/2026-10-06-resemblance-baseline --no-write
```

`analyze_v2.py --verify` recomputes v1 aggregates and query results using the preserved original protocol, checks hashes of v1 and review files, then compares all v2 outputs exactly. Use this wrapper after the amendment: unchanged `analyze.py --verify` reads the amended protocol and cannot reproduce the old protocol hash. `verify_package.py` now uses the original protocol witness for v1 checks; `verify_v2.py` independently checks amended counts and formulas. New output directories refuse overwriting. For new live acquisition, run `amendment_sources.py --directory amendment-sources-review-01`. Temporary directories remain inside the raw path.

The saved difference between `coder-a-controls-tamil.json` and endpoint `coder-a.json` documents a pre-outcome **T18 correction: T 3→1, L 0→2, terminals 3→2**, with no match-count change. The earlier retrospective also reported an **I24 terminal correction 6→4** before outcomes, but no earlier Indus file survives to verify that history. Both accounts appear in [RETROSPECTIVE.md](RETROSPECTIVE.md). V2 records each change, source crop and reason in local `amendment-20261007/corrections-v2.json`.

[Verification](verification-v2.json) records completed checks. [FILES-v2.json](FILES-v2.json) lists every file created or changed in this amendment pass; [FILES.json](FILES.json) remains the v1 inventory. [registry-entry.json](registry-entry.json) proposes the coordinator's update; the shared registry was not edited.
