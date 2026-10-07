"""Reviewer check of the Wells 090/091 identification using two independent annotations of the same seals.

The Lipi export codes signs with Wells numbers. The Mayig corpus annotates 179 unicorn-seal faces
from Mohenjo-daro with its own sign classes (P-classes) whose schema lists Wells compatibility.
For faces present in both (joined on the CISI number) with equal sign counts, this script counts
how often a Lipi code in {090, 091, 093, 097} sits at the same reading position as a Mayig class
in {P013, P014, P015, P016}. Aggregate counts only; no sequences are written.
"""
import json, re, collections, ast
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
lipi = [json.loads(l) for l in open(ROOT / 'data/normalized/lipi_observed_faces.jsonl', encoding='utf-8')]
may = [json.loads(l) for l in open(ROOT / 'data/normalized/mayig_faces.jsonl', encoding='utf-8')]
schema = json.load(open(ROOT / 'data/normalized/mayig_sign_schema.json', encoding='utf-8'))['signs']

def base(s):
    m = re.fullmatch(r'([A-Za-z]+)-?(\d+)([A-Za-z]?)', str(s).strip())
    return (m[1].upper(), int(m[2])) if m else None

by = collections.defaultdict(list)
for r in lipi:
    b = base(r['source_cisi'])
    if b: by[b].append(r)
TARGET_W = {'090', '091', '093', '097'}; TARGET_P = {'P013', 'P014', 'P015', 'P016'}
cross = collections.Counter(); joined = same_len = positions = 0
for m in may:
    b = base(m['object_family_id'])
    if not b or b not in by: continue
    joined += 1
    ms = m['signs_reading_rtl']; ms = ast.literal_eval(ms) if isinstance(ms, str) else ms
    for r in by[b]:
        ls = r['signs_reading_rtl']
        if len(ls) == len(ms) and r['complete_observed']:
            same_len += 1
            for a, p in zip(ls, ms):
                positions += 1
                if a in TARGET_W or p in TARGET_P: cross[(a, p)] += 1
            break
agree = sum(n for (a, p), n in cross.items() if schema.get(p, {}).get('wells_graphemes') and ('W' + a) in schema[p]['wells_graphemes'])
out = {'status': 'Reviewer check, not a package result',
       'mayig_faces_joined_to_lipi_cisi_number': joined, 'faces_with_equal_length_used': same_len, 'aligned_positions': positions,
       'positions_involving_a_target_code_or_class': sum(cross.values()), 'positions_where_lipi_wells_code_is_listed_for_the_mayig_class': agree,
       'cross_tabulation': [{'lipi_code': a, 'mayig_class': p, 'positions': n, 'wells_listed_for_class': schema.get(p, {}).get('wells_graphemes')} for (a, p), n in sorted(cross.items())],
       'note': 'No co-annotated position carries Wells 091 or 097, so the twins identification has no independent data-level check here.'}
Path(__file__).with_name('lipi_mayig_alignment.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in out.items() if k != 'cross_tabulation'}, indent=2)); print(out['cross_tabulation'])
