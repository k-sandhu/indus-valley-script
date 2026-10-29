# Package O retrospective

The package produced a local candidate with 19 configurations, 2,739 table rows and 949 attributed PNGs, and documented the existing private backup. Both staged benchmarks reproduce their frozen numerical endpoints. The [report](REPORT.md) gives the resulting populations and limits, and [validation.json](validation.json) records the checks.

## Reused work and approach

The registry and October 6 contribution assessment were reviewed before selection. The earlier chart source audit, redistribution record and consolidated atlas audit supplied the 1979 source licence, crop provenance and 16 retained ambiguities. Package M’s portable prediction copy avoided the original local-only prediction path; its unchanged scorers, frozen references, two repaired readings, source adjudication and chart cards supplied the benchmark. Synthesis v6 and the trimmed census registers supplied the site-level facts and aggregate tables. The corrected metrology summaries supplied four mass-band and nine chance-control rows. No recognition training, full digitization, census rebuild or metrological fit was repeated.

The protocol was written before packaging or score computation. A builder selected fields explicitly, serialized heterogeneous returned rows as JSON strings inside Parquet and copied only the approved PNGs. Source hashes and per-file decisions were retained. Every manifest-listed private prediction/model file was individually excluded in the audit. New scorer code loaded only the staged tables; the original core scoring functions were copied unchanged. A separate fresh build compared all 971 data/image/scorer files byte for byte.

## Problems and fixes

The preliminary directory inspection looked for a first-run `blind/CONVENTIONS.md` that does not exist. The repaired v2 convention file exists and was staged; v1’s original reading conventions and disclosures remain in its reader metadata. A preliminary JSON inspection encountered a UTF-8 BOM; source readers use `utf-8-sig`.

The first validation attempt failed before a completed report because `datasets` generated a Windows lock filename exceeding the path limit. Changing the working directory to Package O’s local raw folder and using a relative cache path fixed that failure without changing data. The next attempt computed scores but stopped in the prose scanner because `utf8-sig` is not a recognized encoding name; replacing it with `utf-8-sig` fixed the scanner and the optional prediction-file reader. Both partial logs and score files remain under the local raw directory.

The first completed validation reported five failures. Four were schema-string comparisons: Parquet renamed a list child from `item` to `element` while preserving its type, nullability and values. The validator now normalizes only that child-name spelling. The fifth comparison filtered the Gujarat/north India edition as `CISI1`, but those source rows use `CISI1-1987`; applying the source’s actual identifier recovered the declared 19 ranges and 493/327/166 counts. No source table or benchmark result changed. The failed report is preserved as `validation-2026-10-08-v3-failed.json`.

The next pass succeeded. A later checksum review found that a regenerated file manifest would otherwise include its own previous checksum. The final manifest excludes itself and hashes every other staged file. Subsequent passed reports preserve the intermediate validation states. The scorer’s CLI default was also made valid from both the package script and its staged `code/` copy. A fresh build confirmed unchanged payload bytes after those repairs.

A final package-check helper initially decoded PowerShell’s redirected prose log as UTF-8. That log is UTF-16, so decoding it with its actual encoding fixed the check. The prose scan itself had completed with no flags; this failure occurred while reading its result.

## Outcomes and remaining work

The prose/sequence screens found no candidate overlap at their declared windows and complete-singleton scope. They supplement the source/field allowlist and do not replace provenance or expert review. The final prose scan inspected all package Markdown, including the candidate and private cards. No upload, repository creation, visibility change, contact, submission, Git history operation or edit to another contributor’s directory occurred. The authorized dependency installation used `pip --no-cache-dir` in `indus-ml`; its package file record is separate from research outputs.

The owner must confirm licences for our work and supply author, affiliation and contact. The coordinator’s future private upload must be followed by hosted loading/viewer checks. Package N’s initial snapshot contained a Proposed protocol only; any later verified transcription needs its own rights and source audit before addition. The private backup’s remote state and a full restore were not reverified. The metrology tables link to private methods and omit the catalogue inputs. These remaining decisions and checks are explicit in the release checklist.
