"""Write the follow-up narrative from the current aggregate file, offline."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
PREFIX = 'experiments/2026-10-06-evidence-census/sites-deep/c-north-india/'

def main():
    a = json.loads((OUT/'aggregates.json').read_text(encoding='utf-8'))
    assert (a['sites'], a['cisi1_catalogue_objects']) == (25,176)
    readme = '''# North India site census: completed follow-up

The register covers **25 sites**: the 23 supplied sites, Tigrana from the local Inter-Riverine register, and Rohira from CISI 1 p. 361. Every site has at least five distinct executed follow-up searches and an opened primary or substantial secondary source. The 220 follow-up queries are indexed in [searches.json](searches.json). Findings remain **Exploratory**; unavailable fields carry search and source-location records.

[aggregates.json](aggregates.json) records six sites with an identified final excavation monograph and nine with reported inscribed discoveries after the 1987 India catalogue baseline. Three of those nine were already in CISI 1. The nine inspected CISI 1 sections contain **176 catalogue objects**. The local register contains **290 faces, 271 object families and 232 distinct CISI identifiers** across this batch. These totals have different units and dates.

## Files and reused inputs

- [REPORT.md](REPORT.md): findings, comparisons, gaps and review targets.
- [site-rows.json](site-rows.json) and [site-rows.csv](site-rows.csv): all ten requested field groups for each site. CSV mapping/list cells contain JSON strings.
- [sources.json](sources.json): bibliography, opened versus snippet status, locations, access and reuse terms for 896 observed records. Unused leads can have unresolved authors or dates.
- [PROTOCOL.md](PROTOCOL.md): protocol and dated amendments.
- [RETROSPECTIVE.md](RETROSPECTIVE.md): approaches, corrections and disk recovery.
- [registry-entry.json](registry-entry.json): proposed entry; the shared registry was not edited.
- [checks.json](checks.json), [validation.json](validation.json), [file-manifest.json](file-manifest.json): aggregate checks, record checks and the complete retained path inventory.

The prior broad census supplied site/publication leads. The coordinator's `experiments/2026-10-06-research-program/local-site-coverage.json` supplies local figures unchanged for matching rows. Existing CISI 1 scan/OCR witnesses were reused and catalogue pages inspected to establish ranges and classes. The ten original files remain byte-for-byte in `first-pass/`, checked against [first-pass-manifest.json](first-pass-manifest.json). Active deliverables are UTF-8; the archive retains its original damaged text.

PDFs, OCR, web responses, acquisition failures and recovery records are local-only under `data/raw/2026-10-06-evidence-census/sites-deep/c-north-india/`. No third-party page or image payload is included in this owned directory. A fresh checkout needs those excluded witnesses to rebuild the index.

## Rerun from the repository root

```powershell
python -X utf8 experiments/2026-10-06-evidence-census/sites-deep/c-north-india/build_site_census.py
python -X utf8 experiments/2026-10-06-evidence-census/sites-deep/c-north-india/write_reports.py
python -X utf8 experiments/2026-10-06-evidence-census/sites-deep/c-north-india/validate_census.py
python tools/review_prose.py --path experiments/2026-10-06-evidence-census/sites-deep/c-north-india --no-write
```

The builder reads [evidence_notes.py](evidence_notes.py), the local register and saved search/acquisition records, with no network requests. Validation checks references, JSON/CSV agreement, active encoding and archive hashes; it does not verify archaeological claims. `finalize_manifest.py` separately checks retained PDFs and writes the path inventory. Acquisition helpers are retained for source recovery, with temporary directories confined to local raw. The audit and cleanup scripts record one-time actions and should not be rerun over their original manifests.
'''
    report = '''# North India census findings

The follow-up covers **25 sites**, with **220 executed queries** and an opened primary or substantial secondary source for each. Six sites have an identified final excavation monograph; nine have reported inscribed discoveries after the 1987 India catalogue baseline. Nine inspected CISI 1 sections contain **176 catalogue objects**. Local coverage totals **290 faces, 271 object families and 232 distinct CISI identifiers**. The bases are [aggregates.json](aggregates.json), `sites`, `followup_queries`, `final_excavation_monograph_count`, `post_1987_inscribed_find_count`, `cisi1_catalogue_objects` and `local_totals`.

## Scope and sources

The supplied list contains 23 sites. Tigrana was added from the Indian Inter-Riverine local coverage row, which contains one TAG-class face. IAR 1987-88 p. 21 documents its excavation; independent primary inscription confirmation remains unlocated. Rohira was added from Rhr1-2 in Joshi and Parpola's *Corpus of Indus Seals and Inscriptions. 1. Collections in India* (1987), p. 361; IAR 1982-83 pp. 65-66 and plate 39 supplies the excavation account. See those rows in [site-rows.json](site-rows.json), `primary_source_opened`, `reported_object_counts` and `open_problems`.

Additional regional queries investigated Mandi, Bargaon, Girawad, Balu and Nagar without establishing an eligible inscription securely attributable to another site. Snippets crossing site-paragraph boundaries were insufficient for inclusion. The selection record is [searches.json](searches.json), `adaptive-search-38-q1` through `q4`; it does not establish archaeological absence.

Every row has at least five distinct follow-up queries. Records give exact strings, dates, service, source IDs and response paths. Grouped results cannot be assigned to individual member queries. The 33 first-pass query records are retained separately and excluded from the follow-up count because their original responses were not saved. The 896 source records include unused and failed leads; `opened`, `access`, `inspected` and `witnesses` identify what was read. Twenty-two failed downloads remain in `searches.json.failed_downloads`; web-opening failures also remain in raw response records.

## Final publications and later discoveries

The six final-monograph sites are Kalibangan, Farmana, Mitathal, Hulas, Tarkhanewala Dera and Bhagwanpura. Relevant full volumes were obtained for Mitathal, Hulas and Bhagwanpura. Kalibangan Part II was inspected, but the inscription catalogue belongs to inaccessible Part I. Farmana's 2011 volume and Trivedi's 2009 *Excavations at Tarkhanewala-Dera and Chak 86 (2003–2004)*, MASI 99, were identified bibliographically; their full inventories were not obtained. Final-report identification therefore does not imply inventory access. Manda and Siswal have published short chapters, counted separately. Rakhigarhi and Sanghol 2014 submissions remain drafts. The basis is each row's `primary_and_final_publications` and `final_excavation_monograph_identified`, plus `aggregates.json.final_monograph_access`.

| Site with discovery after 1987 | Evidence location | Scope limitation |
|---|---|---|
| Rakhigarhi | IAR 1999-2000, pp. 31-33: seals, tablets, sealings and graffiti | Class totals unstated; later seasons unjoined |
| Farmana | 2008 preliminary report, pp. 100-105, figs. 106-109: two seals and two impression objects | One impression has lost its text area; final count unavailable |
| Bhirrana | Puratattva 35, pp. 64-65: four steatite seals, three with legends | Ministry snippet reports five seals and two inscribed copper celts; full count page inaccessible |
| Sanauli | Puratattva 36, plate 21: sherd captioned with a Harappan character | Lower bound from a caption; plate page unnumbered in accessible OCR |
| Ropar (Rupar) | Submitted IAR 2011-12, pp. 74-75, plate 30: three broken sherds with signs and graffiti on a chakla base | Possible overlap in wording; edition status unresolved |
| Karanpura | IAR 2013-14, pp. 116-123: two seals and 157 graffiti instances | 134 sherds, 22 whorls and one ring; not all marks establish texts |
| Binjor (4MSR) | Frontline, 22 July 2016, pp. 72-78: separate 2015 and 2016 seals | Director quotations and object photograph; final catalogue unavailable |
| Baror | Puratattva 35, p. 54: inscribed terracotta sealing | Preliminary account; later inventory unresolved |
| Tarkhanewala Dera | Puratattva 34, pp. 30-34: 2003-04 seal impression | Final 2009 inventory unavailable |

Exact titles, authors, dates and URLs are in [sources.json](sources.json), IDs `iar1999`, `farmana2008`, `puratattva35`, `sanauli2006`, `iar2011`, `iar2013`, `binjor2016` and `puratattva34`; each row also records eligibility and locations in `reported_object_counts` and `post_cisi_finds`. Rakhigarhi, Rupar and Tarkhanewala Dera were already catalogued in CISI 1. The other six use 1987 as a calendar baseline, with no inspected CISI 1 section. A later publication alone does not date the discovery after 1987.

## Published inventory against local coverage

'''
    report += '| Site | CISI 1 pages | Catalogue objects | Local faces | Local families | Local distinct CISI IDs |\n|---|---:|---:|---:|---:|---:|\n'
    rows = json.loads((OUT/'site-rows.json').read_text(encoding='utf-8'))['rows']
    by_name={r['canonical_name']:r for r in rows}
    for c in a['comparisons']:
        r=by_name[c['site']]
        report += f"| {c['site']} | {r['cisi_coverage']['page_range']} | {c['cisi1_catalogue_objects']} | {c['local_faces']} | {c['local_families']} | {c['local_distinct_cisi_ids']} |\n"
    report += '''| **Total on nine sites** | | **176** | **266** | **248** | **232** |

The table comes from `aggregates.json.comparisons` and `local_totals_on_cisi1_sites`. Its 176 entries comprise **91 seals, 16 sealings, 15 tablets, 52 pottery/graffiti objects and two metal objects**. No entries in these sections were assigned to the residual other class. Page ranges and class boundaries are in `site-rows.json.cisi_coverage` and `reported_object_counts`. Some objects are geometric, blank or indeterminate; 176 is a catalogue total. The inspected 1987 site runs are contiguous.

Banawali's 23 distinct local identifiers against B1-37 give 62.16% of the catalogue run. Chandigarh has 3/4 (75%); Tarkhanewala Dera 1/3 (33.33%); Rohira has no local site label against two catalogue objects. The other four comparable early runs have all catalogue IDs represented. These are identifier comparisons. Archaeological coverage requires registration-number joins and later-find inventories. Kalibangan's 197 local identifiers include numbering through K476, so comparison with K1-122 cannot yield a coverage percentage. CISI 3.2 pages and K123-476 continuity remain unverified. See `within_cisi1_run_count_comparable`, `identifier_fraction` and Kalibangan's `cisi_coverage.later_volume`.

Mahadevan's 1977 main-corpus table gives **118 selected objects across seven batch sites**, with **four more in its addendum**. Kalibangan contributes 99 main objects: 56 seals, 21 sealings, 20 pottery pieces and two bronze implements. The basis is *The Indus Script: Texts, Concordance and Tables*, printed p. 6 section 4, p. 7 section 6.2 and p. 24 section 16, in the opened 48-page excerpt. Appendix V, pp. 816-829, was absent; the ICIT preview exposed contents rather than site-count pages. These selected counts and CISI's later inventory remain separate. See `mahadevan_1977_or_icit_count` and source `m77`.

## Metadata and remaining gaps

For cited inscription samples, the most frequently unlocated fields are absolute dates (**20/25 sites**), drawings (**18/25**), findspot (**18/25**), registration numbers (**17/25**) and dimensions (**12/25**). Stratum/phase, material and photographs are each unlocated at seven sites. These are document-availability counts from `main_publication_metadata`, aggregated in `missing_metadata_fields`. They include sites without a secure inscription sample. A `no` means the field was not located for that sample, or explicitly absent. `partial` includes site-level dates, scales and incomplete contexts.

Numerical counts remain unresolved at 13 sites for seals, 17 for sealings, 22 for tablets, 16 for pottery/graffiti, 23 for metal and 24 for other objects (`aggregates.json.unresolved_counts_by_class`). Reported quantities retain unit, date, eligibility and page; missing classes are search-linked nulls. Kunal's geometric seals, historic Sanghol seals and Bhagwanpura's marked objects cannot be converted wholesale into Indus-text inventories.

Coordinates require selective review. Hulas has inconsistent printed coordinates in its introduction and Appendix III; an opened gazetteer supplies a village proxy. Manda's gazetteer locality is available only in a snippet, while its excavation volume and IAR contain incompatible latitudes. Binjor's paper uses malformed notation; an official register snippet lists two mound points without establishing which is 4MSR. Literal alternatives are retained. Kotla Nihang, Rohira and Lohari Ragho gazetteer points are locality proxies. Masudpur's component renumbering prevents a cluster point from locating every mound. Chandigarh's excavation-point coordinates remain unlocated. Each `coordinates` field links a source or failed searches.

Custody records are dated snapshots, usually CISI 1's 1987 table, pp. 374-375. Present holdings remain unresolved without newer object-specific evidence; generic museum descriptions and souvenirs were insufficient. Most publications and images have no verified open reuse terms and remain local. Gazetteer text/data terms are distinguished from image rights in `current_holding` and `digital_availability_and_reuse`.

## Reviewer checks

Repeat the commands in [README.md](README.md). Sample CISI 1 Kalibangan and Banawali class boundaries, Rohira p. 361 and custody pp. 374-375; Mahadevan pp. 6-7 and 24; Karanpura pp. 116-123; Farmana figs. 106-109; and Rupar's submitted IAR pp. 74-75 without importing the preceding Sisupalgarh sealings. Review coordinate conflicts before mapping. [validation.json](validation.json) checks record structure, encoding, arithmetic and archive preservation; source-page review remains necessary.
'''
    retro = '''# Retrospective: northern India follow-up

## Reused work and source checks

The broad census supplied site labels and publication leads. The coordinator's local register supplied face, family, CISI-prefix and metadata-presence figures. Existing CISI 1 scan/OCR witnesses served as locators; catalogue pages supplied the verified ranges and classes. The ten original package files were copied to `first-pass/` before active replacement. [first-pass-manifest.json](first-pass-manifest.json) records their hashes.

The first pass had too few saved queries and little verified metadata. The follow-up executed 220 queries, with at least five distinct strings per site, and opened a primary or substantial source for every row. Missing fields link to these searches and inspected publication locations. Grouped responses cannot assign each result to an individual query. The response paths and source identities are in [searches.json](searches.json) and [sources.json](sources.json).

Several identities required correction. `puratattva36_retry.pdf` contains volume 34, while `puratattva35_retry.pdf` contains volume 35. The initial `kalibangan2020.pdf` was Suryanarayan's thesis; the actual Part II report was acquired as `kalibangan_report2020.pdf`. The mismatched acquisition history was retained and excluded from report-based counts. Visual inspection confirmed Baror author N. K. Sinha; a later citation used another surname. Tarkhanewala Dera's final volume is Trivedi 2009, MASI 99. Rakhigarhi and Sanghol submissions were retained as drafts. See [evidence_notes.py](evidence_notes.py) and source inspection records.

Catalogue objects, selected texts, graffiti instances and local faces were stored separately. Karanpura's graffiti instances include sherds, whorls and a ring. A report-section boundary check kept the preceding Sisupalgarh sealings out of Rupar's count. Geometric Kunal seals and historic Sanghol seals were not assigned Indus legends. Conflicting printed coordinates were preserved with their sources. These decisions appear in [site-rows.json](site-rows.json), `reported_object_counts`, `coordinates` and `main_publication_metadata`.

## Disk interruption and recovery, 7 October 2026

Windows error 112 stopped the preceding turn when the shared disk filled. After the coordinator freed space, the recovery audit inventoried 644 saved files. All recovered JSON parsed; no truncated JSON required reconstruction. Active deliverables were still first-pass outputs, while the new searches, downloads and OCR survived. Empty OCR files corresponded to blank or image-only pages. The initial record is the local raw `recovery-audit.json`.

Cleanup removed 231 temporary page renders whose retained PDFs permit regeneration, freeing **253,209,317 bytes**. PDFs, OCR, failed acquisition records and the first-pass archive were retained. The raw `cleanup-manifest.json` lists removed paths. Acquisition code now deletes a render after OCR and confines temporary locations to local raw. Small active outputs were rebuilt from surviving records. [file-manifest.json](file-manifest.json) inventories retained files; [validation.json](validation.json) checks active UTF-8 text and archive hashes. The original audit and cleanup manifests should be preserved rather than regenerated.

## Access limits and outcome

Twenty-two failed downloads remain documented. CISI 3.2's Kalibangan pages, full Farmana and Tarkhanewala Dera final inventories, Mahadevan Appendix V and ICIT count pages were not obtained. Some newer-season inventories, present custody and registration joins remain unlocated after the recorded searches. The output is classified Exploratory, with every site represented and unresolved fields explicit. Structural checks establish consistency; the reviewer should repeat the source-page checks in [REPORT.md](REPORT.md).
'''
    for filename,content in [('README.md',readme),('REPORT.md',report),('RETROSPECTIVE.md',retro)]:
        content=content.replace('220',str(a['followup_queries'])).replace('896',str(a['source_records']))
        (OUT/filename).write_text(content,encoding='utf-8')
    entry=dict(id='site-census-north-india-2026-10-06',theme='Archaeological site and publication census',status='Exploratory',
        question='What published excavation, inscription-count and object-metadata evidence is available for the northern India batch, and how does it compare with the local export?',
        outcome='25 rows, 220 executed follow-up queries, minimum five distinct queries/site, and an opened primary/substantial source at all 25. Six final-monograph sites identified; nine sites with reported post-1987 inscribed finds, including three previously catalogued in CISI 1. Nine CISI 1 sections contain 176 catalogue objects; local totals are 290 faces, 271 families, 232 distinct CISI IDs. Counts keep units, dates and eligibility separate.',
        challenge='Disk-full interruption; conflicting coordinates and count bases; 22 failed downloads; inaccessible later CISI and final inventories; incomplete registration joins and current custody.',
        remedy='Audited recovered files, preserved ten first-pass files, removed 253209317 bytes of temporary renders, rebuilt UTF-8 outputs, inspected primary pages and retained exact search/failure records. Unresolved fields link to their searches and inspected sources.',
        evidence=[PREFIX+n for n in ['README.md','REPORT.md','PROTOCOL.md','RETROSPECTIVE.md','site-rows.json','site-rows.csv','sources.json','searches.json','aggregates.json','checks.json','validation.json','first-pass-manifest.json','file-manifest.json']],
        retry_when='When CISI 3.2 Kalibangan pages, Farmana/Tarkhanewala final inventories, Mahadevan Appendix V or ICIT site-count pages become accessible; when new object-specific season, registration or custody records permit reconciliation.')
    entry['outcome']=entry['outcome'].replace('220',str(a['followup_queries']))
    (OUT/'registry-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Wrote README.md, REPORT.md, RETROSPECTIVE.md and registry-entry.json as UTF-8.')

if __name__=='__main__':main()
