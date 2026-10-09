"""Reviewer recomputation of the post-outcome target attribution, written to review-pdf only.

Uses the package's Grammar class read-only with the frozen first/second/agreed-only operational mappings.
From the repository root:
    python -B -X utf8 experiments/2026-10-08-bonta-review/review-pdf/attribution_recheck.py
"""
import collections, copy, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/2026-10-08-bonta-review'))
from second_coder_sensitivity import Grammar, BASE
rd = lambda p: json.loads(p.read_text(encoding='utf-8'))
first = rd(BASE / 'mapping-first.json'); second = {r['sign_id']: r for r in rd(BASE / 'mapping-second.json')['rows']}
agreed = {r['sign_id'] for r in rd(BASE / 'mapping-agreed_only.json')['rows']}
rows = [json.loads(l) for l in (ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]
g = collections.defaultdict(list)
for r in rows: g[r['object_family_id']].append(r)
chosen = [sorted(v, key=lambda r: (-len(r['signs_reading_rtl']), r['record_id']))[0] for v in g.values()]
base = Grammar(first); b0 = [base.assess(tuple(r['signs_reading_rtl']))[0] for r in chosen]
out = []
for mode in ('second replacement', 'agreed omission'):
    for t in ('B069', 'B074', 'B075', 'B078'):
        if mode == 'agreed omission' and t in agreed: continue
        mp = copy.deepcopy(first)
        mp['rows'] = [second[r['sign_id']] if mode == 'second replacement' and r['sign_id'] == t else r for r in mp['rows']]
        if mode == 'agreed omission': mp['rows'] = [r for r in mp['rows'] if r['sign_id'] != t]
        gr = Grammar(mp); c = collections.Counter(); adj = 0; ch = 0
        for r, o in zip(chosen, b0):
            s = gr.assess(tuple(r['signs_reading_rtl'])); c[s[0]] += 1; adj += s[3]; ch += s[0] != o
        out.append({'mode': mode, 'target': t, 'classification': dict(c), 'fish_adjacent_pairs': adj, 'changed_classifications': ch})
pkg = rd(BASE / 'target-attribution.json')['diagnostic_results']
same = out == pkg
(Path(__file__).resolve().parent / 'attribution-recheck.json').write_text(json.dumps({'status': 'Exploratory (reviewer recomputation)', 'equals_package_diagnostic_results': same, 'results': out}, indent=1), encoding='utf-8')
print(same); [print(x) for x in out]
