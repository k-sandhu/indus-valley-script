# Intermediate material evidence for practical transmission

12 October 2026. This is the material contribution to the [transmission study](../README.md).

Bhagwanpura's unfinished stone objects, Hulas's ceramic joining traces and Jognakhera's dated crop specimens provide specific candidates for work after urban contraction. The inspected observations do not yet identify a teacher, an uninterrupted technical lineage or the selected Vedic operation sequence. The [report](REPORT.md) develops a testable carrier hypothesis: recurring tasks and exchange of prepared by-products could preserve some operations as products and institutions changed.

The frozen comparison has eight work/page records, 26 observations and three candidate families. Twelve broad rival decisions remain ten `compatible` and two `unresolved`; three narrower controls concern claims with a smaller scope. These are qualitative documentary decisions. The source records share excavation and publication lineages and must not be counted as independent evidence for a single historical route.

| File | Purpose |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Fixed candidate families and rival rules, including prior exposure and chronology restrictions |
| [REPORT.md](REPORT.md) | Source findings, rival comparisons and the developed mechanism |
| [TESTS.md](TESTS.md) | Prospective collection, sourcing, production and plant-temper tests |
| [sources.json](sources.json) | Work identities, reading scopes, rights, dependence and local witness hashes |
| [observations.json](observations.json) | Exact loci, author interpretation, dating kind and the scope of current inference |
| [comparisons.json](comparisons.json) | Candidate-specific broad rivals and narrower claim controls |
| [operation-joins.json](operation-joins.json) | Seven supplied material/text operation comparisons and their missing relations |
| [source-checks.json](source-checks.json) | Twelve source controls, acquisition failures and inspection qualifications |
| [acquisition-index.json](acquisition-index.json) | Eleven acquisition attempts, including challenges and one failed route |
| [run-v1/summary.json](run-v1/summary.json) | Frozen descriptive counts and 300 integrity checks |
| [run-v1/input-hashes.json](run-v1/input-hashes.json) | Exact analysis input hashes |
| [verify_package.py](verify_package.py) | Frozen-input, local-link and raw-exclusion audit with an optional change inventory |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Methods, challenges, corrections and conditions for a useful continuation |

The carrier hypothesis and empirical programme were developed after coding. Existing proposals of learning from neighboring Late Harappans, including the Bhagwanpura report's printed p.30, are attributed in the report. Neither the proposed mechanism nor the status counts establish a transmission route.

## Reproduce the documentary audit

Run from the repository root with Python 3.13. The completed run requires the local witnesses identified in `sources.json` and the selected OCR derivatives. A fresh public checkout contains the authored package and aggregate outputs; it does not contain these excluded source files. Reacquired files may differ, so retain the frozen hashes and put a new capture in a new directory.

```powershell
& C:/Python313/python.exe -X utf8 experiments/2026-10-12-transmission-hypothesis/material/analyze.py experiments/2026-10-12-transmission-hypothesis/material/run-reproduction-v1
```

`analyze.py` refuses an existing output directory. It validates source and observation joins, witness bytes, allowed candidate/rival decisions, chronology qualifications and 142 OCR derivatives. Its checks establish internal consistency and preservation of source controls. They do not independently reclassify ancient artifacts or validate a historical route. The empty-evidence check is a declared bookkeeping control, with no fitted identifiability test.

`verify_package.py` checks the frozen input hashes, acquisition and extraction metadata, local links and Git exclusion of the raw files. Run it with a new output-directory argument inside this package. Its optional `--change-inventory` writes `changed-paths.json` once and refuses an existing inventory. That snapshot lists authored files and local-only witnesses with byte counts and hashes, excluding its own recursive hash.

The acquisition utilities also require fresh output directories. `acquire.py` takes a request JSON and output directory; `extract.py` takes an output directory followed by input paths. `ocr_pages.py` takes a PDF, one-based page list or ranges, and output directory. PyMuPDF, BeautifulSoup, lxml and Tesseract are the extraction dependencies. OCR was used for navigation and checked against selected rendered pages; an OCR operation does not imply that every page was manually read.

For example, to reproduce a new capture and selected page OCR without altering the frozen witnesses:

```powershell
& C:/Python313/python.exe -X utf8 experiments/2026-10-12-transmission-hypothesis/material/acquire.py experiments/2026-10-12-transmission-hypothesis/material/requests-v1.json data/raw/2026-10-12-transmission-hypothesis/material/acquisition-reproduction-v1
$env:PATH = 'C:\Program Files\Tesseract-OCR;' + $env:PATH
& C:/Python313/python.exe -X utf8 experiments/2026-10-12-transmission-hypothesis/material/ocr_pages.py data/raw/2026-10-12-transmission-hypothesis/material/acquisition-reproduction-v1/bhagwanpura-full.pdf 55,154,156,158 data/raw/2026-10-12-transmission-hypothesis/material/ocr-reproduction-v1
```

The Jognakhera publisher challenge responses are retained as failed article-access evidence. The normally requested author PDF returned HTTP 403; selected article loci were inspected through the web tool and saved as converted text, while the publisher's supplementary DOCX was acquired normally. Converted text does not supply the original PDF's byte hash. The source ledger records this access distinction.

Raw PDFs, HTML, DOCX, OCR, renders, image-caption extraction and source-table derivatives remain under the ignored local raw directory. The tracked ledgers contain bibliographic information and our bounded observations. This contribution adds no publication, deployment or recurring workflow.
