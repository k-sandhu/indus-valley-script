"""Independent aggregate replay, without the parser or repair adapter."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PKG=Path(__file__).resolve().parents[1]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-lexical-extraction-extension/run-v1')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    with (RAW/'winslow-entries.jsonl').open(encoding='utf8') as f:rows=[json.loads(l) for l in f]
    deltas=read(RAW/'member-deltas.json')
    result=read(PKG/'results-v1.json')
    transition=Counter(f"{len(r['before'])}->{len(r['after'])}" for r in deltas)
    checks={
        'row_count':len(rows)==result['records']==69310,
        'selected_two_member_count':sum(len(r['members'])==2 for r in rows)==result['revised_two_member'],
        'member_delta_count':sum(r['members']!=r['original_members'] for r in rows)==len(deltas)==result['member_changes'],
        'output_hash':sha(RAW/'winslow-entries.jsonl')==result['output_sha256'],
        'delta_hash':sha(RAW/'member-deltas.json')==result['delta_sha256'],
        'eligibility_remains_false':all(r['comparative_scorer_eligible'] is False for r in rows),
        'all_subentries_have_parent_mark_fields':all(r['parent_origin_mark_present'] is not None for r in rows if r['kind']=='sub'),
        'active_adapter_pin':sha(PKG/'code/extract.py')==read(PKG/'FREEZE-v3.json')['pins'][(PKG/'code/extract.py').relative_to(ROOT).as_posix()],
        'archived_adapter_v1_pin':sha(PKG/'code/extract-v1-frozen.py')==read(PKG/'FREEZE-v1.json')['pins'][(PKG/'code/extract.py').relative_to(ROOT).as_posix()],
        'archived_adapter_v2_pin':sha(PKG/'code/extract-v2-frozen.py')==read(PKG/'FREEZE-v2.json')['pins'][(PKG/'code/extract.py').relative_to(ROOT).as_posix()],
        'author_validation_v2_pass':read(PKG/'validation-v2.json')['pass_all']}
    value=dict(pass_all=all(checks.values()),checks=checks,transition_counts=dict(transition),
        other_member_changes=len(deltas)-result['added_two_member']-result['removed_two_member']-result['changed_two_member'],
        independent_reviewer=False,scope='Author independent arithmetic and hashes; no linguistic adjudication')
    with (PKG/'verification-v1.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2);f.write('\n')
    print(json.dumps(value))
    return 0 if value['pass_all'] else 1
if __name__=='__main__':raise SystemExit(main())
