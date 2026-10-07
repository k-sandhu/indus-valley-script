"""Reviewer check of the headline numbers in synthesis README.md and REPORT.md (independent recomputation).

'stated' values are typed from the prose (location given). 'recomputed' values come from the inputs:
data/normalized/*.jsonl, the batch site-rows.json files, the collections raw records, and saved outputs when the
quantity is only stored there. The IM77 site table (printed p. 6) is typed from the page image the reviewer read.
Writes review/headline-numbers-check.csv.
"""
import csv
import json
import re
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SYN = ROOT / 'experiments/2026-10-06-evidence-census/synthesis'
BATCH = ROOT / 'experiments/2026-10-06-evidence-census/sites-deep'
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07'


def J(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def jl(p):
    return [json.loads(x) for x in Path(p).read_text(encoding='utf-8-sig').splitlines() if x.strip()]


faces = jl(ROOT / 'data/normalized/lipi_observed_faces.jsonl')
mayig = jl(ROOT / 'data/normalized/mayig_faces.jsonl')
by_site = collections.defaultdict(list)
for f in faces:
    by_site[f['site']].append(f)
out = []


def add(claim, stated, recomputed, where, note=''):
    ok = (stated == recomputed)
    out.append(dict(claim=claim, stated=stated, recomputed=recomputed, result='confirmed' if ok else 'DISCREPANCY', stated_in=where, note=note))


def rows_of(p):
    d = J(p)
    return d if isinstance(d, list) else d.get('sites') or d.get('rows')


batches = {b: rows_of(BATCH / b / 'site-rows.json') for b in ['a-pakistan-afghanistan', 'b-gujarat-kutch-maharashtra', 'c-north-india', 'd-finds-abroad']}
for b, want in zip(batches, [37, 25, 25, 36]):
    add('rows in ' + b[:1].upper(), want, len(batches[b]), 'REPORT table')
add('total site rows', 123, sum(len(v) for v in batches.values()), 'README para 2')

labels_by_batch = {}
for b, rr in batches.items():
    labels = []
    for r in rr:
        lc = r.get('local_corpus') or {}
        for l in (lc.get('records') or [lc]):
            if l.get('site'):
                labels.append(l['site'])
    labels_by_batch[b] = labels
    fs = sum(len(by_site[l]) for l in labels)
    fam = sum(len({x['object_family_id'] for x in by_site[l]}) for l in labels)
    cis = sum(len({x['source_cisi'] for x in by_site[l] if x['source_cisi'] != '-'}) for l in labels)
    want = {'a-pakistan-afghanistan': (4837, 3908, 3637), 'b-gujarat-kutch-maharashtra': (496, 460, 199), 'c-north-india': (290, 271, 232), 'd-finds-abroad': (42, 42, 9)}[b]
    add(b[:1].upper() + ' faces', want[0], fs, 'REPORT table')
    add(b[:1].upper() + ' families', want[1], fam, 'REPORT table')
    add(b[:1].upper() + ' sum of site-level distinct CISI ids', want[2], cis, 'REPORT table')

allfaces = sum(len(by_site[l]) for ls in labels_by_batch.values() for l in ls)
uniq = {l for ls in labels_by_batch.values() for l in ls}
add('pooled face mentions across batches', 5665, allfaces, 'REPORT para 3')
add('represented local faces (each label once)', 5652, sum(len(by_site[l]) for l in uniq), 'README para 2')
add('represented local families', 4668, len({x['object_family_id'] for l in uniq for x in by_site[l]}), 'README para 2')
add('repeated face mentions removed', 13, allfaces - sum(len(by_site[l]) for l in uniq), 'REPORT para 3')
add('Unknown-label faces', 28, len(by_site['Unknown']), 'README para 2')
add('Unknown-label families', 27, len({x['object_family_id'] for x in by_site['Unknown']}), 'README para 2')
add('all local faces / families', (5680, 4695), (len(faces), len({x['object_family_id'] for x in faces})), 'README para 2')

seen = set()
reg = {}
for b in batches:
    mine = {l for l in labels_by_batch[b] if l not in seen}
    reg[b] = sum(len(by_site[l]) for l in mine)
    seen |= mine
add('regional faces A/B/C/D', (4837, 491, 290, 34), tuple(reg.values()), 'REPORT section Coverage')


def key(v):
    m = re.fullmatch(r'\s*([A-Za-z]+)-?(\d+)\s*', str(v))
    return (m[1].casefold(), int(m[2])) if m else None


def rng(t):
    m = re.fullmatch(r'\s*([A-Za-z]+)\s*(\d+)\s*[–-]\s*(\d+)\s*', t)
    return m[1], int(m[2]), int(m[3])


rr = []
for r in batches['b-gujarat-kutch-maharashtra']:
    for c in r.get('cisi_coverage', []):
        if c.get('volume') == 'CISI1' and c.get('identifier_range'):
            rr.append(('B', r['canonical_name'], c['identifier_range'], (r.get('local_corpus') or {}).get('site')))
for r in batches['c-north-india']:
    c = r['cisi_coverage']
    if c.get('entry_range'):
        rr.append(('C', r['canonical_name'], c['entry_range'], (r.get('local_corpus') or {}).get('site')))
acc = collections.defaultdict(lambda: [0, 0, 0])
per = {}
for b, name, text, lab in rr:
    p, lo, hi = rng(text)
    exp = {(p.casefold(), n) for n in range(lo, hi + 1)}
    have = {key(f['source_cisi']) for f in by_site.get(lab, [])} if lab else set()
    m = len(exp & have)
    per[name] = (len(exp), m, len(exp) - m)
    for k in (b, 'ALL'):
        acc[k][0] += len(exp)
        acc[k][1] += m
        acc[k][2] += len(exp) - m
add('number of CISI 1 ranges (B+C)', 19, len(rr), 'README para 1')
add('Gujarat ten ranges: entries/match/absent', (317, 196, 121), tuple(acc['B']), 'REPORT range table')
add('North India nine ranges: entries/match/absent', (176, 131, 45), tuple(acc['C']), 'REPORT range table')
add('Combined 19 ranges: entries/match/absent', (493, 327, 166), tuple(acc['ALL']), 'README para 1')
add('match percentage of 493', 66.33, round(100 * acc['ALL'][1] / acc['ALL'][0], 2), 'REPORT para 1')
for n, w in [('Lothal', (290, 179, 111)), ('Kalibangan', (122, 96, 26)), ('Banawali', (37, 23, 14))]:
    add(n + ': entries/match/absent', w, per[n], 'REPORT range table')

rd = {key(f['source_cisi']) for f in by_site['Rahman-deri']}
exp = {('rhd', n) for n in range(1, 271)}
add('Rehman Dheri: entries/match/absent', (270, 2, 268), (270, len(exp & rd), 270 - len(exp & rd)), 'REPORT paragraph on pools')
sk = {key(f['source_cisi']) for f in faces if 'sarai' in f['site'].casefold() or 'skh' in str(f['source_cisi']).casefold()}
add('Sarai Khola: 10 entries, no local keys', (10, 0), (10, len({('skh', n) for n in range(1, 11)} & sk)), 'REPORT paragraph on pools')

cc = list(csv.DictReader((SYN / 'catalogue-coverage.csv').open(encoding='utf-8')))
a1 = [r for r in cc if r['batch'].startswith('a') and r['edition'] == 'CISI1']
add('A selected CISI 1 ranges: count', 6, len(a1), 'REPORT (six selected CISI 1 ranges)', 'catalogue-coverage.csv lists four: Amri, Chanhu-daro, Harappa, Mohenjo-daro')
add('A selected CISI 1 ranges: entries/matches', (936, 813), (sum(int(r['catalogue_entries']) for r in a1), sum(int(r['local_matching_entries']) for r in a1)), 'REPORT range paragraph')

im77 = {'Mohenjo-daro': 1540, 'Harappa': 985, 'Chanhu-daro': 66, 'Lothal': 165, 'Kalibangan': 99, 'Alamgirpur': 3, 'Amri': 2, 'Banawali': 7,
        'Chandigarh': 4, 'Desalpar': 2, 'Dholavira': 1, 'Jhukar': 1, 'Kot Diji': 1, 'Lohumjo-daro': 1, 'Rakhigarhi': 1, 'Rojdi': 2,
        'Ropar (Rupar)': 2, 'Surkotada': 5, 'Tarkhanewala Dera': 1}
cov = J(SYN / 'coverage.json')
true_im = collections.defaultdict(lambda: [0, 0])
for s in cov['sites']:
    if s['site'] in im77:
        true_im[s['assigned_region'][:1]][0] += im77[s['site']]
        true_im[s['assigned_region'][:1]][1] += 1
add('IM77 selected objects, region A (sum, sites)', (2596, 7), tuple(true_im['a']), 'REPORT IM77 paragraph')
add('IM77 selected objects, region B (sum, sites)', (175, 5), tuple(true_im['b']), 'REPORT IM77 paragraph')
add('IM77 selected objects, region C (sum, sites)', (118, 7), tuple(true_im['c']), 'REPORT IM77 paragraph', 'IM77 p.6 prints Tarkhanawala Dera 1; batch C row records 2')
add('IM77 total 2,906 = 3,455 - 549', 2906, 3455 - 549, 'REPORT table')


def present(v):
    s = str(v).strip().casefold() if v is not None else ''
    return s not in {'unknown', 'none', 'null', 'n/a'} and bool(re.sub(r'[\s\-?]', '', s))


def pos(v):
    try:
        return float(v) > 0
    except (TypeError, ValueError):
        return False


def M(f, k):
    return f['metadata'].get(k)


rg = sum(present(M(f, 'room-grid')) for f in faces)
pp = sum(present(M(f, 'period')) or present(M(f, 'phase')) for f in faces)
d3 = sum(all(pos(M(f, k)) for k in ['horizontal(mm)', 'vertical(mm)', 'thickness(mm)']) for f in faces)
add('room/grid present (faces, percent)', (2191, 38.57), (rg, round(100 * rg / len(faces), 2)), 'README/REPORT table')
add('period or phase present (faces, percent)', (3172, 55.85), (pp, round(100 * pp / len(faces), 2)), 'REPORT table')
add('all three positive dimensions (faces, percent)', (1151, 20.26), (d3, round(100 * d3 / len(faces), 2)), 'REPORT table')

rec = J(RAW / 'focused-records.json')
pairs = J(RAW / 'paired-comparisons.json')
add('museum original records', 114, len(rec), 'README para 1')
inst = ['National Museum, New Delhi', 'Indian Museum, Kolkata', 'British Museum', 'Penn Museum', 'Louvre', 'Metropolitan Museum of Art']
add('by institution NM/Kolkata/BM/Penn/Louvre/Met', (76, 18, 6, 5, 4, 5), tuple(sum(r['institution'] == n for r in rec) for n in inst), 'task statement and join-summary.json')
add('confirmed identifier joins / unjoined', (61, 53), (len(pairs), len(rec) - len(pairs)), 'README para 1')
meth = ['published_CISI_concordance', 'exact_excavation', 'normalized_excavation', 'shared_field_and_published_plate', 'published_Marshall_composite']
add('join methods 36/13/6/5/1', (36, 13, 6, 5, 1), tuple(sum(p['join']['join_method'] == m for p in pairs) for m in meth), 'REPORT join paragraph')
ids = {r['record_id'] for p in pairs for r in p['corpus_faces']}
fam = {r['object_family_id'] for p in pairs for r in p['corpus_faces']}
add('joined faces / families', (67, 61), (len(ids), len(fam)), 'REPORT join paragraph')
cmp_ = collections.Counter()
for p in pairs:
    for k, v in p['comparison'].items():
        if isinstance(v, str):
            cmp_[(k, v)] += 1
add('museum-corpus disagreements site/material/dimension/count', (1, 4, 5, 9),
    (cmp_[('site_comparison', 'disagreement')], cmp_[('material_comparison', 'disagreement')], cmp_[('dimensions_comparison', 'outside_tolerance')], cmp_[('inscription_comparison', 'count_disagreement')]),
    'REPORT last metadata paragraph')

rj = J(SYN / 'register-joins.json')
add('register joins: publications / pub-batch links / dataset links / collection links', (17, 32, 15, 37),
    (len(rj['publication_site_links']), len(rj['publication_batch_source_links']), len(rj['dataset_source_links']), len(rj['collection_source_links'])), 'REPORT join paragraph')
ta = J(SYN / 'source-title-audit.json')
tr = J(SYN / 'source-title-review.json')
add('flagged titles / files / prose payload / bookseller', (17, 5, 13, 4),
    (len(ta['flags']), len(ta['affected_files']), sum(r['classification'] == 'prose_or_search_snippet_payload' for r in tr['records']),
     sum(r['classification'] == 'extended_bookseller_or_review_metadata' for r in tr['records'])), 'REPORT last section')
sa = J(SYN / 'source-sample-audit.json')
add('20-site sample outcomes supported/qualified', (14, 6), (sum(r['outcome'] == 'supported' for r in sa['rows']), sum(r['outcome'] == 'qualified' for r in sa['rows'])), 'README para 3')
add('priority pools / conflicts / sources', (8, 7, 19), (len(J(SYN / 'priority-gaps.json')['gaps']), len(J(SYN / 'conflicts.json')['conflicts']), len(J(SYN / 'sources.json')['sources'])), 'README outputs table')
add('Harappa + Mohenjo-daro faces / families', (4640, 3716),
    (len(by_site['Harappa']) + len(by_site['Mohenjo-daro']), len({x['object_family_id'] for s in ('Harappa', 'Mohenjo-daro') for x in by_site[s]})), 'REPORT where further evidence')
add('Mayig faces / tokens / all Mohenjo-daro', (179, 1003, True), (len(mayig), J(ROOT / 'data/normalized/mayig_summary.json')['tokens'], all(m['site'] == 'Mohenjo-daro' for m in mayig)), 'REPORT table')
add('checks.json count / verification v2 count / package checks', (728, 1069, 94),
    (J(SYN / 'checks.json')['checks_count'], J(SYN / 'verification-2026-10-07-v2.json')['checks_count'], J(SYN / 'package-checks-2026-10-07-v1.json')['checks_count']), 'README paras 3-4')

with (SYN / 'review/headline-numbers-check.csv').open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
print(len(out), 'claims;', sum(o['result'] == 'confirmed' for o in out), 'confirmed')
for o in out:
    if o['result'] != 'confirmed':
        print('DISCREPANCY:', o['claim'], '| stated', o['stated'], '| recomputed', o['recomputed'], '|', o['note'])
