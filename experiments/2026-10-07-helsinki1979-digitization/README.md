# Package M: Helsinki 1979 cropping v3

V3 is frozen and supplies **11,769 physical-line proposals, 11,702 numbered occurrences, 67 continuation lines and 54,384 proposed unit windows (5 unresolved) across 159 pages (PDF22–180)**. Every proposal remains quarantined; **zero are released**. The fresh blind packet contains 80 numbered occurrences, 18 new random count pages and three stress pages. No fresh reference or v3 evaluation outcome exists. The coordinator will obtain two independent readings, adjudication and the frozen evaluation; a separate option-B package will check every source row. [Full inventory](repair/2026-10-08-v3/full-summary.json), `rows`, `numbered_occurrences`, `continuation_lines`, `units`, `pages`; [packet](repair/2026-10-08-v3/blind/selection.json).

The 80 v2 rows are development data for v3. Their 28/26/26 section quotas and 352 reference units are reused unchanged; they selected the crop method. The intervals below describe these rows and do not estimate fresh v3 accuracy. The first frame contains 60 numbered-section rows from PDF31–79, sampled from 3,460/11,369 detections, with no sorted-section row. The v2 frozen frame contains 80 rows across numbered, end-sorted and beginning-sorted sections.

| Outcome, descriptive 95% Wilson interval | First frozen: 60 numbered rows, PDF31–79 | V2 frozen: 80 rows, 28/26/26 sections | V3 development: same 80 v2 targets |
|---|---|---|---|
| Matching unit count | 33/60 (55.0%; 42.5–66.9%) | 59/80 (73.8%; 63.2–82.1%) | 71/80 (88.8%; 80.0–94.0%) |
| Literal inscription number | 23/60 (38.3%; 27.1–51.0%) | 62/80 (77.5%; 67.2–85.3%) | 69/80 (86.2%; 77.0–92.1%) |
| Five-position classification | 19/60 (31.7%; 21.3–44.2%) | 55/80 (68.8%; 57.9–77.8%) | 67/80 (83.8%; 74.2–90.3%) |
| Compatible whole row, top one | 13/60 (21.7%; 13.1–33.6%) | 20/80 (25.0%; 16.8–35.5%) | 33/80 (41.2%; 31.1–52.2%) |
| Compatible whole row, top five | 24/60 (40.0%; 28.6–52.6%) | 40/80 (50.0%; 39.3–60.7%) | 60/80 (75.0%; 64.5–83.2%) |
| Crop acceptance | 23/60 (38.3%; 27.1–51.0%) | 44/80 (55.0%; 44.1–65.4%) | No new independent crop labels |

The new numbered-row detections match **1,847/1,847** source occurrences on the 21 reused count pages (descriptive Wilson interval 99.8–100.0%; precision also 1,847/1,847). All five earlier segmentation/underline failure rows (3,25,50,52,58) now have matching counts and compatible top-five sequences in development. [Development diagnosis](repair/2026-10-08-development-record-v1/diagnosis.json), `development_summary`, `development_numbered_recall`, `prior_five_segmentation_underline_failures`. The two earlier frozen endpoints remain unchanged and failed their release criteria.

## Freeze, fresh packet and complete verification

The [method freeze](repair/2026-10-08-v3/freeze-manifest.json) records code, parameters, chart, evaluator, unchanged model/digits/calibration and source hashes at 2026-10-08T14:11:23.905485+00:00. The [prediction freeze](repair/2026-10-08-v3/prediction-freeze.json) follows at 2026-10-08T14:13:49.280280+00:00, before any fresh reference. The [source-only conventions](repair/2026-10-08-v3/blind/CONVENTIONS.md) specify continuation checks, complete underline slots, the 597/598 spacing rule, separate reader scratch directories and both numbered/physical-line counts.

The fresh 80-row quotas are 28 numbered,26 end-sorted,26 beginning-sorted. The eligible pools are **572,2,004,2,004 numbered occurrences on 8,28,28 pages**. Page exclusions remove every page with any of the first 60 or v2 80 targets, plus the original ten development pages. All sampled targets happen to have no detected continuation, so the recognition test has limited direct continuation evidence. The 18 random count pages exclude the old count pages; stress pages 62,129,130 remain development checks. [Selection](repair/2026-10-08-v3/blind/selection.json), `denominators`, `eligible_pages`, `excluded_pages`, `random_count_pages`, `stress_pages`; [protocol](PROTOCOL.md).

The large JSONL is local, named with its byte count and SHA256 in [HOST-FILES.txt](HOST-FILES.txt) for coordinator backup. Its [option-B contract](OPTION-B-INTERFACE.md) and [schema](option-b-schema.json) retain one record per physical line, source boxes, provisional continuation links, literal field proposals, candidate sets, inherited-calibration confidence and quarantine. Existing object-ledger identity/surface requirements remain in force. [Import contract](IMPORT_INTERFACE.md).

## Reproduce from the repository root

Use the recorded Python environment and a new output directory for each replay. Construction refuses to overwrite a freeze, packet or full output. The acquired source PDF and original chart crops are needed for inference.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/develop_crop_v3.py --out experiments/2026-10-07-helsinki1979-digitization/review/development-v3-repeat
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/record_crop_v3.py --development experiments/2026-10-07-helsinki1979-digitization/repair/2026-10-08-development-v3h/development.json --out experiments/2026-10-07-helsinki1979-digitization/review/development-record-repeat
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/prepare_crop_v3.py freeze --run experiments/2026-10-07-helsinki1979-digitization/review/v3-reconstruction
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/prepare_crop_v3.py packet --run experiments/2026-10-07-helsinki1979-digitization/review/v3-reconstruction
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/complete_crop_v3_full.py --run experiments/2026-10-07-helsinki1979-digitization/review/v3-reconstruction --raw-output data/raw/2026-10-07-helsinki1979-digitization/reviewer-v3-full --reuse data/raw/2026-10-07-helsinki1979-digitization/reviewer-no-reuse
```

The reconstruction's new freeze timestamp/hash changes its embedded provenance fields; compare geometry, selected source targets and proposals separately. The separate transport helper marks non-finite windows unresolved without changing frozen inference. A stopped full run can resume only from intact hash-checked page files with `--resume`. After coordinator references are present, run the frozen scorer into a new owned directory:

```powershell
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/evaluate_crop_v3.py --out experiments/2026-10-07-helsinki1979-digitization/review/v3-evaluation-repeat
```

The scorer currently stops because references are absent. It retains all five original global criteria, Wilson row intervals, stratified row bootstraps, equal-count calibration and numbered recall, and adds physical-line recall. It creates no reference. For both older endpoint replay commands and their reader-process disclosures, see the [preserved earlier README](repair/2026-10-08-record-v1/README.md.before-v3.txt).

## Limits, rights and checks

Known development boxes 27,53,76 still include field ink or cut a final drawing. Short-component-only continuations can be missed. Number reading, graphic variants and inherited calibration remain limits beside the crop repair; [REPORT.md](REPORT.md) links their measured results. The full detection count is not an independently verified complete corpus denominator. Complete source-page inspection belongs to the option-B package.

Source-derived crops and proposals are modifications of Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki; [handle](http://hdl.handle.net/10138/342677), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The 1980 source rights remain unresolved. The coordinator must integrate the listed image exceptions in [TRACK-EXCEPTIONS.txt](TRACK-EXCEPTIONS.txt); no shared ignore file was changed.

Repeat [verification](repair/2026-10-08-record-v1/verification.json), verify both old endpoints and the v3 freeze/packet hashes, inspect development boxes 27,53,76 and all five segmentation repairs, check full JSONL schema/continuation ownership, and have the coordinator complete both blind readers plus adjudication before scoring. Every created or changed path is listed in [changed-paths.json](repair/2026-10-08-record-v1/changed-paths.json).
