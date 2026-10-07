"""Read-only independent checks of source hashes, census arithmetic and manifests."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-06-resemblance-baseline'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    counts={'source_hashes':0,'census_cells':0,'exact_formula_cells':0,'interval_cells':0}
    sources=json.loads((OWN/'sources.json').read_text(encoding='utf-8'))['sources']
    for s in sources:
        if 'sha256' in s:
            assert sha(ROOT/s['local_path']) == s['sha256'], s['id']
            counts['source_hashes']+=1
    assert sha(RAW/'morphology-alt.pdf')==sha(ROOT/'data/raw/2026-10-02-connections-and-priority/south-india/morphological-study-2025.pdf')
    primary=json.loads((RAW/'coder-a.json').read_text(encoding='utf-8'))
    queries=[x for x in primary if x['inventory']=='tamil']
    ints='segments curved loops L T X Y other terminals components dots'.split()
    rules={'R1':['segments','loops'],'R2':ints,'R3':ints+['symmetry','orientation']}
    observed=json.loads((OWN/'run-v1/observed.json').read_text(encoding='utf-8'))
    for record in observed:
        refs=[x for x in primary if x['inventory']==record['inventory'] and x['readable']]
        fields=rules[record['rule']]
        # Direct pair loop rather than the analysis script's signature support set.
        hits=sum(any(all(q[f]==r[f] for f in fields) for r in refs) for q in queries)
        assert hits==record['matched'] and hits/len(queries)==record['rate']
        counts['census_cells']+=1
    null=json.loads((OWN/'run-v1/synthetic-null.json').read_text(encoding='utf-8'))
    for record in null:
        refs=[x for x in primary if x['inventory']==record['inventory'] and x['readable']]
        fields=rules[record['rule']]
        freq=Counter(tuple(x[f] for f in fields) for x in refs)
        n=record['n']
        expected=sum((k/len(refs))*(1-(1-k/len(refs))**n) for k in freq.values())
        assert abs(expected-record['surrogate_query']['exact_mean'])<1e-12
        counts['exact_formula_cells']+=1
        for key in ('surrogate_query','fixed_tamil_query'):
            stats=record[key]
            assert 0 <= stats['q025'] <= stats['q975'] <= 1
            assert 0 <= stats['mean'] <= 1+1e-14
            counts['interval_cells']+=1
    manifest=json.loads((OWN/'run-v1/manifest.json').read_text(encoding='utf-8'))
    # The amended protocol preserves the exact original witness separately.
    protocol=OWN/'history/2026-10-07-before-amendment/PROTOCOL.md'
    if not protocol.exists():
        protocol=OWN/'PROTOCOL.md'
    for key,path in [('protocol_sha256',protocol),('code_sha256',OWN/'analyze.py'),
                     ('coder_a_sha256',RAW/'coder-a.json'),('coder_b_sha256',RAW/'coder-b.json'),
                     ('indus_selection_sha256',RAW/'indus-selection.json')]:
        assert manifest[key]==sha(path),key
    proposed=json.loads((OWN/'registry-entry.json').read_text(encoding='utf-8'))
    assert set(proposed)=={'id','theme','status','question','outcome','challenge','remedy','evidence','retry_when'}
    assert all((ROOT/f).is_file() for f in proposed['evidence'])
    print(json.dumps({'status':'Verified computation','checks':counts,'frozen_manifest_hashes_checked':5,
                      'brochure_bytes_identical':True,'registry_entry_schema_and_links':True},indent=2))

if __name__=='__main__':
    main()
