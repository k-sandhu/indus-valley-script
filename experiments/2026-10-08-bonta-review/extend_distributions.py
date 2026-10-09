"""Exploratory completion of declared compound-fish and broad-MS proxies."""
from pathlib import Path
import argparse, collections, hashlib, json

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-08-bonta-review'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='distribution-sensitivities.json')
    a=ap.parse_args();dest=OWN/a.output
    if dest.exists():raise FileExistsError(dest)
    path=ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl'
    rows=[json.loads(z) for z in path.read_text(encoding='utf-8').splitlines() if z.strip()]
    groups={}
    for r in rows:
        g=r['object_family_id']
        if g not in groups or (-r['length'],r['record_id'])<(-groups[g]['length'],groups[g]['record_id']):groups[g]=r
    sel=json.loads((OWN/'selection.json').read_text(encoding='utf-8'));fish=set(sel['fish_proxy_wells'])
    hist=collections.Counter();repeats=0;over=0;absorbed=0;ambiguous=0;broad=0;conservative=0
    for r in groups.values():
        seq=r['signs_reading_rtl'];pairs={};reverse=collections.defaultdict(list)
        for i,x in enumerate(seq):
            if x=='220':
                adj=[j for j in [i-1,i+1] if 0<=j<len(seq) and seq[j] in {'002','032'}]
                if len(adj)==1:pairs[i]=adj[0];reverse[adj[0]].append(i)
                elif len(adj)>1:ambiguous+=1
        valid={i:j for i,j in pairs.items() if len(reverse[j])==1}
        ambiguous+=sum(len(v)>1 for v in reverse.values());absorbed+=len(valid)
        consumed=set(valid.values());out=[]
        for i,x in enumerate(seq):
            if i in consumed:continue
            out.append('220+'+seq[valid[i]] if i in valid else x)
        run=[]
        for x in out+['END']:
            if x in fish or x in {'220+002','220+032'}:run.append(x)
            elif run:
                hist[len(run)]+=1;repeats+=len(run)!=len(set(run));over+=len(run)>3;run=[]
        broad+=sum(seq[i] in {'704','705','706','707'} and seq[i+1]=='033' for i in range(len(seq)-1))
        conservative+=sum(seq[i] in {'705','706'} and seq[i+1]=='033' for i in range(len(seq)-1))
    result={'status':'Exploratory','input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'objects':len(groups),'absorbed_pairs':absorbed,'ambiguous_neighbour_cases':ambiguous,
      'compound_fish_runs':sum(hist.values()),'run_lengths':dict(sorted(hist.items())),
      'maximum_run':max(hist),'repeating_runs':repeats,'runs_over_three':over,
      'MS_conservative_adjacencies':conservative,'MS_broad_adjacencies':broad,
      'scope':'Mutually unique adjacent pair absorption; no certified seven-sign M-field segmentation'}
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
