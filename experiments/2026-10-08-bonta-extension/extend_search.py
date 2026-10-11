"""Extend the preserved lexical pass with newly proposed Sanskrit comparisons."""
import argparse, json
from collections import defaultdict
from pathlib import Path
from analyze import HERE, ROOT, RAW, INPUTS, load, lines, write, sha, import_seeds, lexical_search, slp
from new_anchors import ANCHORS, seeds_for_scenario

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',default='run-2026-10-09-v2');args=p.parse_args()
    out=HERE/args.run; raw=RAW/args.run
    out.mkdir(parents=True,exist_ok=False); raw.mkdir(parents=True,exist_ok=False)
    inherited,_=import_seeds()
    entries=load('data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json')
    unique=defaultdict(list)
    for r in lines(INPUTS[1]):unique[tuple(r['signs_reading_rtl'])].append(r)
    anchors=[]
    for a in ANCHORS:
        words=sorted(set(a['sanskrit_comparisons']+[a['alternative_probe']]))
        attested={w:[{'entry_id':x['entry_id'],'page_column':x['page_column']}
                    for x in entries.get(slp(w),[])] for w in words}
        assert all(attested.values()), (a['id'],attested)
        anchors.append({**a,'dictionary_attestations':attested})
    write(out/'new-anchors.json',anchors)
    write(out/'input-manifest.json',{'status':'Exploratory',
        'inputs':[{'path':x,'sha256':sha(ROOT/x)} for x in INPUTS],
        'preserved_first_pass':'run-2026-10-08-v1',
        'amendment_sha256':sha(HERE/'AMENDMENT-2026-10-09.json'),
        'anchor_code_sha256':sha(HERE/'new_anchors.py'),
        'search_code_sha256':sha(Path(__file__)),
        'pdf_sha256':sha(ROOT/'data/raw/2026-10-08-bonta-review/papers/A_Partial_Decipherment_of_the_Indus_Vall.pdf')})
    scenarios={}
    new_codes={w for a in ANCHORS for w in a['codes']}
    for name,alternative in [('preferred',False),('alternative',True)]:
        print('Dictionary search:',name,flush=True)
        lex,witness,values=lexical_search(unique,seeds_for_scenario(inherited,alternative),entries)
        write(raw/f'{name}-lexical-witnesses.json',witness)
        write(raw/f'{name}-lexical-summary-with-examples.json',lex)
        safe={u:{**{k:v for k,v in r.items() if k!='top'},'top':[
                {k:v for k,v in c.items() if k!='examples'} for c in r['top']]} for u,r in lex.items()}
        write(out/f'{name}-lexical-summary.json',safe)
        added={u:[p['pattern'] for p in w['patterns'] if set(p['window'])&new_codes] for u,w in witness.items()}
        added={u:v for u,v in added.items() if v}
        write(out/f'{name}-new-anchor-context-counts.json',{u:len(v) for u,v in added.items()})
        scenarios[name]={'searched_unknown_codes':len(lex),
            'unknown_codes_in_new_anchor_windows':len(added),
            'distinct_new_anchor_windows':sum(map(len,added.values())),
            'multiple_context_codes':sum(r['pattern_count']>=2 for r in lex.values()),
            'nonempty_full_intersections':sum(r['full_intersection_classes']>0 for r in lex.values())}
    write(out/'search-summary.json',{'anchor_families':len(ANCHORS),'new_anchor_codes':len(new_codes),'scenarios':scenarios})
    print(json.dumps(scenarios,indent=2),flush=True)

if __name__=='__main__':main()
