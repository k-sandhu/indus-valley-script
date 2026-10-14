# Pipeline implementation plan, 13 October 2026

The code will compare the two blind readings, require adjudication of every disagreement, build each final block, merge by volume, check the other local sources and report coverage and the two numerical predictions. Tests will use generated synthetic readings and the pilot's final table. This session will not inspect the full run's active pass files or images.

Shared helpers will keep row identity, whitespace comparison, uncertainty matching, input hashes and local output paths consistent. The parser will retain the pilot's fields and add excavation markers, multiple numbers and generic institution parsing. Unknown codes and unparsed fragments will be reported locally, with counts in tracked reports. Institution names without a sourced expansion will retain their printed code.

An identical overlap row will count once. Separate piece lines will be combined only when their piece markers distinguish them. Conflicting duplicate rows and rows present in one pass require a whole-row adjudication. Missing rows will be reported as omissions separately from wrong definite cells. Corrigenda will be compared as text lines and reported separately from the five-column entry accuracy.

Blind adjudications take precedence over the later recheck, including undecidable outcomes. Accuracy will use the blind decisions before any recheck. Merging will refuse duplicate catalogue identifiers, including block-boundary continuations that need an explicit coordinator repair. Coverage will use the pilot's conservative family join and the inventory's usable-value and grouping rules. Both coverage including brackets and coverage with no brackets in a supplied cell will be reported.

The implementation sequence is parser and shared helpers, comparison and final building, merge and cross-check, family join and predictions, then synthetic and pilot regression checks. The final review will run the prose scanner, inspect the created file list and record observed problems, fixes and results in RETROSPECTIVE-CODEX.md. Shared records and frozen protocol files will remain untouched.
