# Package M: completed Helsinki 1979 v3 endpoint

V3 fails four of five frozen release criteria. On **80 fresh rows across three sections, excluding both earlier samples**, it has 71 accepted crops, 71 correct numbers, 72 classifications, 72 counts, 38 top-one and 62 top-five whole rows. Random-page numbered recall passes at 1,289/1,289. Every proposal remains quarantined; zero are released. [Frozen metrics](repair/2026-10-08-v3/evaluation-2026-10-08-adjudicated/metrics.json), `summary`, `negative_result_criteria`.

| Outcome, Wilson 95% interval | First: 60 numbered rows, PDF 31–79 | V2: 80 rows, three sections | V3: 80 fresh rows, three sections |
|---|---|---|---|
| Crop acceptance | 23/60 (38.3%; 27.1–51.0%) | 44/80 (55.0%; 44.1–65.4%) | 71/80 (88.8%; 80.0–94.0%) |
| Drawing-unit count | 33/60 (55.0%; 42.5–66.9%) | 59/80 (73.8%; 63.2–82.1%) | 72/80 (90.0%; 81.5–94.8%) |
| Literal inscription number | 23/60 (38.3%; 27.1–51.0%) | 62/80 (77.5%; 67.2–85.3%) | 71/80 (88.8%; 80.0–94.0%) |
| Five-position classification | 19/60 (31.7%; 21.3–44.2%) | 55/80 (68.8%; 57.9–77.8%) | 72/80 (90.0%; 81.5–94.8%) |
| Whole row, top one | 13/60 (21.7%; 13.1–33.6%) | 20/80 (25.0%; 16.8–35.5%) | 38/80 (47.5%; 36.9–58.3%) |
| Whole row, top five | 24/60 (40.0%; 28.6–52.6%) | 40/80 (50.0%; 39.3–60.7%) | 62/80 (77.5%; 67.2–85.3%) |
| Exact singleton-reference sequence | 10/52 (19.2%; 10.8–31.9%) | 19/66 (28.8%; 19.3–40.6%) | 28/54 (51.9%; 38.9–64.6%) |

The first frame is 60 numbered-section rows from PDF 31–79, with no sorted row. V2 is 80 rows across numbered/end-sorted/beginning-sorted sections (28/26/26). V3 is 80 fresh rows across those sections (28/26/26), excluding all earlier target pages and development pages, from 572/2,004/2,004 eligible occurrences. These frames and references differ. Exact-sequence subsets contain 52/66/54 singleton-reference rows. [REPORT.md](REPORT.md) gives unit recall, calibration, source-count intervals and their denominators.

| V3 frozen criterion, all 80 rows unless stated | Observed | Minimum passing numerator | Additional passing rows needed |
|---|---|---|---|
| Crop ≥90% | 71/80 | 72/80 | 1 |
| Number ≥90% | 71/80 | 72/80 | 1 |
| Count ≥95% | 72/80 | 76/80 | 4 |
| Top-five whole rows ≥80% | 62/80 | 64/80 | 2 |
| Random-page numbered recall ≥95% | 1289/1289 | 1225/1289 | 0 |

V3 random-page numbered recall and precision are 1,289/1,289 (Wilson 95% 99.7–100%). Physical-line recall and precision are 1,296/1,296 (99.7–100%); stress-page numbered and physical recall/precision are 561/561 (99.3–100%). The count frame is 18 fresh random pages plus stress 62, 129, 130; the latter remain development pages for recognition. [Metrics](repair/2026-10-08-v3/evaluation-2026-10-08-adjudicated/metrics.json), `source_row_recall`, `physical_line_recall`.

The 18 top-five failures begin at 8 crops, 7 segmentation/underline defects and 3 unresolved strict-reference rows; no resolved graphic-proposal miss remains on the inspected correct windows. Numbers or classifications fail in 15/80 rows, overlapping those stages. Three chart-label differences appear in reference or proposal cells; the frozen card vocabulary is preserved, and [package P](../2026-10-08-chart-reference-audit/PROTOCOL.md) owns correction. [Diagnosis](repair/2026-10-08-endpoint-record-v1/diagnosis.json); [window audit](repair/2026-10-08-endpoint-record-v1/unit-window-audit.json); [REPORT.md](REPORT.md).

## Proposals and verification

The full inventory contains **11,769 physical-line proposals, 11,702 numbered occurrences, 67 continuations and 54,384 unit windows**, including five unresolved empty windows, across 159 pages(PDF 22–180). All remain quarantined. [Full summary](repair/2026-10-08-v3/full-summary.json), `rows`, `units`, `released_rows`; [HOST-FILES.txt](HOST-FILES.txt) lists the 106,190,599-byte local JSONL for coordinator backup.

[Package N's pilot](../2026-10-08-helsinki1979-row-verification/pilot/PILOT-RESULTS.md) recommends a second pilot with v3 proposals, clarified conventions and P's reviewed chart before a full verification run. It has not established the human/expert acceptance route. Use the immutable [option-B contract](OPTION-B-INTERFACE.md) and [schema](option-b-schema.json), preserving physical-line keys, coordinates, continuation links, literal suffixes and source/freeze hashes. Complete source-page review must recover omissions and resolve continuation ownership. L's reviewed identity/surface joins remain separate. Release requires a new validated acceptance rule or a fresh pipeline passing every frozen criterion plus its per-row rule.

The 80 v2 rows were used for v3 development, giving 71 counts, 69 numbers, 67 classifications, 33 top-one and 60 top-five rows. They selected the method and remain Exploratory. [Development diagnosis](repair/2026-10-08-development-record-v1/diagnosis.json). Both older frozen endpoints and the frozen v3 files are unchanged.

## Repeat the small record from the repository root

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/record_v3_endpoint.py --out experiments/2026-10-07-helsinki1979-digitization/review/v3-endpoint-record-repeat
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/evaluate_crop_v3.py --out experiments/2026-10-07-helsinki1979-digitization/review/v3-evaluation-repeat
& 'C:\Users\sandh\.venvs\indus-ml\Scripts\python.exe' experiments/2026-10-07-helsinki1979-digitization/verify_v3_endpoint_record.py --out experiments/2026-10-07-helsinki1979-digitization/review/v3-record-check-repeat.json
python tools/review_prose.py --path experiments/2026-10-07-helsinki1979-digitization --no-write
```

Use new output paths; scripts refuse to overwrite prior runs. The evaluator replay is byte-identical to the coordinator's metrics. `inspect_v3_endpoint.py` renders ten small source/window overlays into a new local raw directory; `audit_v3_endpoint_windows.py` records the observed failure cases. `write_v3_endpoint_docs.py` regenerates these living documents from aggregates and their pre-record snapshots. Earlier inference and packet construction commands remain in the [preserved previous README](repair/2026-10-08-endpoint-record-v1/documentation-snapshot.json).

The [preservation check](repair/2026-10-08-endpoint-record-v1/preservation-check.json) covers 520 frozen witnesses; [verification](repair/2026-10-08-endpoint-record-v1/verification-final.json) also checks replay, stage partitions, chart uses and costs. Inspect row 31's seven shifted unit windows, the six accepted-crop count failures, unresolved rows 3/35/70 and the row 58 chart locator conflict. Every path changed for this follow-up is listed in [changed-paths.json](repair/2026-10-08-endpoint-record-v1/changed-paths.json).

Source attribution: Kimmo Koskenniemi and Asko Parpola, *Corpus of Texts in the Indus Script* (1979), Research Reports 1, Department of Asian and African Studies, University of Helsinki; [handle](http://hdl.handle.net/10138/342677), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Source crops, proposals and annotations are modifications. Raw renders and large exports remain local. [sources.json](sources.json) records access and rights; this follow-up downloaded nothing and changed no shared repository file.
