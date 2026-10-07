# Follow-up for package F from the coordinator: rebuild on GPT-6.1-Sol

The coordinator has switched this session to GPT-6.1-Sol. A Sonnet review of the first pass is in `experiments/2026-10-06-field-recommendations/REVIEW.md`, with row-level findings in `review/row-audit.csv`, source checks in `review/source-checks.csv` and missing recommendations with locators in `review/missing-recommendations.csv`. It found that 7 of 33 rows are supported by their cited sources, 9 are partly supported, 8 attribute recommendations the sources do not contain and 5 attribute nothing; 14 of 31 source records have wrong titles, venues, years, authors or URLs; and five files have damaged characters. The coordinator's caption check of the lecture is `experiments/2026-10-06-research-program/frenez-talk-check.md`.

Copy the current files into `first-pass/` before editing. Then carry out the review's required fixes:

1. Rebuild every row from a source you open and read, stating the researcher's own recommendation with its page or timestamp. Drop a row rather than infer a recommendation the source does not make. A paper's method is not a recommendation unless the author presents it as one.
2. Correct the 14 source records and remove the Miller record unless you find the actual source.
3. Write every file as UTF-8 without a byte-order mark, repair the damaged characters, and add an encoding check to `build_tables.py`.
4. Replace the four lecture rows with the caption-checked statements and timestamps from `frenez-talk-check.md`, and add the written parallel in Frenez 2018, *Walking with the Unicorn*, printed pp. 186–187, where he argues the unbalanced-oligopoly reading (a local copy exists in the repository; search `research/literature/` and `data/` for it).
5. Correct the report statements the review lists (lines 5, 11, 19 and 55 of `REPORT.md`, and line 3 of `README.md`), including that Fuls's 2023 abstract compares sign frequencies against per-site artefact counts.
6. Fix the two broken repository links.
7. Replace `comparison_source_ids` with opened sources that actually state agreement or dispute, and include the published replies in the Sproat and Farmer–Sproat–Witzel debates.
8. Save the fetched pages or their hashes in the local raw directory, and check `research/literature/sources/` before searching again.
9. Label the rows and report Exploratory.
10. Add the missing recommendations listed in `review/missing-recommendations.csv` after reading each source.

Then update `REPORT.md`, `README.md`, `RETROSPECTIVE.md`, `registry-entry.json` and add a dated amendment to `PROTOCOL.md`. In the report, group recommendations by theme, mark which are shared and which are disputed, and rank those this project can act on with its current data, linking the October 6 packages (D1, D2, E, G, H and the census) where they already address a recommendation.
