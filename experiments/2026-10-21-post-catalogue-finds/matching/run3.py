"""Merge identity rows, propose joins, and count the eligible rows."""
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from identity_io import (ROOT, PACKAGE, OUT, LOCAL, CORPUS, TOP, META, sha,
                         read_csv, write_csv, write_json, corpus_rows,
                         projected_json, compact, normalise, id_rule, usable, clean)

PARTS = ('N', 'G', 'D', 'P', 'E', 'F')
EXTRA = ('provisional_row_id', 'cisi_in_baseline', 'local_match',
         'local_family_ids', 'match_basis', 'match_evidence')
TYPE_MAP = {'seal': {'SEAL'}, 'sealing': {'TAG'}, 'tag': {'TAG'},
            'tablet': {'TAB'}, 'inscribed-pottery': {'POT'},
            'inscribed-tool': {'IMPL', 'MISC'}, 'other': {'IMPL', 'MISC'},
            'uncertain': {'IMPL', 'MISC'}}
INPUTS = set()


def input_csv(path):
    INPUTS.add(path)
    return read_csv(path)


def site_setup():
    _, seeds = input_csv(PACKAGE / 'selection/sites-seed.csv')
    sites = {r['site']: dict(r) for r in seeds}
    notes, logs = [], []
    for part in PARTS:
        _, part_notes = input_csv(PACKAGE / f'extraction/{part}/site-notes-{part}.csv')
        _, part_logs = input_csv(PACKAGE / f'extraction/{part}/merge-log-{part}.csv')
        notes.extend(dict(r, part=part) for r in part_notes)
        logs.extend(dict(r, part=part) for r in part_logs)
        for row in part_notes:
            if row['site_code'] == 'new':
                continue  # This is a regional summary, without a named site.
            if row['site'] not in sites:
                sites[row['site']] = {k: row.get(k, '') for k in
                                      ('site', 'site_code', 'aliases', 'cisi_prefix')}
    ordered = list(sites)
    aliases = {}
    for site, row in sites.items():
        for alias in [site, *row.get('aliases', '').split('|')]:
            if alias:
                key = compact(alias)
                assert key not in aliases or aliases[key] == site
                aliases[key] = site
    return sites, ordered, aliases, notes, logs


def prefixes_for(site, sites):
    codes = {'RGR', 'DLV', 'DHR', 'FRM', 'KNM', 'KMR', 'SKP', 'BHR', 'KRP',
             'BSR', 'HLS', 'SKTD', 'TKWD', 'DLP', 'RPR', 'BNL', 'DHL'}
    row = sites[site]
    codes |= {compact(row.get('site_code', '')), compact(row.get('cisi_prefix', '')),
              compact(site)}
    return codes - {''}


def source_register():
    fields = ('source_id', 'title', 'authors_or_editors', 'publication_year',
              'volume_year', 'kind', 'venue', 'volume_issue_pages', 'identifier',
              'url', 'local_path', 'file_name', 'bytes', 'sha256', 'pdf_pages',
              'text_basis', 'rights_notice_observed', 'status', 'register_inputs')
    records, origins, variants = {}, defaultdict(set), []

    def add(raw, origin):
        row = {k: str(raw.get(k, '') or '') for k in fields}
        sid = row['source_id']
        if not sid:
            return
        origins[sid].add(origin)
        if sid not in records:
            records[sid] = row
        else:
            for key, value in row.items():
                if value and key != 'register_inputs':
                    old = records[sid].get(key, '')
                    if old and old != value:
                        variants.append({'source_id': sid, 'field': key,
                                         'earlier': clean(old), 'later': clean(value),
                                         'later_input': origin})
                    records[sid][key] = value

    paths = [PACKAGE / 'acquisition/source-register-1a.csv',
             PACKAGE / 'acquisition-web/source-candidates-1b.csv']
    for path in paths:
        for row in input_csv(path)[1]:
            row = dict(row)
            row['authors_or_editors'] = row.get('authors_or_editors') or row.get('authors', '')
            row['volume_year'] = row.get('year_or_volume') or row.get('year', '')
            if row.get('year'):
                row['publication_year'] = row['year']
            row['status'] = row.get('status') or row.get('access', '')
            add(row, path.relative_to(ROOT).as_posix())
    path = PACKAGE / 'acquisition-coordinator/manifest-proposals-coordinator.json'
    INPUTS.add(path)
    for row in json.loads(path.read_text(encoding='utf-8'))['sources']:
        fetch = row.get('fetch', {})
        count = re.search(r'\b(\d+)(?:-page| pages)\b', row.get('notes', ''))
        add({'source_id': row['id'], 'title': row['title'], 'kind': row.get('kind', ''),
             'identifier': '|'.join(row.get('identifiers', [])),
             'url': fetch.get('url', ''), 'file_name': fetch.get('filename', ''),
             'bytes': fetch.get('bytes', ''), 'sha256': fetch.get('sha256', ''),
             'local_path': '|'.join(row.get('local_paths', [])),
             'pdf_pages': count[1] if count else '',
             'rights_notice_observed': row.get('rights', {}).get('status', ''),
             'status': 'cover-only' if row.get('kind') == 'excavation-report-cover' else row.get('status', '')},
            path.relative_to(ROOT).as_posix())
    for path in sorted(PACKAGE.glob('extraction/*/source-register*.csv')):
        for row in input_csv(path)[1]:
            row = dict(row)
            row['rights_notice_observed'] = (row.get('rights_notice_observed') or
                                            row.get('rights_status') or row.get('rights', ''))
            # The coordinator's asset status is more specific than a supplement label.
            if row['source_id'] in records:
                row['status'] = records[row['source_id']]['status']
            add(row, path.relative_to(ROOT).as_posix())
    for sid, row in records.items():
        row['register_inputs'] = '|'.join(sorted(origins[sid]))
    sanitized = []
    for sid, row in records.items():
        for key, value in row.items():
            filtered = clean(value)
            if filtered != value:
                sanitized.append({'source_id': sid, 'field': key, 'action': 'restricted token withheld'})
                row[key] = filtered
    write_csv(OUT / 'source-register.csv', fields, [records[k] for k in sorted(records)])
    write_csv(OUT / 'source-register-variants.csv',
              ['source_id', 'field', 'earlier', 'later', 'later_input'], variants)
    return records, sanitized


def merged_rows(sites, ordered):
    columns, rows = [], []
    for part in PARTS:
        path = PACKAGE / f'extraction/{part}/objects-{part}.csv'
        header, extracted = input_csv(path)
        columns.extend(k for k in header if k not in columns)
        for i, row in enumerate(extracted):
            row = dict(row, provisional_row_id=row['row_id'], _part=part, _index=i)
            rows.append(row)
            if row['site'] not in sites:
                sites[row['site']] = {'site': row['site'], 'site_code': row['site_code']}
                ordered.append(row['site'])
    rows.sort(key=lambda r: (ordered.index(r['site']), r['primary_publication'],
                             PARTS.index(r['_part']), r['_index']))
    counters = Counter()
    identifiers = {}
    for row in rows:
        counters[row['site']] += 1
        row['row_id'] = f"PCF-{sites[row['site']]['site_code']}-{counters[row['site']]:03d}"
        identifiers[(row['_part'], row['provisional_row_id'])] = row['row_id']
        for key in EXTRA[1:]:
            row[key] = ''
    for row in rows:
        old = row.get('possible_duplicate_of', '')
        if old:
            row['possible_duplicate_of'] = re.sub(
                r'X[A-Z]-[A-Z]+-\d+',
                lambda m: identifiers.get((row['_part'], m[0]), m[0]), old)
    return columns + [k for k in EXTRA if k not in columns], rows


def duplicates(rows, sites):
    groups = defaultdict(list)
    pairs = set()
    for row in rows:
        for other in re.findall(r'PCF-[A-Z]+-\d+', row.get('possible_duplicate_of', '')):
            pairs.add(tuple(sorted((row['row_id'], other))))
        if usable(row['registration']):
            groups[(row['site'], normalise(row['registration'], prefixes_for(row['site'], sites)))].append(row)
    cross, within = [], []
    for (site, key), group in groups.items():
        for a, b in itertools.combinations(group, 2):
            pairs.add(tuple(sorted((a['row_id'], b['row_id']))))
            (cross if a['_part'] != b['_part'] else within).append({
                'site': site, 'row_id_a': a['row_id'], 'row_id_b': b['row_id'],
                'part_a': a['_part'], 'part_b': b['_part'],
                'provisional_id_a': a['provisional_row_id'],
                'provisional_id_b': b['provisional_row_id'],
                'registration_a': a['registration'], 'registration_b': b['registration'],
                'basis': 'site and normalised registration agree; retained as separate rows'})
    fields = ('site', 'row_id_a', 'row_id_b', 'part_a', 'part_b',
              'provisional_id_a', 'provisional_id_b', 'registration_a', 'registration_b', 'basis')
    write_csv(OUT / 'cross-part-duplicates.csv', fields, cross)
    write_csv(OUT / 'same-part-duplicates.csv', fields, within)
    return pairs, cross, within


def families(aliases):
    INPUTS.add(CORPUS)
    result = {}
    for row in corpus_rows():
        site = aliases.get(compact(row['site']))
        if site is None:
            continue
        fid = str(row['object_family_id'])
        if fid not in result:
            result[fid] = {'site': site, 'faces': []}
        assert result[fid]['site'] == site
        result[fid]['faces'].append(row)
    return result


def cisi_numbers(value):
    return {m[1].upper() + '-' + str(int(m[2]))
            for m in re.finditer(r'\b([A-Za-z]{1,5})\s*[-\u2010-\u2014]\s*(\d+)\b', value)}


def distance_one(a, b):
    if abs(len(a)-len(b)) > 1 or a == b:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    short, long = sorted((a, b), key=len)
    return any(long[:i] + long[i+1:] == short for i in range(len(long)))


def containment(rows, sites):
    prefix_site = {compact(r.get('cisi_prefix', '')): s for s, r in sites.items()
                   if r.get('cisi_prefix')}
    prefix_site.update({'SKTD': 'Surkotada', 'TKWD': 'Tarkhanewala Dera',
                        'DLP': 'Desalpar', 'HLS': 'Hulas'})
    baseline = defaultdict(list)
    for name in ('cisi1', 'cisi2'):
        path = ROOT / f'data/raw/2026-10-13-cisi-basic-data-full/assembled/{name}-basic-data.jsonl'
        INPUTS.add(path)
        with path.open(encoding='utf-8') as stream:
            for raw in stream:
                entry = projected_json(raw, {'cisi': None, 'col3_excavation': None,
                                            'parsed': {'excavation': None}, 'printed_page': None})
                code = re.match(r'[A-Za-z]+', str(entry.get('cisi', '')))
                site = prefix_site.get(code[0].upper()) if code else None
                if not site:
                    continue
                raw_cell = entry.get('col3_excavation', '') or ''
                parsed = entry.get('parsed', {}).get('excavation', [])
                if isinstance(parsed, str):
                    parsed = [parsed]
                values = []
                for item in parsed:
                    value = item.get('printed', '') if isinstance(item, dict) else item
                    if isinstance(value, str) and usable(value):
                        values.append(re.sub(r'\s*\([ot]\)\s*', '', value, flags=re.I))
                if usable(raw_cell):
                    # The final parenthetic letters are source qualifiers.
                    cell = re.sub(r'\s*\([ot]\)\s*', '', raw_cell, flags=re.I)
                    values.append(cell)
                baseline[site].append((entry['cisi'], values))
    path = ROOT / 'experiments/2026-10-13-cisi3-range-coverage/run-2026-10-13/absent-numbers.csv'
    _, absent_rows = input_csv(path)
    absent_codes = {r['prefix'].upper() + '-' + str(int(r['number'])) for r in absent_rows}
    reviews, moved = [], []
    for row in rows:
        citations = cisi_numbers(row['other_numbers'])
        hit_codes = set()
        if citations & absent_codes:
            hit_codes |= citations & absent_codes
        if row['catalogue_status'] == 'in-baseline-catalogue':
            hit_codes |= citations
        if row['baseline_volume'].strip() in {'1', '2', 'CISI 1', 'CISI 2'} and usable(row['registration']):
            prefs = prefixes_for(row['site'], sites)
            a = normalise(row['registration'], prefs)
            for cisi, values in baseline[row['site']]:
                found, near = False, set()
                for value in values:
                    if '[' in value or '?' in value or '[' in row['registration'] or '?' in row['registration']:
                        continue
                    b = normalise(value, prefs)
                    if a and a == b:
                        found = True
                    elif a and b:
                        if distance_one(a, b):
                            near.add('one-character difference')
                        if re.findall(r'\d+', a) == re.findall(r'\d+', b) and a != b:
                            near.add('same digits; different prefix')
                if found:
                    hit_codes.add(cisi)
                elif near:
                    reviews.append({'row_id': row['row_id'], 'provisional_row_id': row['provisional_row_id'],
                                    'site': row['site'], 'registration': row['registration'],
                                    'cisi': cisi, 'review_basis': '; '.join(sorted(near)),
                                    'decision': 'coordinator review pending; status unchanged by this comparison'})
        if hit_codes:
            row['cisi_in_baseline'] = '|'.join(sorted(hit_codes))
            if row['catalogue_status'] != 'in-baseline-catalogue':
                moved.append(row['row_id'])
            row['catalogue_status'] = 'in-baseline-catalogue'
    write_csv(OUT / 'containment-review.csv',
              ['row_id', 'provisional_row_id', 'site', 'registration', 'cisi', 'review_basis', 'decision'], reviews)
    return moved, reviews


def tidy(value):
    value = value.upper().replace('\u2010', '-').replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-')
    return re.sub(r'\s+', ' ', value).strip()


def roman_token(value):
    value = compact(value)
    m = re.fullmatch(r'(VIII|VII|VI|IV|V|III|II|IX|I|X)([A-C]?)', value)
    if m:
        nums = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6,
                'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
        return str(nums[m[1]]) + m[2]
    return re.sub(r'\d+', lambda m: str(int(m[0])), value)


def location_tokens(value):
    value = tidy(value)
    result = defaultdict(set)
    for m in re.finditer(r'\b(?:TR\.?|TRENCH)\s*([A-Z]{0,3}\s*\d+[A-Z]?)', value):
        result['trench'].add(roman_token(m[1]))
    for m in re.finditer(r'\b\d+\s*X\s*\d+(?:\s*X\s*\d+)?\b', value):
        result['grid'].add(compact(m[0]))
    for m in re.finditer(r'\b(NORTH|SOUTH|EAST|WEST|CENTRAL)\s+AREA\b', value):
        result['area'].add(m[1])
    if 'BAILEY' in value:
        result['named-area'].add('BAILEY')
    return result


def findspot_check(a, b):
    if not usable(a) or not usable(b):
        return 'missing'
    aa, bb = compact(a), compact(b)
    if aa in bb or bb in aa:
        return 'agrees'
    left, right = location_tokens(a), location_tokens(b)
    outcomes = []
    for key in left.keys() & right.keys():
        outcomes.append('agrees' if left[key] & right[key] else 'conflict')
    return 'conflict' if 'conflict' in outcomes else ('agrees' if outcomes else 'not-comparable')


def chronology_check(row, meta):
    value = tidy(row['period_or_phase'])
    if not usable(value):
        return 'missing'
    left = re.sub(r'\b(?:KMR|PERIOD|STAGE|PHASE)\b', '', value).strip()
    if not re.fullmatch(r'[IVX\d]+\s*[A-C]?', left):
        return 'not-comparable'
    left = roman_token(left)
    keys = ['phase'] if 'PHASE' in value else ['period'] if 'PERIOD' in value or 'STAGE' in value or 'KMR' in value else ['period', 'phase']
    right = []
    for key in keys:
        text = tidy(str(meta.get(key, '')))
        if usable(text) and re.fullmatch(r'[IVX\d]+\s*[A-C]?', text):
            right.append(roman_token(text))
    if not right:
        return 'not-comparable'
    if left in right:
        return 'agrees'
    # A broad period and its named subperiod are compatible.
    if any((x.startswith(left) and x[len(left):].isalpha()) or
           (left.startswith(x) and left[len(x):].isalpha()) for x in right):
        return 'compatible'
    return 'conflict'


def depth_check(row, meta):
    a, b = tidy(row['depth_or_layer']), tidy(str(meta.get('depth', '')))
    if not usable(a) or not usable(b):
        return 'missing'
    if compact(a) == compact(b):
        return 'agrees'
    # Compare numeric ranges only when both inputs state the same unit.
    unit = r'\b(?:M' + 'M|C' + r'M|M|FT|FEET)\b'
    ua, ub = re.findall(unit, a), re.findall(unit, b)
    if not ua or not ub or ua[-1] != ub[-1]:
        return 'not-comparable'
    aa = re.sub(r'\b(?:LAYER|STRATUM)\s+[A-Z0-9]+[;,]?', '', a)
    na, nb = re.findall(r'\d+(?:\.\d+)?', aa), re.findall(r'\d+(?:\.\d+)?', b)
    if not na or not nb:
        return 'not-comparable'
    low_a, high_a = min(map(float, na)), max(map(float, na))
    low_b, high_b = min(map(float, nb)), max(map(float, nb))
    return 'agrees' if max(low_a, low_b) <= min(high_a, high_b) else 'conflict'


def layer_check(row, meta):
    left = re.search(r'\b(?:LAYER|STRATUM)\s+(?:PIT\s*)?(\d+)', tidy(row['depth_or_layer']))
    right = re.search(r'\b(?:LAYER|STRATUM)\s+(?:PIT\s*)?(\d+)', tidy(str(meta.get('period', ''))))
    if not left or not right:
        return 'not-comparable'
    return 'agrees' if int(left[1]) == int(right[1]) else 'conflict'


def plate_tokens(value):
    return {re.sub(r'\s+', '', m[1].upper()) + ':' + compact(m[2])
            for m in re.finditer(r'(?i)\b(PL|PLATE|FIG|FIGURE)\.?\s*([IVXLC\d]+(?:\s*[:.]\s*\d+)?)', value)}


def compare(row, family, prefs):
    faces = family['faces']
    detail, rules = [], set()
    for face in faces:
        meta = face.get('metadata', {})
        code = str(meta.get('type') or face.get('object_type', '')).split(':')[0].upper()
        rule = id_rule(row['registration'], meta.get('excavation-idno', ''), prefs)
        rp, lp = plate_tokens(row['plate_or_figure']), plate_tokens(str(meta.get('excavation-idno', '')))
        if not rule and rp & lp:
            rule = 'plate-citation'
        if rule:
            rules.add(rule)
        reg_status = ('agrees' if rule and rule != 'plate-citation' else
                      'conflict' if usable(row['registration']) and usable(meta.get('excavation-idno', '')) else 'missing')
        state = {'record_id': str(face['record_id']), 'site': 'agrees',
                 'excavation-idno': reg_status,
                 'object_type/type': 'agrees' if code in TYPE_MAP[row['object_type']] else 'conflict',
                 'findspot/area-section,block-house,room-grid': findspot_check(
                     row['findspot'], ' '.join(str(meta.get(k, '')) for k in ('area-section', 'block-house', 'room-grid') if usable(meta.get(k, '')))),
                 'depth_or_layer/depth': depth_check(row, meta),
                 'depth_or_layer/period': layer_check(row, meta),
                 'period_or_phase/period,phase': chronology_check(row, meta),
                 'time': 'not-comparable',
                 'material': 'agrees' if usable(row['material']) and usable(meta.get('material', '')) and compact(row['material']) == compact(meta['material']) else 'not-used-for-exclusion'}
        detail.append(state)
    context_keys = ['object_type/type', 'findspot/area-section,block-house,room-grid',
                    'depth_or_layer/depth', 'depth_or_layer/period', 'period_or_phase/period,phase']
    conflict = any(s[k] == 'conflict' for s in detail for k in context_keys)
    reg_conflict = not rules and any(s['excavation-idno'] == 'conflict' for s in detail)
    ranking = ['registration-exact', 'registration-normalised', 'registration-contained', 'plate-citation']
    rule = next((r for r in ranking if r in rules), None)
    return {'compatible': not conflict and not reg_conflict, 'rule': rule,
            'context_conflict': conflict, 'registration_conflict': reg_conflict,
            'checks': detail}


def propose(rows, fams, sites, duplicate_pairs, absent_witnesses):
    at_site = defaultdict(dict)
    for fid, fam in fams.items():
        at_site[fam['site']][fid] = fam
    by_cisi = defaultdict(set)
    for fid, family in fams.items():
        for face in family['faces']:
            for number in cisi_numbers(str(face.get('source_cisi', ''))):
                by_cisi[(family['site'], number)].add(fid)
    pairs, proposals = {}, {}
    reserved = defaultdict(set)
    for row in rows:
        rid = row['row_id']
        if row['catalogue_status'] == 'in-baseline-catalogue':
            fids = set()
            for code in row['cisi_in_baseline'].split('|'):
                fids |= by_cisi[(row['site'], code.upper())]
            row['local_match'] = 'in-baseline-catalogue'
            row['local_family_ids'] = '|'.join(sorted(fids, key=int))
            row['match_basis'] = 'context' if fids else 'no-local-family'
            row['match_evidence'] = json.dumps({'source_cisi': 'agrees' if fids else 'not-present',
                                                'site': 'agrees', 'catalogue_status': 'in-baseline-catalogue'})
            for fid in fids:
                reserved[fid].add(rid)
            continue
        witness = absent_witnesses.get((row['site'], normalise(row['registration'], prefixes_for(row['site'], sites))))
        if witness:
            row.update(local_match='absent', local_family_ids='', match_basis='no-local-family',
                       match_evidence=json.dumps({'site': 'agrees', 'registration': 'agrees with museum accession',
                                                   'museum_join_table': 'object recorded absent from corpus',
                                                   'witness': witness}))
            continue
        pairs[rid] = {fid: compare(row, fam, prefixes_for(row['site'], sites))
                      for fid, fam in at_site[row['site']].items()}
        identified = [fid for fid, v in pairs[rid].items() if v['compatible'] and v['rule']]
        if len(identified) == 1:
            proposals[rid] = identified[0]
    users = defaultdict(set)
    for rid, fid in proposals.items():
        users[fid].add(rid)
    collisions = []
    for rid, fid in list(proposals.items()):
        other_users = (users[fid] | reserved[fid]) - {rid}
        if any(tuple(sorted((rid, other))) not in duplicate_pairs for other in other_users):
            collisions.append({'row_id': rid, 'local_family_id': fid,
                               'other_rows': '|'.join(sorted(other_users)),
                               'action': 'unresolved shared identifier; candidate proposal'})
            del proposals[rid]
    assigned = defaultdict(set)
    for rid, fid in proposals.items():
        assigned[fid].add(rid)
    for fid, rids in reserved.items():
        assigned[fid] |= rids
    for row in rows:
        rid = row['row_id']
        if row['local_match']:
            continue
        checks = pairs[rid]
        if rid in proposals:
            selected = [proposals[rid]]
            status, basis = 'matched', checks[selected[0]]['rule']
        else:
            selected = [fid for fid, v in checks.items() if v['compatible'] and
                        all(tuple(sorted((rid, other))) in duplicate_pairs for other in assigned[fid])]
            if selected:
                status = 'candidate'
                basis = 'conflict' if any(v['rule'] and v['compatible'] for v in checks.values()) else 'type-only'
            else:
                status = 'absent'
                if not checks:
                    basis = 'no-local-family'
                elif any(v['compatible'] for v in checks.values()):
                    basis = 'all-families-assigned'
                else:
                    basis = 'conflict'
        selected.sort(key=int)
        rejected = Counter()
        for fid, v in checks.items():
            if fid in selected:
                continue
            if v['context_conflict']:
                rejected['object_type_or_context_conflict'] += 1
            elif v['registration_conflict']:
                rejected['registration_conflict'] += 1
            elif assigned[fid]:
                rejected['already_assigned'] += 1
        evidence = {'site': 'agrees', 'families_compared': len(checks),
                    'families': {fid: checks[fid]['checks'] for fid in selected},
                    'rejected_family_counts': dict(rejected)}
        outcomes = defaultdict(Counter)
        for comparison in checks.values():
            for state in comparison['checks']:
                for field, outcome in state.items():
                    if field != 'record_id':
                        outcomes[field][outcome] += 1
        evidence['comparison_outcomes'] = {k: dict(v) for k, v in outcomes.items()}
        if not selected:
            evidence['outcome'] = basis
        row.update(local_match=status, local_family_ids='|'.join(selected),
                   match_basis=basis, match_evidence=json.dumps(evidence, separators=(',', ':')))
    write_csv(OUT / 'identifier-collisions.csv',
              ['row_id', 'local_family_id', 'other_rows', 'action'], collisions)
    return at_site, reserved, assigned


def publication_rank(source_id, register):
    row = register[source_id]
    kind = row['kind'].lower()
    title = row['title'].lower()
    if 'annual' in kind or source_id.startswith('iar-'):
        return 4
    if 'news' in kind:
        return 5
    if 'final' in kind or source_id in {'farmana-2006-08', 'surkotada-1990'}:
        return 1
    if 'excavation' in kind or 'monograph' in kind or 'excavations at' in title or source_id.startswith('kanmer-frame-'):
        return 2
    return 3


COUNT_FIELDS = ('rows_total', 'rows_individual', 'rows_enumerated', 'rows_uncertain_status',
                'rows_possibly_in_cisi3', 'rows_in_baseline_catalogue', 'rows_post_catalogue',
                'matched', 'candidate', 'absent', 'local_families_at_site', 'local_families_matched',
                'local_candidate_families_unassigned', 'absent_lower_bound', 'absent_upper_bound')


def site_counts(rows, fams, sites, ordered, register):
    main_assigned = {fid for r in rows if r['local_match'] == 'matched'
                     for fid in r['local_family_ids'].split('|') if fid}
    main_assigned |= {fid for r in rows if r['local_match'] == 'in-baseline-catalogue'
                      for fid in r['local_family_ids'].split('|') if fid}
    results = []
    for site in ordered:
        all_rows = [r for r in rows if r['site'] == site]
        eligible = [r for r in all_rows if r['catalogue_status'] == 'post-catalogue' and r['inscription_status'] == 'stated']
        counts = Counter(r['local_match'] for r in eligible)
        matched = {fid for r in eligible if r['local_match'] == 'matched' for fid in r['local_family_ids'].split('|') if fid}
        candidates = {fid for r in eligible if r['local_match'] == 'candidate' for fid in r['local_family_ids'].split('|') if fid} - main_assigned
        publications = Counter(r['primary_publication'] for r in eligible)
        ranked = sorted(publications, key=lambda sid: (publication_rank(sid, register), -publications[sid], sid))
        best = ranked[0] if ranked else ''
        basis = ('Best-ranked primary publication among eligible rows; ' +
                 '; '.join(f'{sid}: {publications[sid]} rows' for sid in ranked)) if best else 'No eligible row in the supplied extraction tables'
        result = {'site_code': sites[site]['site_code'], 'site': site,
                  'rows_total': len(eligible),
                  'rows_individual': sum(r['row_basis'] == 'individual' for r in eligible),
                  'rows_enumerated': sum(r['row_basis'] == 'enumerated-count' for r in eligible),
                  'rows_uncertain_status': sum(r['inscription_status'] != 'stated' for r in all_rows),
                  'rows_possibly_in_cisi3': sum(r['catalogue_status'] == 'possibly-in-cisi3' for r in all_rows),
                  'rows_in_baseline_catalogue': sum(r['catalogue_status'] == 'in-baseline-catalogue' for r in all_rows),
                  'rows_post_catalogue': len(eligible),
                  'matched': counts['matched'], 'candidate': counts['candidate'], 'absent': counts['absent'],
                  'local_families_at_site': sum(f['site'] == site for f in fams.values()),
                  'local_families_matched': len(matched),
                  'local_candidate_families_unassigned': len(candidates),
                  'absent_lower_bound': counts['absent'] + max(0, counts['candidate'] - len(candidates)),
                  'absent_upper_bound': len(eligible) - counts['matched'],
                  'best_publication': best, 'publication_basis': basis}
        results.append(result)
    total = {key: sum(r[key] for r in results) for key in COUNT_FIELDS}
    total.update(site_code='TOTAL', site='TOTAL', best_publication='',
                 publication_basis='Sum of site counts; bounds use each site separately')
    return results + [total]


def unlisted(rows, fams):
    named = {fid for row in rows for fid in row['local_family_ids'].split('|') if fid}
    records, edits = [], []
    for fid, family in sorted(fams.items(), key=lambda item: (item[1]['site'], int(item[0]))):
        if fid in named:
            continue
        result = {'site': family['site'], 'object_family_id': fid}
        for key in TOP:
            if key not in {'site', 'object_family_id'}:
                result[key] = '|'.join(dict.fromkeys(str(f.get(key, '')) for f in family['faces']))
        for key in META:
            result[key] = '|'.join(dict.fromkeys(str(f.get('metadata', {}).get(key, '')) for f in family['faces']))
        for key, value in result.items():
            filtered = clean(value)
            if filtered != value:
                edits.append({'object_family_id': fid, 'field': key,
                              'action': 'restricted unit expression withheld'})
            result[key] = filtered
        records.append(result)
    write_csv(OUT / 'local-unlisted.csv',
              ['site', 'object_family_id', *[k for k in TOP if k not in {'site', 'object_family_id'}], *META], records)
    return records, edits


def locators(rows, register, logs):
    results = []

    def verdict(sid, pdf_page):
        source = register.get(sid)
        if not source:
            return 'source not registered'
        maximum = int(source['pdf_pages']) if source['pdf_pages'].isdigit() else None
        page_ids = [int(x) for x in re.findall(r'\d+', pdf_page)]
        if not page_ids:
            return 'registered; printed locator recorded'
        if maximum is None:
            return 'registered; extent unavailable'
        return 'within registered extent' if all(1 <= p <= maximum for p in page_ids) else 'outside registered extent'

    for row in rows:
        sid = row['primary_publication']
        results.append({'row_id': row['row_id'], 'source_id': sid,
                        'locator_kind': 'primary', 'printed_page': row['page'],
                        'pdf_page': row['pdf_page'], 'plate_or_figure': row['plate_or_figure'],
                        'check': verdict(sid, row['pdf_page'])})
        for segment in filter(None, map(str.strip, row['other_publications'].split(';'))):
            match = re.match(r'^([A-Za-z0-9_-]+)\s*:\s*(.*)$', segment)
            sid, locator = (match[1], match[2]) if match else (segment, '')
            is_pdf = bool(re.search(r'\bPDF\b', locator, flags=re.I))
            results.append({'row_id': row['row_id'], 'source_id': sid,
                            'locator_kind': 'other-publication',
                            'printed_page': '' if is_pdf else locator,
                            'pdf_page': locator if is_pdf else '', 'plate_or_figure': '',
                            'check': verdict(sid, locator if is_pdf else '')})
    for log in logs:
        sid = log['merged_source']
        results.append({'row_id': next((r['row_id'] for r in rows if r['_part'] == log['part'] and r['provisional_row_id'] == log['kept_row_id']), ''),
                        'source_id': sid, 'locator_kind': 'regional-merge-log',
                        'printed_page': log['merged_page'], 'pdf_page': '', 'plate_or_figure': '',
                        'check': 'registered; printed locator recorded' if sid in register else 'source not registered'})
    write_csv(OUT / 'locator-checks.csv',
              ['row_id', 'source_id', 'locator_kind', 'printed_page', 'pdf_page', 'plate_or_figure', 'check'], results)
    return results


def museum_witnesses():
    path = ROOT / 'experiments/2026-10-13-museum-open-access/joins/join-table.csv'
    INPUTS.add(path)
    # Project only identity and decision columns from the existing join table.
    with path.open(encoding='utf-8-sig', newline='') as stream:
        import csv
        reader = csv.DictReader(stream)
        witnesses = [{k: r.get(k, '') for k in ('accession', 'joined', 'family', 'method', 'cisi_in_local_corpus')}
                     for r in reader if r.get('accession', '') in {'DHR-22198', 'DHR-6032', 'DHR-7860'}]
    return {('Dholavira', w['accession'].removeprefix('DHR-')): 'museum-open-access/joins/join-table.csv: ' + w['accession']
            for w in witnesses if w['joined'].lower() == 'false' and w['method'] == 'no_local_family' and not w['family']}


def museum_checks(rows, witnesses):
    results = []
    for number in ('22198', '6032', '7860'):
        matching = [r for r in rows if r['site'] == 'Dholavira' and r['registration'] == number]
        results.append({'registration': number,
                        'museum_witness_found': ('Dholavira', number) in witnesses,
                        'row_ids': [r['row_id'] for r in matching],
                        'proposed_statuses': [r['local_match'] for r in matching],
                        'used_as': 'independent absence witness; not an identifier join'})
    return results


def run():
    OUT.mkdir(exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    corpus_hash = sha(CORPUS)
    assert corpus_hash.startswith('1220f559'), 'Corpus pin differs'
    for name in ('PROTOCOL.md', 'AMENDMENT-1.md'):
        INPUTS.add(PACKAGE / name)
    sites, ordered, aliases, notes, logs = site_setup()
    register, withheld_sources = source_register()
    columns, rows = merged_rows(sites, ordered)
    duplicate_pairs, cross, within = duplicates(rows, sites)
    fams = families(aliases)
    moved, reviews = containment(rows, sites)
    witnesses = museum_witnesses()
    at_site, reserved, assigned = propose(rows, fams, sites, duplicate_pairs, witnesses)
    records, unit_edits = unlisted(rows, fams)
    locator_rows = locators(rows, register, logs)
    museum = museum_checks(rows, witnesses)
    write_csv(OUT / 'objects-merged.csv', columns, rows)
    counts = site_counts(rows, fams, sites, ordered, register)
    write_csv(OUT / 'site-counts.csv', ['site_code', 'site', *COUNT_FIELDS, 'best_publication', 'publication_basis'], counts)
    summary = {'authors': ['OpenAI GPT-6, Codex desktop API harness, run 3'],
               'corpus_sha256': corpus_hash, 'rows_merged': len(rows),
               'rows_by_part': dict(Counter(r['_part'] for r in rows)),
               'counts_by_local_status_all_rows': dict(Counter(r['local_match'] for r in rows)),
               'counts_by_catalogue_status_all_rows': dict(Counter(r['catalogue_status'] for r in rows)),
               'counts_by_site_all_rows': {s: {'rows': sum(r['site'] == s for r in rows),
                                              'local_status': dict(Counter(r['local_match'] for r in rows if r['site'] == s)),
                                              'catalogue_status': dict(Counter(r['catalogue_status'] for r in rows if r['site'] == s))}
                                            for s in ordered},
               'counts_by_site': counts, 'newly_in_baseline_catalogue': moved,
               'cross_part_duplicate_pairs': len(cross), 'same_part_duplicate_pairs': len(within),
               'containment_review_pairs': len(reviews),
               'containment_review_rows': len({r['row_id'] for r in reviews}),
               'local_unlisted_by_site': {s: sum(r['site'] == s for r in records) for s in ordered},
               'source_register_rows': len(register),
               'locator_checks': dict(Counter(r['check'] for r in locator_rows)),
               'museum_checks': museum, 'output_filter_actions': {'source_cells': withheld_sources, 'unlisted_cells': unit_edits},
               'count_scope': 'Main counts use stated post-catalogue rows; total rows in this scope are rows_total. Audit and uncertain rows are separate. Zero-row named sites from the seed and regional notes are retained.',
               'assignment_scope': 'All identifier joins and baseline audit identities reserve families before candidate lists are formed. A flagged duplicate may name an assigned family. Candidate capacity counts only unassigned families.',
               'publication_order': 'Site seed order, then new named sites in part order; primary publication source id order within each site; extraction order breaks ties.',
               'input_hashes': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(INPUTS)}}
    write_json(OUT / 'match-summary.json', summary)
    write_json(LOCAL / 'identity-run-audit.json', {'input_hashes': summary['input_hashes'],
                                                 'allowed_top_fields': TOP, 'allowed_metadata_keys': META,
                                                 'local_projection': 'Unselected JSON values skipped without deserialization',
                                                 'page_images_opened': 0})
    print(json.dumps({'rows': len(rows), 'eligible': counts[-1]['rows_total'],
                      'matched': counts[-1]['matched'], 'candidate': counts[-1]['candidate'],
                      'absent': counts[-1]['absent'], 'moved_to_baseline': len(moved),
                      'reviews': len(reviews), 'source_rows': len(register)}))


if __name__ == '__main__':
    run()
