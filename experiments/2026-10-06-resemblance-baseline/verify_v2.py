"""Independent checks of v2 arithmetic, saved source witnesses and coding changes."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

OWN=Path(__file__).resolve().parent
ROOT=OWN.parents[1]
RAW=ROOT/'data/raw/2026-10-06-resemblance-baseline'
INTS='segments curved loops L T X Y other terminals components dots'.split()
RULES={'R1':['segments','loops'],'R2':INTS,'R3':INTS+['symmetry','orientation'],'R3S':INTS+['symmetry']}

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    rows=read(RAW/'amendment-20261007/coder-a.json');queries=[r for r in rows if r['inventory']=='tamil']
    refs={name:[r for r in rows if r['inventory']==name and r.get('readable',True)] for name in ['indus','ogham','tifinagh']}
    counts=Counter()
    for record in read(OWN/'run-v2/observed.json'):
        fields=RULES[record['rule']]; inv=refs[record['inventory']]
        hit=[any(all(q[f]==r[f] for f in fields) for r in inv) for q in queries]
        assert sum(hit)==record['matched'];assert sum(hit)/42==record['rate'];counts['census_cells']+=1
        for band,stats in record['complexity'].items():
            inds=[i for i,q in enumerate(queries) if ('1-3' if q['segments']<=3 else '4-6' if q['segments']<=6 else '7+')==band]
            assert stats['matched']==sum(hit[i] for i in inds);assert stats['queries']==len(inds);counts['stratified_cells']+=1
    for record in read(OWN/'run-v2/subsampling.json'):
        fields=RULES[record['rule']];inv=refs[record['inventory']];n=record['n']
        sig=lambda r:tuple(r[f] for f in fields)
        freq=Counter(map(sig,inv));den=math.comb(len(inv),n)
        exact=sum(1-(math.comb(len(inv)-freq[sig(q)],n)/den if len(inv)-freq[sig(q)]>=n else 0) for q in queries)/42
        assert abs(exact-record['exact_mean'])<1e-12;counts['finite_subset_formula_cells']+=1
    for record in read(OWN/'run-v2/synthetic-null.json'):
        fields=RULES[record['rule']];inv=refs[record['inventory']];n=record['n'];sig=lambda r:tuple(r[f] for f in fields)
        freq=Counter(map(sig,inv));p={s:c/len(inv) for s,c in freq.items()}
        exact=sum(prob*(1-(1-prob)**n) for prob in p.values())
        fixed=sum(1-(1-p.get(sig(q),0))**n for q in queries)/42
        assert abs(exact-record['surrogate_query']['exact_mean'])<1e-12
        assert abs(fixed-record['fixed_tamil_query']['exact_mean'])<1e-12;counts['collision_formula_cells']+=1
    for rel,expected in read(OWN/'preserved-v1-review.json').items():assert sha(ROOT/rel)==expected;counts['preserved_hashes']+=1
    manifest=read(OWN/'run-v2/manifest.json')
    for key,path in [('protocol_sha256',OWN/'PROTOCOL.md'),('code_sha256',OWN/'analyze.py'),('amendment_code_sha256',OWN/'analyze_v2.py'),('coder_a_sha256',RAW/'amendment-20261007/coder-a.json'),('coder_b_sha256',RAW/'amendment-20261007/coder-b.json'),('corrections_sha256',RAW/'amendment-20261007/corrections-v2.json'),('reviewer_coding_sha256',OWN/'review/reviewer-coding.json'),('indus_selection_sha256',RAW/'amendment-20261007/indus-selection.json')]:assert manifest[key]==sha(path);counts['v2_manifest_hashes']+=1
    source_dir=RAW/'amendment-sources-20261007'
    for record in read(source_dir/'acquisition.json'):
        if 'local_path' in record:assert sha(ROOT/record['local_path'])==record['sha256'];counts['new_source_payload_hashes']+=1
    old=read(RAW/'coder-a-controls-tamil.json'); endpoint=read(RAW/'coder-a.json');old_lookup={r['id']:r for r in old}
    diffs={r['id']:{f:(old_lookup[r['id']][f],r[f]) for f in INTS+['symmetry','orientation'] if old_lookup[r['id']][f]!=r[f]} for r in endpoint if r['id'] in old_lookup}
    assert {k:v for k,v in diffs.items() if v}=={'T18':{'L':(0,2),'T':(3,1),'terminals':(3,2)}}
    for name in refs:
        inv=[r for r in endpoint if r['inventory']==name and r.get('readable',True)]
        for rule in ['R1','R2','R3']:
            fields=RULES[rule];q0=[r for r in endpoint if r['inventory']=='tamil'];q1=[old_lookup.get(q['id'],q) for q in q0]
            match=lambda qs:sum(any(all(q[f]==r[f] for f in fields) for r in inv) for q in qs)
            assert match(q0)==match(q1);counts['T18_invariance_cells']+=1
    sens=read(OWN/'run-v2/coding-sensitivity.json')['cells']
    for cell in sens:
        if cell['inventory']=='indus':
            tif=next(x for x in sens if x['inventory']=='tifinagh' and all(x[k]==cell[k] for k in ['query_coding','reference_coding','rule']))
            assert tif['matched']>=cell['matched'];counts['control_ordering_cells']+=1
    proposed=read(OWN/'registry-entry.json')
    assert set(proposed)=={'id','theme','status','question','outcome','challenge','remedy','evidence','retry_when'}
    for path in proposed['evidence']:assert (ROOT/path).is_file()
    print(json.dumps({'status':'Verified computation','checks':dict(counts),'registry_schema_and_evidence':True,'random_mark_generator_built':False},indent=2))

if __name__=='__main__':main()
