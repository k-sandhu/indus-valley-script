"""Replay exactness from the audit payload without importing its implementation."""
import hashlib
import json
from pathlib import Path
PKG=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    summary=read(PKG/'increment-audit-v1.json')
    detailed=read(Path(summary['outputs'][0]['physical_path']))
    subset=read(Path(summary['outputs'][1]['physical_path']))
    exact=0;flagged=0
    for row in detailed:
        for c in row['candidates']:
            a,b=c['original_candidate']['surface_members']
            left,right=c['original_candidate']['lemma_candidates']
            eligible=(left.endswith('u') and len(left)>=3 and a in [left[:-1]+z for z in ['am','aṅ','añ','an']] and b==right and a+b==row['form'])
            assert eligible==c['exact_candidate']
            exact+=eligible;flagged+=c['folding_dependent']
    checks={'frozen_extraction_unchanged':sha(Path(summary['source']))==summary['input_sha256'],
        'audit_output_hashes_match':all(sha(Path(p['physical_path']))==p['sha256'] for p in summary['outputs']),
        'exact_count_replayed':exact==summary['exact_candidate_analyses']==57,
        'folding_count_replayed':flagged==summary['folding_dependent_analyses']==2,
        'filtered_count_replayed':sum(len(r['exact_candidates']) for r in subset)==57,
        'all_subset_rows_unresolved_and_ineligible':all(r['morphology_status']=='unresolved_increment_morphology' and r['scorer_eligible'] is False for r in subset),
        'audit_tests_pass':summary['tests_pass']}
    out=dict(pass_all=all(checks.values()),checks=checks,author_check=True,substantive_rebus_recomputed=False)
    with (PKG/'increment-audit-verification-v1.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps(out))
    return 0 if out['pass_all'] else 1
if __name__=='__main__':raise SystemExit(main())
