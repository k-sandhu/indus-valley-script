"""Export observational many-to-many catalogue compatibility from Mayig schemas.

This is an annotator's inventory crosswalk, not a semantic interpretation and not
an independently adjudicated mapping for every token. Run from any directory.
"""
from pathlib import Path
import json, collections, hashlib

ROOT = Path(__file__).resolve().parents[2]
src = ROOT / 'data/normalized/mayig_sign_schema.json'
schema = json.loads(src.read_text(encoding='utf-8'))['signs']
by_w = collections.defaultdict(list)
by_p = {}
for p, row in schema.items():
    out = {
        'mayig_class': p, 'description': row['description'],
        'wells_candidates': row.get('wells_graphemes', []),
        'mahadevan_candidates': row.get('mahadevan_graphemes', []),
        'parpola_candidates': row.get('parpola_graphemes', []),
        'features': row.get('features', []),
    }
    by_p[p] = out
    for w in out['wells_candidates']:
        by_w[w.removeprefix('W').zfill(3)].append(p)
pairs = [('817','861'),('817','820'),('233','235'),('235','240'),('390','405'),('705','706')]
target_pairs = []
for a,b in pairs:
    shared = sorted(set(by_w[a]) & set(by_w[b]))
    target_pairs.append({'wells_a':a,'wells_b':b,'a_classes':by_w[a],
                         'b_classes':by_w[b],'shared_mayig_classes':shared,
                         'shares_a_class': bool(shared)})
out = {
    'source': 'https://github.com/mayig/indus-valley-script-corpus',
    'commit': 'ad2f1e218a34b8c33c57de0d6cb8d99272765bbb',
    'license': 'MIT, Michael Carlson 2024',
    'source_schema_sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
    'mapping_status': 'Many-to-many candidate compatibility supplied by the Mayig annotator; not a token-level adjudication or transitive equivalence relation.',
    'sensitivity_rule': 'A pair shares a Mayig class iff its two Wells IDs have a nonempty intersection of listed classes. Do not use graph-connected components: overlapping candidate sets need not imply equivalence.',
    'by_wells_id': dict(sorted(by_w.items())), 'by_mayig_class': by_p,
    'target_pairs': target_pairs,
}
dest = ROOT / 'data/normalized/mayig_wells_class_crosswalk.json'
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'path':str(dest), 'wells_ids':len(by_w), 'classes':len(by_p), 'target_pairs':target_pairs},indent=2))
