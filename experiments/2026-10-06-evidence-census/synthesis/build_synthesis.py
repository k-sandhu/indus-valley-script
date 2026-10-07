"""Offline census synthesis. New endpoints only; third-party rows stay in raw."""
from pathlib import Path
from collections import Counter, defaultdict
from hashlib import sha256
import argparse
import csv
import json
import re
import os

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/synthesis'
BASE = ROOT / 'experiments/2026-10-06-evidence-census'
BATCHES = ['a-pakistan-afghanistan', 'b-gujarat-kutch-maharashtra', 'c-north-india', 'd-finds-abroad']
PINS = {}
MISSING = {'', '-', '--', '- -', '?', 'unknown', 'none', 'null', 'n/a'}


def read(path):
    data = path.read_bytes()
    PINS[path.relative_to(ROOT).as_posix()] = {'bytes': len(data), 'sha256': sha256(data).hexdigest()}
    return json.loads(data.decode('utf-8-sig'))


def jsonl(path):
    data = path.read_bytes()
    PINS[path.relative_to(ROOT).as_posix()] = {'bytes': len(data), 'sha256': sha256(data).hexdigest()}
    return [json.loads(line) for line in data.decode('utf-8-sig').splitlines() if line.strip()]


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def csvout(path, rows, fields=None):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in r.items()} for r in rows)


def rows(data):
    return data if isinstance(data, list) else data.get('sites', data.get('rows', data.get('sources', [])))


def name(row):
    return row.get('canonical_name', row.get('site'))


def norm(value):
    return re.sub(r'[^a-z0-9]', '', str(value).casefold())


ALIASES = {'gharobhiro': 'Nuhato', 'nuhato': 'Nuhato', 'nindowaridamb': 'Nindowari',
           'nindowari': 'Nindowari', 'roparrupar': 'Ropar (Rupar)', 'rupar': 'Ropar (Rupar)',
           'ropar': 'Ropar (Rupar)', 'goladhorobagasra': 'Gola Dhoro (Bagasra)',
           'bagasra': 'Gola Dhoro (Bagasra)', 'girsu': 'Girsu/Tello', 'tello': 'Girsu/Tello',
           'girsutello': 'Girsu/Tello', 'balakot': 'Balakot', 'chandudaro': 'Chanhu-daro',
           'chanhudaro': 'Chanhu-daro', 'lohumjodaro': 'Lohumjo-daro', 'kotdiji': 'Kot Diji',
           'mohenjodaro': 'Mohenjo-daro', 'shorthugai': 'Shortughai', 'shortughai': 'Shortughai'}


def canonical(value):
    return ALIASES.get(norm(value), value)


def populated(value):
    return value is not None and str(value).strip().casefold() not in MISSING


def number(value):
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def calendar_label(value):
    value = str(value or '')
    return bool(re.search(r'\d', value) and (re.search(r'b\.?c\.?e?\.?|av\.\s*j|century|mill', value, re.I) or re.search(r'\(-\d{3,4}', value)))


def cisi_id(value):
    # Source-qualified base catalogue key only. Alternative strings remain unresolved.
    m = re.fullmatch(r'([A-Za-z]+)-?(\d+)', str(value).strip())
    return (m[1].casefold(), int(m[2])) if m else None


def ranges_in(text):
    """Parse all identifier runs before the page-reference semicolon."""
    found = []
    for part in text.split(';', 1)[0].split(','):
        m = re.fullmatch(r'\s*([A-Za-z]+)\s*-?\s*(\d+)(?:\s*[\u2013\u2014-]\s*(?:[A-Za-z]+\s*-?\s*)?(\d+))?\s*', part)
        if not m:
            raise ValueError('Unparsed catalogue run: ' + part)
        found.append((m[1], int(m[2]), int(m[3] or m[2])))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir', required=True, help='New dated directory within this package')
    ap.add_argument('--raw-dir', required=True, help='New dated directory within the paired raw package')
    args = ap.parse_args()
    out = (ROOT / args.output_dir).resolve()
    raw = (ROOT / args.raw_dir).resolve()
    if not out.is_relative_to(OWN) or not raw.is_relative_to(RAW) or out.exists() or raw.exists():
        raise ValueError('Both endpoints must be new directories inside the two owned roots')
    out.mkdir(parents=True)
    raw.mkdir(parents=True)
    tmp = raw / 'tmp'
    tmp.mkdir()
    for key in ['TMP', 'TEMP', 'MPLCONFIGDIR']:
        os.environ[key] = str(tmp)

    coordinator_path = ROOT / 'experiments/2026-10-06-research-program/local-site-coverage.json'
    coord = read(coordinator_path)['sites']
    cm = {r['site']: r for r in coord}
    lipi = jsonl(ROOT / 'data/normalized/lipi_observed_faces.jsonl')
    mayig = jsonl(ROOT / 'data/normalized/mayig_faces.jsonl')
    corrections = read(OWN / 'v6-correction-inputs.json')
    im77_source = ROOT / corrections['im77_source']
    PINS[corrections['im77_source']] = {'bytes': im77_source.stat().st_size, 'sha256': sha256(im77_source.read_bytes()).hexdigest()}
    bysite = defaultdict(list)
    for row in lipi:
        bysite[canonical(row['site'])].append(row)
    checks = []

    def check(label, actual, expected):
        checks.append({'check': label, 'actual': actual, 'expected': expected, 'passed': actual == expected})

    check('coordinator_faces', sum(r['faces'] for r in coord), len(lipi))
    check('coordinator_family_sum', sum(r['object_families'] for r in coord), len({r['object_family_id'] for r in lipi}))
    for r in coord:
        subset = [x for x in lipi if x['site'] == r['site']]
        check('coordinator:' + r['site'] + ':faces', len(subset), r['faces'])
        check('coordinator:' + r['site'] + ':families', len({x['object_family_id'] for x in subset}), r['object_families'])
        check('coordinator:' + r['site'] + ':cisi', len({x['source_cisi'] for x in subset if populated(x['source_cisi'])}), r['distinct_cisi_ids'])

    batches = []
    groups = defaultdict(list)
    assertions = []
    catalogue = []
    snippet_flags = []
    for b in BATCHES:
        directory = BASE / 'sites-deep' / b
        rr = rows(read(directory / 'site-rows.json'))
        totals = Counter()
        for i, row in enumerate(rr):
            lc = row.get('local_corpus') or {}
            site = canonical(name(row))
            ALIASES.setdefault(norm(name(row)), site)
            for l in lc.get('records', [lc]):
                if l.get('site'):
                    ALIASES.setdefault(norm(l['site']), site)
                for field in ['faces', 'object_families', 'distinct_cisi_ids']:
                    totals[field] += l.get(field, 0)
                if l.get('site') in cm:
                    for field in ['faces', 'object_families', 'distinct_cisi_ids']:
                        check(f'{b}:{i}:{field}', l.get(field), cm[l['site']][field])
            site = canonical(name(row))
            pointer = f'experiments/2026-10-06-evidence-census/sites-deep/{b}/site-rows.json#row={i};name={name(row)}'
            groups[site].append({'batch': b, 'row': row, 'pointer': pointer})
            count_rows = row.get('reported_object_counts', row.get('reported_counts', row.get('published_counts', []))) or []
            for j, c in enumerate(count_rows):
                v = c.get('count', c.get('value'))
                if not isinstance(v, (int, float)):
                    continue
                evidence = c.get('evidence', []) or []
                sids = c.get('source_ids', [c['source_id']] if c.get('source_id') else [c['source']] if c.get('source') else [])
                sids = sids or [e['source_id'] for e in evidence]
                assertions.append({'site': site, 'batch': b, 'value': v,
                    'unit': c.get('unit', c.get('basis', c.get('unit_or_basis'))),
                    'object_class': c.get('object_class', c.get('class')),
                    'date': c.get('date_of_count', c.get('count_date', c.get('date'))),
                    'basis': c.get('count_basis', c.get('scope', c.get('basis', c.get('claim')))),
                    'classification': c.get('inscription_assessment', c.get('inscription_eligibility', c.get('note'))),
                    'sources': [b + ':' + s for s in sids],
                    'locator': c.get('location', c.get('source_page', c.get('source_location'))) or '; '.join(e.get('location', '') for e in evidence),
                    'input_pointer': pointer + f';count={j}', 'additive': False})
            if b.startswith('b'):
                for c in row.get('cisi_coverage', []):
                    if c.get('catalogue_object_slots') is not None:
                        catalogue.append({'site': site, 'batch': b, 'edition': 'CISI1-1987', 'prefix': c['identifier_prefix'],
                            'first': 1, 'last': c['catalogue_object_slots'], 'pages': c['page_range'], 'input_pointer': pointer})
            if b.startswith('c'):
                c = row['cisi_coverage']
                if c.get('catalogue_objects') is not None:
                    catalogue.append({'site': site, 'batch': b, 'edition': 'CISI1-1987', 'prefix': c['prefix'],
                        'first': 1, 'last': c['catalogue_objects'], 'pages': c['page_range'], 'input_pointer': pointer})
            if b.startswith('a'):
                for vol, value in (row.get('cisi') or {}).get('verified_ranges', {}).items():
                    runs = ranges_in(value) if vol in ['1', '2'] else []
                    for prefix, first, last in runs:
                        # Catalogue aliases do not create extra edition entries.
                        catalogue.append({'site': site, 'batch': b, 'edition': 'CISI' + vol,
                            'prefix': prefix, 'first': first, 'last': last, 'pages': value, 'input_pointer': pointer})
        aggname = {'a': 'aggregate.json', 'b': 'aggregate-results.json', 'c': 'aggregates.json', 'd': 'aggregate-results.json'}[b[0]]
        agg = read(directory / aggname)
        expected = {'faces': agg.get('local_faces', agg.get('local_totals', {}).get('faces')),
                    'object_families': agg.get('local_object_families', agg.get('local_object_family_label_sum', agg.get('local_totals', {}).get('object_families'))),
                    'distinct_cisi_ids': agg.get('local_distinct_cisi_ids', agg.get('distinct_local_cisi_ids_sum', agg.get('local_distinct_cisi_id_label_sum', agg.get('local_totals', {}).get('distinct_cisi_ids'))))}
        if b.startswith('a'):
            expected = {'faces': agg['local_label_sum_faces'], 'object_families': agg['local_label_sum_object_families'],
                        'distinct_cisi_ids': agg['local_label_sum_distinct_cisi_ids']}
        for field in totals:
            if expected[field] is not None:
                check(b + ':saved:' + field, totals[field], expected[field])
        check(b + ':saved:rows', len(rr), agg.get('sites', agg.get('rows', agg.get('site_label_rows'))))
        batches.append({'batch': b, 'rows': len(rr), **dict(totals), 'saved_aggregate': str((directory / aggname).relative_to(ROOT))})
        if b.startswith('b'):
            check(b + ':CISI1_entries', sum(c['last'] - c['first'] + 1 for c in catalogue if c['batch'] == b), agg['cisi1']['catalogue_object_slots'])
            check(b + ':IM77_selected', sum((r.get('mahadevan1977') or {}).get('value', 0) or 0 for r in rr), agg['mahadevan1977']['selected_inscribed_objects'])
        if b.startswith('c'):
            check(b + ':CISI1_entries', sum(c['last'] - c['first'] + 1 for c in catalogue if c['batch'] == b), agg['cisi1_catalogue_objects'])
            check(b + ':IM77_selected', sum((r.get('mahadevan_1977_or_icit_count') or {}).get('main_corpus_objects', 0) for r in rr), agg['mahadevan1977_main_objects_on_seven_sites'])
        if b.startswith('d'):
            check(b + ':selected_related_minima', sum(c['count'] for r in rr for c in r['published_counts'] if c.get('include_in_indus_minimum')), agg['selected_indus_related_object_minimum_sum'])
        # Record suspected snippet titles without reproducing the title or body.
        for source_path in directory.rglob('*sources.json'):
            data = read(source_path)
            ss = data if isinstance(data, list) else data.get('sources', [])
            for s in ss:
                title = s.get('title', '')
                if not isinstance(title, str):
                    continue
                removed = title.startswith('Search-result text removed by the coordinator')
                rules = [rule for rule, matches in [('length_over_150', len(title) > 150),
                         ('mid_sentence_start', bool(re.match(r'^[a-z]', title))),
                         ('multiple_sentences', bool(re.search(r'[.!?]\s+[A-Z].*[.!?]', title)))] if matches]
                if rules and not removed:
                    snippet_flags.append({'file': source_path.relative_to(ROOT).as_posix(), 'record_id': s.get('id', s.get('source_id')),
                        'title_characters': len(title), 'title_words': len(title.split()), 'rules': rules,
                        'review': 'Screening candidate only; bibliographic titles can trigger. No title payload copied.'})

    bysite = defaultdict(list)
    for row in lipi:
        bysite[canonical(row['site'])].append(row)
    for site, prefix, last, pages in [('Rehman Dheri', 'Rhd', 270, 'CISI2 pp.352–378,416'),
                                     ('Sarai Khola', 'Skh', 10, 'CISI2 pp.410–411')]:
        catalogue.append({'site': site, 'batch': BATCHES[0], 'edition': 'CISI2', 'prefix': prefix,
                          'first': 1, 'last': last, 'pages': pages, 'input_pointer': groups[site][0]['pointer']})
    # Exact base-key comparisons within inspected catalogue runs.
    unique_catalogue = {}
    for c in catalogue:
        key = (c['site'], c['edition'], c['prefix'].casefold(), c['first'], c['last'])
        unique_catalogue.setdefault(key, c)
    catalogue = list(unique_catalogue.values())
    raw_missing = []
    for c in catalogue:
        keys = {cisi_id(r['source_cisi']) for r in bysite[c['site']]}
        # CISI 2 republishes CISI 1's Amri 1-2 as Ai 1-2; preserve the
        # catalogue's printed prefix while comparing its attested alias.
        key_prefix = 'Ai' if c['site'] == 'Amri' and c['edition'] == 'CISI1' else c['prefix']
        c['matching_prefix'] = key_prefix
        c['prefix_basis'] = 'CISI2 pp.389-390; Ai1-2 refer to CISI1 Amri1-2' if key_prefix != c['prefix'] else 'printed catalogue prefix'
        expected_keys = {(key_prefix.casefold(), n) for n in range(c['first'], c['last'] + 1)}
        c['printed_number_slots'] = len(expected_keys)
        exclusions = [x for x in corrections['catalogue_exclusions'] if x['site'] == c['site'] and x['edition'] == c['edition'] and x['prefix'] == c['prefix'] and c['first'] <= x['number'] <= c['last']]
        c['exclusions'] = exclusions
        expected_keys -= {(key_prefix.casefold(), x['number']) for x in exclusions}
        present = keys & expected_keys
        missing = expected_keys - keys
        c.update(catalogue_entries=len(expected_keys), local_matching_entries=len(present), local_absent_entry_keys=len(missing),
                 fraction=len(present) / len(expected_keys), scope='Catalogue base-key coverage; mixed inscription classes; no physical-object recall estimate')
        raw_missing.append({'site': c['site'], 'edition': c['edition'], 'prefix': c['prefix'],
                            'absent_base_identifiers': sorted(f'{p}-{n}' for p, n in missing)})
    csvout(out / 'catalogue-coverage.csv', catalogue)
    write(raw / 'absent-catalogue-identifiers.json', raw_missing)

    # Classify absent keys by the reviewed catalogue section, not by a
    # presumed linguistic status of each marked object.
    review_csv = ROOT / corrections['section_split_source']
    PINS[corrections['section_split_source']] = {'bytes': review_csv.stat().st_size, 'sha256': sha256(review_csv.read_bytes()).hexdigest()}
    reviewed_sections = list(csv.DictReader(review_csv.open(encoding='utf-8-sig')))
    section_rows = []
    def graffiti_section(site, n):
        return (site == 'Lothal' and n >= 221) or (site == 'Kalibangan' and 90 <= n <= 120) or (site == 'Banawali' and n >= 24) or (site == 'Daimabad' and n >= 6) or site in ['Rangpur', 'Chandigarh'] or (site == 'Tarkhanewala Dera' and n >= 2)
    for r in reviewed_sections:
        c = next(x for x in catalogue if x['site'] == r['site'] and x['edition'] == 'CISI1-1987')
        keys = {cisi_id(x['source_cisi']) for x in bysite[c['site']]}
        absent = {(c['matching_prefix'].casefold(), n) for n in range(c['first'], c['last'] + 1)} - keys
        graffiti = sum(graffiti_section(c['site'], n) for _, n in absent)
        other = len(absent) - graffiti
        check('review_section:' + c['site'] + ':absent', len(absent), int(r['local_absent']))
        check('review_section:' + c['site'] + ':graffiti', graffiti, int(r['absent_in_graffiti_or_pottery_sections']))
        check('review_section:' + c['site'] + ':other', other, int(r['absent_in_seal_impression_tablet_sections']))
        section_rows.append({'site': c['site'], 'range': r['range'], 'entries': c['catalogue_entries'], 'matching_keys': c['local_matching_entries'],
                             'absent_keys': len(absent), 'absent_graffiti_or_pottery_sections': graffiti,
                             'absent_seal_impression_tablet_other_sections': other, 'printed_pages': r['printed_pages_read'],
                             'classification_basis': 'Reviewed printed section boundaries; Banawali B24-29 is a mixed tablets/graffiti section; eligibility remains object-specific',
                             'evidence': corrections['section_split_source']})
    csvout(out / 'catalogue-section-split.csv', section_rows)

    # Source-level joins connect registers without treating a shared publication as a new object.
    pub = read(BASE / 'sites-and-publications/publication-register.json')['publications']
    datasets = read(BASE / 'collections-and-datasets/dataset-register.json')['datasets']
    collections = read(BASE / 'collections-and-datasets/collection-register.json')['collections']
    landscape = read(ROOT / 'experiments/2026-10-02-dataset-landscape/landscape.json')
    publication_links = []
    source_links = []
    source_summaries = []
    for b in BATCHES:
        for s in rows(read(BASE / 'sites-deep' / b / 'sources.json')):
            if isinstance(s, dict):
                source_summaries.append((b, s))
    for p in pub:
        title = p.get('title', '')
        linked = [s for s in groups if norm(s) and norm(s) in norm(title)]
        publication_links.append({'publication_id': p['id'], 'site_links': linked,
                                  'status': 'candidate_name_link' if linked else 'source_scope_only',
                                  'url': p['url'], 'input_pointer': 'sites-and-publications/publication-register.json#' + p['id']})
        for b, s in source_summaries:
            exact_url = bool(s.get('url')) and s['url'].rstrip('/') == p['url'].rstrip('/')
            title_year = norm(s.get('title', '')) == norm(p['title']) and s.get('year') == p.get('year')
            if exact_url or title_year:
                source_links.append({'publication_id': p['id'], 'batch_source_id': b + ':' + str(s.get('id')),
                    'status': 'confirmed_same_source_URL' if exact_url else 'candidate_title_year_link', 'object_join': False})
    write(out / 'register-joins.json', {'publication_site_links': publication_links,
          'site_aliases': [{'canonical': s, 'labels': [name(x['row']) for x in v], 'row_pointers': [x['pointer'] for x in v],
                            'status': 'source_attested_alias' if s == 'Nuhato' else 'shared_name_or_recorded_alias'} for s, v in groups.items() if len(v) > 1],
          'publication_batch_source_links': source_links,
          'dataset_source_links': [{'dataset': d['name'], 'source_ids': d.get('source_ids', []), 'object_join': False} for d in datasets],
          'collection_source_links': [{'institution': c['institution'], 'source_ids': c.get('source_ids', []), 'object_join': False} for c in collections]})

    museum_raw = ROOT / 'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07'
    museum = read(museum_raw / 'focused-records.json')
    paired = read(museum_raw / 'paired-comparisons.json')
    candidates = read(museum_raw / 'unconfirmed-join-candidates.json')
    concordance = read(museum_raw / 'cisi1-concordance-transcription.json')
    saved_summary = read(BASE / 'collections-and-datasets/focused-summary.json')
    corpus_by_id = {r['record_id']: r for r in lipi}
    method_counts = Counter()
    confirmed = []
    for p in paired:
        j = p['join']
        face_ids = [r['record_id'] for r in p['corpus_faces']]
        faces = [corpus_by_id[x] for x in face_ids]
        check('museum:' + p['key'] + ':source_faces', faces, p['corpus_faces'])
        check('museum:' + p['key'] + ':family', sorted({r['object_family_id'] for r in faces}), [j['object_family_id']])
        if j['join_method'] == 'published_CISI_concordance':
            hit = [c for c in concordance if norm(c['museum_accession']) == norm(j['museum_accession']) and c['cisi'] in {r['source_cisi'] for r in faces}]
            check('museum:' + p['key'] + ':concordance', bool(hit), True)
        method_counts[j['join_method']] += 1
        confirmed.append({'key': p['key'], 'museum_url': j['museum_url'], 'method': j['join_method'],
                          'family': j['object_family_id'], 'face_ids': face_ids, 'source_evidence': j['join_evidence'],
                          'status': 'reported_confirmed_identifier_join; numerical_consistency_rechecked'})
    joins = {'museum_original_records': len(museum), 'confirmed_identifier_joins': len(paired),
             'unconfirmed_records': len(candidates), 'confirmed_families': len({r['family'] for r in confirmed}),
             'confirmed_faces': len({x for r in confirmed for x in r['face_ids']}), 'methods': dict(method_counts),
             'by_institution': dict(Counter(r['institution'] for r in museum)),
             'comparisons': {k: dict(Counter(p['comparison'][k] for p in paired)) for k in ['site_comparison', 'material_comparison', 'dimensions_comparison', 'inscription_comparison']},
             'status': 'Exploratory; inherited source joins checked against pinned records, not all primary pages independently re-reviewed'}
    for key, previous in [('museum_original_records', 'inspected_original_records'), ('confirmed_identifier_joins', 'confirmed_join_records'),
                          ('unconfirmed_records', 'unconfirmed_join_records'), ('confirmed_families', 'confirmed_distinct_corpus_families'), ('confirmed_faces', 'confirmed_corpus_faces')]:
        check('museum_summary:' + key, joins[key], saved_summary[previous])
    check('museum_partition', len(paired) + len(candidates), len(museum))
    check('museum_methods', dict(method_counts), saved_summary['join_methods'])
    supplement = read(ROOT / corrections['museum_supplement'])
    new_pairs = []
    for s in supplement:
        selected = [r for r in museum if r['institution'] == s['institution'] and r['accession'] == s['accession']]
        check('additional_museum:' + s['record_id'] + ':unique_record', len(selected), 1)
        m = selected[0]
        original = ROOT / s['raw_record']
        digest = sha256(original.read_bytes()).hexdigest()
        PINS[original.relative_to(ROOT).as_posix()] = {'bytes': original.stat().st_size, 'sha256': digest}
        check('additional_museum:' + s['record_id'] + ':original_hash', digest, s['raw_sha256'])
        hits = [r for r in lipi if r['source_cisi'] == s['source_cisi']]
        id_hits = [r for r in lipi if norm(r['metadata'].get('excavation-idno')) == norm(s['excavation_idno'])]
        check('additional_museum:' + s['record_id'] + ':unique_cisi_family', len({r['object_family_id'] for r in hits}), 1)
        check('additional_museum:' + s['record_id'] + ':same_id_family', sorted({r['object_family_id'] for r in hits}), sorted({r['object_family_id'] for r in id_hits}))
        if s['method'].startswith('normalized_full_excavation'):
            key = m['accession'].removesuffix('-1145') if m['accession'] == 'BNL-1-170-84-1145' else m['accession']
            check('additional_museum:' + s['record_id'] + ':full_string', norm(key), norm(s['excavation_idno']))
        family = hits[0]['object_family_id']
        key = m['institution'] + '|' + m['accession']
        check('additional_museum:' + s['record_id'] + ':unused_record', key in {r['key'] for r in confirmed}, False)
        check('additional_museum:' + s['record_id'] + ':unused_family', family in {r['family'] for r in confirmed}, False)
        faces = [r for r in lipi if r['object_family_id'] == family]
        confirmed.append({'key': key, 'museum_url': m['url'], 'method': s['method'], 'family': family,
                          'face_ids': [r['record_id'] for r in faces], 'source_evidence': s['source_evidence'], 'status': s['review_status']})
        method_counts[s['method']] += 1
        new_pairs.append({'museum': m, 'corpus_faces': faces, 'join_evidence': s['source_evidence'], 'method': s['method'], 'field_comparison_status': 'not adjudicated'})
    joined_keys = {r['key'] for r in confirmed}
    candidates = [r for r in candidates if r['institution'] + '|' + r['accession'] not in joined_keys]
    def candidate_status(r):
        if r['attempts']:
            return 'failed_string_match'
        return 'untried_usable_key' if r['usable_identifier'] else 'no_usable_key_in_original_pass'
    for r in candidates:
        r['query_disposition'] = candidate_status(r)
    joins.update(confirmed_identifier_joins=len(confirmed), unconfirmed_records=len(candidates),
                 confirmed_families=len({r['family'] for r in confirmed}),
                 confirmed_faces=len({x for r in confirmed for x in r['face_ids']}), methods=dict(method_counts),
                 previous_confirmed_lower_bound=len(paired), additional_checked_joins=len(supplement),
                 comparison_denominator=len(paired), additional_field_comparisons='Seven new joins have not received the full paired-field adjudication',
                 unresolved_query_dispositions=dict(Counter(r['query_disposition'] for r in candidates)),
                 join_count_is_lower_bound=True)
    check('expanded_museum_partition', len(confirmed) + len(candidates), len(museum))
    check('expanded_museum_unique_records', len(joined_keys), len(confirmed))
    check('expanded_museum_unique_families', len({r['family'] for r in confirmed}), len(confirmed))
    write(raw / 'confirmed-object-joins.json', confirmed)
    write(raw / 'candidate-object-joins.json', candidates)
    write(raw / 'additional-join-pairs.json', new_pairs)
    write(out / 'join-summary.json', joins)

    field_rows = []
    def field(index, unit, total, key, count, basis, source, measurement='measured_export_presence'):
        field_rows.append({'index': index, 'unit': unit, 'denominator': total, 'field': key, 'present': count,
            'missing': total - count if total is not None and count is not None and measurement != 'structural_schema_absence' else None,
            'percent': round(100 * count / total, 4) if total and count is not None and measurement != 'structural_schema_absence' else None,
            'measurement': measurement, 'basis': basis, 'evidence': source})
    lp = 'data/normalized/lipi_observed_faces.jsonl; metadata fields named in basis; input-manifest.json'
    n = len(lipi)
    definitions = {
        'named_site': (lambda r: populated(r['site']), 'site; Unknown is missing'),
        'findspot': (lambda r: populated(r['metadata'].get('room-grid')), 'room-grid; spatial-unit proxy, not an independently reviewed findspot'),
        'spatial_context_any': (lambda r: any(populated(r['metadata'].get(k)) for k in ['area-section', 'block-house', 'room-grid']), 'any area-section, block-house or room-grid; broad spatial context presence'),
        'stratum_or_phase': (lambda r: any(populated(r['metadata'].get(k)) for k in ['period', 'phase']), 'period or phase; generic/site-specific labels retained'),
        'depth': (lambda r: populated(r['metadata'].get('depth')), 'depth; dash-space placeholder normalized to missing'),
        'date_or_period_label': (lambda r: populated(r['metadata'].get('time')), 'time; includes source cultural-period codes'),
        'calendar_date_assertion': (lambda r: calendar_label(r['metadata'].get('time')), 'time with a numeral and explicit era/century/millennium; calendar attribution, not an independent dated sample'),
        'absolute_date': (lambda r: False, 'No dated-sample identifier, measurement method or calibrated interval linkage in this derivative'),
        'dimensions': (lambda r: any(number(r['metadata'].get(k)) for k in ['horizontal(mm)', 'vertical(mm)', 'thickness(mm)']), 'at least one strictly positive numeric millimetre dimension'),
        'dimensions_all_three': (lambda r: all(number(r['metadata'].get(k)) for k in ['horizontal(mm)', 'vertical(mm)', 'thickness(mm)']), 'all three strictly positive numeric millimetre dimensions'),
        'material': (lambda r: populated(r['metadata'].get('material')), 'metadata.material; source term presence'),
        'photographs': (lambda r: False, 'No image URL/view/asset linkage in normalized face records; parent photographs not censused here'),
        'registration_numbers': (lambda r: populated(r['metadata'].get('excavation-idno')), 'excavation-idno; museum accession namespace not independently separated'),
        'CISI_identifier': (lambda r: populated(r['source_cisi']), 'source_cisi; raw identifier strings retained'),
        'licence': (lambda r: False, 'No per-row asset/source rights link in normalized derivative; Lipi bulk terms unresolved')}
    for key, (rule, basis) in definitions.items():
        structural = key in ['absolute_date', 'photographs', 'licence']
        field('Lipi pinned derivative', 'face records', n, key, sum(rule(r) for r in lipi), basis, lp,
              'structural_schema_absence' if structural else 'measured_export_presence')
    for key, (rule, _) in definitions.items():
        if key in ['named_site', 'findspot', 'stratum_or_phase', 'absolute_date', 'dimensions', 'material', 'photographs', 'registration_numbers', 'licence']:
            count = sum(populated(r['site']) for r in mayig) if key == 'named_site' else 0
            basis = 'site' if key == 'named_site' else 'Field absent from this normalized annotation; upstream assets and MIT notice have separate scope'
            field('Mayig pinned derivative', 'face records', len(mayig), key, count, basis, 'data/normalized/mayig_faces.jsonl',
                  'measured_export_presence' if key == 'named_site' else 'structural_schema_absence')
    field('Mayig pinned derivative', 'face records', len(mayig), 'CISI_identifier', len(mayig), 'object_family_id is a CISI key, not a museum/excavation registration', 'data/normalized/mayig_faces.jsonl')
    field('Mayig pinned derivative', 'face records', len(mayig), 'calendar_date_assertion', 0, 'No calendar-date field in normalized annotation', 'data/normalized/mayig_faces.jsonl', 'structural_schema_absence')
    field_path = BASE / 'collections-and-datasets/focused-field-counts.csv'
    PINS[field_path.relative_to(ROOT).as_posix()] = {'bytes': field_path.stat().st_size, 'sha256': sha256(field_path.read_bytes()).hexdigest()}
    fr = list(csv.DictReader(field_path.open(encoding='utf-8-sig')))
    for s in fr:
        subset = [r for r in museum if r['institution'] == s['source']]
        check('museum_field_denominator:' + s['source'], len(subset), int(s['records_inspected']))
        direct = {'accession_number': 'accession', 'findspot': 'site', 'date': 'date', 'dimensions': 'dimensions', 'material': 'material', 'bibliography': 'bibliography'}
        for old, raw_key in direct.items():
            check('museum_field:' + s['source'] + ':' + old, sum(bool(r[raw_key]) for r in subset), int(s[old]))
        for old, rule in [('photographs', lambda r: r['image_slots'] is not None and r['image_slots'] > 0), ('multiple_views', lambda r: r['image_slots'] is not None and r['image_slots'] > 1)]:
            check('museum_field:' + s['source'] + ':' + old, sum(rule(r) for r in subset), int(s[old]))
        for old, key in [('named_site', 'named_site'), ('excavation_number', 'registration_numbers'), ('date', 'date_or_period_label'), ('dimensions', 'dimensions'), ('material', 'material'), ('photographs', 'photographs'), ('bibliography', 'bibliography')]:
            basis = 'Saved field numerator independently recomputed from original records' if old not in ['named_site', 'excavation_number'] else 'Inherited named-site or source-assisted excavation-key rule; denominator rechecked'
            if old == 'photographs':
                basis += '; image slots, not inspected photographs; BM six records unmeasured'
            unknown_images = old == 'photographs' and int(s['image_count_unmeasured']) == len(subset)
            field(s['source'], 'inspected museum originals', len(subset), key, None if unknown_images else int(s[old]), basis,
                  field_path.relative_to(ROOT).as_posix(), 'unmeasured' if unknown_images else 'inherited_rule_not_recomputed' if old in ['named_site', 'excavation_number'] else 'measured_export_presence')
        field(s['source'], 'inspected museum originals', len(subset), 'site_label_raw_presence', sum(bool(r['site']) for r in subset), 'Nonempty raw site string; no named-site adjudication', 'focused-records.json; input-manifest.json')
        field(s['source'], 'inspected museum originals', len(subset), 'excavation_raw_presence', sum(bool(r['excavation_raw']) for r in subset), 'Nonempty excavation_raw; source-assisted concordance keys have separate scope', 'focused-records.json; input-manifest.json')
        field(s['source'], 'inspected museum originals', len(subset), 'accession_number', int(s['accession_number']), 'Museum accession presence', field_path.relative_to(ROOT).as_posix())
        field(s['source'], 'inspected museum originals', len(subset), 'calendar_date_assertion', sum(calendar_label(r['date']) for r in subset),
              'Numeral plus explicit era/century/millennium or French negative-year range; includes broad catalogue/style attributions, not direct object dates', 'focused-records.json; input-manifest.json')
        for key in ['findspot', 'stratum_or_phase', 'absolute_date', 'licence']:
            field(s['source'], 'inspected museum originals', len(subset), key, None, 'Exact excavation context, independent absolute dating and item-level rights completeness not adjudicated', field_path.relative_to(ROOT).as_posix(), 'unmeasured')
    for index in ['ICIT historical 2023', 'CISI editions', 'IM77 web application']:
        for key in ['findspot', 'stratum_or_phase', 'absolute_date', 'dimensions', 'material', 'photographs', 'registration_numbers', 'licence']:
            field(index, 'objects, denominator unavailable for field audit', None, key, None, 'Published features/edition examples establish availability only; no full object-field census', 'collections-and-datasets/dataset-register.json; sources.json', 'unmeasured')
    csvout(out / 'field-completeness.csv', field_rows)

    coverage = []
    for site, entries in groups.items():
        local = bysite[site]
        # Region attribution follows batch A for Pakistan/Afghanistan overlaps, then B/C/D.
        chosen = sorted(entries, key=lambda x: BATCHES.index(x['batch']))[0]
        region = chosen['batch']
        m77 = None
        for e in entries:
            r = e['row']
            if e['batch'].startswith('a'):
                obs = [a['value'] for a in assertions if a['batch'] == e['batch'] and a['site'] == site and a['object_class'] == 'all classes' and a['date'] == 1977]
                if obs:
                    m77 = obs[0]
            elif e['batch'].startswith('b'):
                v = (r.get('mahadevan1977') or {}).get('value')
                if isinstance(v, int):
                    m77 = v
            elif e['batch'].startswith('c'):
                v = (r.get('mahadevan_1977_or_icit_count') or {}).get('main_corpus_objects')
                if isinstance(v, int):
                    m77 = v
        inherited_m77 = m77
        m77 = corrections['im77_site_table'].get(site)
        m77_status = 'printed_IM77_p6_count' if m77 is not None else 'not_listed_in_IM77_p6_site_table'
        cat = [c for c in catalogue if c['site'] == site]
        coverage.append({'site': site, 'assigned_region': region, 'batch_mentions': [e['batch'] for e in entries],
            'local_faces': len(local), 'local_families': len({r['object_family_id'] for r in local}),
            'local_cisi_identifiers': len({r['source_cisi'] for r in local if populated(r['source_cisi'])}),
            'IM77_main_selected_objects': m77, 'IM77_count_status': m77_status,
            'IM77_inherited_count': inherited_m77, 'IM77_evidence': corrections['im77_locator'], 'catalogue_runs': cat,
            'published_count_assertions': [a for a in assertions if a['site'] == site],
            'ICIT_object_count': None, 'worldwide_missing_objects': None,
            'coverage_basis': 'Source/version-specific count assertions; no common worldwide object denominator',
            'evidence': [e['pointer'] for e in entries]})
    region_rows = []
    for b in BATCHES:
        rr = [r for r in coverage if r['assigned_region'] == b]
        cat = [c for r in rr for c in r['catalogue_runs'] if c['edition'] in ['CISI1-1987', 'CISI1']]
        region_rows.append({'region': b, 'site_or_provenance_entities': len(rr), 'local_faces': sum(r['local_faces'] for r in rr),
            'local_families': sum(r['local_families'] for r in rr), 'IM77_main_selected_objects_available': sum(r['IM77_main_selected_objects'] or 0 for r in rr),
            'IM77_sites_with_count': sum(r['IM77_main_selected_objects'] is not None for r in rr),
            'IM77_count_status': 'sum_of_named_sites_in_frame; unknown-provenance entries excluded',
            'CISI1_catalogue_entries': sum(c['catalogue_entries'] for c in cat) if cat else None, 'CISI1_matching_local_keys': sum(c['local_matching_entries'] for c in cat) if cat else None,
            'CISI1_absent_local_keys': sum(c['local_absent_entry_keys'] for c in cat) if cat else None,
            'CISI1_count_status': 'selected_source_ranges' if cat else 'not_applicable_to_abroad_frame', 'worldwide_missing_objects': None})
    check('corrected_IM77_north', next(r['IM77_main_selected_objects_available'] for r in region_rows if r['region'].startswith('c')), 117)
    check('IM77_site_table_plus_unknown', sum(corrections['im77_site_table'].values()) + corrections['im77_unknown_south_asian'] + corrections['im77_unknown_west_asian'], 2906)
    represented = {r['site'] for r in coverage}
    excluded_local = [{'site': r['site'], 'faces': r['faces'], 'families': r['object_families']} for r in coord if canonical(r['site']) not in represented]
    cisi1 = [c for c in catalogue if c['edition'] == 'CISI1-1987']
    # CISI1 in A has less consistently normalized labels; headline range comparison uses the checked B/C sets.
    bc = [c for c in cisi1 if c['batch'][0] in ['b', 'c']]
    summary = {'raw_batch_rows': sum(b['rows'] for b in batches), 'site_or_provenance_entities_after_aliases': len(coverage),
               'summed_batch_faces_before_overlap_removal': sum(b['faces'] for b in batches),
               'represented_local_faces': sum(r['local_faces'] for r in coverage),
               'represented_local_families': sum(r['local_families'] for r in coverage),
               'excluded_local_labels': excluded_local,
               'local_all_faces': len(lipi), 'local_all_provisional_families': len({r['object_family_id'] for r in lipi}),
               'CISI1_BC_entries': sum(c['catalogue_entries'] for c in bc), 'CISI1_BC_matching_keys': sum(c['local_matching_entries'] for c in bc),
               'CISI1_BC_absent_keys': sum(c['local_absent_entry_keys'] for c in bc),
               'CISI1_BC_absent_graffiti_or_pottery_sections': sum(r['absent_graffiti_or_pottery_sections'] for r in section_rows),
               'CISI1_BC_absent_seal_impression_tablet_other_sections': sum(r['absent_seal_impression_tablet_other_sections'] for r in section_rows),
               'worldwide_missing_objects': None, 'worldwide_coverage_percent': None}
    frame_omissions = []
    for gap in corrections['frame_omissions']:
        check('frame_omission:' + gap['site'] + ':no_row', canonical(gap['site']) in groups, False)
        check('frame_omission:' + gap['site'] + ':no_local_label', any(norm(x['site']) == norm(gap['site']) for x in lipi), False)
        frame_omissions.append(dict(gap))
    result = {'status': 'Exploratory', 'computation_status': 'Verified computation' if all(c['passed'] for c in checks) else 'Failed',
              'as_of': '2026-10-07', 'summary': summary, 'batch_recomputation': batches, 'regions': region_rows, 'sites': coverage,
              'frame_omissions': frame_omissions, 'input_state': corrections['post_trim_note'],
              'definitions': {'face': 'One normalized record for a source-defined object side or text-bearing view; not an independently excavated object',
                 'local_corpus': 'Pinned Lipi derivative with 5680 face rows, whose internal numbering follows the ICIT-derived export; relation to current ICIT inventory unverified',
                 'provisional_family': 'Local object_family_id groups face rows; physical identity has not been adjudicated across all families',
                 'absent_key': 'A catalogue base identifier has no exact or recorded source-attested alias match among the local keys; object absence remains unresolved'},
              'index_counts': [{'index': s['id'], 'counts': s.get('counts'), 'basis': s.get('count_basis', s.get('observations')), 'input': '2026-10-02-dataset-landscape/landscape.json'} for s in landscape['sources'] if s['id'] in ['ICIT', 'MAYIG', 'LIPI', 'IM77-WEB', 'CISI']]}
    write(out / 'coverage.json', result)
    csvout(out / 'coverage.csv', [{k: r[k] for k in ['site', 'assigned_region', 'local_faces', 'local_families', 'local_cisi_identifiers', 'IM77_main_selected_objects', 'IM77_count_status', 'IM77_inherited_count', 'catalogue_runs', 'published_count_assertions', 'ICIT_object_count', 'worldwide_missing_objects', 'evidence']} for r in coverage])
    csvout(out / 'region-coverage.csv', region_rows)
    write(out / 'source-title-audit.json', {'rule': 'title >150 characters, lowercase mid-sentence start, or multiple sentences; coordinator removal markers excluded; candidates require manual review', 'input_state': corrections['post_trim_note'], 'flags': snippet_flags,
          'affected_files': dict(Counter(r['file'] for r in snippet_flags)), 'copied_title_payload': False})
    write(out / 'checks.json', {'status': 'Verified computation' if all(c['passed'] for c in checks) else 'Failed', 'checks_count': len(checks),
                              'failed': [c for c in checks if not c['passed']],
                              # Source rows never enter tracked checks.
                              'checks': [{k: v for k, v in c.items() if k not in ['actual', 'expected']} if ':source_faces' in c['check'] else c for c in checks]})
    write(out / 'input-manifest.json', PINS)
    print(json.dumps({'summary': summary, 'batches': batches, 'checks': len(checks), 'failed': [c for c in checks if not c['passed'] and ':source_faces' not in c['check']], 'title_flags': len(snippet_flags)}, ensure_ascii=False, indent=2))
    if not all(c['passed'] for c in checks):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
