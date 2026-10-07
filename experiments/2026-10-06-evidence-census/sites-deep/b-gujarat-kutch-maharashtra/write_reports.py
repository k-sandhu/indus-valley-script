"""Write the reader-facing census reports and inventories after aggregation."""
from pathlib import Path
import hashlib,json,re
OWN=Path(__file__).resolve().parent
ROOT=OWN.parents[3]
RAW=ROOT/'data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra'
M=json.loads((OWN/'aggregate-results.json').read_text(encoding='utf-8'))
R=json.loads((OWN/'site-rows.json').read_text(encoding='utf-8'))
def readable_prose(text):
    # Preserve code, file paths, URLs and inline field names while spacing prose.
    parts=re.split(r'(```.*?```|`[^`]*`|https?://[^\s)]+)',text,flags=re.S)
    for i in range(0,len(parts),2):
        value=parts[i]
        value=re.sub(r'(?<=[a-z])(?=\d)', ' ', value)
        value=re.sub(r'(?<=\d)(?=[a-z])', ' ', value)
        value=re.sub(r'\bCISI(?=[123])', 'CISI ', value)
        value=re.sub(r'\b(p|pp)\.(?=\d)', r'\1. ', value)
        value=re.sub(r',(?=[A-Za-z0-9])', ', ', value)
        value=re.sub(r':(?=[A-Za-z0-9])', ': ', value)
        value=re.sub(r'(?<=[A-Za-z])\((?=\d)', ' (', value)
        value=value.replace('bundleB37','bundle B37').replace('batchA','batch A').replace('rawB/O','raw B/O').replace('TMP,TEMP','TMP, TEMP').replace('IARp.', 'IAR p.').replace('phasesII', 'phases II')
        parts[i]=value
    return ''.join(parts)

def md(name,text): (OWN/name).write_text(readable_prose(text).strip()+'\n',encoding='utf-8')

table=['| Site | CISI1 objects / pages | Local faces / families / CISI IDs |','| --- | --- | --- |']
for r in R:
    cat=next((c for c in r['cisi_coverage'] if c['volume']=='CISI1'),{})
    text=str(cat['catalogue_object_slots'])+' / '+cat['page_range'] if 'catalogue_object_slots' in cat else 'No site section in inspected contents'
    l=r['local_corpus'];table.append(f"| {r['canonical_name']} | {text} | {l['faces']} / {l['object_families']} / {l['distinct_cisi_ids']} |")
md('REPORT.md',f'''# Gujarat, Kutch and Maharashtra site census

Status: Exploratory. Source audit:7 October2026 UTC. This revision replaces the first pass for current use; the original ten files remain unchanged in [first-pass](first-pass/preservation-manifest.json).

The25-site batch contains496 local corpus faces in460 object families, distributed across13 site labels. Direct inspection of ten CISI1 site ranges gives317 catalogue objects. The catalogue includes geometric, pictorial and graffiti material alongside inscriptions; its objects and the local faces have different units and cutoffs. Every site has a read primary or substantial secondary passage and at least three site-specific live searches. There are130 actual queries:127 site-specific query records and three shared ICIT queries. These bases are recorded in [aggregate-results.json](aggregate-results.json), fields `sites`, `local_faces`, `local_object_families`, `cisi1` and `minimum_distinct_searches_per_site`.

## Scope and report access

There are23 Gujarat sites, Daimabad in Maharashtra and the explicitly requested Nuhato cross-reference in Sindh. Pabumath was added from the local coverage list and verified against CISI1 Pbm1. Juna Khatiya was added as a local pottery-record lead. Kanewal was found while reading *Indian Archaeology1977–78 – A Review*, p.21, item22: the passage explicitly reports incised Harappan characters on potsherds. Its1980 final-report bibliography was then verified in the [CiNii record](https://ci.nii.ac.jp/ncid/BA82253260). Addition evidence is in `site-rows.json[].addition_basis`; search bundleB37 contains its three searches.

Twelve sites have a bibliographically identified completed campaign publication, including the121-page Nuhato2018 departmental report. Relevant passages from six were read: Lothal, Dholavira, Kanmer, Rangpur, Nuhato and Daimabad. The other six are bibliographic identifications. The12 sites are listed in `aggregate-results.json.completed_report_sites`; each row’s `final_report` states access. This count does not imply a final publication for all seasons. Nageshwar’s1990 report date is taken from Rawat2015,p.213; the first pass’s1992 attribution was not independently reproduced.

## Published counts and local coverage

{chr(10).join(table)}

The table’s published counts are CISI1 identifier slots from the printed site sections and contents, not complete excavation totals. At those ten sites the local export has466 faces,432 families and199 distinct CISI identifiers, including later Dholavira material and Rojdi identifiers extending beyond CISI1. The local source is [local-site-coverage.json](../../../2026-10-06-research-program/local-site-coverage.json); exact unchanged source fields and hash are copied into each row’s `local_corpus.evidence`. No completeness percentage is calculated across these units. CISI1’s scan contains a duplicate431-page sequence; the audit used the first sequence and treated photographic views/impressions separately from object identifiers.

Mahadevan1977,p.6,Table1 gives175 selected legible inscribed objects across five sites: Lothal165, Desalpar2, Dholavira1, Rojdi2 and Surkotada5. Lothal’s class table,p.7, gives89 seals,75 sealings and one pottery object. These objects overlap CISI records and cannot be added to317. The values and selection rules are in `mahadevan1977` and `counts_by_class`.

Several larger source inventories require separate interpretation. Rangpur’s report,p.130, counts26 figurative,188 linear-symbol and eight combined-sign potsherds, a total of222 broadly marked sherds; its CISI1 selection has two objects and the local export has none. Dholavira’s2015 report,p.242, marks139 of194 analysed seals as inscription-bearing; its overall inventory,p.232, has225 seals. The same report gives60 sealings in its overview and61 in the detailed chapter,p.308, whose subtraction is internally inconsistent. Lothal’s1985 report,p.305, gives91 sealings; Frenez and Tosi2005,pp.67–68, give93. These differences are retained side by side in each row’s `count_comparisons`; [sources.json](sources.json) supplies exact bibliographies and witnesses.

Daimabad’s final report,pp.504–507, explicitly describes two script-bearing terracotta seals and five marked sherds across phasesII andIII. CISI1 catalogues nine objects with different classifications, including a cylinder scene and a crescent scene object. Desalpar’s primary review,p.10, has two script-bearing seals and one lettered clay sealing. The first pass’s three-seal claim is corrected. Shikarpur’s2008–09 report,pp.3–5, has two inscribed sealing objects and one tablet; three impressions on one sealing remain one object. Each observation has its own count unit, date and source page in `reported_counts`.

Fuls2023’s ICIT-based regional list,§5.3,p.501, supplies1446 legible sign occurrences across13 batch sites. Those are signs, not objects, faces or texts; they are stored in `icit_site_count` and excluded from object totals. No ICIT object denominator was verified. Juna Khatiya’s two signs in that transcription require an original artifact source before archaeological inscription status can be verified.

## Finds after catalogue coverage

Two sites have directly established CISI1 sections followed by dated new inscribed finds: Dholavira’s1989–2005 campaign and Khirsara’s2009–10 campaign. Nuhato adds a third dated later-find case: the2018 report,pp.14,41–42, describes a newly excavated inscribed terracotta seal distinct from the1973 find. It cites the older seal in CISI2,p.390; that catalogue page remains uninspected. Thus the total is two with directly checked catalogue baselines, plus one with a baseline reported by the excavation author. Nuhato is outside the regional-only denominator.

Four further sites have explicit script-material reports published after1987 and no CISI1 site section: Kanmer, Shikarpur, Gola Dhoro and Nagwada. Nagwada’s sealing is from the1987–88 season and the annual review was published in1993; its excavation date cannot be narrowed to before or after CISI1 publication. Padri’s later fish-pattern button seal has uncertain inscription status. Bet Dwarka’s two reported protohistoric inscriptions have disputed attribution and unverified recovery dates. Rojdi’s later catalogue publication does not by itself date new inscription discoveries. Details are in `post_cisi_finds`.

## Remaining gaps

All25 sites have sourced coordinates or a published extent:24 points and Bet Dwarka’s island bounds. Conflicts are retained in `coordinates.conflicts`, including the erroneous Juni Kuran point removed from the first pass and the differing Prabhas, Pithad, Khirsara and Nageshwar locations.

The fields most often lacking a usable value in the inspected witnesses are ICIT object counts(25 sites), inscribed metal-class totals(24), other-object totals(23) and tablet totals(22). Inscription drawings were not demonstrated in19 sites’ inspected passages and registrations in15. These figures describe this audit’s source access, not the contents of all unpublished or inaccessible records. Each unresolved field includes actual search IDs, returned URLs and an inspected passage in `unresolved_fields`; [searches.json](searches.json) links to verbatim local responses.

Rojdi’s CISI3.2 site pages and count remain unavailable. Nuhato’s CISI2 page needs direct inspection. Full final object inventories for Surkotada, Nageshwar, Kuntasi, Rojdi, Somnath and Kanewal remain unread. No identified inscribed artifact was verified for Nageshwar, Kotada Bhadli, Navinal or Pithad; Juni Kuran’s steatite seal has unverified script status. Seventeen sites have unresolved current object holdings. `source-access.json` retains13 failed acquisitions among45 attempts and three HTTP200 challenge payloads. Successful alternate IAR downloads and the Nuhato departmental PDF are recorded alongside earlier failures. Source rights are retained per publication; raw scans, images and responses remain local.
''')

md('README.md','''# Site census batch B

Status: Exploratory. Revision audited7 October2026 UTC.

The batch covers25 sites, including added Kanewal, with130 recorded live queries and at least three site-specific searches per site. It records496 local faces/460 families; ten CISI1 ranges contain317 catalogue objects; Mahadevan1977 gives175 selected inscribed objects across five sites. Twelve completed campaign reports are identified and relevant passages from six are read. Two directly checked catalogue baselines have later inscribed finds; Nuhato provides one further case whose older CISI2 citation still needs direct checking. See [REPORT.md](REPORT.md) and [aggregate-results.json](aggregate-results.json) for the count bases.

## Files

[site-rows.json](site-rows.json) contains one structured row per site; [site-rows.csv](site-rows.csv) serializes nested cells as JSON. [sources.json](sources.json) records curated bibliographies and every discovered source header, with opened, preview, bibliography and snippet states separated. [searches.json](searches.json) records actual queries and raw-response paths. [source-access.json](source-access.json) records downloads and failures. [PROTOCOL.md](PROTOCOL.md) includes dated amendments, and [RETROSPECTIVE.md](RETROSPECTIVE.md) describes changes and limitations. The proposed shared-registry record is [registry-entry.json](registry-entry.json).

The original ten files are preserved byte for byte in [first-pass](first-pass/preservation-manifest.json). They contain historical errors and damaged text; the current UTF-8 files replace them for use. [build-audit.json](build-audit.json) reports archive hash checks. [created-paths.json](created-paths.json) inventories every owned/raw artifact.

## Reproduce from the repository root

```powershell
$env:PYTHONIOENCODING = 'utf-8'
python experiments/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/build_site_rows.py
python experiments/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/write_reports.py
python tools/review_prose.py --path experiments/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra --no-write
```

The builder uses Python’s standard library, `evidence_catalog.py`, the coordinator’s unchanged local coverage file and preserved rawB/O response logs. It makes no network requests. Markdown/report inventories are written by the second command. `first-pass/` is never modified.

For source acquisition, run `acquire_sources.py <plan-path>` using one of the four `acquisition-plan*.json` files here. It requires requests, beautifulsoup4 and PyMuPDF, already available during this audit. Acquisitions are cached, including failures; use a new ID to retry a failed route. It sets TMP,TEMP and MPLCONFIGDIR under the paired raw directory. The documented live-search queries require manual/tool replay; they are not fabricated by the builder.

## Reviewer checks

Rebuild aggregates and compare the JSON/CSV rows. Check all first-pass SHA-256 values, the printed CISI ranges, Mahadevan’s pp.6–7 tables, Rangpur p.130, Desalpar IARp.10, Nagwada IARp.20 and Nuhato pp.14,41–42. Sample the source/page evidence and coordinate conflicts. Resolve Rojdi’s CISI3.2 pages and directly inspect Nuhato’s CISI2 citation. Review the prose findings for current files separately from the unchanged archive.
''')

md('RETROSPECTIVE.md','''# Retrospective

Status: Exploratory.7 October2026.

## Revision and reused work

The first pass left many fields unverified and described normalized search strings as though they were an executed search trail. Its ten files were copied before revision, with byte counts and SHA-256 values. The new130-query record comes from actual live-tool responses. Every site was revisited, including the added Kanewal; shared ICIT queries are excluded from the three-query site minimum.

The coordinator’s local-site-coverage.json was reused unchanged. The earlier sites-and-publications census and October6 contribution assessment supplied leads, not verified field values. The existing CISI1 scan and its counting/errata audit avoided repeating a scan acquisition. The Mahadevan1977 full scan came from batchA’s common-revision witness. Existing Frenez–Tosi2005 and Rangpur1963 PDFs, plus the backward-chronology Rangpur OCR, were reused. The Rangpur count was checked visually on the original p.130 rather than accepted from OCR alone. Acquisition records name every reused path.

## Access problems and fixes

Several NMMA annual-review downloads timed out. Alternate official ASI Aurangabad URLs supplied readable PDFs. Other routes returned404 and remain in the record. Lothal, Kanmer and Bet Dwarka mirrors returned HTTP200 challenge/HTML pages to requests; web-indexed original report content was readable separately. Transport success was therefore audited apart from content access.

The Nuhato2019 journal download failed. Its Sindh departmental publication page exposed another public PDF link, which supplied a121-page2018 report. That report yielded coordinates, campaign history, two inscribed seals and illustrated graffiti; its2019 journal pagination is not assumed equivalent. Publisher downloads for Juna Khatiya’s2021 paper returned404 while the indexed full PDF remained readable. Rojdi’s CISI3.2 pages and the cited Nuhato CISI2 page could not be obtained.

## Corrections and count decisions

The first pass assigned Juna Khatiya’s coordinates and pottery lead to Juni Kuran. The gazetteer and site sources now keep these records separate. Desalpar’s three objects are two seals and a sealing. The verified Somnath monograph is by Nanavati,Mehta and Chowdhary,1971. Rangpur’s222 marked sherds, Dholavira’s225 recovered versus194 analysed seals, and Lothal’s91 versus93 sealings required count bases and disagreements to be preserved explicitly.

CISI contents and plates establish contiguous catalogue ranges for ten sites. Object identifiers were separated from multiple faces and modern impression photographs. The local export also contains later finds, so a single coverage percentage would mix dates and units. The ICIT-related publication search yielded13 site aggregates totaling1446 legible signs; these are excluded from object counts. Current files are UTF-8; original archive bytes remain intact, including their damaged characters.

## Limits and follow-up

Six identified final reports remain unread at their object pages. Several sources describe a site without exposing an inscription inventory, so availability assessments are tied to the inspected passage and accompanied by failed-search records. Current museum destinations, exact later-season class totals and several campaign directors remain unresolved. The next useful work is direct inspection of Rojdi’s2019 catalogue, Nuhato’s1991 citation and the six remaining final inventories, followed by registration-number matching to the local export. The dataset supports that review through source IDs, locations, count units and preservation hashes.
''')

entry=dict(id='2026-10-06-evidence-census-sites-deep-b-gujarat-kutch-maharashtra',theme='Archaeological evidence and corpus coverage',status='Exploratory',question='Which site-level inscription inventories, excavation histories and metadata can be sourced for Gujarat, Kutch and Maharashtra, retaining the requested Nuhato cross-reference?',outcome='25 sites;130 actual queries; at least3 site-specific queries/site;496 local faces/460 families;317 CISI1 catalogue object slots across10 sites;175 Mahadevan1977 selected objects across5 sites;12 completed reports identified,6 relevant passages read. Two direct catalogue baselines with later finds plus Nuhato with report-cited baseline;13 ICIT-based published sign aggregates,1446 signs, excluded from object totals.',challenge='First pass had unsupported values and search descriptions; full final inventories and Rojdi CISI3.2 pages unavailable; count units and selection rules differ; some downloads failed or returned challenge pages.',remedy='Archive ten originals with hashes; preserve actual searches/access failures; inspect primary passages and catalogue plates; retain count disagreements and site-specific unresolved fields; UTF-8 current files.',evidence=['experiments/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/'+p for p in ['REPORT.md','site-rows.json','sources.json','searches.json','aggregate-results.json','build-audit.json','source-access.json','first-pass/preservation-manifest.json']],retry_when='Full Rojdi CISI3.2, Nuhato CISI2 p.390 or unread final object inventories become available, or the local export gains registration/source crosswalks.')
(OWN/'registry-entry.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

inventory=[]
for base,label in [(OWN,'owned'),(RAW,'local_raw')]:
    for p in sorted(base.rglob('*')):
        if p.is_file() and p.name!='created-paths.json':
            inventory.append(dict(path=str(p.relative_to(ROOT)).replace('\\','/'),scope=label,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(OWN/'created-paths.json').write_text(json.dumps(dict(inventory=inventory,note='Includes every current artifact and first-pass archive. The inventory file itself is listed here without a self-hash.',self_path=str((OWN/'created-paths.json').relative_to(ROOT)).replace('\\','/')),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(written=['README.md','REPORT.md','RETROSPECTIVE.md','registry-entry.json','created-paths.json'],inventoried_files=len(inventory))))
