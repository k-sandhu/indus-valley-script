"""Independent scalar replay from source caption, first forms and count notes."""
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations, permutations
import json, csv, hashlib, re, datetime, shutil

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
OLD=ROOT/'experiments/2026-10-02-six-hour/harappa-object-frame'
RAW=ROOT/'data/raw/2026-10-02-connections-and-priority/harappa-short-records/main-v2'
checks=[]
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,actual,expected): checks.append({'check':name,'passed':actual==expected,'actual':actual,'expected':expected})

out=BASE/'review-v1'
if out.exists(): raise FileExistsError(out)
result=read(BASE/'main-v2/results.json')
obs=read(BASE/'observations.json')
caption=read(OLD/'figure4-caption-ledger.json')['registrations']
forms={r['specimen']:dict(r) for r in read(OLD/'figure4-first-observations.json')['tablets']}
for change in read(OLD/'figure4-native-reinspection.json')['changes']:
    forms[change['specimen']][change['field']]=change['revised_value']
rows=[json.loads(line) for line in (ROOT/'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
targets={f'H-{n}' for n in range(2218,2240)}
selected=[r for r in rows if r['source_cisi'] in targets]
check('target object count',len({r['source_cisi'] for r in selected}),22)
check('source face rows',len(selected),66)
check('principal length inclusion',sum(r['clean_rtl_singleline'] and r['length']>=3 for r in selected),0)
check('three records per target',sorted(Counter(r['source_cisi'] for r in selected).values()),[3]*22)
families={'154':'C','156':'C','700':'A','861':'D'}
numbers={'003':3,'033':3,'034':4}
bykey=defaultdict(list)
for r in selected: bykey[r['source_cisi']].append(r)
independent=[]
for cap in caption:
    if cap['specimen']==1: continue
    reg=cap['literal'].split('/')[0]
    candidates={r['source_cisi'] for r in selected if re.match(r'H\d{2}-\d+',r['metadata']['excavation-idno']).group()==reg}
    check('unique caption join '+str(cap['specimen']),len(candidates),1)
    key=next(iter(candidates)); rs=sorted(bykey[key],key=lambda x:x['record_id'])
    symbol={families[r['signs_visual_ltr'][0]]:r['signs_visual_ltr'] for r in rs}
    check('one module per family '+key,sorted(symbol),['A','C','D'])
    source=forms[cap['specimen']]
    counts=obs['counts_by_displayed_specimen'][str(cap['specimen'])]
    slots=[('C','left'),(source['middle_form'],source['middle_position']),(source['bottom_form'],source['bottom_position'])]
    possible={f:{3,4} for f in ['C','A','D']}
    for (f,pos),n in zip(slots,counts):
        if f is not None and n is not None:
            possible[f]={n}
            check('count compatibility '+key+' '+f,n,numbers[symbol[f][1]])
    independent.append({'key':key,'specimen':cap['specimen'],'group':cap['published_manufacturing_group'],'unit':cap['literal'].split('/')[1].split('-')[0],'modules':symbol,'counts':counts,'slots':slots,'possible':possible,'order':[tuple(r['signs_visual_ltr']) for r in rs]})

fixed=Counter(tuple(r['order']) for r in independent)
cycle=Counter()
dihedral=Counter()
exact=Counter()
broad=Counter()
for r in independent:
    order=r['order']
    rotations=[]
    for n in [0,1,2]: rotations.append(tuple(order[n:]+order[:n]))
    cycle[min(rotations)]+=1
    reverse=list(reversed(order))
    for n in [0,1,2]: rotations.append(tuple(reverse[n:]+reverse[:n]))
    dihedral[min(rotations)]+=1
    exact[tuple(sorted(order))]+=1
    broad[tuple(sorted((f,numbers[c[1]]) for f,c in r['modules'].items()))]+=1
for name,groups in [('fixed_imported_row_order',fixed),('cyclic_imported_row_rotation',cycle),('rotation_and_imported_row_reversal',dihedral),('unordered_exact_modules',exact),('unordered_broad_family_and_stroke_count',broad)]:
    check(name+' classes',len(groups),result['representations'][name]['classes'])
    check(name+' sizes',sorted(groups.values(),reverse=True),result['representations'][name]['class_sizes'])
    check(name+' pair count',sum(n*(n-1)//2 for n in groups.values()),result['representations'][name]['same_class_object_pairs'])
    if name=='rotation_and_imported_row_reversal':
        check('three-face dihedral action equals all row permutations',all(set(rot for rot in permutations(r['order']))==set(tuple(r['order'][k:]+r['order'][:k]) for k in range(3))|set(tuple(list(reversed(r['order']))[k:]+list(reversed(r['order']))[:k]) for k in range(3)) for r in independent),True)

pair=Counter(); source_pair=Counter()
for a,b in combinations(independent,2):
    nd=sum(a['modules'][f]!=b['modules'][f] for f in ['C','A','D'])
    nc=sum(numbers[a['modules'][f][1]]!=numbers[b['modules'][f][1]] for f in ['C','A','D'])
    pair['all_object_pairs']+=1
    pair[['exact_same_modules','exact_one_module_changed','exact_two_modules_changed'][nd]]+=1
    pair['count_only_changes']+=(nd==1 and nc==1)
    pair['graphic_variant_only_changes']+=(nd==1 and nc==0)
    lower=sum(not(a['possible'][f]&b['possible'][f]) for f in ['C','A','D'])
    upper=sum(any(x!=y for x in a['possible'][f] for y in b['possible'][f]) for f in ['C','A','D'])
    source_pair['certain_identical_count_profile_pairs']+=(upper==0)
    source_pair['possible_identical_count_profile_pairs']+=(lower==0)
    source_pair['possible_one_count_difference_pairs']+=(lower<=1<=upper)
    source_pair['certain_one_count_difference_pairs']+=(lower==upper==1)
for key,value in result['pair_counts'].items(): check('exact pair '+key,pair[key],value)
for key,value in result['native_source']['pair_bounds'].items(): check('source pair '+key,source_pair[key],value)

direct=Counter()
for r in independent:
    for (f,pos),n in zip(r['slots'],r['counts']):
        if n is not None: direct[(f,n)]+=1
check('directly counted faces',sum(direct.values()),32)
check('direct family/count cells',[{'family':f,'count':n,'faces':v} for (f,n),v in sorted(direct.items())],result['native_source']['direct_family_count_table'])
for nfour,key in enumerate(['333','334','344','444']):
    certain=possible=0
    for r in independent:
        low=sum(v=={4} for v in r['possible'].values())
        high=sum(4 in v for v in r['possible'].values())
        certain+=(low==high==nfour)
        possible+=(low<=nfour<=high)
    check('profile '+key+' certain',certain,result['native_source']['conditional_sorted_count_profile_bounds'][key]['certain_objects'])
    check('profile '+key+' possible',possible,result['native_source']['conditional_sorted_count_profile_bounds'][key]['possible_objects'])
complete=[r for r in independent if all(len(v)==1 for v in r['possible'].values())]
check('complete source profile targets',sorted(r['key'] for r in complete),sorted(result['native_source']['complete_count_profile_keys']))
check('observed required profile',(sum(all(r['possible'][f]=={n} for f,n in [('C',3),('A',4),('D',3)]) for r in independent),sum(all(n in r['possible'][f] for f,n in [('C',3),('A',4),('D',3)]) for r in independent)),(5,22))
readable=[r for r in independent if all(f is not None and pos is not None for f,pos in r['slots'][1:])]
check('readable lower pairs',len(readable),19)
source_states=[(r['slots'][1][0],r['slots'][1][1],r['slots'][2][1]) for r in readable]
check('source fixed display classes',len(set(source_states)),8)
same=sum(r['slots'][1][1]==r['slots'][2][1] for r in readable)
check('source same/opposite',(same,len(readable)-same),(11,8))
check('source complete profile arrangement variation',len({(r['slots'][1][0],r['slots'][1][1],r['slots'][2][1]) for r in complete}),3)
check('caption groups',dict(Counter(r['group'] for r in independent)),{1:6,2:9,3:7})
check('unit8040 dependency',sum(r['unit']=='8040' for r in independent),16)
local_faces=list(csv.DictReader((RAW/'source_faces.csv').open(encoding='utf-8')))
check('restored source positions',sum(bool(r['displayed_form_position']) for r in local_faces),63)
for r in independent:
    for side,(f,pos) in zip(['top','middle','bottom'],r['slots']):
        match=[z for z in local_faces if z['target_id']==r['key'] and z['displayed_side']==side]
        check('face position '+r['key']+' '+side,match[0]['displayed_form_position'],pos or '')
for rec in read(BASE/'main-v2/source-locators.json')['source_hashes']:
    check('input hash '+rec['path'],sha(ROOT/rec['path']),rec['sha256'])
for rec in read(BASE/'main-v2/source-locators.json')['registered_crop_locators']:
    check('crop hash '+rec['target_id'],sha(ROOT/rec['crop_path']),rec['crop_sha256'])
for rec in result['local_output_hashes']:
    check('local dataset hash '+rec['path'],sha(ROOT/rec['path']),rec['sha256'])
check('analysis source snapshot',sha(BASE/'analyze.py'),sha(BASE/'main-v2/code_snapshot.py'))
old=read(BASE/'main-v1/results.json')
for key in ['objects','faces','exact_unordered_module_set_class_sizes','pair_counts','native_source','production_and_deposit_summary']:
    check('preserved v1 unaffected result '+key,old[key],result[key])
comparison=next(r for r in rows if r['source_cisi']=='H-1682')['signs_visual_ltr']
shared=(comparison[0],comparison[1])
matching=[r['key'] for r in independent if tuple(r['modules']['C'])==shared]
check('same-context exact C variant module',matching,['H-2237'])
check('source photo panel counts',(sum(len(r['count_candidates'])==1 for r in obs['gallery_photo']['panels']),sum(len(r['count_candidates'])>1 for r in obs['gallery_photo']['panels'])),(8,1))
out.mkdir()
payload={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent scalar replay. The reviewer is the same agent; root supplied a separate informed photo reading. No separate epigraphic expertise is claimed.','endpoint':'main-v2','passed':sum(c['passed'] for c in checks),'checks':len(checks),'failures':[c for c in checks if not c['passed']],'records':checks}
(out/'checks.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copyfile(__file__,out/'code_snapshot.py')
print(json.dumps({k:v for k,v in payload.items() if k!='records'},indent=2))
if payload['failures']: raise SystemExit(1)
