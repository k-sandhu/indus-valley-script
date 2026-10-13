# Literature package

The [survey](SURVEY.md) explains mechanisms supporting continued provision, learning and collective work. The [gap assessment](GAP-ASSESSMENT.md) develops six conditional comparisons and identifies their predecessors. These are exploratory research proposals; no archaeological parameters were fitted.

[SOURCES.json](SOURCES.json) contains 28 records, of which 25 support selected primary readings. Each record states the actual inspected scope, exact locators, witness hashes, access attempts, rights and collaborator dependencies. The three further leads comprise a publisher description and two works whose full primary text was unavailable. Download size does not determine reading depth.

[OBSERVATIONS.json](OBSERVATIONS.json) contains 45 source statements and constructions. [COMPARISONS.json](COMPARISONS.json) distinguishes the six proposed tests and a chronology control from the authors' recommendations. [QUERY-LOG.json](QUERY-LOG.json) records search themes, access failures and the reason for the limited 2026 follow-up. The [retrospective](RETROSPECTIVE.md) records corrections and remaining limits.

The acquisition helpers use Python, Requests, Beautiful Soup and PyMuPDF. The selected Sraffa OCR also uses Tesseract. All publications, OCR, extracted text, search renderings and diagnostic images remain in ignored local raw directories. Source identity is checked separately from file integrity; hashes establish which bytes were used. The [source audit](source-checks-v1.json) passes 312 checks of bytes, lineage, IDs, declarations and ignored status. It does not reproduce the published analyses.

To check the retained package, run `python experiments/2026-10-11-societal-persistence/literature/verify_package.py` from the repository root. Re-running acquisition helpers requires a fresh capture tag or output because they preserve existing witnesses. `audit_sources.py` also refuses to overwrite its retained v1 audit. Metadata and prose are authored artifacts listed in [changed-paths.json](changed-paths.json); ignored compiled bytecode is listed separately as a local generated helper.
