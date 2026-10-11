"""Replay corpus counts, sampled lexical witnesses and coverage independently."""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, re
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',default='run-2026-10-09-v3');args=p.parse_args()
    out=HERE/args.run;x=read(out/'candidates.json');rows=x['rows'];s=x['summary'];checks={}
    assert len(rows)==713 and len({r['code'] for r in rows})==713
    assert not ({'000','999'}&{r['code'] for r in rows})
    assert all(r['preferred_meaning'] and r['alternatives'] for r in rows)
    assert sum(not r['inherited'] for r in rows)==596
    checks['complete_inventory_and_assignment']=True
    allrows=[json.loads(v) for v in (ROOT/'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
    clean=[json.loads(v) for v in (ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]
    distinct={tuple(r['signs_reading_rtl']) for r in clean}
    tokens=Counter(s for r in allrows for s in r['signs_visual_ltr'] if s not in {'000','999'})
    pos={}
    for seq in distinct:
        for i,code in enumerate(seq):
            position='singleton' if len(seq)==1 else 'initial' if i==0 else 'final' if i==len(seq)-1 else 'medial'
            pos.setdefault(code,Counter())[position]+=1
    for r in rows:
        assert tokens[r['code']]==r['observations']['whole_corpus_tokens'],r['code']
        assert dict(pos.get(r['code'],{}))==r['observations']['positions'],r['code']
    assert len(distinct)==1859 and len(allrows)==5680 and len(clean)==2930
    checks['independent_corpus_and_position_recount']=True
    manifest=read(HERE/'run-2026-10-08-v1/input-manifest.json')
    assert all(digest(ROOT/v['path'])==v['sha256'] for v in manifest['inputs'])
    checks['first_pass_inputs_still_match']=True
    assert digest(HERE/'analyze.py')==manifest['code_sha256']
    checks['first_pass_analysis_code_unchanged']=True
    for name in ['new-anchors.json','preferred-lexical-summary.json','alternative-lexical-summary.json']:
        assert digest(out/name)==digest(HERE/'run-2026-10-09-v2'/name),name
    checks['preserved_lexical_outputs_reused_exactly']=True
    assert {r['code'] for r in rows if r['inherited']}==set(read(HERE/'run-2026-10-08-v1/inherited-seeds.json')['by_wells'])
    checks['inherited_anchors_preserved']=True
    for r in rows:
        if not r['inherited']:assert all(r['dictionary_attestations'].values()),r['code']
        assert (ROOT/r['font_drawing']['path']).is_file(),r['code']
        for ref in r['reference_class_drawings']:assert (ROOT/ref['path']).is_file()
    checks['new_comparison_attestations_and_drawing_links']=True
    # A separate raw-header parse checks witnesses against the retained lexicon.
    text=(ROOT/'data/raw/2026-10-08-bonta-review/acquisition-2026-10-08-v1/mw.txt').read_text(encoding='utf-8')
    headers={m[1]:m[2] for m in re.finditer(r'<L>([^<\n]+)<pc>[^<\n]+<k1>([^<\n]+)',text)}
    table=str.maketrans({'A':'a','I':'i','U':'u','k':'k','K':'k','g':'k','G':'k','c':'c','C':'c','j':'c','J':'c',
        'w':'t','W':'t','q':'t','Q':'t','t':'d','T':'d','d':'d','D':'d','p':'p','P':'p','b':'p','B':'p',
        'S':'s','z':'s','R':'n','F':'f','X':'x'})
    sample=Counter()
    for scenario in ['preferred','alternative']:
        witness=read(ROOT/f'data/raw/2026-10-08-bonta-extension/run-2026-10-09-v2/{scenario}-lexical-witnesses.json')
        for code in sorted(witness)[::11]:
            for rank in witness[code]['ranking'][:3]:
                for e in rank['examples'][:2]:
                    assert headers[e['lexicon_record']]==e['headword']
                    made=e['pre']+e['residual']+e['post']
                    if e['match']=='exact':assert made==e['headword'];sample['exact']+=1
                    else:assert made.translate(table)==e['headword'].translate(table);sample['normalized']+=1
        for u,r in witness.items():
            for context in r['patterns']:
                window=tuple(context['window']);assert any(window==seq[i:i+len(window)] for seq in distinct for i in range(len(seq)-len(window)+1))
        checks[f'{scenario}_window_and_sampled_word_reconstruction']=True
    checks['dictionary_witness_samples']=dict(sample)
    base=read(ROOT/'data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/lexical-witnesses.json')
    expanded=read(ROOT/'data/raw/2026-10-08-bonta-extension/run-2026-10-09-v2/preferred-lexical-witnesses.json')
    new={w for a in read(out/'new-anchors.json') for w in a['codes']}; added={}
    for u,r in expanded.items():
        old={v['pattern'] for v in base.get(u,{}).get('patterns',[])}
        for c in r['patterns']:
            if set(c['window'])&new:
                assert c['pattern'] not in old
                added.setdefault(u,[]).append(c['pattern'])
    assert len(added)==111 and sum(map(len,added.values()))==256
    checks['new_anchor_windows_were_additional']=True
    examples=read(ROOT/f'data/raw/2026-10-08-bonta-extension/{args.run}/worked-examples.json')
    records={r['record_id']:r for r in clean}
    for e in examples:
        assert e['sequence']==records[e['record_id']]['signs_reading_rtl']
        assert [g['code'] for g in e['working_glosses']]==e['sequence']
    checks['worked_examples_retain_actual_records']=True
    result={'status':'Verified computation; semantic claims remain exploratory','run':args.run,
        'checks':checks,'catalogue_sha256':digest(out/'candidates.json'),
        'verification_code_sha256':digest(Path(__file__))}
    target=out/'verification.json'
    if target.exists():raise FileExistsError(target)
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
