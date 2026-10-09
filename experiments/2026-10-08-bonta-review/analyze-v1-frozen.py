"""Rerunnable Package Q aggregates; all text-level outputs remain local.

Run from repository root. Requires numpy. Fresh --run names preserve endpoints.
"""
from pathlib import Path
import argparse, collections, hashlib, itertools, json, re, sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'
SEED = 20261008

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def rows(path): return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def bh(ps):
    n=len(ps); order=np.argsort(ps); out=np.ones(n); last=1.
    for j in range(n-1,-1,-1):
        i=int(order[j]); last=min(last, ps[i]*n/(j+1)); out[i]=last
    return out.tolist()

def bootstrap(a, b, groups, rng, draws=2000):
    agg=collections.defaultdict(lambda:[0.,0.])
    for x,y,g in zip(a,b,groups): agg[g][0]+=x;agg[g][1]+=y
    v=np.array(list(agg.values())); ans=[]
    for start in range(0,draws,100):
        idx=rng.integers(0,len(v),size=(min(100,draws-start),len(v)))
        t=v[idx].sum(axis=1); valid=t[:,1]>0
        ans.extend((t[valid,0]/t[valid,1]).tolist())
    return np.quantile(ans,[.025,.975]).tolist() if ans else None

def positions(rs, targets):
    seqs=[r['signs_reading_rtl'] for r in rs]
    rng=np.random.default_rng(SEED+1); total=sum(map(len,seqs)); answer={}
    for sign in targets:
        tokens=[s.count(sign) for s in seqs]; final=[int(s[-1]==sign) for s in seqs]
        initial=[int(s[0]==sign) for s in seqs]
        n=sum(tokens); ranks=[(i/(len(s)-1) if len(s)>1 else .5) for s in seqs for i,x in enumerate(s) if x==sign]
        answer[sign]={'tokens':n,'token_base':total,'token_fraction':n/total,
            'final':sum(final),'initial':sum(initial), 'final_fraction':sum(final)/n if n else None,
            'nonfinal':n-sum(final), 'mean_relative_position':float(np.mean(ranks)) if ranks else None,
            'token_fraction_object_bootstrap_95':bootstrap(tokens,list(map(len,seqs)),[r['object_family_id'] for r in rs],rng),
            'final_fraction_object_bootstrap_95':bootstrap(final,tokens,[r['object_family_id'] for r in rs],rng)}
    return answer

def fish_summary(seqs, fish, basic, short, long):
    counts=collections.Counter(); lengths=collections.Counter(); repeat=0; maxrun=0; absorbed=0; examples=[]
    for rowno,s in enumerate(seqs):
        i=0
        while i<len(s):
            if s[i] not in fish: i+=1;continue
            run=[]; j=i
            while j<len(s) and s[j] in fish:run.append(s[j]);j+=1
            lengths[len(run)]+=1;maxrun=max(maxrun,len(run));repeat+=int(len(set(run))<len(run))
            if len(run)>3 or len(set(run))<len(run):examples.append(rowno)
            i=j
        for i,x in enumerate(s):
            if x==basic:
                for off in [-1,1]:
                    if 0<=i+off<len(s) and s[i+off] in {short,long}:counts[(s[i+off], 'before' if off==-1 else 'after')]+=1
                    if 0<=i+off<len(s) and s[i+off] in {short,long}:absorbed+=1
    return {'runs':sum(lengths.values()),'run_lengths':dict(sorted(lengths.items())),
            'repeating_runs':repeat,'runs_over_three':sum(v for k,v in lengths.items() if k>3),
            'maximum_run':maxrun, 'basic_fish_paired_stroke_adjacencies':[
                {'stroke':k[0],'reading_position':k[1],'events':v} for k,v in sorted(counts.items())],
            'note':'Unsegmented elementary fish-run proxy; paired strokes are adjacency events, not certified compound identities'}, sorted(set(examples))

def permutations(rs, targets, n=4999):
    seqs=[r['signs_reading_rtl'] for r in rs]; length=np.array(list(map(len,seqs))); width=int(max(length))
    vocabulary=sorted(set(itertools.chain.from_iterable(seqs))); lookup={x:i for i,x in enumerate(vocabulary)}
    arr=np.full((len(seqs),width),-1,int)
    for i,s in enumerate(seqs):arr[i,:len(s)]=[lookup[x] for x in s]
    valid=arr>=0; ranks=np.zeros(arr.shape,float)
    for i,l in enumerate(length):ranks[i,:l]=np.arange(l)/(l-1) if l>1 else .5
    rng=np.random.default_rng(SEED+2); null={x:[] for x in targets}; pair=[]
    ma={lookup[x] for x in ['705','706'] if x in lookup}; tra=lookup.get('033',-99)
    observed_pair=int(sum(sum(s[i] in {'705','706'} and s[i+1]=='033' for i in range(len(s)-1)) for s in seqs))
    for rep in range(n):
        noise=rng.random(arr.shape);noise[~valid]=2.;order=np.argsort(noise,axis=1);a=np.take_along_axis(arr,order,axis=1)
        final=a[np.arange(len(a)),length-1]
        for sign,role in targets.items():
            mask=a==lookup.get(sign,-99); nt=int(mask.sum())
            if role=='terminal': stat=float((final==lookup.get(sign,-99)).sum())
            else: stat=float((mask*ranks).sum()/nt) if nt else 0.
            null[sign].append(stat)
        pair.append(int((np.isin(a[:,:-1],list(ma)) & (a[:,1:]==tra)).sum()))
    results={}
    for sign,role in targets.items():
        code=lookup.get(sign,-99);mask=arr==code;nt=int(mask.sum())
        obs=float((arr[np.arange(len(arr)),length-1]==code).sum()) if role=='terminal' else float((mask*ranks).sum()/nt) if nt else 0.
        v=np.array(null[sign]); tail=int((v<=obs+1e-12).sum()) if role=='early' else int((v>=obs-1e-12).sum())
        results[sign]={'statistic':role, 'observed':obs,'null_mean':float(v.mean()),'null_95':np.quantile(v,[.025,.975]).tolist(), 'tail_count':tail,'p':(tail+1)/(n+1)}
    qs=bh([v['p'] for v in results.values()])
    for value,q in zip(results.values(),qs):value['q']=q
    results['MS_pair_proxy']={'observed':observed_pair,'null_mean':float(np.mean(pair)),'null_95':np.quantile(pair,[.025,.975]).tolist(),'p':(1+sum(x>=observed_pair for x in pair))/(n+1), 'correction':'Separate descriptive adjacency endpoint; no value inference'}
    return results, {'positions':null,'MS_pair':pair}

# SLP1 is the source data's transliteration. Every equivalence is explicit.
TABLE=str.maketrans({**dict.fromkeys('Aa','a'),**dict.fromkeys('Ii','i'),**dict.fromkeys('Uu','u'),
    **dict.fromkeys('kKgG','k'),**dict.fromkeys('cCjJ','c'),**dict.fromkeys('wWqQ','t'),
    **dict.fromkeys('tTdD','t'),**dict.fromkeys('pPbB','p'),**dict.fromkeys('Szs','s'),'R':'n','F':'f','X':'x'})

def normalize(word):
    # Retroflex and dental stops are separate until the next line; preserve them
    # using a sentinel, rather than conflating places of articulation.
    word=re.sub('[wWqQ]','Z',word)
    return word.translate(TABLE)

def lexical(selection, dictionary, rawout):
    text=dictionary.read_text(encoding='utf-8'); allkeys=re.findall(r'<k1>([^<\n]+)',text)
    keys=set(k for k in allkeys if re.fullmatch('[a-zA-Z]+',k))
    norm=set(normalize(k) for k in keys); roles=list(selection['values_slp1']); panel=selection['panel']
    values={k:selection['values_slp1'][k] for k in roles}
    details=[]
    def score(mapping):
        exact=0; normalized=0; hits=[]
        for item in panel:
            choices=[]
            for i,role in enumerate(item['roles']):
                v=mapping[role]
                if i>0:v=[x for x in v if x not in ['maha','mahA']]
                choices.append(v)
            forms={''.join(x) for x in itertools.product(*choices)}
            ex=sorted(forms&keys); nh=sorted({normalize(x) for x in forms}&norm)
            exact+=bool(ex);normalized+=bool(nh)
            hits.append({'id':item['id'],'exact_matches':ex,'normalized_classes':nh,'generated_forms':sorted(forms)})
        return exact,normalized,hits
    observed=score(values)
    for perm in itertools.permutations(roles):
        mapping={r:values[p] for r,p in zip(roles,perm)};ex,nh,hits=score(mapping)
        details.append({'assignment':dict(zip(roles,perm)),'exact_score':ex,'normalized_score':nh})
    exscores=[x['exact_score'] for x in details]; nscores=[x['normalized_score'] for x in details]
    # Prefix candidate intersection: X plus each of the three fixed anchor suffixes.
    def intersection(suffixroles):
        pools=[]
        for role in suffixroles:
            suffixes={normalize(x) for x in values[role] if x not in ['maha','mahA']}
            pools.append({w[:-len(s)] for w in norm for s in suffixes if w.endswith(s) and len(w)>len(s)})
        return set.intersection(*pools)
    candidates=intersection(['DHANA','MA','PALA'])
    inter=[]
    for chosen in itertools.combinations(roles,3):inter.append({'suffix_roles':list(chosen),'candidate_count':len(intersection(chosen))})
    dump(rawout/'lexical-observed.json',observed[2]);dump(rawout/'lexical-permutations.json',details)
    dump(rawout/'intersection-candidates.json',{'normalized_candidates':sorted(candidates),'comparisons':inter})
    return {'status':'Frozen evaluation', 'selection_scope':'Bonta-selected anchor types, not held-out texts',
            'roles':len(roles),'reading_types':len(panel),'permutations':len(details),
            'dictionary_k1_rows':len(allkeys),'distinct_alphabetic_headwords':len(keys),'normalized_headword_classes':len(norm),
            'excluded_k1_rows':sum(not re.fullmatch('[a-zA-Z]+',k) for k in allkeys),
            'normalization':'SLP1 vowel length, stops within place including voicing/aspiration, all sibilants, retroflex/dental n; fixed Table 18 variants',
            'exact':{'observed':observed[0],'null_mean':float(np.mean(exscores)),'null_histogram':dict(sorted(collections.Counter(exscores).items())), 'tail_n':sum(x>=observed[0] for x in exscores), 'p':sum(x>=observed[0] for x in exscores)/len(exscores)},
            'normalized':{'observed':observed[1],'null_mean':float(np.mean(nscores)),'null_histogram':dict(sorted(collections.Counter(nscores).items())), 'tail_n':sum(x>=observed[1] for x in nscores), 'p':sum(x>=observed[1] for x in nscores)/len(nscores)},
            'consistency_intersection':{'candidate_classes':len(candidates),'PU_normalized_value_survives':normalize('BU') in candidates,'three_suffix_sets':len(inter),'minimum_candidates':min(x['candidate_count'] for x in inter),'maximum_candidates':max(x['candidate_count'] for x in inter),'scope':'All dictionary headwords, no name/title semantic filter; order of the same three suffixes cannot change an intersection'},
            'coverage':{'table18_stated_signs':55,'graphic_roles_tested':6,'warning':'Roles pool illustrated allographs; 6/55 is a role-count indicator, not token or inscription coverage'},
            'limitations':['Panel selected by Bonta for lexical fit before this test','Entire developmental search and plausible unattested compounds are not modelled','No historical-language conclusion','Full 55-sign map remains unresolved']}

def normalize_cisi(text):
    m=re.fullmatch(r'([A-Za-z]+)[ -]*(\d+)([A-Za-z]*)',text.strip())
    return (m[1].lower(),int(m[2])) if m else None

def validation_audit(pages, lipi, rawout):
    # One catalogue example starts with a primary MH/ICIT number, not a cross-reference
    # inside its explanatory bracket. Track bracket depth to separate those cases.
    examples=[]
    for segment in range(85,217):
        s=pages[segment]; depth=0; starts=[]
        for m in re.finditer(r'\[|\]|\b(?:MH\s*\d{3,5}|ICIT\s*\d{1,5})\b',s):
            if m[0]=='[':depth+=1
            elif m[0]==']':depth=max(0,depth-1)
            elif depth==0:starts.append((m.start(),m[0]))
        for k,(start,label) in enumerate(starts):
            end=starts[k+1][0] if k+1<len(starts) else len(s)
            excerpt=s[start:end]
            # catalogue identities elsewhere in the excerpt may be comparisons;
            # retain them as candidates rather than certifying a carrier.
            cisi=re.findall(r'\b(M|H|L|K|C|Ad|Blk|Ns|Krs|Sktd|B)\s*-?\s*(\d{1,4})\b',excerpt)
            mhs=re.findall(r'\bMH\s*(\d{3,5})\b',excerpt)
            icits=re.findall(r'\bICIT\s*(\d{1,5})\b',excerpt)
            examples.append({'segment':segment,'primary':label.replace(' ',''),'primary_scheme':'ICIT' if label.startswith('ICIT') else 'MH','cisi_candidates':sorted(set(f'{x}-{y}' for x,y in cisi)),'MH_ids':sorted(set(mhs)),'ICIT_ids':sorted(set(icits)),'excerpt':excerpt})
    index=collections.defaultdict(set)
    for row in lipi:
        key=normalize_cisi(row.get('source_cisi',''))
        if key:index[key].add(row['object_family_id'])
    mh_objects={normalize_cisi(c) for e in examples if e['primary_scheme']=='MH' for c in e['cisi_candidates']}
    icit=[e for e in examples if e['primary_scheme']=='ICIT']; cats=collections.Counter(); resolved=set(); overlap=set(); withmh=set()
    for e in icit:
        keys={normalize_cisi(c) for c in e['cisi_candidates']};keys.discard(None)
        fam={f for k in keys for f in index.get(k,set())}
        e['lipi_family_candidates']=sorted(fam);e['also_MH_reference']=bool(e['MH_ids']);e['object_in_MH_primary_examples']=bool(keys&mh_objects)
        if e['also_MH_reference']:withmh.add(e['primary'])
        if len(fam)==1:resolved.add(e['primary'])
        if e['object_in_MH_primary_examples']:overlap.add(e['primary'])
        cats['no_cisi' if not keys else 'unique_family' if len(fam)==1 else 'unresolved_or_multiple_family']+=1
    dump(rawout/'paper-examples.json',examples)
    return {'status':'Exploratory','parser':'Bracket-depth primary-label parser; form-feed continuation may lose a split example',
            'all_example_occurrences':len(examples),'MH_primary_occurrences':sum(e['primary_scheme']=='MH' for e in examples),
            'ICIT_primary_occurrences':len(icit),'ICIT_primary_unique_ids':len(set(e['primary'] for e in icit)),
            'ICIT_primary_unique_ids_with_explicit_MH_reference':len(withmh),
            'ICIT_primary_unique_ids_with_catalogue_object_also_in_MH_primary_examples':len(overlap),
            'ICIT_primary_unique_ids_joining_one_current_Lipi_family':len(resolved),
            'occurrence_join_categories':dict(cats),
            'overlap_identifiers':sorted(overlap),'explicit_MH_identifiers':sorted(withmh),
            'claimed_validation_readable_range':[12,15],'exact_validation_ids_reported':False,
            'attempted_total_reported':False,'failure_total_reported':False,
            'independent_validation_rate':None,'note':'Overlap is in the paper source-history proxy; cannot assign it to the unidentified 12–15 lecture examples.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',default='run-2026-10-08-v1');ap.add_argument('--permutations',type=int,default=4999)
    a=ap.parse_args();out=OWN/a.run;rawout=RAW/a.run
    out.mkdir(exist_ok=False);rawout.mkdir(exist_ok=False)
    paths=[OWN/'PROTOCOL.md',OWN/'selection.json',ROOT/'data/normalized/lipi_observed_faces.jsonl',ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl',ROOT/'data/normalized/mayig_lines.jsonl',ROOT/'data/normalized/mayig_wells_class_crosswalk.json',RAW/'papers/bonta-2024-partial-decipherment-2nd-ed.page-text.txt',RAW/'papers/page-segments.json',RAW/'acquisition-2026-10-08-v1/mw.txt',RAW/'acquisition-2026-10-08-v1/csl-LICENSE']
    manifest={'seed':SEED,'permutations':a.permutations,'python':sys.version,'numpy':np.__version__,'inputs':[{ 'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p),'bytes':p.stat().st_size} for p in paths]}
    dump(out/'manifest.json',manifest)
    selection=read(OWN/'selection.json');allrows=rows(paths[2]);clean=rows(paths[3]);longest={}
    for r in clean:
        g=r['object_family_id']
        if g not in longest or (-r['length'],r['record_id'])<(-longest[g]['length'],longest[g]['record_id']):longest[g]=r
    principal=list(longest.values());unique={tuple(r['signs_reading_rtl']):r for r in principal}
    populations={'clean_faces':clean,'longest_eligible_object_faces':principal,'unique_object_texts':list(unique.values()),'principal_length_ge_two':[r for r in principal if r['length']>=2]}
    dist={'status':'Exploratory','populations':{},'orientation':'Reuse checked reading-rlt lists; no new reversal', 'all_faces':{'rows':len(allrows),'tokens':sum(r['length'] for r in allrows),'740_tokens':sum(r['signs_reading_rtl'].count('740') for r in allrows)}}
    for name,rs in populations.items():
        print('positions',name,flush=True)
        dist['populations'][name]={'rows':len(rs),'objects':len(set(r['object_family_id'] for r in rs)),'tokens':sum(r['length'] for r in rs),'signs':positions(rs,selection['position_targets'])}
    nulls,refs=permutations(principal,selection['position_targets'],a.permutations);dist['principal_reference_tests']=nulls;dump(rawout/'position-references.json',refs)
    fish=selection['fish_proxy_wells'];summary,exceptions=fish_summary([r['signs_reading_rtl'] for r in principal],set(fish),'220','002','032');dist['fish_proxy']=summary
    dump(rawout/'fish-exceptions.json',[principal[i] for i in exceptions])
    ml=rows(paths[4]);clear=[r for r in ml if not r['has_unknown_sign'] and r['max_damage']==0 and r['max_uncertainty']==0]
    mf,mi=fish_summary([r['signs_reading_rtl'] for r in clear],set(selection['fish_proxy_mayig']),'P050','P122','P145');dist['clear_Mayig']={'lines':len(clear),'objects':len(set(r['object_family_id'] for r in clear)),'tokens':sum(r['length'] for r in clear),'fish_proxy':mf,'signs':positions(clear,{'P324':'terminal','P217':'terminal','P122':'early','P147':'late'})}
    dump(rawout/'mayig-fish-exceptions.json',[clear[i] for i in mi])
    dist['U_stroke_proxy']={'objects_with_U':sum('700' in r['signs_reading_rtl'] for r in principal), 'adjacency_by_stroke':{x:sum(sum((s[i]=='700' and s[j]==x) for i in range(len(s)) for j in [i-1,i+1] if 0<=j<len(s)) for s in [r['signs_reading_rtl'] for r in principal]) for x in ['031','032','033','034','035','001','002','003','004','005','055']},'scope':'Adjacent tokens on selected faces; cannot select the opposite-side numeral field from this proxy'}
    dump(out/'distributions.json',dist)
    print('lexical',flush=True);lex=lexical(selection,paths[8],rawout);dump(out/'lexical.json',lex)
    print('validation',flush=True);val=validation_audit(read(paths[7]),allrows,rawout);dump(out/'validation.json',val)
    crosswalk=read(paths[5])['by_mayig_class'];maps=[]
    targets={**{k:v['mayig'] for k,v in selection['graphic_roles'].items()},'jar':'P324','arrow':'P217','U':'P310','short_tick':'P121','short_pair':'P122','long_pair':'P145','basic_fish':'P050','internal_fish':'P056','barred_fish':'P058','caret_fish':'P060','whiskered_fish':'P062'}
    for name,p in targets.items():
        row=crosswalk[p]
        maps.append({'role':name,'mayig':p,'wells_candidates':row['wells_candidates'],'mahadevan_sign_candidates':row['mahadevan_candidates'],'parpola_schema_candidates':row['parpola_candidates'],'helsinki1979_confirmed_codes':[], 'basis':'Letter PDF 2/4 for anchors; schema description for position/fish proxies. Mayig direct candidate mapping; no transitive closure.', 'status':'Provisional graphic identification; annotator candidate sets', 'fine_mapping_unresolved':len(row['wells_candidates'])>1})
    dump(out/'concordance.json',{'mappings':maps,'unresolved':selection['unresolved'],'Helsinki':'No accepted archaeological layer/crosswalk; current digitization release gate Failed. V-prefixed schema candidates are not certified 1979 lower codes.'})
    dump(out/'metrology.json',{'usable_inscription_physical_quantity_joins':0,'physical_sign_value_test':'Proposed','reason':'No source-qualified inscription-to-measured-weight/content join for Bonta anchor/M fields in available inputs','reuse':'Package G review-response-v4 fits; no re-fitting','fish_denominations':[1,2,4,8,16,32,64],'oval_denominations':[160,320,640],'status':'Proposed'})
    print(json.dumps({'run':a.run,'principal_objects':len(principal),'lexical':lex['normalized'],'validation':{k:v for k,v in val.items() if k.endswith('ids') or k.endswith('occurrences')}},indent=2))

if __name__=='__main__': main()
