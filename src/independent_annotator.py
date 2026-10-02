"""Held-out candidate-event scoring of an independent CISI photo annotator.

Mayig P IDs identify coarse observed glyph classes, not Parpola1994 codes.
Wells compatibility sets stay local; they are never transitively merged.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import hashlib,itertools,json,math,re,sys,time
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/methods'))
from conditional_structure import Model,load_records,group_records,UNKNOWN
from nested_conditional import tune


def event_scores(model,sets,kind,stratum=('Mohenjo-daro','SEAL:S')):
    """Forward filtering over compatible observed events in the fine alphabet."""
    n=len(sets);posterior=None;output=[]
    if kind=='PMB':
        ratio=np.asarray([model.smooth(model.bigram.get(i,{}),model.unigram)/model.unigram
                          for i in range(len(model.signs))])
    for i,candidates in enumerate(sets):
        p,pm,_=model.distributions(n,i,stratum,None)
        if kind=='U':pred=model.unigram.copy()
        elif kind=='P':pred=p.copy()
        elif kind=='PM' or i==0:pred=pm.copy()
        else:
            transition=ratio*pm[None,:]
            transition/=transition.sum(axis=1)[:,None]
            pred=posterior@transition
        allowed=[model.index[c] for c in sorted(candidates) if c in model.index and c!=UNKNOWN]
        mass=float(pred[allowed].sum())
        if mass<=0:raise ValueError('Observed event has no supported fine-code path')
        output.append(math.log2(mass))
        posterior=np.zeros(len(model.signs));posterior[allowed]=pred[allowed]/mass
    return output


def conservative_training(unique,allrows,tests):
    source_artifacts={r['artifact'] for r in allrows if any(1<=int(n)<=199
                     for n in re.findall(r'\bM\s*-?\s*(\d+)',r.get('source_cisi',''),flags=re.I))}
    source_sequences={r['seq'] for r in allrows if r['artifact'] in source_artifacts}
    bylength=defaultdict(list)
    for r in tests:bylength[len(r['sets'])].append(r['sets'])
    def compatible(seq):
        return any(all(s in candidates for s,candidates in zip(seq,sets)) for sets in bylength[len(seq)])
    direct=set();coarse=set()
    for i,r in enumerate(unique):
        if source_artifacts.intersection(r['artifact_aliases']) or r['seq'] in source_sequences:direct.add(i)
        if compatible(r['seq']):coarse.add(i)
    groups=group_records(unique)
    forbidden={i for g in groups if set(g)&(direct|coarse) for i in g}
    train=[r for i,r in enumerate(unique) if i not in forbidden]
    assert all(not source_artifacts.intersection(r['artifact_aliases']) for r in train)
    assert all(not compatible(r['seq']) for r in train)
    return train,{'source_range':'CISI M1..M199, including sources not in eligible test set',
        'matched_source_artifacts':len(source_artifacts),'source_direct_texts':len(direct),
        'coarse_compatible_direct_texts':len(coarse),'excluded_component_texts':len(forbidden)}


def bootstrap(records,unique=False,seed=20261009,repeats=10000):
    if unique:
        selected={}
        for r in records:
            if r['p_sequence'] not in selected:
                selected[r['p_sequence']]=dict(r,artifact_aliases=list(r.get('artifact_aliases',[r['artifact']])))
            else:
                selected[r['p_sequence']]['artifact_aliases'].extend(r.get('artifact_aliases',[r['artifact']]))
        records=list(selected.values())
    if not records:return {'status':'insufficient supported texts','texts':0}
    grouping=[dict(r,seq=r['p_sequence']) for r in records]
    components=group_records(grouping)
    groups={g:sum((np.array([records[i]['gain_bits'],records[i]['noninitial_glyphs']]) for i in ix),np.zeros(2))
            for g,ix in enumerate(components)}
    a=np.asarray(list(groups.values()));rng=np.random.default_rng(seed);values=[]
    for start in range(0,repeats,250):
        ix=rng.integers(0,len(a),size=(min(250,repeats-start),len(a)))
        summed=a[ix].sum(axis=1);values.extend((summed[:,0]/summed[:,1]).tolist())
    return {'texts':len(records),'artifact_P_text_groups':len(a),'noninitial_glyphs':int(a[:,1].sum()),
            'gain_bits_per_noninitial_candidate_event':float(a[:,0].sum()/a[:,1].sum()),
            'conditional_cluster_bootstrap_95_ci':np.quantile(values,[.025,.975]).tolist(),
            'bootstrap':repeats,'bootstrap_conditions_on_fitted_model':True}


def main():
    started=time.monotonic();inp=ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl'
    mayig=ROOT/'data/normalized/mayig_faces.jsonl';cross=ROOT/'data/normalized/mayig_wells_class_crosswalk.json'
    raw=[json.loads(l) for l in mayig.read_text(encoding='utf-8').splitlines()]
    mapping=json.loads(cross.read_text(encoding='utf-8'))['by_mayig_class']
    eligible=[r for r in raw if r['clear_transcription'] and r['line_count']==1 and r['length']>=3]
    tests=[];exclusions=[]
    for r in eligible:
        sets=[{w.removeprefix('W').zfill(3) for w in mapping.get(p,{}).get('wells_candidates',[])}
              for p in r['signs_reading_rtl']]
        if any(not re.fullmatch(r'\d{3}',w) for s in sets for w in s):
            raise ValueError('Invalid numeric Wells candidate in source schema')
        if not all(sets):
            exclusions.append({'id':r['record_id'],'reason':'unmapped P class','classes':[p for p,s in zip(r['signs_reading_rtl'],sets) if not s]});continue
        tests.append(dict(r,sets=sets))
    unique,_=load_records(inp,min_length=3,unique=True)
    observed=ROOT/'data/normalized/lipi_observed_faces.jsonl'
    # Source identity comes from the full observational register, including
    # damaged, short, multiline and direction-excluded records.
    allrows=[{'artifact':str(r['object_family_id']),'source_cisi':r.get('source_cisi',''),
              'seq':tuple(r['signs_reading_rtl'])} for r in
             [json.loads(l) for l in observed.read_text(encoding='utf-8').splitlines()]]
    train,removal=conservative_training(unique,allrows,tests)
    groups=group_records(train)
    for g,indices in enumerate(groups):
        for i in indices:train[i]['analysis_group']=g
    baseline,dependent,inner=tune(train,20261009)
    models={name:Model(train,alpha) for name,alpha in [baseline,dependent]}
    scored=[];candidates=[]
    for r in tests:
        supported=[set(s)&set(models[dependent[0]].signs) for s in r['sets']]
        unsupported=[sorted(s-set(models[dependent[0]].signs)) for s in r['sets']]
        if not all(supported):
            exclusions.append({'id':r['record_id'],'reason':'no training-supported fine glyph in at least one event',
                               'candidate_sets':[sorted(s) for s in r['sets']]});continue
        b=event_scores(models[baseline[0]],supported,baseline[0])
        d=event_scores(models[dependent[0]],supported,dependent[0])
        fallback_stratum=('Mohenjo-daro','UNSPECIFIED_SEAL_SUBTYPE')
        fb=event_scores(models[baseline[0]],supported,baseline[0],fallback_stratum)
        fd=event_scores(models[dependent[0]],supported,dependent[0],fallback_stratum)
        scored.append({'record_id':r['record_id'],'p_sequence':tuple(r['signs_reading_rtl']),
            'artifact':r['object_family_id'],'artifact_aliases':[r['object_family_id']],
            'gain_bits':sum(d[1:])-sum(b[1:]),'noninitial_glyphs':len(supported)-1,
            'unspecified_subtype_gain_bits':sum(fd[1:])-sum(fb[1:]),
            'baseline_event_log2':b,'dependent_event_log2':d,
            'candidate_sets':[sorted(s) for s in r['sets']],
            'unsupported_candidates':unsupported,'has_unsupported_candidate':any(unsupported)})
    result={'design':'Independent-annotator candidate-event structural sensitivity; no meanings or sounds.',
        'input_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [inp,observed,mayig,cross]},
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'eligible_clear_single_line_length3plus':len(eligible),'candidate_mapped_texts':len(tests),
        'scored_texts':len(scored),'exclusions':exclusions,'training_unique_texts':len(train),
        'training_groups':len(groups),'training_exclusion':removal,
        'chosen_baseline':baseline,'chosen_dependent':dependent,'inner_scores':inner,
        'main_test_metadata_assumption':{'site':'Mohenjo-daro','object_type':'SEAL:S'},
        'all_clear_weighting':bootstrap(scored),'unique_P_text_sensitivity':bootstrap(scored,unique=True),
        'unspecified_seal_subtype_sensitivity':bootstrap([dict(r,gain_bits=r['unspecified_subtype_gain_bits']) for r in scored]),
        'all_fine_candidates_training_supported_sensitivity':bootstrap([r for r in scored if not r['has_unsupported_candidate']]),
        'records_with_unsupported_fine_candidate':sum(r['has_unsupported_candidate'] for r in scored),
        'limitations':['Candidate compatibility is shared catalogue interpretation, not photo-certified fine truth.',
          'Event sets may overlap across P labels; scores are conditional fine-code event probabilities, not a normalized P-label predictor.',
          'Unseen fine candidates are not credited through UNKNOWN. Supported events underrepresent unresolved fine possibilities.',
          'This is an independent manual annotator of the same CISI objects, not an independent archaeological corpus.',
          'No corpus-shuffle significance or general population accuracy is asserted.'],
        'records':scored,'runtime_seconds':time.monotonic()-started}
    out=ROOT/'results/independent_annotator';out.mkdir(parents=True,exist_ok=True)
    (out/'candidate_event_test.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['records','inner_scores','exclusions']},indent=2))


if __name__=='__main__':main()
