# Harappan renewal evidence

The [application](APPLICATION.md) develops source-linked comparisons of operating services, repairs, replacement tools and settlement reorganization. The [tests](TESTS.md) specify the next measurements and rejection conditions. This package contributes to the parent study of [societal persistence](../THEORY.md).

There are 14 included works, 34 documentary observations and two excluded candidates. The works overlap in excavations and data; these counts are catalogue sizes. The strongest cases are a replaced and rerouted Harappa drain, selective reservoir-related wall retention and stone salvage after a Dholavira desertion, and the East reservoir's loss of water function followed by later activity. Tool-production traces and changed craft configurations supply another set of renewal questions.

The sources provide no complete demand, initial-output, import or joint-work account. No archaeological minimum capacity, historical probability or population total was estimated. The three post-audit hypotheses are selective retention for continuing services, failure of support operations before contraction of dependent products, and concentration of renewal tasks within shared work windows.

## Records and validation

| File | Purpose |
|---|---|
| [PROTOCOL.md](PROTOCOL.md) | Frozen documentary protocol before new coding |
| [sources.json](sources.json) | Exact bibliographic identity, inspection depth, lineage, local witness hash and scoped reuse |
| [observations.json](observations.json) | Source observations, attributed interpretation, dating/outcome unit, alternatives and unmeasured quantities |
| [acquisition-index.json](acquisition-index.json) | All 37 new access attempts, including failed routes and acquired challenge pages |
| [source-checks.json](source-checks.json) | Manual source controls and the unresolved sample-count discrepancy |
| [run-v2/summary.json](run-v2/summary.json) | Final 275 documentary checks, all passed |
| [run-v1/summary.json](run-v1/summary.json) | Preserved first audit; two literal source-anchor failures caused by scanned-PDF extraction |
| [audit-v1.py](audit-v1.py) | Original audit code, matching its recorded input hash |
| [verification-v2/verification.json](verification-v2/verification.json) | Deterministic ledger reconstruction, overwrite guards and document references; 16 checks passed |
| [RETROSPECTIVE.md](RETROSPECTIVE.md) | Approaches, acquisition difficulties, repairs and limits |
| [changed-paths.json](changed-paths.json) | Owned authored paths and local-only raw inventory |

Twelve current source pages were visually inspected and seventeen code-generated text derivatives have verified parent/output hashes. Two earlier craft papers and their OCR were read in place, with their prior inspection and scope declared. The final checks validate the record's integrity and joins; the archaeological interpretation remains dependent on the inspected sources and stated assumptions.

## Reproduce without replacing frozen files

Run from the repository root with Python 3.13, PyMuPDF and BeautifulSoup. The working interpreter was `C:/Python313/python.exe`. Raw witnesses must already be available locally; their redistribution rights remain separate from a host's upload label.

```powershell
C:/Python313/python.exe -X utf8 experiments/2026-10-11-societal-persistence/evidence/build_ledger.py experiments/2026-10-11-societal-persistence/evidence/rebuilt-v3
C:/Python313/python.exe -X utf8 experiments/2026-10-11-societal-persistence/evidence/audit.py experiments/2026-10-11-societal-persistence/evidence/run-v3
C:/Python313/python.exe -X utf8 experiments/2026-10-11-societal-persistence/evidence/verify_package.py experiments/2026-10-11-societal-persistence/evidence/verification-v3
```

The builder refuses an existing documentary endpoint, and the auditor refuses an existing run directory. A builder reconstruction can be compared byte-for-byte with the frozen ledgers. The auditor reads the frozen package and verifies current source hashes. To audit a deliberately changed documentary package, first make its version explicit in the auditor's package path and preserve both versions.

[acquire.py](acquire.py) and the six request files record the public source routes used. They require fresh raw directories and verified TLS. A repeat acquisition may return a changed page or an access challenge; it cannot silently replace an inspected witness. [extract.py](extract.py) takes a fresh output directory and a list of local source files, preserving parent and derivative hashes. Tables and scanned-PDF text still require inspection against their source format.

Acquisition `retrieved_utc` records the start of an attempt, rather than the completion time of a large download. The prose scan found one flag for the em dash in the preserved ASI source title; manual review retained that bibliographic wording.

The initial [package verification](verification-v1/verification.json) ran before its own report link existed and recorded that missing link. A fresh second run passed after the report was present. Both runs and their rebuilt ledgers remain available.

All downloaded documents, page renders and source-text extracts remain local-only under `data/raw/2026-10-11-societal-persistence/evidence/`. No files outside this contributor's two directories were changed, and no publication, commit, push or automation was performed.
