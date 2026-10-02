"""Marginalize a physically bounded gap with unknown sign count.

Candidate counts and code suggestions do not identify sounds or meanings.
Only left/right surviving glyphs and metadata enter the predictor.
"""
from __future__ import annotations
import argparse,hashlib,json,math,time
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from methods.conditional_structure import Model,load_records,group_records,make_folds,UNKNOWN
from restoration import paired_ci

ROOT=Path(__file__).resolve().parents[1]


class GapModel:
    def __init__(self,rows,alpha=20):
        self.model=Model(rows,alpha);self.alpha=alpha
        m=self.model
        self.ratio=np.asarray([m.smooth(m.bigram.get(i,{}),m.unigram)/m.unigram for i in range(len(m.signs))])
        self.max_length=max(32,max(len(r['seq']) for r in rows))
        prior=np.full(self.max_length+1,.5);prior[0]=0.
        self.length_counts=defaultdict(Counter)
        for r in rows:
            prior[len(r['seq'])]+=1;self.length_counts[r['stratum']][len(r['seq'])]+=1
        self.length_prior=prior/prior.sum();self.transitions={}

    def prior(self,length,stratum):
        counts=self.length_counts.get(stratum,{})
        return (counts.get(length,0)+self.alpha*self.length_prior[length])/(sum(counts.values())+self.alpha)

    def transition(self,length,i,stratum,bidirectional):
        key=(length,i,stratum,bidirectional)
        if key not in self.transitions:
            pm=self.model.distributions(length,i,stratum,None)[1]
            matrix=self.ratio*pm[None,:] if bidirectional else np.broadcast_to(pm,self.ratio.shape).copy()
            matrix/=matrix.sum(axis=1)[:,None]
            self.transitions[key]=matrix
        return self.transitions[key]

    def log_surviving_probability(self,left,right,k,stratum,bidirectional=True):
        seq=list(left)+[None]*k+list(right);length=len(seq);m=self.model
        posterior=None;logp=0.
        for i,code in enumerate(seq):
            if i==0:pred=m.distributions(length,i,stratum,None)[1].copy()
            else:pred=posterior@self.transition(length,i,stratum,bidirectional)
            if code is None:posterior=pred
            else:
                c=m.index.get(code,m.index[UNKNOWN]);mass=float(pred[c]);logp+=math.log(mass)
                posterior=np.zeros(len(m.signs));posterior[c]=1.
        return logp

    def count_distribution(self,left,right,stratum,counts=(1,2,3),bidirectional=True):
        scores=np.asarray([math.log(self.prior(len(left)+len(right)+k,stratum))+
                           self.log_surviving_probability(left,right,k,stratum,bidirectional) for k in counts])
        probs=np.exp(scores-scores.max());probs/=probs.sum()
        return [{'count':int(k),'model_mass':float(p)} for k,p in zip(counts,probs)]


def summary(scores):
    confusion=Counter((s['actual'],s['predicted']) for s in scores)
    bins=[]
    for a,b in [(0.,.4),(.4,.6),(.6,.8),(.8,1.000001)]:
        rows=[s for s in scores if a<=s['top_mass']<b]
        bins.append({'interval':[a,min(b,1.)],'n':len(rows),
                     'mean_model_mass':float(np.mean([s['top_mass'] for s in rows])) if rows else None,
                     'accuracy':float(np.mean([s['top1'] for s in rows])) if rows else None})
    return {'texts':len(scores),'exact_count_accuracy':float(np.mean([s['top1'] for s in scores])),
            'constant_one_glyph_design_control_accuracy':float(np.mean([s['actual']==1 for s in scores])),
            'true_count_distribution':dict(Counter(s['actual'] for s in scores)),
            'confusion':[{'actual':a,'predicted':b,'n':n} for (a,b),n in sorted(confusion.items())],
            'calibration':bins}


def benchmark(args):
    start=time.monotonic();inp=ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl'
    rows,_=load_records(inp,min_length=3,unique=True);groups=group_records(rows)
    folds,loads=make_folds(rows,groups,5,20261006)
    lookup={rows[i]['record_id']:g for g,ix in enumerate(groups) for i in ix}
    rng=np.random.default_rng(20261012);queries={}
    for row in rows:
        k=int(rng.integers(1,min(3,len(row['seq'])-2)+1))
        i=int(rng.integers(1,len(row['seq'])-k))
        queries[row['record_id']]={'left':row['seq'][:i],'right':row['seq'][i+k:],'actual':k,'start':i}
    scores={'baseline':[],'local':[]};oov=0;surviving=0
    for f in range(5):
        train=[r for i,r in enumerate(rows) if folds[i]!=f]
        test=[r for i,r in enumerate(rows) if folds[i]==f]
        model=GapModel(train,20)
        for row in test:
            q=queries[row['record_id']];known=q['left']+q['right']
            oov+=sum(c not in model.model.index for c in known);surviving+=len(known)
            for name,bi in [('baseline',False),('local',True)]:
                pp=model.count_distribution(q['left'],q['right'],row['stratum'],bidirectional=bi)
                best=max(pp,key=lambda z:(z['model_mass'],-z['count']))
                scores[name].append({'record_id':row['record_id'],'slot':q['start'],
                    'length':1,'actual':q['actual'],'predicted':best['count'],'top1':best['count']==q['actual'],
                    'top_mass':best['model_mass'],'posterior':pp,'fold':f,
                    'left':list(q['left']),'right':list(q['right'])})
        print(json.dumps({'stage':'gap_fold','fold':f,'seconds':time.monotonic()-start}),flush=True)
    result={'task':'Predict erased internal glyph count from survivors; no glyph identity or translation.',
        'input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'unique_texts':len(rows),'groups':len(groups),'alpha':20,'count_candidates':[1,2,3],
        'query_seed':20261012,'fold_seed':20261006,'models':{k:summary(v) for k,v in scores.items()},
        'paired_gain':paired_ci(scores['baseline'],scores['local'],lookup),
        'surviving_OOV_codes':oov,'surviving_codes':surviving,
        'limitations':['The erased-count sampling law is artificial and not a historical missing-sign prior.',
           'Count masses are uncalibrated. Real gaps can contain more than three signs or separators.',
           'Unseen surviving signs use the common UNKNOWN bucket; this is not a fine-glyph recognition test.',
           'Smoothing is frozen from the earlier one-slot benchmark; this is an exploratory conditional comparison.'],
        'runtime_seconds':time.monotonic()-start}
    out=ROOT/args.out;out.mkdir(parents=True,exist_ok=True)
    (out/'gap_benchmark.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    for name,ss in scores.items():(out/f'{name}_count_audit.jsonl').write_text('\n'.join(json.dumps(s) for s in ss),encoding='utf-8')
    print(json.dumps(result,indent=2))


def predict(args):
    rows,_=load_records(ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl',unique=True)
    forbidden=set(args.exclude_artifact);groups=group_records(rows)
    removed={i for g in groups if any(forbidden.intersection(rows[i]['artifact_aliases']) for i in g) for i in g}
    train=[r for i,r in enumerate(rows) if i not in removed]
    left=tuple(s.strip() for s in args.left.split(',') if s.strip())
    right=tuple(s.strip() for s in args.right.split(',') if s.strip())
    if not left or not right:raise ValueError('This prototype requires surviving glyphs on both sides of the gap')
    counts=tuple(int(c) for c in args.counts.split(','));model=GapModel(train,20)
    print(json.dumps({'warning':'Model masses are suggestions about a bounded gap, not authenticated sign counts or meanings.',
         'excluded_artifacts':sorted(forbidden),'removed_training_texts':len(removed),
         'candidate_counts':model.count_distribution(left,right,(args.site,args.type),counts)},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['benchmark','predict'])
    p.add_argument('--out',default='results/gap_restoration');p.add_argument('--left');p.add_argument('--right')
    p.add_argument('--counts',default='1,2,3');p.add_argument('--site',default='Mohenjo-daro');p.add_argument('--type',default='SEAL:S')
    p.add_argument('--exclude-artifact',action='append',default=[]);a=p.parse_args()
    benchmark(a) if a.mode=='benchmark' else predict(a)
