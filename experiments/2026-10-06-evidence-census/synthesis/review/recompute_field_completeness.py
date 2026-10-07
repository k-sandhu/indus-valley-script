"""Independent recomputation of the Lipi field-completeness table (reviewer script).

Uses its own missing-value rule (a value is missing when nothing is left after removing
hyphens, whitespace and question marks, or when it is one of unknown/none/null/n/a) and
compares it with the package's field-completeness.csv. Reads the pinned local corpus only.
"""
import csv, json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
rows = [json.loads(l) for l in (ROOT / 'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8-sig').splitlines() if l.strip()]
N = len(rows)


def present(v):
    if v is None:
        return False
    s = str(v).strip().casefold()
    if s in {'unknown', 'none', 'null', 'n/a'}:
        return False
    return bool(re.sub(r'[\s\-?]', '', s))


def pos(v):
    try:
        return float(v) > 0
    except (TypeError, ValueError):
        return False


M = lambda r, k: r['metadata'].get(k)
dims = ['horizontal(mm)', 'vertical(mm)', 'thickness(mm)']
mine = {
    'named_site': sum(present(r['site']) for r in rows),
    'findspot(room-grid)': sum(present(M(r, 'room-grid')) for r in rows),
    'findspot(any of area-section, block-house, room-grid)': sum(any(present(M(r, k)) for k in ['area-section', 'block-house', 'room-grid']) for r in rows),
    'stratum_or_phase(period or phase)': sum(present(M(r, 'period')) or present(M(r, 'phase')) for r in rows),
    'depth': sum(present(M(r, 'depth')) for r in rows),
    'date_or_period_label(time)': sum(present(M(r, 'time')) for r in rows),
    'dimensions(any positive)': sum(any(pos(M(r, k)) for k in dims) for r in rows),
    'dimensions_all_three': sum(all(pos(M(r, k)) for k in dims) for r in rows),
    'material': sum(present(M(r, 'material')) for r in rows),
    'registration(excavation-idno)': sum(present(M(r, 'excavation-idno')) for r in rows),
    'CISI_identifier(source_cisi)': sum(present(r['source_cisi']) for r in rows),
}
# calendar-date attribution: any numeral in the time field accompanied by BC/BCE/AD/century/millennium
cal = sum(bool(re.search(r'\d', str(M(r, 'time'))) and re.search(r'b\.?c|a\.?d\.?|b\.?p|century|mill|cal', str(M(r, 'time')), re.I)) for r in rows)
mine['calendar_date_assertion(time)'] = cal
# keys that could hold images, rights or dates anywhere in the normalized face rows
keyset = set()
for r in rows:
    keyset |= set(r.keys()) | set(r['metadata'].keys())
mine['_keys_matching_image|photo|url|licen|rights|date|c14|radiocarbon'] = sorted(k for k in keyset if re.search(r'image|photo|url|licen|right|date|c14|radiocarbon|bp', k, re.I))

pkg = {}
with (ROOT / 'experiments/2026-10-06-evidence-census/synthesis/field-completeness.csv').open(encoding='utf-8') as f:
    for r in csv.DictReader(f):
        if r['index'] == 'Lipi pinned derivative':
            pkg[r['field']] = (int(r['present']) if r['present'] != '' else None, r['denominator'], r['percent'], r['measurement'])
print('N faces', N)
names = {'named_site': 'named_site', 'findspot(room-grid)': 'findspot', 'stratum_or_phase(period or phase)': 'stratum_or_phase', 'depth': 'depth',
         'date_or_period_label(time)': 'date_or_period_label', 'dimensions(any positive)': 'dimensions', 'dimensions_all_three': 'dimensions_all_three',
         'material': 'material', 'registration(excavation-idno)': 'registration_numbers', 'CISI_identifier(source_cisi)': 'CISI_identifier',
         'calendar_date_assertion(time)': 'calendar_date_assertion'}
for k, v in mine.items():
    if k in names:
        p = pkg[names[k]]
        print(f'{k:55s} mine={v:5d} ({100*v/N:6.2f}%)  package={p[0]} ({p[2]}%)  match={v == p[0]}  label={p[3]}')
    else:
        print(k, v)
print('package rows for structural fields:', {k: pkg[k] for k in ['absolute_date', 'photographs', 'licence']})
