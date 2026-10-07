# Review files

Supporting files for [REVIEW.md](../REVIEW.md), written on 7 October 2026. Scripts read the pinned inputs and write only into this directory. Nothing outside `review/` and `REVIEW.md` was edited.

| File | Contents |
|---|---|
| `check_headline_numbers.py`, `headline-numbers-check.csv` | 57 headline numbers from the README and REPORT, each recomputed from the corpus, batch rows, museum records or saved outputs; 55 confirmed, 2 discrepancies. |
| `recompute_cisi_ranges.py` | Independent recomputation of the 327/493 comparison, with a cross-label check of every absent key. |
| `recompute_batch_totals.py` | Recount of every batch row's faces, families and CISI identifiers from the corpus. |
| `recompute_field_completeness.py` | Recomputation of the Lipi field table with a separate missing-value rule. |
| `cisi1_range_verification.py`, `cisi1-range-verification.csv`, `cisi1-class-split.csv` | The 19 CISI 1 ranges read against page headers of the local scan, with absent keys split by catalogue section. |
| `rerun-build/`, `rerun-build-stdout.json`, `rerun-verification.json`, `rerun-verification-stdout.json` | Output of the README commands (builder and verifier) run into new names. |
| `annotation-replay/`, `annotation-replay-stdout.txt` | Replay of the four authored ledgers. |
| `d-build.py-verify.txt`, `d-verify.py-verify.txt`, `d-inventory.py-verify.txt` | Output of batch D's read-only `--verify` commands. |
| `scan_long_strings.py`, `scan_snippet_titles.py`, `residual_snippet_titles.py` | Scans of tracked files for long strings and for source titles that look like search-result prose. |
| `residual-snippet-title-ids.json`, `residual-snippet-title-judgement.json` | Record IDs only, no title text: 72 flagged records and the reviewer's reading of the long ones (32 search-result prose, 13 legitimate long titles). |
| `site-check-A.md` to `site-check-D.md` | Row checks for Rappwala Ther, Chanhu-daro, Pabumath, Daimabad, Chandigarh, Rakhigarhi, Susa and Ur (read-only subagents). |
| `sample-recheck-AB.md`, `sample-recheck-CD.md` | Independent re-adjudication of the 20-site source sample and checks of the 14 sources it uses. |
| `museum-join-check.md` | Check of ten museum-to-corpus joins and two side checks on the unjoined records. |
