"""Write authorized root documentation from the completed review-response outputs."""
import json
from pathlib import Path
from common import OWN, RAW, write

RUN='revision-2026-10-07-v4'
CHECK='verification-2026-10-07-v3'
COMPARISON='review-response-2026-10-07-v3'

README=r'''# Two 200-object ledger selections

The original pilot has **200 carriers, 180 corpus-linked and 20 catalogue-only**, but its alphabetical 74-slot fill drew only from Eastern Headwaters, Gujarat/Kutch and Harappa. Its percentages cannot represent the corpus. The preserved first selection covers 34 export site labels; the new hash-ordered selection covers **39**, including **10 Kalibangan carriers**. Both corrected registers are Exploratory. [Coverage comparison](revision-2026-10-07-v4/coverage-comparison.json), `original`, `hash_ordered`; [report](REPORT.md).

The corrected original selection has **26 confirmed museum joins**, **34 candidate links**, **62 attributed calendar intervals** and **130 dimension-bearing carriers**, a gain of **three** over its 127-carrier corpus baseline. The hash-ordered selection has 25 confirmed museum joins, 15 candidate links, 57 intervals and 130 dimension-bearing carriers. Both have zero dating-sample links. Their queues contain 156 questions on 85 carriers and 138 questions on 81 carriers. [Original summary](revision-2026-10-07-v4/corrected-original/summary.json), [hash-ordered summary](revision-2026-10-07-v4/hash-ordered/summary.json), `joins`, `review_questions`, `review_objects`; each directory's `completeness.json` gives field denominators.

Read the [dated amendment](AMENDMENT-2026-10-07-review-response.md) and appended [protocol](PROTOCOL.md), then the [new selection](revision-2026-10-07-v4/selection.json). The first selection and every earlier endpoint remain unchanged. The revised files are named `ledger-without-transcription-payloads-or-images.json`, in the two selection directories under `revision-2026-10-07-v4/`. They contain attributed metadata, identifiers, pointers and missingness reasons. Lipi record-level metadata needs a reuse basis before public release. Full registers and every new replay copy stay in local `data/`.

[Schema version 2](revision-2026-10-07-v4/schema-v2.json), [builder](revision_builder.py) and [validator](validate_v2.py) implement the corrections. The sequence guard is a heuristic with numeric-metadata exclusions. The [Helsinki interface](HELSINKI-INTERFACE.md) and [importer](import_helsinki1979_v2.py) accept occurrence IDs, suffixed text numbers and reviewed new surfaces. No real Helsinki transcription entered either ledger.

## Rerun from the repository root

Python and `jsonschema` are required; no download or installation is needed. Every output directory must be new. The first command below writes substantive owned outputs; the replay writes only to raw. Change suffixes after using these names.

```powershell
$taskTmp = 'data/raw/2026-10-07-object-ledger/tmp'
New-Item -ItemType Directory -Path $taskTmp -Force | Out-Null
$env:TMP = (Resolve-Path $taskTmp).Path
$env:TEMP = $env:TMP
$env:MPLCONFIGDIR = $env:TMP
$env:PYTHONDONTWRITEBYTECODE = '1'

python experiments/2026-10-07-object-ledger/revise_pilot.py --output-dir experiments/2026-10-07-object-ledger/reviewer-revision-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-registers-v1
python experiments/2026-10-07-object-ledger/check_revision.py --run-dir experiments/2026-10-07-object-ledger/revision-2026-10-07-v4 --output-dir experiments/2026-10-07-object-ledger/reviewer-verification-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-verification-v1
python experiments/2026-10-07-object-ledger/revise_pilot.py --output-dir data/raw/2026-10-07-object-ledger/reviewer-replay-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-replay-registers-v1 --canonical-selection-path experiments/2026-10-07-object-ledger/revision-2026-10-07-v4/selection.json
python experiments/2026-10-07-object-ledger/summarize_revision.py --run-dir experiments/2026-10-07-object-ledger/revision-2026-10-07-v4 --replay-dir data/raw/2026-10-07-object-ledger/reviewer-replay-v1 --output-dir experiments/2026-10-07-object-ledger/reviewer-comparison-v1
python experiments/2026-10-07-object-ledger/validate_v2.py --ledger experiments/2026-10-07-object-ledger/revision-2026-10-07-v4/hash-ordered/ledger-without-transcription-payloads-or-images.json --scan-dir experiments/2026-10-07-object-ledger/revision-2026-10-07-v4
python tools/review_prose.py --path experiments/2026-10-07-object-ledger --no-write
```

For the original pipeline, `replay_original.py` verifies the preserved protocol prefix, supplies its hash in memory and permits output only under raw. These corrected `analyze.py` and `check_pilot.py` lines have no `--lothal-assertions` argument:

```powershell
python experiments/2026-10-07-object-ledger/replay_original.py select_pilot.py --output-dir data/raw/2026-10-07-object-ledger/reviewer-old-selection-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-old-exclusions-v1
python experiments/2026-10-07-object-ledger/replay_original.py build.py --selection experiments/2026-10-07-object-ledger/selection-2026-10-07-v1/selection.json --lothal-assertions experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/source-assertions.json --output-dir data/raw/2026-10-07-object-ledger/reviewer-old-ledger-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-old-register-v1
python experiments/2026-10-07-object-ledger/replay_original.py analyze.py --ledger-dir data/raw/2026-10-07-object-ledger/reviewer-old-ledger-v1 --selection experiments/2026-10-07-object-ledger/selection-2026-10-07-v1/selection.json --output-dir data/raw/2026-10-07-object-ledger/reviewer-old-analysis-v1
python experiments/2026-10-07-object-ledger/replay_original.py check_pilot.py --ledger-dir data/raw/2026-10-07-object-ledger/reviewer-old-ledger-v1 --analysis-dir data/raw/2026-10-07-object-ledger/reviewer-old-analysis-v1 --selection experiments/2026-10-07-object-ledger/selection-2026-10-07-v1/selection.json --output-dir data/raw/2026-10-07-object-ledger/reviewer-old-checks-v1 --raw-dir data/raw/2026-10-07-object-ledger/reviewer-old-fixtures-v1
```

## Required local inputs

A fresh checkout lacks the following data. [local-inputs.json](review-response-2026-10-07-v3/local-inputs.json) gives exact paths and hashes for all twenty reused inputs and the supplements. [common.py](common.py), `PATHS`, is the adapter map.

- `data/normalized/lipi_observed_faces.jsonl` and `mayig_faces.jsonl`.
- `data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/{focused-records,paired-comparisons}.json`.
- `data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/{confirmed-object-joins,candidate-object-joins,absent-catalogue-identifiers}.json`.
- `data/six-hour/lothal/table-coding/reviewed-pass.csv` and `data/six-hour/lothal/independent-review/independent-first-pass.csv`.
- `data/raw/2026-10-07-object-ledger/review-response-2026-10-07/source-observations.json`, fourteen located correction observations. The parent scans are `research/literature/sources/joshi_parpola_1987_cisi1.pdf` and `data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/gadd1932.pdf`.
- Original replay also requires `data/raw/2026-10-07-object-ledger/review-response-2026-10-07/original-root/PROTOCOL.md`.

The interface check additionally reads Package M's tracked `integration/2026-10-07-v1/ledger-import.jsonl` in place. Other tracked source frames and period tables are listed in the input manifest. Compare decompressed raw registers rather than gzip headers. [FILES-REVIEW-RESPONSE-2026-10-07.json](FILES-REVIEW-RESPONSE-2026-10-07.json) lists every created or changed path.
'''

def main():
    read=lambda p:json.loads((OWN/p).read_text(encoding='utf-8'))
    coverage=read(RUN+'/coverage-comparison.json');comparison=read(COMPARISON+'/comparison.json')
    old=read(RUN+'/corrected-original/summary.json');new=read(RUN+'/hash-ordered/summary.json')
    region_rows='\n'.join('| '+r+' | '+str(coverage['frame_regions'].get(r,0))+' | '+str(coverage['original']['regions_export'].get(r,0))+' | '+str(coverage['hash_ordered']['regions_export'].get(r,0))+' |' for r in sorted(set(coverage['frame_regions'])|set(coverage['original']['regions_export'])|set(coverage['hash_ordered']['regions_export'])))
    countries='\n'.join('| '+r+' | '+str(coverage['original']['external_by_country'].get(r,0))+' | '+str(coverage['hash_ordered']['external_by_country'].get(r,0))+' |' for r in sorted(set(coverage['original']['external_by_country'])|set(coverage['hash_ordered']['external_by_country'])))
    sites='\n'.join('| '+r+' | '+str(coverage['original']['external_by_site'].get(r,0))+' | '+str(coverage['hash_ordered']['external_by_site'].get(r,0))+' |' for r in sorted(set(coverage['original']['external_by_site'])|set(coverage['hash_ordered']['external_by_site'])))
    fields=['museum_accession','material','area','room_grid','period_label','calendar_interval','excavation_unit','excavation_item','measurement','dating_sample']
    field_rows='\n'.join('| '+f+' | '+str(comparison['endpoints']['corrected-original']['field_presence'][f]['corpus'])+' | '+str(comparison['endpoints']['corrected-original']['field_presence'][f]['ledger'])+' | '+str(comparison['endpoints']['hash-ordered']['field_presence'][f]['corpus'])+' | '+str(comparison['endpoints']['hash-ordered']['field_presence'][f]['ledger'])+' |' for f in fields)
    report=f'''# Object-ledger review response

The preserved first selection contains **200 carriers**, but its **74-slot alphabetical fill reached only Eastern Headwaters, Gujarat/Kutch and Harappa**. Lower Indus has 46% of the 4,104 frame carriers and entered that selection through only 18 museum-linked objects; Kalibangan entered zero. The new hash-ordered selection also has 200 carriers, with 44 Lower Indus and ten Kalibangan records. It covers 39 export site labels, compared with 34 originally. Both selections are purposive, and the revised selection follows the observed review, so its status is Exploratory. [Coverage](revision-2026-10-07-v4/coverage-comparison.json), `frame_regions`, `original`, `hash_ordered`.

## Selection and coverage

The original fill visited alphabetically ordered strata and stopped at position 90 among 313 strata. It added 17 Eastern Headwaters, 31 Gujarat/Kutch and 26 Inter-Riverine carriers. The revised fill orders JSON-encoded stratum keys by SHA-256 with seed `object-ledger-review-20261007|`, then uses the original within-bucket object hash. Its 74 additions comprise 27 Inter-Riverine, 26 Lower Indus, eight Gujarat/Kutch, four Eastern Headwaters, four export-labelled Iranian Plateau, two Persian Gulf, two Upper Indus and one South India carrier. The period, tablet, museum and Lothal stages retain their original quotas. [Selection code](revision_selection.py), `seeded_round_robin`, `revised_selection`; [frozen reviewer recount](review/selection-check.json), `fill_last_stratum_position_in_sorted_order`.

| Export region | Frame carriers | Original selection | Hash-ordered selection |
|---|---:|---:|---:|
{region_rows}

The site tables are complete in `coverage-comparison.json`, `sites_export` and `sites_accepted`. After census alias normalization there are 33 and 38 distinct site/area labels, respectively; Girsu and Tello are one site. Luristan and Ornach area are regional/area labels. The frame omits 591 export families without an eligible catalogue base, including 228 Dholavira and eight Kanmer families. The revised sample still reflects the mandatory Harappa and Lothal quotas. [Coverage file](revision-2026-10-07-v4/coverage-comparison.json), `original_fill_audit`, `original_unreached_frame_sites`, `hash_unreached_frame_sites`.

Over all 4,695 export families, area, room/grid and period labels are present on 73.887%, 39.723% and 50.692%. On the original 180 matched carriers these rates are 52.222%, 15.556% and 38.333%; on the revised 180 they are 61.667%, 25.000% and 37.778%. This demonstrates the effect of selection on metadata coverage. [Comparison](review-response-2026-10-07-v3/comparison.json), `full_export_presence`, `endpoints.*.field_presence`.

## External carriers

The original Iranian Plateau quota included one Iranian and four Pakistani carriers by census country. The revised mandatory group takes all four Iranian frame carriers: two Susa, one Tepe Yahya and one Luristan. Its other mandatory groups are six Gulf, five Mesopotamian and three Central Asian carriers. BM-123208 is assigned to Mesopotamia by its Ur excavation. Later fill adds seven other external export carriers, including four Pakistani cross-references; those are shown by country below and retain attributed export-region assertions. The original and revised external totals are 18 and 25. [Coverage](revision-2026-10-07-v4/coverage-comparison.json), `external_carriers`, `external_by_country`, `external_by_site`.

| Country from census | Original | Hash ordered |
|---|---:|---:|
{countries}

| Canonical site/area | Original | Hash ordered |
|---|---:|---:|
{sites}

Gadd's *Seals of ancient Indian style found at Ur* (C. J. Gadd, 1932, Proceedings of the British Academy 18:191-210), printed13-14/PDF24-25, identifies BM 123208 and U.17649 in Ur tomb-shaft filling. The accepted site and findspot now read Ur. Dilmun is a separately attributed production-place assertion; its independent basis and the export-family match remain review questions. [Primary scan](https://ignca.gov.in/Asi_data/33779.pdf); [corrected register](revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json), `objects[selection_key=BM-123208]`, corresponding context and assertions.

## Identifiers, dimensions and dates

The original 149 accepted excavation strings comprise **126 registrations free of the identified citations/placeholders**, 20 figure/plate-bearing cells and three other leading-hyphen values. Across all source assertions, 42 carriers have explicit figure/plate citations. Forty-two distinct contaminated alias strings occupy 92 repeated alias rows because multiple faces repeat metadata. The revised view separates registrations, lots, bibliography and original export strings. It has zero figure/plate-bearing accepted registration cells or registration aliases. Two prefix-only BNL strings enter specific review questions. [Identifier recount](review-response-2026-10-07-v3/comparison.json), `original_identifier_restated`; each revised `identifier-audit.json` records normalized registrations. The 104-carrier strict unparsed export baseline and newly parsed identifiers are distinct from the original accepted-view count of 126.

After parsing and corrections, accepted registration fields are present on 145 original-selection and 151 revised-selection carriers. Their corpus-derived parsed fields are present on 143 and 149 carriers. These counts include registrations separated from combined export/citation strings; they do not change the original 126 clean-string recount. [Original identifier audit](revision-2026-10-07-v4/corrected-original/identifier-audit.json), [revised identifier audit](revision-2026-10-07-v4/hash-ordered/identifier-audit.json), `accepted_registrations`, `export_registrations`.

H-2218's full export string is `H97-3319Figure 12.11`. Its primary caption restores `H97-3319/8040-13`, with unit8040 and item13 separated. PBM-1 receives PBM024 and dated holder code KC from CISI 1 printed375/PDF411; PMB024 remains a candidate variant. B3-V6-016 records the applied action. A dated holder code describes the catalogue snapshot, without establishing a current institution. [Corrected register](revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json), `export_excavation_identifier`, `excavation_identifier`, `lot_identifier`, `bibliographic_locator`, `correction_overlays[correction_id=B3-V6-016]`.

The museum parser now accepts explicit mm, cm/cms., centimetre/centimeter variants, labelled axes and inches. Inches convert at 25.4mm. Unlabelled arrays remain dimension_1 etc.; labelled height/width/thickness/diameter preserve their stated axes. It adds fifteen measurement assertions from seven previously skipped records in the corrected original selection. H-221's 0.8x1.8cms. becomes 8 and18mm, giving **130 dimension-bearing carriers against127**, a gain of **three**. [Parser](revision_builder.py), `dimensions`; [completeness](revision-2026-10-07-v4/corrected-original/completeness.json), `field=measurement`.

The 22 tablets retain the caption's late Period3B label and receive the full approximate 3B interval, **2450-2200 BCE**. The late qualifier supplies no narrower interval. The export's 2600-1900 BCE conversion remains a historical source assertion. Accepted labels and intervals now share the HARP periodization scheme. H-1688's queue cites the source introduction's Mound E street-deposit attribution at about2600BC, printed liii; that page was reused from the reviewer check. [Period table](../2026-10-06-chronology-region/main-2026-10-07-v1/period_mapping.json), `label=Period 3B`; [register](revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json), tablet `calendar_interval`, `periodization_scheme`.

## Lothal evidence, completeness and review

CISI 1 printed375 corrects L-141's two views to A(1)/A(2) and places L-174 among tags with several impressions. Printed279 shows two square impressions on L-174. The accepted count is now two for each, with the Table1 count one retained. L-141's caption-to-impression interpretation needs expert confirmation. The opened plates are printed272/PDF308 and279/PDF315. The L-173 to L-175 eligibility questions use the catalogue's geometric-design classification; L-173's page attribution is inherited from the reviewer. [Register](revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json), the two `impression_count` cells and their assertion references; [review queue](revision-2026-10-07-v4/corrected-original/review-queue.json), `catalogue_only`, `impression_count_conflict`. Joshi and Parpola are recorded as CISI editors.

The following field counts use the same 180 matched carriers within each selection. Presence means a nonplaceholder, noncandidate attributed assertion. Dates are period or museum attributions; no object-associated dating sample was recovered.

| Field | Original corpus | Corrected original | Revised corpus | Revised ledger |
|---|---:|---:|---:|---:|
{field_rows}

The corrected original register contains 6,991 assertions, 445 measurements and 259 source-record surfaces/transcriptions. The revised register has 7,004 assertions, 449 measurements and262 source-record surfaces/transcriptions. Surface identities preserve annotation boundaries; their physical face alignment remains open. All nulls have reasons. Non-Lothal-table impression/context/contact fields now say not applicable, and derived source-class/region assertions have a derived confidence level. [Summaries](revision-2026-10-07-v4/corrected-original/summary.json), [revised summary](revision-2026-10-07-v4/hash-ordered/summary.json); [missingness counts](review-response-2026-10-07-v3/comparison.json), `endpoints.*.null_reasons`.

Twenty-one catalogue pointers now give individual plate pages in each selection. The remaining 27 corrected-original and 26 revised pointers still locate only the sealing section. Full Finnish Concordance/holder/photo-source columns, the other selected Lothal caption conventions and current holdings behind KRS/RGR catalogue codes remain incomplete. These tasks are recorded in [sources.json](sources.json), `review_response.remaining_source_tasks`.

There are 51 confirmed operational relationships and34 candidate edges on the corrected original selection; the revised selection has50 and15. Confirmed museum objects number26 and25. Both retain21 inherited museum adjudications, including two material, two dimension-tolerance and two inscription-count disagreements; additional unadjudicated pairs number five and four. Distinct attributed values remain grouped by field in each `disagreements.json`; they include compatible source scopes as well as disagreements. [Original joins](revision-2026-10-07-v4/corrected-original/join-report.json), [revised joins](revision-2026-10-07-v4/hash-ordered/join-report.json), `confirmed_relationships`, `candidate_relationships`, `museum_field_adjudications`.

Lookup counts are recomputed from assertion locators after normalization: **1,064**, mean5.32, and **1,044**, mean5.22. Excluding rights-rule rows and selection attribution gives **841**, mean4.205, and **821**, mean4.105. Both medians then equal three. This counts distinct input-record lookups per carrier, without a timed human cost. Six relevant primary pages supplied corrections; the access log records nine inspected page images including initial navigation checks. `new_image_inspections=4` in the summaries counts the four CISI page images. The queues have156 questions on85 carriers and138 on81. [Summaries](revision-2026-10-07-v4/corrected-original/summary.json), [revised summary](revision-2026-10-07-v4/hash-ordered/summary.json), `source_lookup_cost`, `source_lookup_cost_without_rights_and_selection`; [access log](../../data/raw/2026-10-07-object-ledger/review-response-2026-10-07/source-access-log.json).

## Validation, rights and Helsinki import

The strengthened validator catches **26/26 reviewer mutations** and **17/17 sequence fixtures**. It checks source-record existence, cell/row assertion equality, reference ownership, units, mass, finite quantities, broad plausibility limits, Harappa label/interval compatibility and date-source attribution. The disclosure guard scans JSON, JSONL, CSV and Markdown, including one- and two-sign forms. It is a heuristic: ordinary accession, page, aggregate-count and family numerals receive explicit metadata/context exclusions, so a source-content review remains necessary. The final whole-package scan covered 225 files and left eight alerts in the unchanged reviewer's own page/count-run summary. Those describe bibliographic and completeness counts, and are manually classified as metadata. The revised endpoint directory has zero alerts. [Mutation results](verification-2026-10-07-v3/mutations.json), `caught`, `total`; [final fixture repeat](sequence-guard-review-response-2026-10-07-v2.json), `files`; [directory scan](validation-review-response-2026-10-07-v2.json), `errors`; [full scan and classification](full-directory-sequence-review-2026-10-07-v1.json), `flags`, `manual_classification`.

The Lothal chapter's Zenodo record states CC BY4.0, as verified in the supplied reviewer source check; the online notice was not reopened here. The L-174 chapter-image rights record carries that licence, while CISI plate assets retain their separate unresolved rights. No copied images, descriptions or transcription payloads are in the revised metadata layers. The file name describes these exclusions; Lipi metadata is retained under the private research policy, with public reuse unresolved. [Sources](sources.json), `review_response`; [ledger rights](revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json), `source_id=lothal2005`; [author deposit](https://zenodo.org/records/5514283).

Package M supplies11,369 occurrences, including944 unresolved numbers and65 letter-suffixed occurrences. With no historical crosswalk, **zero are accepted and all11,369 quarantined**. Synthetic tests accept suffixes, expand reviewed occurrence mappings, round-trip Package M crosswalk fields and create a surface on a catalogue-only carrier. No synthetic identity enters either register. CISI 1 printed365/PDF401 identifies its Finnish Concordance column; its relationship to the1979 edition requires verification. [Interface results](verification-2026-10-07-v3/helsinki-interface.json), `number_counts`, `real_accepted`, `real_quarantined`; [interface specification](HELSINKI-INTERFACE.md).

All164 pre-response endpoint/review files retain their hashes. The original158 checks pass through the protocol-prefix replay wrapper. Twenty-three revised selection/result files replay byte for byte, with replay copies only in raw. Direct source-value checks compare3,335 original-selection and3,408 revised-selection assertions without a mismatch; other transformations remain outside that resolver's scope. [Preservation](verification-2026-10-07-v3/preservation.json), [replay](review-response-2026-10-07-v3/replay-comparison.json), [assertion audit](review-response-2026-10-07-v3/assertion-values.json), `endpoints.*.counts`.
'''
    # Spaces around counts keep the generated prose readable without changing IDs.
    import re
    report=re.sub(r'\b(all|and|against|about|comprises|contains|has|including|mean|number|on|original|supplies|the|with)(?=\d)',r'\1 ',report)
    report=report.replace('Period3B','Period 3B').replace('Period3','Period 3').replace('2600BC','2600 BC').replace('column2','column 2')
    (OWN/'README.md').write_text(README,encoding='utf-8')
    (OWN/'REPORT.md').write_text(report,encoding='utf-8')
    original=(RAW/'review-response-2026-10-07/original-root/RETROSPECTIVE.md').read_text(encoding='utf-8').replace('L174?s',"L174's")
    original=original.replace('The current endpoint passes 158 checks','The original endpoint passes 158 checks')
    original += '''

## Review response, 7 October 2026

The Sonnet review reproduced the original endpoints and identified selection-order bias and source-field problems. A dated protocol amendment preceded the second selection. The revised rule hashes strata and uses census country for the mandatory external group. Both original and new selected objects were rebuilt with corrected registrations, dimensions, dates, counts, rights and provenance. The original selection and every existing endpoint stayed unchanged; new replay copies are local.

The first revised validation stopped on bibliographic/accession numerals that resembled short sign codes. Explicit metadata exclusions fixed these heuristic false positives. An initial replay passed a relative canonical selection path to an absolute-path locator operation; resolving the argument repaired it. Both failed attempts remain local or in dated exploratory directories. A later parser pass recognized attached Pl. citations and Roman Lothal plate references. The lookup counter was recomputed from final assertion locators after rights-heading normalization, and two BNL prefix-only registrations received review questions. Intermediate v2 and v3 registers remain dated outputs; v4 is the reviewed-response endpoint.

CISI text extraction returned empty strings, and the saved Gadd text lacked usable registration OCR. Four CISI page images and targeted Gadd pages supplied the corrections. Initial Gadd PDF13-14 images were printed6 and plateI; PDF24-25 supplied printed13-14. One JSON read failed under Windows cp1252; UTF-8 reads handled subsequent records. A summary inspection snippet failed to compile from a mismatched bracket before writing anything. The first documentation patch attempted two operations on one path and was rejected without changing the file. These errors are documented as observed operations and did not alter frozen evidence.

The review's 26 mutations all produce new validator errors. Fourteen original disclosure fixtures and three single-sign fixtures are caught. Thirteen integration/preservation checks pass, including mass and synthetic rejection. Package M's 11,369 occurrences remain quarantined without an identity concordance. Twenty-three new selection/result files replay exactly, and direct scalar/measurement-source comparisons find zero mismatches among 3,335 and 3,408 compared assertions. The original 158 checks also pass using the preserved protocol prefix. [Verification](verification-2026-10-07-v3/checks.json), [comparison](review-response-2026-10-07-v3/replay-comparison.json), [source audit](review-response-2026-10-07-v3/assertion-values.json).

The remaining work is source-specific: confirm physical carrier and surface boundaries, the L-141 corrected-caption interpretation, unadjudicated museum fields, prefix-only registrations and the historical Finnish Concordance relation. The new queues contain 156 and138 questions. The source register identifies the local pages actually opened and the inherited Zenodo licence check. No new search, download, installation, contact, publication or repository-history operation occurred. [Report](REPORT.md), [sources](sources.json), [full changed-path manifest](FILES-REVIEW-RESPONSE-2026-10-07.json).
'''
    original=re.sub(r'\b(all|and|against|about|comprises|contains|has|including|mean|number|on|original|supplies|the|with)(?=\d)',r'\1 ',original)
    (OWN/'RETROSPECTIVE.md').write_text(original,encoding='utf-8')
    registry=read('registry-entry.json');registry.update(status='Exploratory',outcome='Preserved original 200-object selection and added hash-ordered selection: 34 versus39 export site labels, 18 versus44 Lower Indus carriers, zero versus10 Kalibangan. Corrected original dimension completeness127 to130, gain3. Original149 excavation strings restated as126 uncontaminated registrations; citations, lots and variants separated. Revised registers have6991 and7004 assertions; museum joins26 and25, candidates34 and15. All26 reviewer mutations and17 sequence fixtures caught;23 result files replay exactly; original158 checks pass. No real Helsinki imports or dating-sample links.',challenge='Alphabetical sample bias; ambiguous export registrations; source/date/count disagreements; surface concordance unavailable; metadata rights unresolved for public release.',remedy='Dated exploratory amendment, hash-ordered strata, country-qualified external quota, source-qualified corrections, schema2 and semantic validator, local-only replays, occurrence-aware Helsinki adapter and specific review queues.',evidence=['experiments/2026-10-07-object-ledger/'+p for p in ['PROTOCOL.md','REPORT.md',RUN+'/selection.json',RUN+'/coverage-comparison.json',RUN+'/corrected-original/summary.json',RUN+'/hash-ordered/summary.json',CHECK+'/checks.json',CHECK+'/mutations.json',COMPARISON+'/replay-comparison.json']],retry_when='Reviewed object/surface concordances, confirmed inscription eligibility, new primary registration/date evidence or a public reuse basis become available; add a new endpoint.')
    for key in ['outcome','remedy']:
        registry[key]=re.sub(r'(?<=[A-Za-z])(?=\d)',' ',registry[key])
    write(OWN/'registry-entry.json',registry)
    sources=read('sources.json')
    for entry in sources['sources']:
        if entry.get('id')=='cisi1':
            entry.update(creator_role='editor',primary_edition_reopened=True,opened_source_record_by_package_L=True,opened_scope='review response: local scan printed272,279,365,375 / PDF308,315,401,411',access_status='opened_targeted_primary_local_pages')
        if entry.get('id')=='lothal2005':
            entry.update(license='CC-BY-4.0',license_basis='supplied REVIEW.md Source checks; Zenodo5514283; inherited verification, online notice not reopened')
    sources['review_response']={'status':'Exploratory','local_source_observations':'data/raw/2026-10-07-object-ledger/review-response-2026-10-07/source-observations.json','access_log':'data/raw/2026-10-07-object-ledger/review-response-2026-10-07/source-access-log.json','sources':[
        {'title':'Corpus of Indus Seals and Inscriptions. 1. Collections in India','authors':['Jagat Pati Joshi','Asko Parpola'],'creator_role':'editor','year':1987,'venue':'Annales Academiae Scientiarum Fennicae B239, Helsinki','url':'https://ignca.gov.in/Asi_data/76884.pdf','opened':True,'snippet_only':False,'access':'local scan printed272,279,365,375 / PDF308,315,401,411','quoted_words':0},
        {'title':'Seals of ancient Indian style found at Ur','authors':['C. J. Gadd'],'year':1932,'venue':'Proceedings of the British Academy18:191-210','url':'https://ignca.gov.in/Asi_data/33779.pdf','opened':True,'snippet_only':False,'access':'local scan printed13-14 / PDF24-25; earlier navigation and plate checks recorded','quoted_words':0},
        {'title':'The Lothal Sealings: Records from an Indus Civilization Town at the Eastern End of the Maritime Trade Circuits across the Arabian Sea','authors':['Dennys Frenez','Maurizio Tosi'],'year':2005,'venue':'M. Perna (ed.), Studi in onore di Enrica Fiandra: Contributi di archeologia egea e vicinorientale, pp.65-103','url':'https://zenodo.org/records/5514283','opened':False,'snippet_only':False,'access':'local source audit and supplied reviewer source check opened; primary online notice not reopened','license':'CC-BY-4.0','licence_basis':'REVIEW.md Source checks, Frenez and Tosi row; inherited reviewer verification','quoted_words':0}],
        'new_searches':[],'new_downloads':[],'remaining_source_tasks':['Full CISI data-column transcription for selected carriers remains incomplete','Twenty-seven corrected-original and26 revised CISI pointers remain section-level','Other selected Lothal captions were not individually inspected for impression-count conventions','Current holdings for KRS/RGR codes and historical Finnish Concordance edition mapping remain unverified']}
    write(OWN/'sources.json',sources)
    print('Updated README, REPORT, RETROSPECTIVE, registry-entry and sources')

if __name__=='__main__':main()
