# Paper 007: Source-linked Indus object reconciliation register, coverage audit and post-catalogue census

Working manuscript draft for GitHub Issue #17, compiled on 22 November 2026. Prepared with AI research, data-engineering and writing assistance (Claude Opus 5.5, Codex CLI with GPT-6.1-Sol, and Antigravity). Author names, institutional affiliations and a target venue have not been assigned.

## Contents

- [manuscript.md](manuscript.md): Complete draft data paper covering positioning against ICIT (Fuls 2023) and Mahadevan (1977), Schema v2.0 and the five-class uncertainty taxonomy, coverage and missingness audits across CISI 1 to 3, museum collections, Mackay 1938 and Marshall 1931 tables, photograph crops and post-catalogue finds (1987–2026), conflict preservation (2,870 unadjudicated CISI 2 cell disagreements, 2,596 cross-source variant families, Lothal CLXI F and Harappa H-2587), rights separation, and a six-stratum pre-submission human accuracy-audit protocol.
- [methods.md](methods.md): Exact Schema v2.0 table definitions, sidecar formats, acceptance and conflict rules, adapter join logic, deterministic replay hashes and reproduction commands.
- [claim-evidence-map.md](claim-evidence-map.md): Traceability table mapping every numerical claim (`C01`–`C27`) in `manuscript.md` to its exact repository file and JSON, CSV or Markdown key.

## Synthesized source packages

This paper integrates frozen outputs from eleven repository packages without modifying any earlier run:

- [2026-10-06-evidence-census](../../experiments/2026-10-06-evidence-census/synthesis/REPORT.md) and findings [F-0007](../../knowledge/findings/F-0007-catalogue-identifiers-missing-from-export.md), [F-0008](../../knowledge/findings/F-0008-museum-joins-are-a-lower-bound.md), [F-0009](../../knowledge/findings/F-0009-site-frame-coverage-in-the-local-export.md)
- [2026-10-12-data-inventory](../../experiments/2026-10-12-data-inventory/README.md)
- [2026-10-13-cisi2-basic-data-pilot](../../experiments/2026-10-13-cisi2-basic-data-pilot/README.md) and [2026-10-13-cisi-basic-data-full](../../experiments/2026-10-13-cisi-basic-data-full/README.md)
- [2026-10-13-cisi3-range-coverage](../../experiments/2026-10-13-cisi3-range-coverage/README.md)
- [2026-10-13-mackay-marshall-tables](../../experiments/2026-10-13-mackay-marshall-tables/README.md)
- [2026-10-13-museum-open-access](../../experiments/2026-10-13-museum-open-access/README.md)
- [2026-10-13-image-index-and-units](../../experiments/2026-10-13-image-index-and-units/README.md)
- [2026-10-21-post-catalogue-finds](../../experiments/2026-10-21-post-catalogue-finds/README.md)
- [2026-10-22-object-register](../../experiments/2026-10-22-object-register/REPORT.md) and [2026-10-22-evidence-integration](../../experiments/2026-10-22-evidence-integration/REPORT.md)
- [2026-10-26-object-pilot](../../experiments/2026-10-26-object-pilot/REPORT.md) and [2026-10-26-source-conflicts](../../experiments/2026-10-26-source-conflicts/REPORT.md)

## Open pre-submission blockers

Following the 22 October field novelty review ([REPORT.md](../../experiments/2026-10-22-field-novelty-review/REPORT.md), Section 4), five concrete gates must close before submitting this draft to a journal:

1. **Six-stratum human accuracy audit (`manuscript.md`, Section 6, Table 8).** Independent human inspection of 350 stratified units across CISI 1 and CISI 2 printed volumes (not only blurred scans), Mackay and Marshall plates, museum photographs, face–image links, post-catalogue reports and cross-source variant families, published in a new dated verification directory.
2. **Epigraphic specialist adjudication.** Human review of the 12 provisional segment-order maps on divided faces, the 4 quarantined image keys (`H-603`, `M-663`, `M-1187`, `M-1202`), the 13 Mohenjo-daro FC-rule exceptions and the 3 weaker-evidence museum joins.
3. **CISI 2 unadjudicated-cell release decision.** Either adjudicate the 2,870 Amendment 2 CISI 2 disagreements against a printed copy of Shah and Parpola (1991), or freeze the journal release table to the adjudicated and unbracketed subset with Amendment 2 unions separated into an unverified supplement.
4. **Redistribution scope confirmation (`Q-1028`).** Decide between publishing a clean CC0 and CC BY 4.0 reconciliation release (identifiers, page locators, presence and conflict flags, coverage counts, open museum and Koshy excavation metadata, plus `fetch_data.py` build recipe) or obtaining documented reuse permission for Lipi and CISI record-level payloads.
5. **Authorship, venue selection and archival follow-ups.** Assign authors and target data journal; optionally fold in acquired CISI 3.1, Vats 1940 Harappa tables, a Dholavira accession-to-CISI bridge, ASI negative records for Lothal CLXI F and HARP 1996 object cards for H-2587 as versioned updates.
