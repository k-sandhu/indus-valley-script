# Package C: inventory of results outside script decipherment

Owned directory: `experiments/2026-10-06-byproduct-inventory/`. Local raw directory: `data/raw/2026-10-06-byproduct-inventory/`. Use live web search for the precedent checks.

## Question

The project produced many analyses on the way to its script questions. Some concern archaeology, metrology, catalogue quality, museum records, statistical method, physical simulation, AI-assisted annotation, reproducibility or other record systems such as khipu. Because they did not advance decipherment, nobody assessed whether they are worth publishing. Find them, describe what each established, and judge which could become a note, data paper or methods paper in its own field.

## Method

Read systematically: every `README.md`, `REPORT.md`, `FINDINGS.md`, `RETROSPECTIVE.md` and result summary under `experiments/`, `research/`, `results/` and `output/`, plus `knowledge/` and the four manuscripts under `papers/`. Use `knowledge/experiments/registry.json` as a checklist so no registered entry is skipped. Large JSON outputs can be sampled for their summary fields.

Candidates include, among others: catalogue and museum-record discrepancies (Susa masses and marks between the 1911 and 2022 catalogues, Lothal impression counts, Tamil Nadu print versus web concordance, Gonur token counts, Harappa registrations); the archaeological context-completeness statistics of the inscribed corpus; the Susa marked-weight census and Dholavira weight records; the Lothal sealing and Kanmer frames; the curved-clay stamp-contact simulation and its laboratory design; the Puruchuco khipu replication and conservation controls; permutation calibration under copied records; exact finite sampling laws; identifiability certificates; the 687-cell chart annotation and its cross-annotator corrections; the failed glyph-OCR and crop-geometry diagnosis; source-acquisition failure records; and the repository's provenance and verification tooling. Add anything else you find.

For each candidate record: a short title; its field and likely audience; what was measured or established, with exact numbers; the evidence paths and fields; its current status label; what makes it potentially new, checked against a bounded web search for close precedents (cite what you find and mark opened versus snippet); what validation or external review is missing; the smallest publishable form (data note, short communication, methods note, erratum letter to a catalogue maintainer, teaching example, software note); candidate venues that actually exist; and an estimate of the remaining work.

## Outputs

`inventory.json` with one record per candidate, a ranked `REPORT.md` that groups candidates by field and explains the top five in connected prose, and `registry-entry.json`. Rank by plausible novelty, readiness and usefulness to that field, and state the ranking criteria. Mark clearly which judgments rest on a precedent search you completed and which remain unchecked. Do not rerun or modify any earlier analysis; if a number cannot be confirmed from the saved outputs, say so.
