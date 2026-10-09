"""Reviewer audit of the reading-to-corpus joins (identifiers and counts only in the output).

Reads the local reading inventory and the pinned Lipi faces (data/), recomputes the CISI join independently,
checks that no join depends on equal ICIT numbers, and compares each joined entry's printed ICIT number and
glyph count with the joined corpus object. From the repository root:
    python -B -X utf8 experiments/2026-10-08-bonta-review/review-pdf/join_audit.py
"""
import collections, json, random, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
W = ROOT / 'data/raw/2026-10-08-bonta-review/pdf-2026-10-09-v1/'
inv = json.loads((W / 'reading-inventory-v4.json').read_text(encoding='utf-8'))
att = [r for r in inv if r['is_reading_attempt']]
faces = [json.loads(l) for l in (ROOT / 'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
canon = lambda c: re.sub(r'\s+', '', c).upper()
bycisi = collections.defaultdict(list)
for f in faces:
    bycisi[canon(f['source_cisi'])].append(f)
fam = collections.defaultdict(list)
for f in faces:
    fam[f['object_family_id']].append(f)
out = {'status': 'Exploratory (reviewer audit)'}
# 1. independent join from the printed CISI aliases only
mine = {}
for r in att:
    recs = sorted({f['record_id'] for c in r['cisi_aliases'] for f in bycisi[canon(c)]})
    mine[r['reading_id']] = recs
out['independent_join_equals_package'] = all(mine[r['reading_id']] == sorted(r['joined_record_ids']) for r in att if r['join_status'] not in ('parent entry explicit CISI', 'joined through explicit same-manuscript MH/CISI alias'))
out['joined_attempts'] = sum(bool(r['joined_record_ids']) for r in att)
out['join_status_counts'] = dict(collections.Counter(r['join_status'] for r in att))
# 2. no joined record is reached through its ICIT-like family number: every joined record's CISI is a printed alias
byrec = {f['record_id']: f for f in faces}
viol = 0
for r in att:
    if r['join_status'] in ('joined explicit CISI', 'ambiguous aliases'):
        for i in r['joined_record_ids']:
            viol += canon(byrec[i]['source_cisi']) not in {canon(c) for c in r['cisi_aliases']}
out['joins_whose_corpus_CISI_is_not_a_printed_alias'] = viol
# 3. printed ICIT number against corpus family id
agree = dis = noic = 0
conflicts = {}
for r in att:
    if not r['joined_record_ids']:
        continue
    famids = {byrec[i]['object_family_id'] for i in r['joined_record_ids']}
    ic = {re.sub(r'\D', '', a) for a in r['icit_aliases']}
    if not ic:
        noic += 1
        continue
    if famids & ic:
        agree += 1
    else:
        dis += 1
        key = (tuple(sorted(r['cisi_aliases'])), tuple(sorted(r['icit_aliases'])))
        g = len(r['sign_sequence_visual_ltr'])
        cis_len = sorted({len(byrec[i]['signs_visual_ltr']) for i in r['joined_record_ids']})
        icit_len = sorted({len(f['signs_visual_ltr']) for i in ic for f in fam.get(i, [])})
        icit_cisi = sorted({f['source_cisi'] for i in ic for f in fam.get(i, [])})
        e = conflicts.setdefault(key, {'cisi_aliases': list(key[0]), 'printed_icit': list(key[1]), 'rows': [], 'figure_glyphs': g,
                                       'corpus_text_lengths_of_CISI_object': cis_len, 'corpus_object_with_printed_ICIT_number': icit_cisi,
                                       'corpus_text_lengths_of_that_object': icit_len})
        e['rows'].append(r['reading_id'])
out['printed_ICIT_agrees_with_joined_corpus_object'] = agree
out['printed_ICIT_disagrees'] = dis
out['no_printed_ICIT'] = noic
out['disagreement_objects'] = list(conflicts.values())
for e in out['disagreement_objects']:
    e['figure_glyph_count_matches_CISI_object'] = e['figure_glyphs'] in e['corpus_text_lengths_of_CISI_object']
    e['figure_glyph_count_matches_printed_ICIT_object'] = e['figure_glyphs'] in e['corpus_text_lengths_of_that_object']
# 4. glyph count against joined corpus text length (screen, not proof)
c = collections.Counter()
for r in att:
    if r['joined_record_ids']:
        g = len(r['sign_sequence_visual_ltr'])
        L = [len(byrec[i]['signs_visual_ltr']) for i in r['joined_record_ids']]
        c['equal' if g in L else 'within1' if any(abs(g - l) <= 1 for l in L) else 'differs'] += 1
out['glyph_count_vs_joined_text_length'] = dict(c)
# 5. seeded sample of 12 joins (identifiers and counts only)
rng = random.Random(909)
sample = rng.sample([r for r in att if r['joined_record_ids']], 12)
out['sample_of_12'] = [{'reading_id': r['reading_id'], 'page': r['source_page'], 'label': r['primary_label'], 'printed_CISI': r['cisi_aliases'],
                        'printed_ICIT': r['icit_aliases'], 'join_status': r['join_status'], 'joined_record_ids': r['joined_record_ids'],
                        'corpus_CISI': sorted({byrec[i]['source_cisi'] for i in r['joined_record_ids']}),
                        'corpus_site': sorted({byrec[i]['site'] for i in r['joined_record_ids']}),
                        'figure_glyphs': len(r['sign_sequence_visual_ltr']),
                        'corpus_text_lengths': [len(byrec[i]['signs_visual_ltr']) for i in r['joined_record_ids']]} for r in sample]
(Path(__file__).resolve().parent / 'join-audit.json').write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding='utf-8')
print(json.dumps({k: v for k, v in out.items() if k not in ('sample_of_12',)}, indent=1, ensure_ascii=False))
