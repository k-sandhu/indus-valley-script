# Retrospective: data inventory, 12 October 2026

## Approach

The owner asked for one page describing all data the project has and lacks, with the per-object metadata made the project's first priority. The work started from the existing record rather than new searches: the evidence census, the dataset landscape, the object ledger pilot, the Helsinki digitization packages, the Hugging Face release and the provenance files. The protocol fixed the units (face and provisional object), the placeholder rules and the planned outputs before any coverage was computed.

Three pieces of code produce the measurements. `coverage.py` reads the hash-checked normalized Lipi faces, the older website export, Mayig and the Lipi image index and writes field coverage by object type and site, placeholder counts, within-object conflicts and cross-source agreement. `holdings.py` walks the local data and literature folders, hashes every PDF and harvests titles from earlier packages' source records. `build_manifest.py` turns the source records into `data/MANIFEST.json` and checks every recorded path and hash against the local copies; `tools/fetch_data.py` reads the manifest. A background agent checked the current status of unheld sources on the web, saving witnesses locally; its findings were reviewed before entering `sources.json`, the manifest and DATA.md.

## What was found that changes plans

CISI 1 and CISI 2 are both held as complete scans. Earlier summaries listed "CISI2/3 complete photographic volumes" as not acquired; the evidence census later acquired the CISI 2 scan and the 1977 Mahadevan PDF, but the source inventory was not updated. The plate check for conjecture C-0004 therefore needs no acquisition. The Lipi repository's 8,722 image crops, already counted by the October 2 readiness audit, cover 53.4% of objects and had not been used as a face-level image layer.

A public transcription of the Mackay 1938 and Marshall 1931 seal tables (709 and 560 rows, data under CC BY 4.0 by its own notice) appeared in the census only as a search result. Its README and data notice were opened and pinned to a commit during this inventory.

## Problems and fixes

The first development run treated printed thickness ranges such as `5 - 9` (530 faces) as unusable, because the protocol had not anticipated them. The final run counts a range as usable and reports the plain-number totals beside it; those reproduce the census's 4,441 faces with any size and 1,151 with all three. The development outputs are preserved under `data/raw/2026-10-12-data-inventory/dev-coverage-v1/` and `dev-coverage-v2/`. The same development run showed that all 45 site disagreements with the older export are the spelling Chanhujo-daro; the final comparison records the alias explicitly.

Earlier packages recorded acquisitions in different JSON shapes. The title harvest found 3,127 distinct titles but linked only 62 to a local PDF path, so the holdings count relies on SHA256 deduplication of the PDFs instead (299 distinct). Some directories under `data/raw/2026-10-06-sign-context-and-seals/plot-deps-2026-10-07/` were unreadable to the walker; they hold plotting libraries, not sources, and their files are missing from the totals.

The web-check agent placed the owner's email address in the User-Agent header of four Wikimedia Commons API requests, against its instructions, and removed it from all later requests. No file written by this package contains the address; the incident is reported to the coordinator. The same agent saw new untracked `.github/ISSUE_TEMPLATE/`, `.claude/`, `CLAUDE.md` and `templates/` files appear during the run; they belong to the parallel restructuring, and `.github/` holds issue templates only, no workflow.

Codex was writing general question cards Q-0001 to Q-0038 at the same time. Several overlap in subject with the data cards (C-0004 plate checks, dimension normalization, chronology labels, duplicate photographs). The data cards were narrowed to corpus-scale acquisition and extraction, and cross-reference the general cards in `related`; Q-1001 assembles the witnesses that Q-0013 to Q-0015 read. Codex's Q-0003 asks for the object-level metadata recount that `run-2026-10-12/` now provides.

## Outcome

DATA.md, the manifest, the fetch tool, 30 question cards and the measured coverage tables are in place. The fetch tool was tested with `--list`, `--show`, `--verify` and dry runs only; no source was downloaded or overwritten. Web access was read-only: no upload, data request to a maintainer or visibility change was made.
