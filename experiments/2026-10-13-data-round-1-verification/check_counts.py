"""Independent offline counts for the two preserved data-round packages.

Run from the repository root. Inputs remain local. Outputs contain counts,
identifiers and flags; detailed comparisons are written under data/raw.
This script never imports either package's scoring or joining functions.
"""
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations, product
import csv
import hashlib
import json
import math
import random
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
LOCAL = ROOT / 'data/raw/2026-10-13-data-round-1-verification'
MUSEUM = LOCAL / 'snapshot/2026-10-13-museum-open-access'
CISI = LOCAL / 'snapshot/2026-10-13-cisi2-basic-data-pilot'
RAW = ROOT / 'data/raw/2026-10-13-cisi2-basic-data-pilot'
COLS = ['col1', 'col2_fc', 'col3_excavation', 'col4_museum', 'col5_photographs']
PLACEHOLDERS = {'', '-', '--', '- -', '?', '??', 'unknown'}
DIMENSIONS = ['horizontal(mm)', 'vertical(mm)', 'thickness(mm)']


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def read_jsonl(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def read_csv(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def ws(raw):
    return ' '.join(str(raw if raw is not None else '').split())


def usable(field, raw):
    s = ws(raw)
    if s.casefold() in PLACEHOLDERS:
        return False
    if field in DIMENSIONS:
        try:
            return float(s) > 0
        except ValueError:
            m = re.fullmatch(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', s)
            return bool(m and max(map(float, m.groups())) > 0)
    return True


def base_key(raw):
    m = re.match(r'^\s*([A-Za-z?]+)-?\s*0*(\d+)', raw or '')
    return f'{m[1]}-{int(m[2])}' if m else None


def pass_rows(path):
    result = {}
    for s in path.read_text(encoding='utf-8').splitlines():
        if not s.strip() or s.startswith('#'):
            continue
        cells = [ws(c) for c in s.split(' | ')]
        assert len(cells) == 5
        key = base_key(cells[0])
        assert key not in result
        result[key] = dict(zip(COLS, cells))
    return result


def permits(candidate, truth):
    pattern = ''
    for part in re.split(r'(\[[^\]]*\])', ws(candidate)):
        if part.startswith('['):
            inside = part[1:-1]
            pattern += '.*' if '?' in inside else '(?:' + '|'.join(re.escape(x) for x in inside.split('/')) + ')'
        else:
            pattern += re.escape(part)
    return re.fullmatch(pattern, ws(truth)) is not None


def accuracy(first, second, keys, adjudications):
    adjud = {(a['cisi'], a['column']): a for a in adjudications}
    differences = {(key, col) for key in keys for col in COLS if first[key][col] != second[key][col]}
    assert differences == set(adjud)
    rows = {}
    for col in COLS:
        counts = Counter()
        for key in keys:
            a, b = first[key][col], second[key][col]
            counts['cells'] += 1
            counts['uncertain_first'] += '[' in a
            if a == b:
                counts['agreed'] += 1
            else:
                d = adjud[key, col]
                assert ws(d['pass1']) == a and ws(d['pass2']) == b
                counts[d['outcome']] += 1
                if d['outcome'] == 'undecidable':
                    counts['undecidable_definite_first'] += '[' not in a
                else:
                    counts['first_errors'] += not permits(a, d['adjudicated'])
                    counts['second_errors'] += not permits(b, d['adjudicated'])
        counts['disagreements'] = counts['cells'] - counts['agreed']
        row = {k: counts[k] for k in ['cells', 'agreed', 'disagreements', 'first-pass-right', 'second-pass-right', 'both-wrong', 'undecidable', 'undecidable_definite_first', 'first_errors', 'second_errors', 'uncertain_first']}
        row['agreement_percent'] = round(100 * row['agreed'] / row['cells'], 1)
        row['first_error_percent'] = round(100 * row['first_errors'] / row['cells'], 1)
        row['first_error_upper_percent'] = round(100 * (row['first_errors'] + row['undecidable_definite_first']) / row['cells'], 1)
        rows[col] = row
    total = {k: sum(r[k] for r in rows.values()) for k in rows['col1'] if not k.endswith('percent')}
    total.update(agreement_percent=round(100 * total['agreed'] / total['cells'], 1),
                 first_error_percent=round(100 * total['first_errors'] / total['cells'], 1),
                 first_error_upper_percent=round(100 * (total['first_errors'] + total['undecidable_definite_first']) / total['cells'], 1))
    return {'columns': rows, 'total': total}


def museum_numbers(text):
    """Extract number-shaped tokens independently of the pilot parser.

    Reject code-only holdings. Preserve complete bracket tokens and letter suffixes.
    A definite token in a mixed cell can still supply a definite museum number.
    """
    return re.findall(r'(?<![A-Za-z0-9])(?:[A-Z]+-)?(?:\[[^\]]+\]|\d)[\d.\[\]/?]*(?:\s*\[[A-Z/]+\]|[A-Za-z]+)?', text)


def squash(text):
    return re.sub(r'[^A-Z0-9]', '', text.upper())


def tails(fc):
    options = [p[1:-1].split('/') if p.startswith('[') else [p] for p in re.split(r'(\[[^\]]+\])', fc)]
    result = {''}
    for choices in product(*options):
        number = ''.join(choices)
        if number.isdigit() and int(number) >= 1000:
            result.update([number[1:], str(int(number[1:]))])
    return result


def excavation_table(joined, families, final):
    expected = {r['cisi']: {squash(p) + tail for p in r['col3_excavation'].split(' // ')
                            if '[' not in p and not p.startswith('???') for tail in tails(r['col2_fc'])}
                for r in final}
    counts = Counter()
    details = []
    for family, row in joined.items():
        if not row['parsed']['excavation_usable']:
            continue
        raw_lipi = families[family][0]['metadata']['excavation-idno']
        lv, pv, fc = squash(raw_lipi), squash(row['col3_excavation']), row['col2_fc']
        if '[' in row['col3_excavation']:
            category = 'uncertain'
        elif lv == pv:
            category = 'equal'
        elif '[' not in fc and any(lv == pv + t for t in tails(fc) if t):
            category = 'fc_tail'
        elif '[' not in fc and any(re.sub('^[A-Z]+', '', lv) == re.sub('^[A-Z]+', '', pv) + t for t in tails(fc)):
            category = 'subarea_added' if lv.startswith('DK') and pv.startswith('DK') else 'dk_prefix_dropped'
        elif any(lv in values for key, values in expected.items() if key != row['cisi']):
            category = 'swapped'
        elif not re.search('[A-Z]', lv):
            category = 'incomplete'
        elif '[' in fc:
            category = 'uncertain'
        elif re.search('[A-Z]$', pv):
            category = 'letter_suffix_dropped'
        elif lv.startswith(pv):
            category = 'plate_suffix'
        else:
            category = 'different_number'
        counts[category] += 1
        details.append({'cisi': row['cisi'], 'family': family, 'category': category,
                        'printed': row['col3_excavation'], 'fc': fc, 'lipi': raw_lipi})
    dump(LOCAL / 'independent-excavation-detail.json', details)
    return dict(counts)


def main():
    faces = read_jsonl(ROOT / 'data/normalized/lipi_observed_faces.jsonl')
    website = read_jsonl(ROOT / 'data/normalized/indus_website_observed.jsonl')
    families = defaultdict(list)
    base_to_families = defaultdict(set)
    for face in faces:
        family = face['object_family_id']
        families[family].append(face)
        key = base_key(ws(face['metadata'].get('cisi')))
        if key:
            base_to_families[key].add(family)
    assert len(families) == 4695
    website_keys = {ws(r.get('source_cisi')) for r in website if usable('MUSEUM', (r.get('metadata') or {}).get('MUSEUM'))}
    web_set = {family for family, fs in families.items() if any(ws(f['metadata'].get('cisi')) in website_keys for f in fs)}
    census_records = read_json(ROOT / 'data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/confirmed-object-joins.json')
    census_set = {r['family'] for r in census_records}
    assert census_set <= set(families)
    joins = read_csv(MUSEUM / 'joins/join-table.csv')
    joined_museum = [r for r in joins if r['cls'] in {'exact', 'confirmed'}]
    museum_set = {r['family'] for r in joined_museum if usable('accession', r['accession'])}
    assert museum_set <= set(families)
    final = read_jsonl(RAW / 'final.jsonl')
    joined_pilot = {}
    statuses = Counter()
    for row in final:
        fs = base_to_families.get(row['cisi'], set())
        if not fs:
            statuses['no-lipi-family'] += 1
        elif len(fs) != 1 or len({base_key(ws(f['metadata'].get('cisi'))) for f in families[next(iter(fs))]}) != 1:
            statuses['ambiguous'] += 1
        else:
            statuses['one-family'] += 1
            family = next(iter(fs))
            assert family not in joined_pilot
            joined_pilot[family] = row
    pilot_set = {family for family, r in joined_pilot.items() if museum_numbers(r['col4_museum'])}
    pilot_clear_cell = {family for family in pilot_set if '[' not in joined_pilot[family]['col4_museum']}
    pilot_clear_number = {family for family in pilot_set if any('[' not in n for n in museum_numbers(joined_pilot[family]['col4_museum']))}
    sets = {'older_website': web_set, 'october_6_census': census_set, 'museum_package': museum_set,
            'cisi2_including_brackets': pilot_set, 'cisi2_without_brackets_in_cell': pilot_clear_cell,
            'cisi2_any_definite_number': pilot_clear_number}
    baseline = web_set | census_set
    counts = {'objects': len(families), 'source_sets': {key: {'count': len(value), 'families': sorted(value, key=int)} for key, value in sets.items()},
              'pairwise_overlaps': {f'{a} & {b}': {'count': len(sets[a] & sets[b]), 'families': sorted(sets[a] & sets[b], key=int)} for a, b in combinations(sets, 2)},
              'holding_institution': {'inventory_has_separate_field': False}}
    stages = {'website_and_census': baseline, 'museum_package_after': baseline | museum_set,
              'cisi2_after_website_only': web_set | pilot_set,
              'combined_including_brackets': baseline | museum_set | pilot_set,
              'combined_without_brackets_in_cell': baseline | museum_set | pilot_clear_cell,
              'combined_any_definite_number': baseline | museum_set | pilot_clear_number,
              'museum_first_over_common_baseline': museum_set - baseline,
              'cisi2_first_over_common_baseline': pilot_set - baseline,
              'cisi2_first_without_brackets_over_common_baseline': pilot_clear_cell - baseline,
              'museum_first_after_cisi2': museum_set - baseline - pilot_set,
              'cisi2_first_after_museum': pilot_set - baseline - museum_set,
              'first_number_from_both_packages': (museum_set & pilot_set) - baseline,
              'three_older_sources_overlap': web_set & census_set & museum_set}
    counts['stages'] = {key: {'count': len(value), 'families': sorted(value, key=int)} for key, value in stages.items()}
    dump(OUT / 'combined-coverage.json', counts)
    with (LOCAL / 'combined-museum-coverage.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, ['family'] + list(sets) + list(stages))
        writer.writeheader()
        for family in sorted(families, key=int):
            writer.writerow({'family': family, **{k: int(family in s) for k, s in (sets | stages).items()}})
    first = pass_rows(RAW / 'pass1-p435.txt') | pass_rows(RAW / 'pass1-p436.txt')
    sample = read_json(CISI / 'sample.json')
    sample_keys = [r['cisi'] for r in sample['sample']]
    seed_sample = random.Random(sample['seed']).sample(read_jsonl(RAW / 'pass1.jsonl'), max(25, math.ceil(len(first) / 10)))
    sample_reproduced = {r['cisi'] for r in seed_sample} == set(sample_keys)
    sampled = accuracy(first, pass_rows(RAW / 'pass2/pass2.txt'), sample_keys, read_json(RAW / 'adjudication.json'))
    full_second = pass_rows(RAW / 'pass2b/pass2b.txt')
    full = accuracy(first, full_second, list(first), read_json(RAW / 'adjudication-full.json'))
    third_agreement = sum(pass_rows(RAW / 'pass2/pass2.txt')[k][col] == full_second[k][col] for k in sample_keys for col in COLS)
    uncertainty = Counter(col for r in final for col in COLS if '[' in r[col])
    replacements = {}
    decided = set()
    for rows in [read_json(RAW / 'adjudication.json'), read_json(RAW / 'adjudication-full.json')]:
        for a in rows:
            key = (a['cisi'], a['column'])
            if key in decided:
                continue
            decided.add(key)
            if a['outcome'] != 'first-pass-right':
                replacements[key] = a['adjudicated']
    rechecks = read_json(RAW / 'recheck/recheck.json')['items']
    for r in rechecks:
        key = (r['cisi'], r['column'])
        if key not in decided:
            replacements[key] = r['final']
    final_cell_differences = [{'cisi': r['cisi'], 'column': col} for r in final for col in COLS if ws(r[col]) != ws(replacements.get((r['cisi'], col), first[r['cisi']][col]))]
    agreement_reopened = [r for r in rechecks if r['column'] == 'col3_excavation' and first[r['cisi']]['col3_excavation'] == full_second[r['cisi']]['col3_excavation'] and '[' in r['final'] and '[' not in r['pass1']]
    before, after, supply = Counter(), Counter(), Counter()
    for family, row in joined_pilot.items():
        fs = families[family]
        def has(field):
            return any(usable(field, f['metadata'].get(field)) for f in fs)
        b = {'museum_number': family in web_set, 'holding_institution': family in web_set, 'fc_number': False,
             'excavation': has('excavation-idno'), 'findspot': any(has(x) for x in ['area-section', 'block-house', 'room-grid']),
             'depth': has('depth'), 'material': has('material'), 'dimensions_any': any(has(x) for x in DIMENSIONS), 'dimensions_all3': all(has(x) for x in DIMENSIONS)}
        c = {'museum_number': family in pilot_set, 'holding_institution': bool(re.search(r'\b(?:MD|MM|NMP|L|HM|EXB|KHP)\b', row['col4_museum'])),
             'fc_number': bool(re.search(r'\d', row['col2_fc'])), 'excavation': any(ws(piece) and not ws(piece).startswith('???') and ws(piece) != '-' for piece in row['col3_excavation'].split(' // '))}
        for key in b:
            before[key] += b[key]
            supply[key] += c.get(key, False)
            after[key] += b[key] or c.get(key, False)
    result = {'museum': {'records_decided': len(joins), 'classes_all': dict(Counter(r['cls'] for r in joins)),
                         'q1019_classes': dict(Counter(r['cls'] for r in joins if r['q1019'] == 'True')),
                         'q1019_dispositions': {key: dict(Counter(r['cls'] for r in joins if r['q1019'] == 'True' and r['census_disposition'] == key)) for key in {r['census_disposition'] for r in joins if r['q1019'] == 'True'}},
                         'census_records': len(census_records), 'census_families': len(census_set),
                         'joined_records': len(joined_museum), 'new_join_records': sum(r['new_join'] == 'True' for r in joined_museum),
                         'first_dimension_families': sorted({r['family'] for r in joined_museum if r['new_join'] == 'True' and r['gain_dims_any'] == 'True'}, key=int),
                         'more_axes_families': sorted({r['family'] for r in joined_museum if r['new_join'] == 'True' and r['gain_dims_more_axes'] == 'True'}, key=int),
                         'candidate_additions': [r['accession'] for r in joins if r['addition']]},
              'cisi2': {'entries': len(final), 'join_status': dict(statuses), 'sample_reproduced': sample_reproduced,
                        'sample_accuracy': sampled, 'full_accuracy': full, 'third_reading_agreement': third_agreement,
                        'uncertain_cells': sum(uncertainty.values()), 'uncertain_rows': sum(any('[' in r[col] for col in COLS) for r in final),
                        'uncertain_by_column': dict(uncertainty), 'final_cell_differences': final_cell_differences,
                        'agreed_excavation_cells_reopened': len(agreement_reopened), 'recheck_outcomes': dict(Counter(r['outcome'] for r in rechecks)),
                        'coverage_before': dict(before), 'coverage_after': dict(after), 'cisi2_supplies': dict(supply),
                        'museum_without_bracketed_cell': len(pilot_clear_cell), 'museum_with_any_definite_number': len(pilot_clear_number),
                        'museum_gained_without_brackets': len(pilot_clear_cell - web_set),
                        'excavation_clear_cells': sum('[' not in row['col3_excavation'] and not row['col3_excavation'].startswith('???') for row in joined_pilot.values())}}
    result['cisi2']['excavation_comparison_table'] = excavation_table(joined_pilot, families, final)
    holdings = Counter()
    for row in joined_pilot.values():
        text = row['col4_museum']
        transfer = re.match(r'^\(.*\)\s*now(?: in)?:?\s*(\S+)\s*$', text)
        holdings.update([transfer[1]] if transfer else set(re.findall(r'\b(?:MD|MM|L|NMP|EXB|HM|KHP)\b', text)))
    result['cisi2']['current_holding_codes'] = dict(holdings)
    accession_pattern = re.compile(r'(?<!\d)(?:\d|\[[^\]]+\]){2}\.(?:\d|\[[^\]]+\])+')
    result['cisi2']['nmp_accession_objects'] = sum(bool(accession_pattern.search(r['col4_museum'])) for r in joined_pilot.values())
    groups = {'seals': {f for f, fs in families.items() if ws(fs[0]['metadata'].get('type')).upper().startswith('SEAL')},
              'mohenjo_daro': {f for f, fs in families.items() if fs[0]['site'] == 'Mohenjo-daro'}}
    result['cisi2']['website_plus_pilot_group_coverage'] = {key: {'denominator': len(ids), 'before': len(ids & web_set),
                                                              'after': len(ids & (web_set | pilot_set))}
                                                         for key, ids in groups.items()}
    dump(OUT / 'independent-counts.json', result)
    print(json.dumps({'combined_stages': {k: len(s) for k, s in stages.items()}, 'pilot': result['cisi2']}, indent=2))


if __name__ == '__main__':
    main()
