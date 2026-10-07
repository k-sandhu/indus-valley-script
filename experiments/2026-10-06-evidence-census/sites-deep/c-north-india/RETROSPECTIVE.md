# Retrospective: northern India follow-up

## Reused work and source checks

The broad census supplied site labels and publication leads. The coordinator's local register supplied face, family, CISI-prefix and metadata-presence figures. Existing CISI 1 scan/OCR witnesses served as locators; catalogue pages supplied the verified ranges and classes. The ten original package files were copied to `first-pass/` before active replacement. [first-pass-manifest.json](first-pass-manifest.json) records their hashes.

The first pass had too few saved queries and little verified metadata. The follow-up executed 223 queries, with at least five distinct strings per site, and opened a primary or substantial source for every row. Missing fields link to these searches and inspected publication locations. Grouped responses cannot assign each result to an individual query. The response paths and source identities are in [searches.json](searches.json) and [sources.json](sources.json).

Several identities required correction. `puratattva36_retry.pdf` contains volume 34, while `puratattva35_retry.pdf` contains volume 35. The initial `kalibangan2020.pdf` was Suryanarayan's thesis; the actual Part II report was acquired as `kalibangan_report2020.pdf`. The mismatched acquisition history was retained and excluded from report-based counts. Visual inspection confirmed Baror author N. K. Sinha; a later citation used another surname. Tarkhanewala Dera's final volume is Trivedi 2009, MASI 99. Rakhigarhi and Sanghol submissions were retained as drafts. See [evidence_notes.py](evidence_notes.py) and source inspection records.

Catalogue objects, selected texts, graffiti instances and local faces were stored separately. Karanpura's graffiti instances include sherds, whorls and a ring. A report-section boundary check kept the preceding Sisupalgarh sealings out of Rupar's count. Geometric Kunal seals and historic Sanghol seals were not assigned Indus legends. Conflicting printed coordinates were preserved with their sources. These decisions appear in [site-rows.json](site-rows.json), `reported_object_counts`, `coordinates` and `main_publication_metadata`.

## Disk interruption and recovery, 7 October 2026

Windows error 112 stopped the preceding turn when the shared disk filled. After the coordinator freed space, the recovery audit inventoried 644 saved files. All recovered JSON parsed; no truncated JSON required reconstruction. Active deliverables were still first-pass outputs, while the new searches, downloads and OCR survived. Empty OCR files corresponded to blank or image-only pages. The initial record is the local raw `recovery-audit.json`.

Cleanup removed 231 temporary page renders whose retained PDFs permit regeneration, freeing **253,209,317 bytes**. PDFs, OCR, failed acquisition records and the first-pass archive were retained. The raw `cleanup-manifest.json` lists removed paths. Acquisition code now deletes a render after OCR and confines temporary locations to local raw. Small active outputs were rebuilt from surviving records. [file-manifest.json](file-manifest.json) inventories retained files; [validation.json](validation.json) checks active UTF-8 text and archive hashes. The original audit and cleanup manifests should be preserved rather than regenerated.

## Access limits and outcome

Twenty-two failed downloads remain documented. CISI 3.2's Kalibangan pages, full Farmana and Tarkhanewala Dera final inventories, Mahadevan Appendix V and ICIT count pages were not obtained. Some newer-season inventories, present custody and registration joins remain unlocated after the recorded searches. The output is classified Exploratory, with every site represented and unresolved fields explicit. Structural checks establish consistency; the reviewer should repeat the source-page checks in [REPORT.md](REPORT.md).
