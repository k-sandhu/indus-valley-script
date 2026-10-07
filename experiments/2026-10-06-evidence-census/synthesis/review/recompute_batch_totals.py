"""Independent recomputation of each batch row's local-corpus figures (reviewer script).

For every row in the four batches, count faces, distinct object_family_id and distinct source_cisi (excluding '-')
in data/normalized/lipi_observed_faces.jsonl under the row's own local_corpus.site label, and compare with the row's
stored figures. Then total each batch and the pooled, de-duplicated figures.
"""
import json, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
faces = [json.loads(l) for l in (ROOT / 'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8-sig').splitlines() if l.strip()]
by = collections.defaultdict(list)
for f in faces:
    by[f['site']].append(f)
B = ROOT / 'experiments/2026-10-06-evidence-census/sites-deep'
def rows_of(p):
    d = json.loads(p.read_text(encoding='utf-8-sig'))
    return d if isinstance(d, list) else d.get('sites') or d.get('rows')
res = {}
mism = []
labels_by_batch = {}
for b in ['a-pakistan-afghanistan', 'b-gujarat-kutch-maharashtra', 'c-north-india', 'd-finds-abroad']:
    tot = collections.Counter(); n = 0; labels = []
    for r in rows_of(B / b / 'site-rows.json'):
        n += 1
        lc = r.get('local_corpus') or {}
        recs = lc.get('records') or [lc]
        name = r.get('canonical_name', r.get('site'))
        for l in recs:
            site = l.get('site')
            sub = by.get(site, []) if site else []
            mine = {'faces': len(sub), 'object_families': len({x['object_family_id'] for x in sub}),
                    'distinct_cisi_ids': len({x['source_cisi'] for x in sub if x['source_cisi'] not in ('-', '', None)})}
            for k in mine:
                stored = l.get(k, 0) or 0
                tot[k] += stored
                if stored != mine[k]:
                    mism.append((b, name, site, k, stored, mine[k]))
            if site:
                labels.append(site)
    res[b] = dict(rows=n, **tot)
    labels_by_batch[b] = labels
print(json.dumps(res, indent=1))
print('row-level mismatches (batch, row, label, field, stored, recomputed):', mism)
allfaces = sum(v['faces'] for v in res.values())
uniq_labels = set(l for ls in labels_by_batch.values() for l in ls)
print('sum of batch faces', allfaces, '| distinct local labels referenced', len(uniq_labels),
      '| faces under distinct labels', sum(len(by[l]) for l in uniq_labels), '| families', len({x['object_family_id'] for l in uniq_labels for x in by[l]}))
print('faces under labels never referenced by any batch:', {s: len(v) for s, v in by.items() if s not in uniq_labels})
