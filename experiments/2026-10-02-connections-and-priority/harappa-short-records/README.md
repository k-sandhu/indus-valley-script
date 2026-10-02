# Harappa short-record dataset

[REPORT.md](REPORT.md) explains the repeated three-face pattern, two corpus exceptions, renewed source readings and the next physical test. The current endpoint is [main-v2](main-v2/results.json), checked by [241 independent scalar checks](review-v1/checks.json). Main-v1 preserves the initial omitted-position defect.

The full dataset is local-only at [data/raw/2026-10-02-connections-and-priority/harappa-short-records/main-v2](../../../data/raw/2026-10-02-connections-and-priority/harappa-short-records/main-v2/). It contains 66 joined inscription rows, 22 object records, 66 source-face rows, 231 exact-module pair comparisons, 231 conditional count comparisons and three separately scoped comparison objects. [Protocol](PROTOCOL.md), [source observations](observations.json), [source locators and hashes](main-v2/source-locators.json), [execution notes](RUN-NOTES.md), [retrospective](RETROSPECTIVE.md).

To produce another endpoint with the preserved local inputs, run:

```powershell
C:/Python313/python.exe -X utf8 experiments/2026-10-02-connections-and-priority/harappa-short-records/analyze.py --endpoint reproduction-YYYY-MM-DD
```

The helper refuses an existing output directory and creates its detailed tables beneath the corresponding local-only data directory. `review.py` checks the frozen main-v2 endpoint without importing the analysis routine. Original figures and corpora are acquired through the routes recorded in the [source frame](../../2026-10-02-six-hour/harappa-object-frame/source-access-log.json), [corpus provenance](../../../knowledge/provenance/SOURCES.md) and [reproduction guide](../../../REPRODUCING.md). A Git checkout requires those local inputs to rerun the record-level joins.
