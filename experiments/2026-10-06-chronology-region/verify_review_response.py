"""Independently check the second amendment; all new writes use --output-dir."""
from __future__ import annotations
import argparse, collections, hashlib, itertools, json, math, re
from pathlib import Path
import numpy as np
import pandas as pd
import analyze as base

CHECKS=collections.Counter()
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def equal(a,b,name):
    assert a==b,(name,a,b)
    CHECKS[name]+=1
def close(a,b,name):
    assert np.allclose(a,b,atol=2e-10,rtol=0,equal_nan=True),(name,a,b)
    CHECKS[name]+=1
def holm(values):
    order=np.argsort(values); result=np.empty(len(values)); running=0
    for rank,i in enumerate(order):
        running=max(running,min(1,float(values[i])*(len(values)-rank))); result[i]=running
    return result
def bh(values):
    order=np.argsort(values); result=np.empty(len(values)); running=1
    for rank in range(len(values)-1,-1,-1):
        i=order[rank]; running=min(running,float(values[i])*len(values)/(rank+1)); result[i]=running
    return result
def js(p,q):
    if not np.isfinite(p).all() or not np.isfinite(q).all(): return np.nan
    result=0
    for a,b in zip(p,q):
        if a>0: result+=.5*a*math.log2(2*a/(a+b))
        if b>0: result+=.5*b*math.log2(2*b/(a+b))
    return result
def distribution(c,ids,position=None):
    counts=collections.Counter()
    for i in ids:
        row=c.rows[i]
        if position is not None:
            if row['clear']: counts[row['seq'][position]]+=1
        else: counts.update(s for s in row['seq'] if s!='000')
    total=sum(counts.values())
    return np.asarray([counts.get(s,0)/total if total else np.nan for s in c.vocab])
def replay_metrics(c,units,labels,types):
    ids=[[i for u,state in zip(units,labels) if state==g for i in u['indices']] for g in [0,1]]
    typed=[[distribution(c,[i for i in group if c.type[i]==t]) for t in types] for group in ids]
    result={'frequency_js_bits':js(np.mean(typed[0],axis=0),np.mean(typed[1],axis=0)),
            'raw_frequency_js_bits':js(distribution(c,ids[0]),distribution(c,ids[1]))}
    for position,name in [(0,'initial'),(-1,'terminal')]:
        result[f'raw_{name}_js_bits']=js(distribution(c,ids[0],position),distribution(c,ids[1],position))
        actual_labels=[u['label'] for u in units]
        actual_ids=[[i for u,state in zip(units,actual_labels) if state==g for i in u['indices'] if c.clear[i]] for g in [0,1]]
        position_types=base.common_types(c,np.asarray(actual_ids[0],int),np.asarray(actual_ids[1],int))
        if position_types:
            values=[[distribution(c,[i for i in group if c.type[i]==t],position) for t in position_types] for group in ids]
            result[f'{name}_js_bits']=js(np.mean(values[0],axis=0),np.mean(values[1],axis=0))
    result['mean_length_b_minus_a']=np.mean([np.mean([len(c.rows[i]['seq']) for i in ids[1] if c.type[i]==t])-np.mean([len(c.rows[i]['seq']) for i in ids[0] if c.type[i]==t]) for t in types])
    return result
def diversity(counts,m):
    n=sum(counts); denominator=math.comb(n,m)
    richness=sum(1-(math.comb(n-x,m)/denominator if n-x>=m else 0) for x in counts)
    entropy=0
    for x in counts:
        for k in range(max(1,m-(n-x)),min(x,m)+1):
            probability=math.comb(x,k)*math.comb(n-x,m-k)/denominator
            entropy-=probability*(k/m)*math.log2(k/m)
    return np.asarray([richness,entropy])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',required=True); parser.add_argument('--raw-dir',required=True)
    parser.add_argument('--output-dir',required=True)
    args=parser.parse_args(); endpoint=Path(args.input_dir).resolve(); local=Path(args.raw_dir).resolve(); output=Path(args.output_dir).resolve()
    if output.exists(): raise FileExistsError('Choose a fresh verification output directory.')
    c=base.Corpus(); audit=read(endpoint/'audit.json'); tests=read(endpoint/'permutation_tests.json')['tests']
    equal(digest(c.path),audit['input_sha256'],'input_hash')
    equal(digest(base.OWN/'review_response.py'),audit['code_sha256'],'analysis_code_hash')
    equal(digest(base.OWN/'PROTOCOL.md'),audit['protocol_sha256'],'amended_protocol_hash')
    preservation=read(base.OWN/'review-response-baseline-2026-10-07-v1/preservation.json')['baseline_files']
    for entry in preservation:
        witness=(base.OWN/'review-response-baseline-2026-10-07-v1'/Path(entry['path']).name) if entry['authorized_document_update'] else base.ROOT/entry['path']
        equal(digest(witness),entry['sha256'],'archived_document' if entry['authorized_document_update'] else 'immutable_prior_file')
    original=(base.OWN/'review-response-baseline-2026-10-07-v1/PROTOCOL.md').read_bytes()
    equal((base.OWN/'PROTOCOL.md').read_bytes().startswith(original),True,'original_protocol_prefix')
    # Rebuild the label-source/mound composition without importing the new analyzer.
    frame=pd.read_csv(endpoint/'excavation_composition.csv',keep_default_na=False)
    for row in frame.to_dict('records'):
        ids=[]
        for i,r in enumerate(c.rows):
            if r['site']!='Harappa' or r['major']!=row['period']: continue
            metadata=r['metadata']; source='stratum' if 'stratum' in str(metadata.get('phase','')).lower() else 'period_field' if str(metadata.get('period','')).strip() not in ['', '-', 'None'] else 'label_without_period_field'
            area=str(metadata.get('area-section','')); mound=next((m for m in ['AB','E','F','J'] if area.startswith(m)),'unknown')
            if (source,mound)==(row['label_source'],row['mound']): ids.append(i)
        for key,value in c.denom(ids).items(): equal(int(row[key]),value,'composition_denominator')
        numbers=[list(map(int,re.findall(r'\bH-?(\d+)',str(c.rows[i]['source_cisi']),re.I))) for i in ids]
        equal(int(row['faces_with_earlier_catalogue_number']),sum(bool(ns) and all(n<=1520 or n==2590 for n in ns) for ns in numbers),'catalogue_proxy')
        equal(int(row['faces_without_parseable_H_number']),sum(not ns for ns in numbers),'missing_catalogue_numbers')
    signs=pd.read_csv(endpoint/'sign_tests.csv',dtype={'sign':str})
    for row in signs.to_dict('records'):
        close(row['p'],(1+row['tail_count'])/(row['permutations']+1),'sign_tail_p')
    for _,family in signs.groupby(['theme','seed'],sort=False): close(family['bh_q'],bh(family['p'].tolist()),'sign_bh')
    for t in tests:
        if 'p' not in t: continue
        expected_budget=19999 if t['theme'] in ['time','subset'] else 9999
        equal(t['permutations'],expected_budget,'permutation_budget')
        stem=f"{t['theme']}_{t['comparison']}_{t['unit']}_seed{t['seed']}".replace('/','-')
        saved=np.load(local/(stem+'.npz')); replay=read(local/(stem+'_replay.json')); fields=saved['fields'].tolist()
        equal(saved['nulls'].shape[0],expected_budget,'saved_null_length')
        actual=replay_metrics(c,replay['units'],[u['label'] for u in replay['units']],t['common_types'])
        for column,key in enumerate(fields):
            values=saved['nulls'][:,column]; valid=values[np.isfinite(values)]; recorded=t['statistics'][key]
            close(recorded['observed'] if recorded['observed'] is not None else np.nan,actual[key],'independent_statistic')
            close(recorded['null_mean'] if recorded['null_mean'] is not None else np.nan,valid.mean() if len(valid) else np.nan,'saved_null_mean')
            if recorded['observed'] is None or not len(valid): equal(recorded['excess_over_null'],None,'unavailable_excess')
            else: close(recorded['excess_over_null'],recorded['observed']-valid.mean(),'saved_excess')
            equal(recorded['finite_null_draws'],len(valid),'finite_null_draws')
            if 'js_bits' in key: equal(recorded['magnitude_interval95'],None,'divergence_interval_withdrawn')
        values=saved['nulls'][:,fields.index('frequency_js_bits')]
        close(t['p'],(1+sum(values>=t['effect_js_bits']-1e-12))/(expected_budget+1),'frequency_saved_p')
        original_margin=collections.Counter((u['label'],u['type'],u['faces']) for u in replay['units'])
        for draw,labels in enumerate(replay['first_three_permuted_labels']):
            equal(collections.Counter((int(state),u['type'],u['faces']) for u,state in zip(replay['units'],labels)),original_margin,'sampled_component_margin')
            values=replay_metrics(c,replay['units'],labels,t['common_types'])
            for column,key in enumerate(fields): close(values[key],saved['nulls'][draw,column],'independent_null_replay')
        selected=signs[(signs['theme']==t['theme'])&(signs['seed']==t['seed'])&(signs['comparison']==t['comparison'])]
        if t['unit']=='physical_component' and t['theme']!='subset':
            for column,sign in enumerate(saved['selected_signs']):
                row=selected[selected['sign']==sign].iloc[0]
                count=int(np.sum(np.abs(saved['selected_sign_nulls'][:,column])>=abs(row['type_adjusted_b_minus_a'])-1e-12))
                equal(count,int(row['tail_count']),'selected_sign_saved_tail')
    for seed,theme,unit in itertools.product([21,22],['time','region','subset'],['physical_component','full_text_closure']):
        family=[t for t in tests if t['seed']==seed and t['theme']==theme and t['unit']==unit and 'p' in t]
        close([t['holm_p'] for t in family],holm([t['p'] for t in family]),'frequency_holm')
    units=read(local/'subset_units.json')['units']; subsets=read(local/'subset_units.json')['subset_physical_ids']
    for row in read(endpoint/'length_comparisons.json')['comparisons']:
        name='all' if row['subset']=='all_tablets' else row['subset']; selected=[u for u in units if u['physical'] in set(subsets[name])]
        ids=[[i for u in selected if u['period']==p for i in u['indices'] if c.known[i]>0] for p in ['3B','3C']]
        expected=np.mean([np.mean([len(c.rows[i]['seq']) for i in ids[1] if c.type[i]==t])-np.mean([len(c.rows[i]['seq']) for i in ids[0] if c.type[i]==t]) for t in row['common_types']])
        close(expected,row['equal_type_length_difference_slots'],'independent_length')
        close(np.quantile(read(local/(row['subset']+'_length_draws.json'))['draws'],[.025,.975]),row['length_interval95'],'length_quantiles')
    for row in read(endpoint/'media_comparisons.json')['comparisons']:
        selected=[u for u in units if u['physical'] in set(subsets[row['subset']]) and u['type'] is not None]
        counts=[collections.Counter(u['type'] for u in selected if u['period']==p) for p in ['3B','3C']]
        raw=diversity(list(counts[1].values()),sum(counts[1].values()))-diversity(list(counts[0].values()),sum(counts[0].values()))
        rare=diversity(list(counts[1].values()),row['family_budget'])-diversity(list(counts[0].values()),row['family_budget'])
        saved=np.load(local/f"media_{row['subset']}_seed{row['seed']}.npz"); fields=saved['fields'].tolist(); ps=[]
        close([row['effects'][f]['effect'] for f in fields],np.r_[raw,rare],'independent_media_combinations')
        equal(saved['permutation'].shape[0],9999,'media_budget')
        for j,f in enumerate(fields):
            close(row['effects'][f]['null_mean'],saved['permutation'][:,j].mean(),'media_null_mean')
            close(row['effects'][f]['interval95'],np.quantile(saved['bootstrap'][:,j],[.025,.975]),'media_quantiles')
            if j>=2:
                p=(1+sum(saved['permutation'][:,j]>=row['effects'][f]['effect']-1e-12))/10000
                close(row['effects'][f]['p'],p,'media_saved_p'); ps.append(p)
        close([row['effects'][f]['holm_p'] for f in fields[2:]],holm(ps),'media_holm')
    other=read(endpoint/'other_permutation_references.json')
    for row in other['external_targets']:
        equal(row['permutations'],9999,'target_budget')
        equal(all(result['holm_p']==1 for result in row['tests'].values()),True,'external_target_nonrejection')
        saved=np.load(local/f"external_targets_{row['unit']}_seed{row['seed']}.npz"); ps=[]
        for j,target in enumerate(saved['targets']):
            p=(1+np.sum(saved['draws'][:,j]>=row['effects'][target]['type_excess']-1e-12))/10000
            close(row['tests'][target]['one_sided_p'],p,'target_saved_tail'); ps.append(p)
            close(row['null_means'][target],saved['draws'][:,j].mean(),'target_null_mean')
        close([row['tests'][t]['holm_p'] for t in saved['targets']],np.r_[holm(ps[:2]),holm(ps[2:])],'target_holm')
    for seed in [21,22]:
        family=[r for r in other['early_inventory'] if r['seed']==seed]
        ps=[]; tps=[]
        for row in family:
            data=read(local/f"early_{row['adjustment']}_seed{seed}_draws.json")
            equal(len(data['permutation']),9999,'early_budget')
            p=(1+sum(x<=row['early_minus_later']+1e-12 for x in data['permutation']))/10000
            close(row['one_sided_p'],p,'early_saved_p'); ps.append(p)
            td=read(local/f"early_{row['adjustment']}_seed{seed}_text_draws.json")['draws']
            p=(1+sum(x<=row['text_component_sensitivity']['effect']+1e-12 for x in td))/10000
            close(row['text_component_sensitivity']['one_sided_p'],p,'early_text_p'); tps.append(p)
        close([r['holm_p'] for r in family],holm(ps),'early_holm')
        close([r['text_component_sensitivity']['holm_p'] for r in family],holm(tps),'early_text_holm')
        family=[r for r in other['external_score_sign_flips'] if r['seed']==seed]
        predictions=read(base.RAW/'main-2026-10-07-v1/external_predictions.json'); rng=np.random.default_rng(seed)
        for row in family:
            close(row['p'],(1+row['tail_count'])/10000,'score_flip_saved_p')
            good=[r for r in predictions if r[row['statistic']] is not None]; groups=sorted({r['physical'] for r in good})
            weights=np.asarray([sum(r[row['statistic']] for r in good if r['physical']==g)/len(good) for g in groups])
            exact=np.asarray(list(itertools.product([-1,1],repeat=len(groups))))@weights
            draws=rng.choice([-1,1],size=(9999,len(groups)))@weights
            close(row['effect'],sum(r[row['statistic']] for r in good)/len(good),'external_score_effect')
            close(row['exact_sign_flip_p'],np.mean(np.abs(exact)>=abs(row['effect'])-1e-12),'external_score_exact_reference')
            equal(row['tail_count'],int(np.sum(np.abs(draws)>=abs(row['effect'])-1e-12)),'external_score_full_random_replay')
            close(row['null_mean'],draws.mean(),'external_score_null_mean')
        close([r['holm_p'] for r in family],holm([r['p'] for r in family]),'score_flip_holm')
    disclosure=read(endpoint/'disclosure.json')
    equal(next(r for r in disclosure['tables'] if r['table']=='site_type')['single_face_cells'],96,'site_singletons')
    for row in disclosure['tables']:
        data=pd.read_csv(endpoint/'disclosure_safe'/f"{row['table']}_strata.csv")
        equal(len(data),row['retained_cells'],'suppression_retained_cells'); equal(bool((data['faces']>=5).all()),True,'suppression_minimum_faces')
        fields={'site_type':['site','type'],'region_type':['region','type'],'harappa_label_type':['time','type'],
                'harappa_major_type':['major','type'],'all_site_time':['site','time']}[row['table']]
        allowed={tuple(x) for x in data[fields].itertuples(index=False,name=None)}
        for path in (endpoint/'disclosure_safe').glob(row['table']+'_*.csv'):
            retained=pd.read_csv(path,dtype=str,keep_default_na=False)
            equal(all(tuple(x) in allowed for x in retained[fields].itertuples(index=False,name=None)),True,'suppression_all_companion_rows')
    output.mkdir(parents=True)
    result={'origin':'second post-launch amendment','status':'Verified computation','input_directory':str(endpoint),
            'checks':dict(CHECKS),'checks_total':sum(CHECKS.values()),'permutation_rows_checked':sum('p' in r for r in tests),
            'sign_rows_checked':len(signs),'independent_null_labels_replayed':CHECKS['sampled_component_margin'],
            'verification_code_sha256':digest(Path(__file__)),
            'scope':'Counts, effects, combinations, saved reference tails/corrections, three independently recounted label draws per frequency test, all prior file hashes. Full independent generation of every draw and archaeological authentication are outside this check.'}
    (output/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
