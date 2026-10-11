"""Additional multiplicity and graphic-variant checks using the saved run."""
from pathlib import Path
import hashlib,json,math
import numpy as np

def fisher_exact(table):
    a,b=table[0];c,d=table[1];n=a+b+c+d;left=a+b;final=a+c
    def prob(k):return math.comb(final,k)*math.comb(n-final,left-k)/math.comb(n,left)
    observed=prob(a)
    p=sum(prob(k) for k in range(max(0,left-(n-final)),min(left,final)+1) if prob(k)<=observed*(1+1e-12))
    return a*d/(b*c) if b*c else float('inf'),min(1,p)

ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
OUT=HERE/'run-v2';RAW=ROOT/'data/raw/2026-10-11-bonta-adversarial/run-v2'
def main():
    dest=OUT/'robustness.json'
    if dest.exists():raise SystemExit('Refusing to overwrite')
    x=json.loads((OUT/'position-audit.json').read_text(encoding='utf-8'));by={r['code']:r for r in x['rows']}
    saved=np.load(RAW/'position-permutations.npz');codes=list(saved['codes']);a=saved['counts'].astype(float)
    idx=[i for i,c in enumerate(codes) if not by[c]['inherited']]
    mean=a.mean(axis=0);sd=a.std(axis=0,ddof=1);valid=sd>0
    z=np.where(valid,(a-mean)/np.maximum(sd,1e-9),-np.inf)
    maxima=z[:,idx,:].max(axis=(1,2));selected=[]
    for c in ['151','154','156','158','161','400','142','527','617','130','001','002','060']:
        i=codes.index(c);p={}
        for k,name in enumerate(['initial','medial','final']):
            observed=by[c]['positions'][name]['observed'];v=(observed-mean[i,k])/sd[i,k] if valid[i,k] else None
            p[name]={'z':float(v) if v is not None else None,'maxT_adjusted_p':float((1+(maxima>=v).sum())/(len(a)+1)) if v is not None else None}
        selected.append({'code':c,'positions':p})
    variant=[]
    for left,right in [('154','156'),('154','158'),('151','161')]:
        l=by[left];r=by[right];tab=[[l['positions']['final']['observed'],l['non_singleton_tokens']-l['positions']['final']['observed']],
              [r['positions']['final']['observed'],r['non_singleton_tokens']-r['positions']['final']['observed']]]
        odds,p=fisher_exact(tab)
        variant.append({'left':left,'right':right,'final_nonfinal_table':tab,'two_sided_fisher_p':float(p),'odds_ratio':float(odds) if np.isfinite(odds) else 'infinite','scope':'Descriptive contrast in distinct strings. Labels were selected after the old outcomes; repeated production traditions are not independently sampled.'})
    data={'position_maxT':'For each saved within-text permutation, take the maximum standardized count across all 596 new codes and three slots with nonzero null variance. Compare each observed statistic with that common maximum distribution. Selection and archaeology remain exploratory.',
          'permutations':len(a),'selected':selected,'variant_contrasts':variant,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    dest.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(data,indent=2))
if __name__=='__main__':main()
