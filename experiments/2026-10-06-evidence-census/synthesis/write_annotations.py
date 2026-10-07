"""Write B3's reviewed source observations and proposed acquisition priorities once."""
from pathlib import Path
from hashlib import sha256
import argparse
import json

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
OUT = OWN
BASE = ROOT / 'experiments/2026-10-06-evidence-census/sites-deep'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(name, data):
    path = OUT / name
    if path.exists():
        raise ValueError('Refusing to overwrite ' + str(path))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


SOURCE_SELECTION = {
    'a-pakistan-afghanistan': {'RCO-M77': 'IM77', 'RMA-CISI2': 'CISI2', 'RMA-HAR2010': 'HARAPPA2010'},
    'b-gujarat-kutch-maharashtra': {'CISI1': 'CISI1', 'LOTHAL2005': 'LOTHAL2005', 'DHOLAVIRA2015': 'DHOLAVIRA2015',
        'RANGPUR1963': 'RANGPUR1963', 'IAR1963-1964-ALT': 'IAR1963', 'IAR1987-1988-ALT': 'IAR1987', 'NUHATO2018': 'NUHATO2018'},
    'c-north-india': {'iar2013': 'IAR2013', 'bhagwanpura1993': 'BHAGWANPURA1993'},
    'd-finds-abroad': {'nippur1993': 'NIPPUR1993', 'cisi33': 'CISI33', 'salut2016': 'SALUT2016', 'gonur2005': 'GONUR2005',
        'laursen2010': 'LAURSEN2010', 'gadd1932': 'GADD1932'}}
OPENED = {'IM77', 'CISI1', 'CISI2', 'LOTHAL2005', 'DHOLAVIRA2015', 'RANGPUR1963', 'IAR1963', 'IAR1987',
          'NUHATO2018', 'IAR2013', 'BHAGWANPURA1993', 'NIPPUR1993', 'CISI33', 'SALUT2016', 'GONUR2005'}


def main():
    global OUT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir', help='New annotation replay directory inside the owned package')
    args = ap.parse_args()
    if args.output_dir:
        OUT = (ROOT / args.output_dir).resolve()
        if not OUT.is_relative_to(OWN) or OUT.exists():
            raise ValueError('Use a new annotation directory inside the owned package')
        OUT.mkdir(parents=True)
    sources = []
    for b, mapping in SOURCE_SELECTION.items():
        data = load(BASE / b / 'sources.json')
        ss = data if isinstance(data, list) else data['sources']
        for old, new in mapping.items():
            found = next((s for s in ss if s.get('id') == old), None)
            if found is None:
                raise ValueError('Source missing: ' + b + ':' + old)
            title = found['title']
            if len(title) > 350 or len(title.split()) > 55:
                raise ValueError('Source title needs manual bibliographic resolution: ' + old)
            sources.append({'id': new, 'title': title, 'authors': found.get('authors'), 'year': found.get('year'),
                'venue': found.get('venue'), 'url': found.get('url'), 'opened_in_B3': new in OPENED,
                'access_in_B3': 'saved_primary_content' if new in OPENED else 'prior_package_bibliography_and_observations_only',
                'search_snippet_only_in_B3': False, 'upstream_source_record': f'sites-deep/{b}/sources.json#{old}',
                'rights': found.get('rights', found.get('reuse', found.get('reuse_terms'))), 'quoted_words_in_B3': 0})
    sources.append({'id': 'ICIT2023', 'title': 'The Interactive Corpus of Indus Texts (ICIT) as an epigraphical database and online tool for Indus script research',
        'authors': ['Andreas Fuls'], 'year': 2023, 'venue': 'CAA 2023 Abstract Book, abstract 76, p. 281',
        'url': 'https://2023.caaconference.org/wp-content/uploads/sites/29/2023/04/abstract_book_v13.pdf#page=281',
        'opened_in_B3': True, 'access_in_B3': 'saved_primary_PDF_page_281', 'search_snippet_only_in_B3': False,
        'rights': 'Database bulk terms and image rights unverified; abstract PDF stays local', 'quoted_words_in_B3': 0})
    manifest = load(ROOT / 'data/raw/2026-10-06-evidence-census/synthesis/source-review-2026-10-07-v2/source-page-manifest.json')
    source_ids = {'IM77': 'IM77', 'CISI2': 'CISI2', 'CISI1': 'CISI1', 'BHAGWANPURA': 'BHAGWANPURA1993', 'DESALPAR': 'IAR1963',
                  'NAGWADA': 'IAR1987', 'KARANPURA': 'IAR2013', 'RANGPUR': 'RANGPUR1963', 'LOTHAL': 'LOTHAL2005',
                  'NIPPUR': 'NIPPUR1993', 'CISI33': 'CISI33', 'SALUT': 'SALUT2016', 'GONUR': 'GONUR2005', 'ICIT2023': 'ICIT2023', 'DHOLAVIRA': 'DHOLAVIRA2015'}
    for source in sources:
        source['inspected_witnesses'] = [m for m in manifest if source_ids.get(m['source_id']) == source['id']]
        if source['id'] == 'NUHATO2018':
            p = ROOT / 'data/raw/2026-10-06-evidence-census/sites-deep/b-gujarat-kutch-maharashtra/NUHATO2018.pdf'
            source['inspected_witnesses'] = [{'source': p.relative_to(ROOT).as_posix(), 'source_sha256': sha256(p.read_bytes()).hexdigest(), 'pdf_pages_1_based': [41, 42]}]
    write('sources.json', {'as_of': '2026-10-07', 'live_web_searches_in_B3': 0, 'direct_quotes_in_B3': 0,
        'scope': 'Opened states describe B3. Unopened literature is attributed to the contributing package, without upgrading its access status.', 'sources': sources,
        'search_and_access_log': [{'operation': 'new_live_search', 'result': 'not used; conflicts resolved with saved primary witnesses'},
            {'operation': 'new_download', 'result': 'not attempted; existing local witnesses reused'},
            {'operation': 'prior_failed_acquisitions', 'evidence': ['sites-deep/b-gujarat-kutch-maharashtra/source-access.json',
             'sites-deep/c-north-india/aggregates.json#failed_download_attempts', 'sites-deep/d-finds-abroad/RETROSPECTIVE.md',
             'collections-and-datasets/focused-query-log.csv'], 'result': 'Preserved upstream; no failed route retried'}]})

    # These are our observations of the selected passages, not extracted third-party rows.
    audit = [
        ('a', 'Harappa', 'IM77', 'p.6 / PDF17', '985 selected inscribed objects', '985 is printed in the site table; section 5.1 defines the selected legible/partly legible population.', 'supported'),
        ('a', 'Mohenjo-daro', 'IM77', 'p.6 / PDF17', '1540 selected inscribed objects', '1540 is printed in the same table; overall selected count is 2906 after 549 exclusions from 3455 photographed objects.', 'supported'),
        ('a', 'Balakot', 'CISI2', 'p.xv note12 / PDF18', '28 early pottery-mark drawings not photographed in CISI2', 'The CISI editors give 28 published drawings and say they could not locate the objects for photography. Dales 1974 itself was not opened in B3.', 'qualified'),
        ('a', 'Sarai Khola', 'CISI2', 'p.xviii note46 / PDF21; pp.410–411 / PDF445–446', '68 reported marked sherds and 10 photographed catalogue entries', 'The introduction attributes 68 to Halim 1972 and states partial photographic recovery. The plates show Skh1–10. Halim was not opened in B3.', 'qualified'),
        ('a', 'Rehman Dheri', 'CISI2', 'p.378 / PDF413', 'Rhd267–269 classified as tentative scrapers', 'Three separate objects and the tentative scraper caption are visible; multiple sides do not add objects.', 'supported'),
        ('b', 'Lothal', 'LOTHAL2005', 'pp.67–68 / PDF5–6', '93 sealings in the reanalysis', 'The reanalysis prints 93 for Lothal. Comparison with the earlier report needs an excavation-number crosswalk.', 'supported'),
        ('b', 'Dholavira', 'DHOLAVIRA2015', 'saved mirror; pp.232,242,308', '225 recovered seals, 139/194 inscription-positive analysed seals, 60–61 sealings', 'All figures occur in the saved report text. The inscription table totals 194; the sealing prose contains inconsistent subtraction. Original page rasters were not acquired.', 'qualified'),
        ('b', 'Rangpur', 'RANGPUR1963', 'p.130 / PDF169', '26+188+8 broadly marked sherds', 'The page gives all three groups explicitly. Their sum is 222; the groups include figurative and linear motifs.', 'supported'),
        ('b', 'Desalpar', 'IAR1963', 'p.10 / PDF19', 'two script-bearing seals plus one sealing', 'The source describes one steatite seal, one copper seal and a lettered terracotta sealing.', 'supported'),
        ('b', 'Nagwada', 'IAR1987', 'p.20 / PDF28', 'one Harappan-inscribed clay sealing', 'The antiquity list describes a clay lump with inscription above a bull impression.', 'supported'),
        ('c', 'Kalibangan', 'CISI1', 'p.326 / PDF362', 'catalogue endpoint K122', 'The page labels K122 and its enlarged views. B3 checks the endpoint, not every intervening entry in the batch count of 122.', 'qualified'),
        ('c', 'Banawali', 'CISI1', 'p.349 / PDF385', 'catalogue endpoint B37', 'The page shows B30–37. B3 checks this endpoint and class, not all earlier entries in the batch count of 37.', 'qualified'),
        ('c', 'Karanpura', 'IAR2013', 'p.120 / PDF125; pp.116–117 / PDF121–122', '157 graffiti instances, comprising 134+22+1', 'The report gives 134 sherd instances, 22 spindle-whorl instances and one ring instance. It separately describes two inscribed seals.', 'supported'),
        ('c', 'Bhagwanpura', 'BHAGWANPURA1993', 'p.139 / PDF177; fig.39 p.140 / PDF178', 'two marked tablets and nineteen marked sherds', 'The chapter opening gives both counts, and the tablet descriptions and figure show two specimens.', 'supported'),
        ('c', 'Rohira', 'CISI1', 'p.361 / PDF397', 'Rhr1–2 seal impressions', 'Both labels and images are visible. They are separate from the Rojdi and Rupar material on the same page.', 'supported'),
        ('d', 'Nippur', 'NIPPUR1993', 'p.81 catalogue / PDF151', '13 N 506, IM78230, one inscribed seal', 'The original catalogue supplies both registrations, an Indus-script description, 2×2×1 cm dimensions, and a floor/fill context.', 'supported'),
        ('d', 'Shortughai', 'CISI33', 'pp.vii,xv / PDF9,17', 'Sh1–84 mixed catalogue; two seals reported', 'The contents give 84 mixed entries; the preface describes two seals and plentiful graffiti. This does not verify two separate script-bearing seals.', 'qualified'),
        ('d', 'Tepe Yahya', 'CISI33', 'pp.vi,xi / PDF8,13', 'TY1–112 mixed catalogue and an Indus seal impression TY106', 'Both the sequence and the specific seal-impression attribution appear in the source. The 112-entry total includes other scripts and glyptics.', 'supported'),
        ('d', 'Salut', 'SALUT2016', 'pp.116–118 / PDF16–18', 'one seal and two impressed fragments, possibly one vessel', 'The seal and first fragment are described separately. The later rim impression is stated to be possibly from the same jar.', 'supported'),
        ('d', 'Gonur Depe', 'GONUR2005', 'pp.258–259 / PDF130, figs.114–115', 'one elephant seal with signs, separate from a cuneiform cylinder', 'The spread illustrates a seal and its impression in figure114 and a different cylinder in figure115. The narrative places the elephant seal in room19, area9.', 'supported')]
    records = [{'batch': next(b for b in SOURCE_SELECTION if b.startswith(letter)), 'site': site, 'source_id': source,
        'locator': location, 'tested_assertion': assertion, 'B3_observation': observation, 'outcome': outcome,
        'reviewer': 'B3 agent; no expert adjudication', 'evidence': 'sources.json#' + source} for letter, site, source, location, assertion, observation, outcome in audit]
    write('source-sample-audit.json', {'status': 'Exploratory', 'selection': 'sample-selection.json', 'rows_checked': len(records),
        'outcomes': {status: sum(r['outcome'] == status for r in records) for status in ['supported', 'qualified', 'contradicted', 'unavailable']},
        'scope': 'Selected assertions, not all fields. Purposive sample; no population error-rate estimate.', 'rows': records})

    conflicts = [
        {'id': 'Nuhato-overlap', 'sites': ['Gharo Bhiro', 'Nuhato'], 'batches': ['a', 'b'],
         'observation': 'CISI2 p.xv explicitly equates the names. The 2018 Nuhato report pp.41–42 describes the 1973 seal and a second seal from the 2018 project. Batch A could not access that report; batch B did.',
         'resolution': 'One site entity; preserve both local label groups. One historical CISI object and two report seals have different dates. The 2018 report cites CISI2 p.390, but the original Grb1 plate is on p.392.',
         'sources': ['CISI2', 'NUHATO2018'], 'object_join': 'Unconfirmed between individual local Nuhato/Gharo Bhiro families and the two report specimens'},
        {'id': 'Pakistan-cross-references', 'sites': ['Nindowari', 'Miri Qalat', 'Sibri', 'Ornach area', 'Murda Sang', 'Shortughai'], 'batches': ['a', 'd'],
         'observation': 'Six shared site entities occur in A and D. Five are Pakistani cross-reference rows; Shortughai is in Afghanistan.',
         'resolution': 'Assign to A for regional sums. Retain D source observations and its original totals. Remove eight repeated local faces from pooled label totals.', 'evidence': 'register-joins.json#site_aliases'},
        {'id': 'Shortughai-classes', 'sites': ['Shortughai'], 'batches': ['a', 'd'],
         'observation': 'A reports two seals from the CISI preface; D confirms one script-bearing specimen and records the 84-entry mixed catalogue.',
         'resolution': 'Two reported seal objects, one independently identified here as script-bearing, and 84 mixed catalogue entries are separate count bases.', 'sources': ['CISI33']},
        {'id': 'Lothal-counts', 'sites': ['Lothal'], 'observation': 'Earlier excavation report gives 91 sealings; 2005 reanalysis gives 93. IM77 selects 75 sealings. CISI1 has 290 entries across classes.',
         'resolution': 'Retain 91–93 as an attributed sealing-inventory disagreement. Do not subtract selected IM77 or all CISI classes from it.', 'sources': ['LOTHAL2005'], 'earlier_source': 'sites-deep/b-gujarat-kutch-maharashtra/site-rows.json#Lothal/reported_counts'},
        {'id': 'Dholavira-counts', 'sites': ['Dholavira'], 'observation': 'Report gives 225 recovered seals, 194 analysed seals and 139 inscription-positive seals. It gives 60 sealings in overview, 61 in detailed text, and inconsistent remaining59 after four exclusions.',
         'resolution': 'Use separate seal populations and the attributed 60–61 sealing range. The inscription table gives 23/194 as 11.9%; nearby prose incorrectly says23%.', 'sources': ['DHOLAVIRA2015']},
        {'id': 'Foreign-find-denominator', 'sites': ['Ur', 'Dilmun', 'Salut', 'Tepe Yahya'], 'observation': 'D selected minima include uncertain Gulf signs, regional provenance labels and fragment/vessel ambiguity. BM123208 has Ur as findspot but appears under the local Dilmun label.',
         'resolution': 'Keep production attribution separate from findspot; Ur/Dilmun family identity remains a candidate. Salut supports two to three carriers if the fragments represent one to two vessels plus one seal. No D-wide recall fraction.', 'sources': ['SALUT2016', 'GADD1932', 'CISI33']},
        {'id': 'Museum-field-conflicts', 'observation': '61 reported identifier joins include one site disagreement, four material disagreements, five dimensions outside the declared tolerance, and nine single-face sign-count disagreements.',
         'resolution': 'Retain the paired assertions and review images/measurement conventions. Exact identifier agreement does not adjudicate other fields.', 'evidence': 'join-summary.json#comparisons; collections-and-datasets/paired-full-audit.csv'}]
    write('conflicts.json', {'status': 'Exploratory', 'conflicts': conflicts})

    common_rights = 'Public reading access supplies no general image or bulk-data redistribution grant; retain raw locally and resolve source/asset terms before release.'
    gaps = [
        {'rank': 1, 'id': 'master-inventory', 'pool': 'Current ICIT, complete CISI editions and major unpublished holding inventories', 'kind': 'unmeasured_inventory_and_identity',
         'scale': {'ICIT_2023_inscribed_objects': 4665, 'current_missing_objects': None}, 'evidence_added': 'A common object denominator and disposition for every nominated inventory entry.',
         'route': ['permissioned database export request to ICIT maintainer', 'full CISI volumes and published concordances', 'museum inventory/archive request for Karachi and ASI site collections'],
         'rights': common_rights, 'evidence': ['sources.json#ICIT2023', 'collections-and-datasets/collection-register.json', 'coverage.json#index_counts']},
        {'rank': 2, 'id': 'major-site-context', 'pool': 'Harappa and Mohenjo-daro contextual records', 'kind': 'under_description',
         'scale': {'local_faces': 4640, 'local_provisional_families': 3716}, 'evidence_added': 'Find units, layers, dated assemblages, dimensions, original registrations and inspected views for the largest local population.',
         'route': ['CISI basic-data and excavation catalogues', 'HARP publications', 'excavator/curatorial archive request for missing field registers'], 'rights': common_rights,
         'evidence': ['coverage.json#sites/Harappa', 'coverage.json#sites/Mohenjo-daro', 'field-completeness.csv#Lipi pinned derivative']},
        {'rank': 3, 'id': 'rehman-dheri', 'pool': 'Rehman Dheri marked-object catalogue', 'kind': 'local_catalogue_key_gap',
         'scale': {'catalogue_entries': 270, 'local_matching_keys': 2, 'local_absent_keys': 268, 'additional_authenticated_Indus_texts': None},
         'evidence_added': 'Early Harappan marked pottery and comparative objects with provenance and classification; source includes three tentative scrapers.',
         'route': ['CISI2 pp.352–378,416 and basic data', 'original excavation publication and Peshawar archive request'], 'rights': common_rights,
         'evidence': ['catalogue-coverage.csv#Rehman Dheri', 'sources.json#CISI2', 'source-sample-audit.json#Rehman Dheri']},
        {'rank': 4, 'id': 'lothal', 'pool': 'Lothal catalogue entries and sealing contexts', 'kind': 'local_catalogue_key_gap_and_context',
         'scale': {'CISI1_entries': 290, 'local_matching_keys': 179, 'local_absent_keys': 111, 'reported_sealings_range': [91, 93]},
         'evidence_added': 'Missing identifier dispositions and sealing reverse/contact/context observations for source-defined sealing groups.',
         'route': ['CISI1 pp.238–297 and basic data pp.372–374', 'Rao 1985 tables', 'Frenez and Tosi 2005', 'ASI museum/archive request for original images and registrations'],
         'rights': common_rights, 'evidence': ['catalogue-coverage.csv#Lothal', 'conflicts.json#Lothal-counts']},
        {'rank': 5, 'id': 'regional-marked-assemblages', 'pool': 'Rangpur, Karanpura, Sarai Khola, Balakot and Bhagwanpura', 'kind': 'related_marks_and_underindexed_assemblages',
         'scale': {'Rangpur_reported_sherds': 222, 'Karanpura_graffiti_instances': 157, 'Sarai_Khola_reported_sherds': 68,
                   'Sarai_Khola_photographed_entries': 10, 'Balakot_drawn_examples': 28, 'Bhagwanpura_tablets_and_sherds': 21},
         'evidence_added': 'Classified comparative mark observations, pre/post-firing information, phase context and carrier relationships. These counts are not additive script-bearing object omissions.',
         'route': ['Rao 1963 p.130', 'IAR2013–14 p.120', 'Halim 1972 pp.95–99 and museum/archive request', 'Dales 1974 p.16 fig.11', 'Joshi 1993 pp.139–142'],
         'rights': common_rights, 'evidence': ['source-sample-audit.json#Rangpur', 'source-sample-audit.json#Karanpura', 'source-sample-audit.json#Sarai Khola', 'source-sample-audit.json#Balakot', 'source-sample-audit.json#Bhagwanpura']},
        {'rank': 6, 'id': 'later-major-regional-inventories', 'pool': 'Dholavira and Kalibangan later catalogues; Farmana, Rakhigarhi and other northern excavation inventories', 'kind': 'unreconciled_publication_inventory',
         'scale': {'Dholavira_recovered_seals': 225, 'Dholavira_positive_inscription_subset': 139, 'Dholavira_analysed_seals': 194,
                   'Kalibangan_CISI1_entries': 122, 'Kalibangan_absent_local_CISI1_keys': 26, 'north_CISI1_absent_keys': 45, 'additional_objects': None},
         'evidence_added': 'Reviewed class inventories, exact catalogue cutoffs, registration joins, newer find contexts and omitted carrier types.',
         'route': ['Bisht 2015 inventory pp.246–333', 'Kalibangan final report and CISI3.2 site section', 'Farmana final excavation volume', 'Rakhigarhi field/collection inventory via publication or excavator request'],
         'rights': common_rights, 'evidence': ['coverage.json#sites/Dholavira', 'coverage.json#sites/Kalibangan', 'conflicts.json#Dholavira-counts', 'catalogue-coverage.csv']},
        {'rank': 7, 'id': 'museum-unjoined', 'pool': '53 confirmed-original museum records lacking confirmed local joins', 'kind': 'identity_gap',
         'scale': {'inspected_originals': 114, 'confirmed_joins': 61, 'unjoined': 53}, 'evidence_added': 'New photographs, dimensions, accessions and possibly objects once aliases and duplicates are resolved.',
         'route': ['53 raw candidate records', 'CISI museum/excavation tables', 'museum request for registration concordances and item-level image terms'],
         'rights': 'Met eligible assets CC0, Penn downloadable data CC BY4.0 and Louvre record data Etalab Open Licence2.0 are recorded policy routes; image permissions and Indian portal/BM bulk terms have separate scopes. Policies were inherited from the focused census.',
         'evidence': ['join-summary.json', 'collections-and-datasets/focused-field-counts.csv', 'collections-and-datasets/REPORT.md#Fields and reuse conditions']},
        {'rank': 8, 'id': 'finds-abroad-and-borderlands', 'pool': 'Foreign-find identity and classification, including Salut, Nippur, Tepe Yahya, Shortughai and Gonur', 'kind': 'small_high_context_pool_and_comparative_inventory',
         'scale': {'Shortughai_mixed_entries': 84, 'Tepe_Yahya_mixed_entries': 112, 'Gonur_elephant_seals_verified_here': 1, 'missing_Indus_objects': None},
         'evidence_added': 'Secure findspot/production separation, exceptional carrier context, foreign accessions, fragment/vessel relationships and candidate sign classification.',
         'route': ['CISI3.3 complete plates and basic data', 'Gonur original catalogue/archive', 'Nippur plate89 and registrations', 'Salut excavation records', 'regional museum/excavator request'],
         'rights': 'Nippur institutional CC BY-NC-ND4.0 route has restrictions. Other source images remain rights-unverified or copyrighted. Comparative corpora require separate scope labels.',
         'evidence': ['sources.json#CISI33', 'sources.json#NIPPUR1993', 'sources.json#SALUT2016', 'sources.json#GONUR2005', 'conflicts.json#Foreign-find-denominator']}]
    write('priority-gaps.json', {'status': 'Proposed', 'ranking_basis': 'Evidence gained, documented scale, source accessibility and identity uncertainty; qualitative judgement. Pools overlap and must not be summed.', 'gaps': gaps})
    print(json.dumps({'sources': len(sources), 'sample_rows': len(records), 'conflicts': len(conflicts), 'priority_pools': len(gaps)}))


if __name__ == '__main__':
    main()
