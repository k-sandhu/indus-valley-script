"""Generate prose summaries from revised aggregate outputs, inside this package."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
def read(name): return json.loads((OUT/name).read_text(encoding='utf-8'))
def text(name,value): (OUT/name).write_text(value.rstrip()+'\n',encoding='utf-8')
a=read('aggregate.json');sites=read('site-rows.json')['sites'];comparison=read('site-count-comparison.json')
final=[s for s in sites if s['final_report']['publication_assessment'] in ('Final excavation monograph','Final exploration publication')]
partial=[s['canonical_name'] for s in sites if s['final_report']['publication_assessment'].startswith('Excavation report identified')]
inspected=[s['canonical_name'] for s in final if s['final_report'].get('full_text_inspected')]
monographs=[s['canonical_name'] for s in final if s['final_report']['publication_assessment']=='Final excavation monograph']
surveys=[s['canonical_name'] for s in final if s['final_report']['publication_assessment']=='Final exploration publication']
table='\n'.join(f"| {c['site']} | {c['published_count']:,} | {c['local_faces']:,} | {c['local_object_families']:,} | {c['local_distinct_cisi_ids']:,} |" for c in comparison)
missing='\n'.join(f'| {k} | {n} |' for k,n in list(a['missing_fields'].items())[:12])
prefix='experiments/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/'
text('README.md',f'''# Pakistan and Afghanistan site census

The revised exploratory census contains **{a['site_label_rows']} label rows** and **{a['catalogue_localities']} site entities** after joining the catalogue aliases Gharo Bhiro and Nuhato. Every row has at least {a['minimum_distinct_revision_queries_per_site']} distinct new live queries and an opened source. The merged ledgers contain {a['search_records']} search or inspection records and {a['sources']} source records, including historical leads and unsuccessful access. The revision added {a['revision_live_web_queries']} live search runs. See [site-rows.json](site-rows.json), [site-rows.csv](site-rows.csv), [searches.json](searches.json) and [sources.json](sources.json).

Final excavation monographs are identified for {len(monographs)} sites and final exploration publications for {len(surveys)}. A full final-report scan was inspected for {len(inspected)} site, Chanhu-daro. Reports for {len(partial)} further rows have unresolved final or comprehensive status. No dated inscription discovery was established after a verified latest site-specific CISI cutoff. These publication and later-find bases are explained in [REPORT.md](REPORT.md).

Mahadevan 1977 pages 6–7 provide a matched historical total of **2,596 included inscribed objects across seven sites**. Their local rows contain **4,732 faces, 3,805 object families and 3,565 distinct CISI identifiers**. The historical and current inventories differ in date and selection. Across all {a['local_matched_label_rows']} matched local labels, the coordinator aggregate sums to **{a['local_label_sum_faces']:,} faces, {a['local_label_sum_object_families']:,} families and {a['local_label_sum_distinct_cisi_ids']:,} identifiers**. See [site-count-comparison.json](site-count-comparison.json), [aggregate.json](aggregate.json) and each row’s `local_corpus`.

## Reproduce

From the repository root, run:

```powershell
python {prefix}make_discovery_row.py
python {prefix}build_revision.py
python {prefix}write_revision_reports.py
python {prefix}repair_active_text.py
python tools/review_prose.py --path {prefix.rstrip('/')} --no-write
python {prefix}inventory_outputs.py
```

`build_revision.py` reads the revision files and the existing local coverage aggregate. It makes no network requests. The CSV has one row per label; nested fields are UTF-8 JSON strings in CSV cells. The first-pass assembler `build_site_rows.py` is retained as a superseded record and must not be used to regenerate the revised census. Acquisition commands are in [acquire_common_sources.py](acquire_common_sources.py) and [inspect_common_pdf.py](inspect_common_pdf.py); dependencies used were requests, PyMuPDF, pypdf and the local Tesseract executable. No installation was performed. Regional helper code is preserved under [research-code](research-code/README.md).

## Preserved evidence and access

All 25 original files were copied byte for byte into [first-pass](first-pass/) before revision. [preservation.json](preservation.json) gives archive hashes. [PROTOCOL.md](PROTOCOL.md) records the dated amendments. [RETROSPECTIVE.md](RETROSPECTIVE.md) records corrections, reuse and failures. New source PDFs, HTML, OCR and page images remain under this package’s local raw directory. Public downloads did not establish image redistribution rights.

New nearby labels and their inclusion trails are recorded in the `discovery` fields and [discovery-candidates.json](discovery-candidates.json). The full list of created or changed paths is [created-paths.json](created-paths.json). Mechanical reference, query and CSV checks are in [revision-audit.json](revision-audit.json); these do not verify archaeological interpretations.
''')
text('REPORT.md',f'''# Pakistan and Afghanistan: revised census

The census now records {a['site_label_rows']} requested or added site labels and {a['catalogue_localities']} site entities after the catalogue alias join. Gharo Bhiro and Nuhato remain separate rows because the local corpus uses both labels; CISI 2 describes them as one locality. {a['sites_with_coordinates']} rows have a numerical coordinate, with source precision and unresolved archaeological identification retained. {a['sites_with_numeric_class_observations']} rows contain a numerical class observation, including historical subsets, comparative catalogue entries and scoped zero-find statements. These figures come from [aggregate.json](aggregate.json) and the individual `coordinates` and `reported_counts_by_class` fields in [site-rows.json](site-rows.json).

## Publications and later finds

Final excavation monographs are identified for {len(monographs)} sites: {', '.join(monographs)}. Final exploration publications cover {len(surveys)} further labels: {', '.join(surveys)}. Only Chanhu-daro’s full final-report scan was inspected during this revision, primarily its title, preface and recording information. Five further reports have unresolved final or comprehensive status: {', '.join(partial)}. This classification uses each row’s `final_report.publication_assessment`; bibliographic identification does not establish a completed modern inscription inventory.

The strict post-CISI tally is **0**. {a['post_cisi_assessment_status_counts'].get('no_dated_find_located',0)} rows have no dated later find recovered by their recorded query sets; {a['post_cisi_assessment_status_counts'].get('unresolved',0)} have an unresolved cutoff or later-find history. Ganweriwala’s 2015 tablet is documented in the opened 2016 account, but its latest catalogue inclusion is unresolved. Chanhu-daro’s renewed 2015–17 work is documented; exact inscription pages and counts remain inaccessible. The Harappa 1998–2000 tablets belong to later CISI coverage, and the earlier first-pass Nausharo attribution was corrected. Balakot’s 1976 excavation is earlier than CISI 2. See those rows’ `post_cisi_finds`, `post_cisi_assessment` and source locations, rather than treating publication dates as discovery dates.

## Published counts and local coverage

Mahadevan’s *The Indus Script: Texts, Concordance and Tables* (1977), page 6, includes objects whose inscriptions were wholly or partly legible. Page 7 supplies a class table for Mohenjo-daro, Harappa and Chanhu-daro. The scan was inspected visually, and the exact extracted totals are in [revision-common-counts.json](revision-common-counts.json), source RCO-M77. Zero cells apply to that included historical inventory.

| Site | Included objects,1977 | Local faces | Local families | Local CISI IDs |
|---|---:|---:|---:|---:|
{table}
| Total | 2,596 | 4,732 | 3,805 | 3,565 |

The local aggregate is a later derivative of catalogue records. Faces, families, identifiers and published physical objects have different definitions. The table therefore supports a dated inventory comparison; a pooled completeness percentage would require a reconciled object crosswalk. The seven comparison records and their units are in [site-count-comparison.json](site-count-comparison.json).

Inspected catalogue ranges expose more specific gaps. Rehman Dheri has 270 catalogue entries: 1 bone seal, 266 marked pottery objects and 3 objects captioned as tentative scrapers, against 2 local identifiers. Sarai Khola has 68 marked sherds reported in Halim 1972, with 10 photographed in CISI 2 and none in the local aggregate. Naru-Waro-dharo has 3 CISI 2 entries and 3 local identifiers. These are mark-inclusive catalogue comparisons, supported by the rows’ count records and CISI 2 pp.352–378,410–411,406,445–447. The numbering checks establish those printed ranges without asserting that every number represents an accepted Indus-script object.

CISI classifications also change the smaller-site comparisons. Nausharo has five clearly script-bearing seal identifiers Ns5–9 in the inspected 1991 plates. Mehrgarh’s Mr1–17 are comparative geometric seal or amulet forms and Mr18 is a bowl graffito. The approximate 850 Mehrgarh figure counts incised marks from early excavation seasons. Pirak’s introduction reports three Mature Harappan surface seals while the plates illustrate Pk1–2. The catalogue’s fragment-number convention prevents a direct conversion of every numbered view into a separate physical object. The exact observations and exclusions remain beside their source pages in `reported_object_counts`.

## Missing fields and source access

The most frequently unresolved fields below count label rows. A recorded numeric class observation can be a limited subset; it does not fill a complete site inventory. Metadata labels apply to the inspected publication portion. An inaccessible report field is unresolved, rather than an asserted absence.

| Field | Unresolved rows |
|---|---:|
{missing}

Later CISI 3.1/3.2 pagination, complete excavation class inventories and modern custody remain the largest substantive gaps. Current custody was not reverified for any site; dated holding codes and Harappa’s2010storage statement remain in `present_holding`, with the unresolved current check in `holding_assessment`. The CISI 3.3 selected excerpt gives Shortughai Sh1–84 on pp.509–523 and Mundigak supplementary Mgk63–66 on p.528, but omits the full object pages needed to audit those mixed inventories. Nuhato’s 2018 report remains inaccessible. Rajanpur Chak 585 coordinates describe a candidate early settlement, whose identity with the local tablet’s label has not been established. These limits appear in the relevant row fields with the exact searches that failed to resolve them.

The source ledger distinguishes an opened body, a bibliographic record, a search snippet and failed access. It retains irrelevant search leads for an auditable search history. The merged source count is a ledger size, not a count of independent excavation publications. Raw acquisitions stay local because no general redistribution permission was established. CISI 2 p.ii assigns separate rights to the volume and object photographs.

## Reviewer checks

Repeat the Mahadevan page 6–7 transcription and three class-table column sums. Recheck the Rehman Dheri scraper captions and Sarai Khola 68-versus-10 basis. Open the latest site-specific CISI 3.2 entries before changing the post-CISI tally. Resolve Sibri Sb4 provenance, Rajanpur’s homonym and Gharo Bhiro/Nuhato object identities. Compare gazetteer coordinates and campaign disagreements with original report maps. Rerun the README commands and sample every source ID used for numerical counts.
''')
text('RETROSPECTIVE.md',f'''# Revision retrospective

The first pass left coordinates, publication pages, class counts and metadata insufficiently checked. It was preserved in 25 files under `first-pass/` before any editing. The revision reuses its scope, query leads and source ledger, the broad census in `sites-and-publications`, the coordinator’s local coverage aggregate, and the repository’s Mackay 1943scan. The registry and literature retrospective helped identify the existing CISI scan and avoid treating repeated scans as separate evidence.

## Approaches and outcomes

Three regional revisions and the nearby-site additions supplied new searches and source inspections. The final assembler copies the coordinator’s local fields exactly, joins spelling variants such as Bala-kot and Balakot, and preserves corpus labels. It combines {a['site_label_rows']}rows, {a['search_records']}search or inspection records and {a['sources']} source records. Every row has at least 3 distinct new queries and an opened source. The classification and mechanical checks are retained in [revision-audit.json](revision-audit.json).

The full CISI 2scan and the full Mahadevan 1977scan were recovered through public Internet Archive metadata and downloads after direct mirrors failed. CISI 2 was searchable. Mahadevan was image-only, so its pages 6–7and828were rendered and visually inspected while a separately downloaded OCR derivative supplied navigation. The primary counts now retain their page, class, unit, selection rule and date. The source PDFs and acquisition hashes are in the local raw directory.

An opened archaeological gazetteer supplied missing coordinates and campaign references. Its letter-spaced PDF text required whitespace normalization for name lookup. It also exposed disagreements with government coordinates and different campaign summaries. Those disagreements remain in the rows. A source-backed check replaced the first-pass Allahdino city-centre coordinate.

## Corrections

The Fuls 2023 regional index counts legible sign occurrences. The first pass had treated several bracketed figures as object totals; those comparisons were removed. CISI entries likewise include geometric seals, pottery marks and comparative material. Rehman Dheri’s270 entries were divided into 1 seal,266 pottery objects and3 tentative scrapers after inspecting the page 378caption. Later discussion of an old object and an excavation before CISI publication were removed from the strict post-CISI tally. Miri Qalat and nearby local labels appeared during the country check of the local corpus’s Iranian Plateau category; their addition is recorded as an exploratory scope amendment.

Nindowari’s 2011publication title was corrected from an unsupported first-pass title. Sutkagen-dor’s Stein reference was corrected to *An Archaeological Tour in Gedrosia*. Shortughai catalogue entries and seals were kept as different counts. UTF-8 repairs preserve the archived witnesses and correct active source summaries. Exact source titles were checked before mechanical repair.

## Failures and remedies

Direct source requests returned HTTP 403, 406 or 404, timed out, failed TLS connections or encountered an access challenge. Their source and acquisition records retain the unsuccessful route. Public previews often omitted the later catalogue and object pages; the revised tables use field-level unresolved records with search IDs instead of filling those pages from snippets.

Drive C filled during integration. Two redundant, regenerable derivatives were removed from this package’s common raw directory: the extracted `cisi2-archive.txt` and 13 Sibri page-render PNGs. The source PDFs, page-text JSON and Sibri OCR were preserved. After disk space returned, all revision JSON files were parsed again. No other package’s files were removed.

## Remaining work

The package completes the search and field-recording checklist, with unresolved values where the recorded sources did not supply an answer. Complete excavation inventories, the missing later CISI pages and current repositories require additional source access. The next numerical change should come from a named report page or object crosswalk. [REPORT.md](REPORT.md) gives the reviewer’s source and recomputation checks.
''')
registry=dict(id='SITE-CENSUS-PAK-AFG-2026-10-06',theme='site census',status='Exploratory',question='What site, publication, inscription-count, metadata, later-find, custody and digital-access evidence can be recovered for Pakistan and Afghanistan?',outcome=f"Revised {a['site_label_rows']} label rows / {a['catalogue_localities']} site entities; minimum 3 new distinct queries per row; {a['search_records']} search/inspection records and {a['sources']} source records. Final publications identified for {len(final)} rows, 1 full final-report scan inspected. Strict dated post-CISI finds 0. M77 matched total 2596 included objects versus 4732 local faces / 3805 families / 3565 identifiers.",challenge='Incomplete later CISI access, mixed catalogue units, unresolved object provenance and missing complete excavation inventories.',remedy='Preserved 25 first-pass files, inspected primary catalogues and M77 tables, joined exact local aggregates, recorded source-specific count units and field-level failures, repaired UTF-8.',evidence=[prefix+n for n in ['README.md','PROTOCOL.md','REPORT.md','RETROSPECTIVE.md','site-rows.json','site-rows.csv','sources.json','searches.json','site-count-comparison.json','revision-audit.json','preservation.json','created-paths.json','build_revision.py']],retry_when='Full later CISI pages, final excavation inventories or institutional object records permit source-page and physical-object reconciliation.')
text('registry-entry.json',json.dumps(registry,ensure_ascii=False,indent=2))
print('Wrote README,REPORT,RETROSPECTIVE and proposed registry entry.')
