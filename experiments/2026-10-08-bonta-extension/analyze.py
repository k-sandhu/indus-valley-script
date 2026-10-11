"""Construct sign dossiers and Bonta-style lexical hypotheses; no decipherment test."""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, hashlib, itertools, json, re, math
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-08-bonta-extension'
INPUTS = json.loads((HERE / 'PROTOCOL.json').read_text(encoding='utf-8'))['inputs']
EXCLUDE = {'000', '999'}
VOWELS = set('aAiIuUfFxXeEoO')
SLP = {'ā':'A','ī':'I','ū':'U','ṛ':'f','ṝ':'F','ḷ':'x','ṅ':'N','ñ':'Y',
       'ṭ':'w','ḍ':'q','ṇ':'R','ś':'S','ṣ':'z','ṃ':'M','ṁ':'M','ḥ':'H'}
ASP = {'kh':'K','gh':'G','ch':'C','jh':'J','ṭh':'W','ḍh':'Q','th':'T',
       'dh':'D','ph':'P','bh':'B','ai':'E','au':'O'}

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def lines(path):
    return [json.loads(x) for x in (ROOT/path).read_text(encoding='utf-8').splitlines() if x]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def slp(word):
    for a,b in ASP.items():
        word = word.replace(a,b)
    return ''.join(SLP.get(c,c) for c in word)

def iast(word):
    table = {'A':'ā','I':'ī','U':'ū','f':'ṛ','F':'ṝ','x':'ḷ','X':'ḹ','e':'e','E':'ai',
             'o':'o','O':'au','K':'kh','G':'gh','N':'ṅ','C':'ch','J':'jh','Y':'ñ',
             'w':'ṭ','W':'ṭh','q':'ḍ','Q':'ḍh','R':'ṇ','T':'th','D':'dh','P':'ph',
             'B':'bh','S':'ś','z':'ṣ','M':'ṃ','H':'ḥ'}
    return ''.join(table.get(c,c) for c in word)

NORM = str.maketrans({**dict.fromkeys('Aa','a'), **dict.fromkeys('Ii','i'),
        **dict.fromkeys('Uu','u'), **dict.fromkeys('kKgG','k'),
        **dict.fromkeys('cCjJ','c'), **dict.fromkeys('wWqQ','t'),
        **dict.fromkeys('tTdD','d'), **dict.fromkeys('pPbB','p'),
        **dict.fromkeys('Szs','s'), 'R':'n', 'F':'f', 'X':'x'})

def normalize(word):
    return word.translate(NORM)

def seed_values(row):
    label = row['label']
    if label == 'AS': return ['as']
    if label == 'ISH': return ['IS','Iz']
    if label == 'ASTI': return ['asti']
    text = row.get('proposed_variants') or ''
    text = text.split(';')[0]
    values = []
    for x in re.split(r'[,/]', text):
        x = x.strip()
        if re.fullmatch(r'[a-zāīūṛṝḷṅñṭḍṇśṣṃḥ]+', x): values.append(slp(x))
    return sorted(set(values))

def import_seeds():
    catalogue = load('data/raw/2026-10-08-bonta-review/pdf-2026-10-09-v1/sign-catalogue-v2.json')
    mapping = {r['sign_id']:r for r in load('experiments/2026-10-08-bonta-review/pdf-2026-10-09-v1/mapping-v1-frozen.json')['rows']}
    seeds = defaultdict(list)
    unmapped = []
    for row in catalogue:
        if row.get('table_entry') is None: continue
        cross = mapping.get(row['sign_id'], {})
        record = {'source_id':row['sign_id'], 'label':row['label'], 'category':row['category'],
                  'slp1':seed_values(row), 'pdf_page':row['pdf_page'],
                  'graphic_mapping_confidence':cross.get('confidence','unmapped'),
                  'mayig_candidates':cross.get('mayig_candidates',[]),
                  'source_crop':row['crop_path']}
        if not cross.get('wells_candidates'): unmapped.append(record)
        for w in cross.get('wells_candidates',[]): seeds[w].append(record)
    return dict(seeds), unmapped

def dictionary():
    text = (ROOT/INPUTS[6]).read_text(encoding='utf-8')
    entries = defaultdict(list)
    for block in text.split('<LEND>'):
        h = re.search(r'<L>([^<\n]+)<pc>([^<\n]+)<k1>([^<\n]+)',block)
        if h and re.fullmatch('[a-zA-Z]+', h[3]):
            plain = re.sub('<[^>]+>',' ',block[h.end():])
            plain = re.sub(r'\s+',' ',plain).strip()
            entries[h[3]].append({'entry_id':h[1], 'page_column':h[2], 'excerpt':plain[:280]})
    return dict(entries)

def dossiers(allrows, clean, cross):
    observed = sorted({s for r in allrows for s in r['signs_visual_ltr']} - EXCLUDE)
    universe = sorted(set(observed)|set(cross['by_wells_id']))
    total=Counter(); families=defaultdict(set)
    for r in allrows:
        for s in r['signs_visual_ltr']:
            if s not in EXCLUDE:
                total[s]+=1; families[s].add(r['object_family_id'])
    unique = {}
    for r in clean:
        unique.setdefault(tuple(r['signs_reading_rtl']),[]).append(r)
    freq=Counter(); positions=defaultdict(Counter); left=defaultdict(Counter); right=defaultdict(Counter)
    sites=defaultdict(Counter); types=defaultdict(Counter); examples=defaultdict(list)
    numeral={w for w,ps in cross['by_wells_id'].items() if any(119<=int(p[1:])<=153 for p in ps)}
    numadj=Counter(); fishadj=Counter()
    fish={w for w,ps in cross['by_wells_id'].items() if any(47<=int(p[1:])<=65 for p in ps)}
    for seq, records in unique.items():
        rep=min(records,key=lambda r:r['record_id'])
        for i,s in enumerate(seq):
            if s in EXCLUDE:continue
            freq[s]+=1
            positions[s]['singleton' if len(seq)==1 else 'initial' if i==0 else 'final' if i==len(seq)-1 else 'medial']+=1
            if i: left[s][seq[i-1]]+=1
            if i+1<len(seq):right[s][seq[i+1]]+=1
            sites[s][rep['site']]+=1; types[s][rep['object_type']]+=1
            neighbours=seq[max(0,i-1):i]+seq[i+1:i+2]
            numadj[s]+=bool(set(neighbours)&numeral)
            fishadj[s]+=bool(set(neighbours)&fish)
            examples[s].append({'record_id':rep['record_id'],'source_cisi':rep['source_cisi'],
                'sequence':list(seq),'slot':i,'object_family_ids':sorted({r['object_family_id'] for r in records})})
    index={s:i for i,s in enumerate(universe)}
    vec=np.zeros((len(universe),2*len(universe)),dtype=float)
    for s in universe:
        for t,n in left[s].items():
            if t in index:vec[index[s],index[t]]=n
        for t,n in right[s].items():
            if t in index:vec[index[s],len(universe)+index[t]]=n
    norms=np.linalg.norm(vec,axis=1)
    unit=vec/np.maximum(norms[:,None],1)
    sims=unit@unit.T
    result=[]
    for s in universe:
        n=freq[s]; pos=positions[s]
        nearest=[]
        for j in np.argsort(-sims[index[s]]):
            t=universe[j]
            if t!=s and freq[t]>=3 and sims[index[s],j]>0:
                nearest.append({'code':t,'cosine':round(float(sims[index[s],j]),4),'unique_frame_tokens':freq[t]})
                if len(nearest)==8:break
        ps=cross['by_wells_id'].get(s,[])
        result.append({'code':s,'mayig_candidates':ps,
            'shape_descriptions':[cross['by_mayig_class'][p]['description'] for p in ps],
            'whole_corpus_tokens':total[s], 'whole_corpus_object_families':len(families[s]),
            'complete_unique_frame_tokens':n,'positions':dict(pos),
            'final_fraction':round(pos['final']/n,4) if n else None,
            'initial_fraction':round(pos['initial']/n,4) if n else None,
            'singleton_fraction':round(pos['singleton']/n,4) if n else None,
            'numeral_adjacent_fraction':round(numadj[s]/n,4) if n else None,
            'fish_adjacent_fraction':round(fishadj[s]/n,4) if n else None,
            'preceding':dict(left[s].most_common(6)), 'following':dict(right[s].most_common(6)),
            'sites':dict(sites[s].most_common(4)), 'object_types':dict(types[s].most_common(4)),
            'context_neighbours':nearest})
    return result,unique,dict(examples),{'observed_codes':len(observed),'catalogue_union_codes':len(universe),
        'clean_faces':len(clean),'complete_unique_sequences':len(unique),'whole_corpus_faces':len(allrows),
        'whole_corpus_object_families':len({r['object_family_id'] for r in allrows})}

def lexical_search(unique, seeds, entries):
    values={s:sorted({v for r in rs for v in r['slp1']}) for s,rs in seeds.items()}
    values={s:v for s,v in values.items() if v}
    patterns=defaultdict(dict)
    for seq,rs in unique.items():
        for length in (2,3):
            for start in range(len(seq)-length+1):
                window=seq[start:start+length]
                unknown=[i for i,s in enumerate(window) if s not in values and s not in EXCLUDE]
                if len(unknown)!=1 or any(s in EXCLUDE for s in window):continue
                slot=unknown[0]; u=window[slot]
                if any(s not in values for i,s in enumerate(window) if i!=slot):continue
                if math.prod(len(values[s]) for i,s in enumerate(window) if i!=slot)>80:continue
                key='-'.join(window)
                if key not in patterns[u]:
                    patterns[u][key]={'window':list(window),'slot':slot,'records':[],'object_families':set()}
                patterns[u][key]['records'].extend(r['record_id'] for r in rs)
                patterns[u][key]['object_families'].update(r['object_family_id'] for r in rs)
    combos={}
    requests=set()
    for u,ps in patterns.items():
        for key,p in ps.items():
            choices=[]
            for i,s in enumerate(p['window']):choices.append(['?'] if i==p['slot'] else values[s])
            joined=[]
            for parts in itertools.product(*choices):
                pre=''.join(parts[:p['slot']]); suf=''.join(parts[p['slot']+1:])
                joined.append((pre,suf));requests.add((pre,suf))
            combos[u,key]=sorted(set(joined))
    forms={False:{w:[w] for w in entries},True:defaultdict(list)}
    for w in entries: forms[True][normalize(w)].append(w)
    slot_hits={False:{},True:{}}
    for relaxed in (False,True):
        req={(normalize(p),normalize(s)) if relaxed else (p,s) for p,s in requests}
        pres={p for p,s in req if p}; sufs={s for p,s in req if s}
        plen={len(x) for x in pres}; slen={len(x) for x in sufs}
        pi=defaultdict(list); si=defaultdict(list)
        for word in forms[relaxed]:
            for length in plen:
                p=word[:length]
                if p in pres and len(word)>length:pi[p].append(word)
            for length in slen:
                s=word[-length:]
                if s in sufs and len(word)>length:si[s].append(word)
        for pre,suf in req:
            pool=pi[pre] if pre else si[suf]
            if pre and suf and len(si[suf])<len(pool):pool=si[suf]
            hits=defaultdict(list)
            for word in pool:
                if len(word)<=len(pre)+len(suf) or not word.startswith(pre) or not word.endswith(suf):continue
                x=word[len(pre):len(word)-len(suf) if suf else len(word)]
                if len(x)>6 or not set(x)&VOWELS:continue
                hits[x].extend(forms[relaxed][word][:3])
            slot_hits[relaxed][pre,suf]=dict(hits)
    summaries={}; witnesses={}
    for u,ps in patterns.items():
        candidates=defaultdict(lambda:{'exact':set(),'relaxed':set(),'heads':set(),'examples':[]})
        context_records=[]
        for key,p in ps.items():
            matched={False:set(),True:set()}
            for relaxed in (False,True):
                for pre,suf in combos[u,key]:
                    query=(normalize(pre),normalize(suf)) if relaxed else (pre,suf)
                    for x,heads in slot_hits[relaxed][query].items():
                        canon=normalize(x)
                        c=candidates[canon]
                        c['relaxed' if relaxed else 'exact'].add(key); c['heads'].update(heads)
                        matched[relaxed].add(canon)
                        if len(c['examples'])<6:
                            c['examples'].append({'pattern':key,'pre':pre,'post':suf,'residual':x,
                                'headword':heads[0],'match':'normalized' if relaxed else 'exact',
                                'lexicon_record':entries[heads[0]][0]['entry_id']})
            context_records.append({'pattern':key,**{k:(sorted(v) if isinstance(v,set) else v) for k,v in p.items()},
                'exact_candidate_classes':len(matched[False]),'normalized_candidate_classes':len(matched[True]),
                'exact_candidates':sorted(matched[False]),'normalized_candidates':sorted(matched[True])})
        ranked=[]
        for x,c in candidates.items():
            support=c['exact']|c['relaxed']
            score=len(support)+0.5*len(c['exact'])
            ranked.append({'normalized_slot':x,'slot_iast':iast(x),'context_count':len(support),
                'exact_context_count':len(c['exact']),'score':score,
                'support_fraction':round(len(support)/len(ps),4),
                'matching_headword_count':len(c['heads']),'examples':c['examples']})
        ranked.sort(key=lambda x:(-x['score'],len(x['normalized_slot']),x['normalized_slot']))
        common=set.intersection(*(set(c['normalized_candidates']) for c in context_records)) if context_records else set()
        summaries[u]={'pattern_count':len(ps),'candidate_classes':len(ranked),
            'full_intersection_classes':len(common),'full_intersection':sorted(common)[:20],
            'top':ranked[:5], 'status':'exploratory lexical ranking; window boundaries are assumed'}
        witnesses[u]={'patterns':context_records,'ranking':ranked[:100]}
    return summaries,witnesses,values

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',default='run-2026-10-08-v1');args=p.parse_args()
    out=HERE/args.run;raw=RAW/args.run
    out.mkdir(parents=True,exist_ok=False);raw.mkdir(parents=True,exist_ok=False)
    manifest={'status':'Exploratory','inputs':[{'path':x,'sha256':sha(ROOT/x),'bytes':(ROOT/x).stat().st_size} for x in INPUTS],
        'protocol_sha256':sha(HERE/'PROTOCOL.json'),'code_sha256':sha(Path(__file__)),
        'source_handling':'Raw corpus contexts, search witnesses and dictionary excerpts remain local-only.'}
    write(out/'input-manifest.json',manifest)
    print('Building observation dossiers',flush=True)
    allrows=lines(INPUTS[0]);clean=lines(INPUTS[1]);cross=load(INPUTS[3])
    ds,unique,examples,counts=dossiers(allrows,clean,cross)
    seeds,unmapped=import_seeds();entries=dictionary()
    print('Searching dictionary with provisional anchors',flush=True)
    lex,witnesses,values=lexical_search(unique,seeds,entries)
    # Brief top hypotheses are project output. Full word lists/context strings stay local.
    write(out/'dossiers.json',{'counts':counts,'rows':ds})
    write(out/'inherited-seeds.json',{'by_wells':seeds,'unmapped_source_rows':unmapped})
    safe={u:{**{k:v for k,v in r.items() if k!='top'},'top':[
        {k:v for k,v in c.items() if k!='examples'} for c in r['top']]} for u,r in lex.items()}
    write(out/'lexical-summary.json',safe)
    write(raw/'lexical-witnesses.json',witnesses)
    write(raw/'observation-witnesses.json',examples)
    write(raw/'dictionary-index.json',entries)
    write(raw/'lexical-summary-with-examples.json',lex)
    summary={**counts,'bonta_mapped_codes':len(seeds),'bonta_unmapped_drawing_entries':len(unmapped),
        'dictionary_headwords':len(entries),'lexically_searched_unknown_codes':len(lex),
        'codes_with_multiple_lexical_contexts':sum(v['pattern_count']>=2 for v in lex.values()),
        'unknown_codes_with_nonempty_full_intersection':sum(v['full_intersection_classes']>0 for v in lex.values())}
    write(out/'construction-summary.json',summary)
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
