# Foreign-find site census, batch D

This exploratory census contains **36 rows**, covering all **23 named sites**, all **27 local export labels** assigned to the four requested regions, and Babylon, added from Laursen's 2010 inventory. Girsu and Tello share one row. Five Pakistani sites retain cross-reference rows because the local export assigns them to the Iranian Plateau. The arithmetic copies **42 faces and 42 object-family labels** from the coordinator's export. These sums retain the original labels and have no archaeological deduplication.

[REPORT.md](REPORT.md) explains the main corrections and gaps. [aggregate-results.json](aggregate-results.json) contains the totals and the complete published/local comparison. **14 rows** have a bibliographically identified excavation synthesis or final specialist catalogue, including **12 of the 23 named sites**. Coordinates have an inspected authority for **9 rows**. Four rows contain later inscription-related reports; **0** have a discovery matched to a supported CISI coverage cutoff. All 36 rows received at least four live queries, within **182 recorded searches**.

The sum of selected published object minima is **36 across 22 rows**. This combines several explicitly distinguished classes, includes uncertain Gulf signs and provisional Hajar/Ornach identifications, and cannot serve as a complete count of Indus inscriptions abroad. [site-rows.json](site-rows.json) records the source, locator, date, counting unit and inclusion decision for each numeric observation. Missing values contain a search-linked acquisition result. Campaign details, complete inventories, holdings and catalogue metadata remain unresolved for many sites; this package completes the row and search frame, with those research gaps exposed.

## Files and reproducibility

The [protocol](PROTOCOL.md) preceded the outcome calculation. [research_data.py](research_data.py) contains the curated observations; [build.py](build.py) combines them with the saved web witness and the coordinator's local coverage file. [site-rows.csv](site-rows.csv) preserves nested fields as JSON in CSV cells. [sources.json](sources.json) records all opened or snippet-seen sources, including failed opening attempts. It has 1,013 records; 46 appear in the row source lists. [searches.json](searches.json) retains every query and its pooled response references. Individual search-result attribution within a multi-query response is unavailable.

Run these commands from the repository root. Python's standard library suffices for the build and checks:

```powershell
python -B experiments/2026-10-06-evidence-census/sites-deep/d-finds-abroad/build.py --verify
python -B experiments/2026-10-06-evidence-census/sites-deep/d-finds-abroad/verify.py --verify
python -B experiments/2026-10-06-evidence-census/sites-deep/d-finds-abroad/inventory.py --verify
python -B tools/review_prose.py --path experiments/2026-10-06-evidence-census/sites-deep/d-finds-abroad --no-write
```

The first three commands compare with the preserved output bytes. To develop different observations, retain this endpoint and build into a new dated subdirectory using `--output-dir`. [validation.json](validation.json) reports structural checks; [review-checks.json](review-checks.json) adds an actual CSV round trip, source/search reference checks and eight PDF hash checks. [prose-check.json](prose-check.json) records the four-file prose scan with zero flags. These checks cannot establish that a source interpretation is correct.

[acquire_sources.py](acquire_sources.py) records the initial download/reuse attempts. Its `--verify` flag checks the saved acquisition hashes without network access; `--raw-subdir` starts a new acquisition under a dated subdirectory. [acquire_s3.py](acquire_s3.py) recovers or verifies Nippur and Tell Asmar through the current ISAC asset links. [acquire_cisi33.py](acquire_cisi33.py) acquires or verifies the institutional 2022 excerpt without replacing its witnesses. The acquisition scripts require PyMuPDF (`fitz`) and use the local raw `tmp` directory. Historical acquisition manifests are preserved inputs. Use the read-only build and checks for endpoint review, and a new raw subdirectory and manifest name for another acquisition.

All PDFs, extracted text, downloaded HTML and web-tool responses remain in `data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/`. No image rights are inferred from online access. [file-manifest.json](file-manifest.json) lists every file created for this package and its hash, apart from its own hash. [RETROSPECTIVE.md](RETROSPECTIVE.md) records acquisition failures and reused work. [registry-entry.json](registry-entry.json) proposes a shared-registry entry without editing the registry.

The reviewer should sample Laursen's Table 1, Nippur's catalogue and plate 89, the CISI 3.3 preface/contents, Salut's two fragments, and the Dilmun/Ur accession join before using these rows in a manuscript.
