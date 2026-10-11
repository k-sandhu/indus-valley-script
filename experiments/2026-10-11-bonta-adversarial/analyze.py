"""Adversarial structural and lexical diagnostics, preserving prior endpoints."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,importlib.util,itertools,json,re,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=HERE/'run-v1'
RAW=ROOT/'data/raw/2026-10-11-bonta-adversarial/run-v1'
OLD=ROOT/'experiments/2026-10-08-bonta-extension'
sys.path.insert(0,str(OLD))
spec=importlib.util.spec_from_file_location('old_analysis',OLD/'analyze.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text(encoding='utf-8').splitlines() if x]

def bh(p):
    n=len(p);order=np.argsort(p);vals=np.asarray(p)[order]*n/np.arange(1,n+1)
    vals=np.minimum(1,np.minimum.accumulate(vals[::-1])[::-1]);ans=np.zeros(n);ans[order]=vals;return ans

def frame_stats(frame,codes):
    ix={s:i for i,s in enumerate(codes)}
    total=np.zeros(len(codes),dtype=int);pos=np.zeros((len(codes),3),dtype=int);expected=np.zeros_like(pos,dtype=float)
    for seq in frame:
        if len(seq)<2:continue
        counts=Counter(seq)
        for s,n in counts.items():
            if s not in ix:continue
            j=ix[s];total[j]+=n
            expected[j]+=np.array([1,max(0,len(seq)-2),1])*n/len(seq)
        for i,s in enumerate(seq):
            if s in ix:pos[ix[s],0 if i==0 else 2 if i==len(seq)-1 else 1]+=1
    return total,pos,expected

def main():
    global OUT,RAW
    p=argparse.ArgumentParser();p.add_argument('--run',default='run-v2');args=p.parse_args()
    OUT=HERE/args.run;RAW=ROOT/'data/raw/2026-10-11-bonta-adversarial'/args.run
    OUT.mkdir(parents=True,exist_ok=False);RAW.mkdir(parents=True,exist_ok=False)
    prior_files=[p for p in OLD.rglob('*') if p.is_file()]
    prior_files += [ROOT/'experiments/2026-10-08-bonta-review/README.md']
    write(OUT/'preservation-inputs.json',{'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in prior_files]})
    candidates=load('experiments/2026-10-08-bonta-extension/run-2026-10-09-v5/candidates.json')['rows']
    by={r['code']:r for r in candidates};codes=sorted(by);ix={s:i for i,s in enumerate(codes)}
    clean=rows('data/normalized/lipi_clean_rtl_singleline.jsonl');allrows=rows('data/normalized/lipi_observed_faces.jsonl')
    unique=defaultdict(list)
    for r in clean:unique[tuple(r['signs_reading_rtl'])].append(r)
    total,pos,expected=frame_stats(unique,codes)
    seed=20261011;reps=5000;rng=np.random.default_rng(seed)
    lexical_rng=np.random.default_rng(20261012)
    groups=defaultdict(list)
    for seq in unique:
        if len(seq)>=2:groups[len(seq)].append([ix[s] for s in seq])
    groups={n:np.asarray(a) for n,a in groups.items()}
    shuffled=np.zeros((reps,len(codes),3),dtype=np.int16)
    print('Position permutations: 5,000, all 713 codes',flush=True)
    for b in range(reps):
        for n,arr in groups.items():
            ranks=np.argsort(rng.random(arr.shape),axis=1)
            first=arr[np.arange(len(arr)),ranks[:,0]];last=arr[np.arange(len(arr)),ranks[:,-1]]
            shuffled[b,:,0]+=np.bincount(first,minlength=len(codes))
            shuffled[b,:,2]+=np.bincount(last,minlength=len(codes))
        shuffled[b,:,1]=total-shuffled[b,:,0]-shuffled[b,:,2]
    p=(1+(shuffled>=pos).sum(axis=0))/(reps+1)
    new=[ix[s] for s,r in by.items() if not r['inherited']]
    q=np.ones_like(p);q[new,:]=bh(p[new,:].ravel()).reshape(len(new),3)
    np.savez_compressed(RAW/'position-permutations.npz',counts=shuffled,codes=codes)
    # A family sensitivity chooses a deterministic longest clean face per family.
    # Repeated moulds and different families can still share a text.
    families=defaultdict(list)
    for r in clean:families[r['object_family_id']].append(r)
    family_frame=[tuple(sorted(rs,key=lambda r:(-len(r['signs_reading_rtl']),r['record_id']))[0]['signs_reading_rtl']) for rs in families.values()]
    ft,fp,fe=frame_stats(family_frame,codes)
    stats=[]
    for s in codes:
        j=ix[s];rs=[r for seq,rs in unique.items() if s in seq for r in rs]
        sites=Counter(r['site'] for seq,rr in unique.items() if s in seq for r in [min(rr,key=lambda r:r['record_id'])])
        per_site={}
        for site in sorted({r['site'] for r in rs}):
            sf={seq for seq,rr in unique.items() if s in seq and any(r['site']==site for r in rr)}
            st,sp,se=frame_stats(sf,[s]);per_site[site]={'tokens':int(st[0]),'final':int(sp[0,2]),'expected_final':round(float(se[0,2]),3)}
        stats.append({'code':s,'inherited':by[s]['inherited'],'non_singleton_tokens':int(total[j]),
          'distinct_sequences':sum(s in seq for seq in unique),'complete_face_count':len(rs),
          'complete_object_families':len({r['object_family_id'] for r in rs}),
          'positions':{name:{'observed':int(pos[j,k]),'shuffle_expected':round(float(expected[j,k]),3),
               'enrichment_ratio':round(float(pos[j,k]/expected[j,k]),3) if expected[j,k] else None,
               'one_sided_p':float(p[j,k]),'q_all_596_new_codes_3_positions':float(q[j,k]) if not by[s]['inherited'] else None}
             for k,name in enumerate(['initial','medial','final'])},
          'representative_site_counts':dict(sites),'site_final_sensitivity':per_site,
          'family_sensitivity':{'tokens':int(ft[j]),'final':int(fp[j,2]),'expected_final':round(float(fe[j,2]),3)},
          'source_old_priority':by[s]['priority']})
    write(OUT/'position-audit.json',{'seed':seed,'permutations':reps,'frame':'1,859 distinct complete sequences; singleton texts excluded from position tests','null':'Uniformly permute signs within each observed text, preserving length, sign multiset and its archaeological grouping. This measures ordering, not meaning.','multiple_tests':'BH over initial, medial and final enrichment for all 596 previously new codes (1,788 tests).','family_sensitivity':'One longest clean face per object family; no mould independence is claimed.','rows':stats})
    anchors=load('experiments/2026-10-08-bonta-extension/run-2026-10-09-v5/new-anchors.json')
    first=load('experiments/2026-10-08-bonta-review/two-coder-2026-10-09-v1/mapping-first.json')
    second=load('experiments/2026-10-08-bonta-review/two-coder-2026-10-09-v1/mapping-second.json')
    frows=first.get('rows',first);srows=second.get('rows',second)
    assert isinstance(frows,list) and isinstance(srows,list)
    fb={r['sign_id']:r for r in frows};sb={r['sign_id']:r for r in srows}
    graphic=[]
    for r in candidates:
        inherited=r['inherited_proposals']
        changes=[]
        for prop in inherited:
            sign=prop['source_id'];a=set(fb.get(sign,{}).get('wells_candidates',[]));b=set(sb.get(sign,{}).get('wells_candidates',[]))
            changes.append({'source_id':sign,'label':prop['label'],'first_contains_code':r['code'] in a,'second_contains_code':r['code'] in b,'overlap_codes':sorted(a&b),'disjoint':bool(a and b and not a&b)})
        newly_bonta=[sign for sign,z in sb.items() if r['code'] in z.get('wells_candidates',[]) and sign.startswith('B') and int(sign[1:])<=65 and r['code'] not in fb.get(sign,{}).get('wells_candidates',[])]
        if changes or newly_bonta:graphic.append({'code':r['code'],'inherited_sensitivity':changes,'additional_second_coder_table18_targets':newly_bonta})
    write(OUT/'graphic-sensitivity.json',{'scope':'Previously frozen first and blind-second graphic candidate sets; agreement concerns drawing identity, not semantics.','rows':graphic})
    entries=load('data/raw/2026-10-08-bonta-extension/run-2026-10-08-v1/dictionary-index.json')
    witnesses=load('data/raw/2026-10-08-bonta-extension/run-2026-10-09-v2/preferred-lexical-witnesses.json')
    source_text=(ROOT/'data/raw/2026-10-08-bonta-review/acquisition-2026-10-08-v1/mw.txt').read_text(encoding='utf-8')
    lexical=[]
    cases=[('233','151','ati',['bhāra','vāha','bhārika','māna','tulā']),('231','151','sam',['bhāra','vāha','bhārika','māna','tulā']),('204','540','sa',['bhāga','saṃyoga','aṃśa'])]
    inherited,_=old.import_seeds()
    values={s:sorted({v for r in rs for v in r['slp1']}) for s,rs in inherited.items()}
    for a in anchors:
        for c in a['codes']:values[c]=[old.slp(a['preferred_probe'])]
    cache={}
    def literal_slots(pattern):
        w=pattern['window'];slot=pattern['slot'];result=set()
        choices=[['?'] if i==slot else values[s] for i,s in enumerate(w)]
        for parts in itertools.product(*choices):
            pre=''.join(parts[:slot]);suf=''.join(parts[slot+1:]);key=(pre,suf)
            if key not in cache:
                hits=set()
                for word in entries:
                    length=len(word)-len(pre)-len(suf)
                    if not 1<=length<=6:continue
                    if word.startswith(pre) and word.endswith(suf):
                        resid=word[len(pre):len(word)-len(suf) if suf else len(word)]
                        if set(resid)&old.VOWELS:hits.add(resid)
                cache[key]=hits
            result.update(cache[key])
        return result
    lengths={len(old.slp(x)) for _,_,_,words in cases for x in words}
    suffix_index={n:defaultdict(set) for n in lengths};suffix_words={n:defaultdict(list) for n in lengths}
    for w in entries:
        for n in lengths:
            if 1<=len(w)-n<=6:
                pre=w[:-n]
                if set(pre)&old.VOWELS:
                    suffix_index[n][w[-n:]].add(old.normalize(pre));suffix_words[n][w[-n:]].append(w)
    print('Lexical rivals and same-length dictionary-stem controls',flush=True)
    for code,anchor,residual,words in cases:
        pats=witnesses[code]['patterns'];target=next(x for x in pats if x['window']==[code,anchor])
        exact_sets=[literal_slots(x) for x in pats];normalized_sets=[set(x['normalized_candidates']) for x in pats]
        target_literals=literal_slots(target)
        inter=set.intersection(*exact_sets) if exact_sets else set()
        variant=[]
        for word in words:
            s=old.slp(word);full=residual+s;cw=suffix_words[len(s)].get(s,[])
            pool=[x for x in entries if len(x)==len(s)];draw=lexical_rng.choice(pool,size=min(1000,len(pool)),replace=False)
            sizes=np.array([len(suffix_index[len(s)].get(x,set())) for x in draw]);actual=len(suffix_index[len(s)].get(s,set()))
            variant.append({'anchor_comparison':word,'candidate_word':old.iast(full),'exact_attested':full in entries,
                 'entry_ids':[x['entry_id'] for x in entries.get(full,[])],
                 'suffix_residual_classes':actual,'controls':len(draw),'control_median_classes':float(np.median(sizes)),
                 'control_fraction_at_least_as_many_classes':float(np.mean(sizes>=actual)),
                 'control_fraction_attesting_selected_prefix':float(np.mean([residual+x in entries for x in draw]))})
        matching=[w for w in entries if w.endswith(old.slp(words[0])) and w[:-len(old.slp(words[0]))] in target_literals]
        lexical.append({'code':code,'anchor_code':anchor,'selected_residual':residual,'searched_patterns':len(pats),
            'old_exact_headword_normalized_slot_classes':target['exact_candidate_classes'],
            'exact_target_candidate_classes':len(target_literals),'normalized_target_candidate_classes':target['normalized_candidate_classes'],
            'exact_target_residuals':[old.iast(x) for x in sorted(target_literals)],
            'selected_residual_exact_pattern_support':sum(residual in x for x in exact_sets),
            'selected_residual_normalized_pattern_support':sum(old.normalize(residual) in x for x in normalized_sets),
            'full_exact_intersection':sorted(inter),'full_normalized_intersection':sorted(set.intersection(*normalized_sets)) if normalized_sets else [],
            'anchor_word_sensitivity':variant,
            'rival_headwords':[{'headword':old.iast(w),'entries':[{'entry_id':e['entry_id'],'page_column':e['page_column']} for e in entries[w]]} for w in matching],
            'target_window_families':len(target['object_families']),
            'status':'Post-selection diagnostics; the three terms were selected in the old run.'})
    write(OUT/'lexical-adversarial.json',{'dictionary_headwords':len(entries),'controls':'Up to 1,000 random alphabetic dictionary headwords of the same SLP1 stem length; compares suffix productivity. It does not simulate an ancient language or a posterior on readings.','rows':lexical})
    write(RAW/'lexical-source-witnesses.json',{'rows':[{**r,'rival_definitions':[{**w,'definitions':entries[old.slp(w['headword'])]} for w in r['rival_headwords']]} for r in lexical]})
    # Exact class substitution after deleting the target token; this identifies
    # distributional alternatives rather than equating every near neighbour.
    selected=['151','154','156','158','161','176','400','413','142','140','143','130','131','134','825','540','645','233','231','204','411','450','452','600','319','121','272','370','818','930']
    holes=defaultdict(set)
    for seq in unique:
        if len(seq)<2:continue
        for i,s in enumerate(seq):holes[(seq[:i]+('?',)+seq[i+1:])].add(s)
    substitution=[]
    for code in selected:
        matches=[]
        for hole,alternatives in holes.items():
            if code in alternatives and len(alternatives)>1:
                matches.append({'alternatives':sorted(alternatives-{code}),'hole':hole})
        substitution.append({'code':code,'substitution_contexts':len(matches),'alternative_counts':dict(Counter(x for m in matches for x in m['alternatives']))})
    write(OUT/'substitution-audit.json',{'definition':'Distinct complete strings become identical when one token is replaced by a placeholder, with length and slot preserved. No one-edit or transitive merging.','rows':substitution})
    write(RAW/'substitution-witnesses.json',{'rows':[{**r,'holes':[list(h) for h,a in holes.items() if r['code'] in a and len(a)>1]} for r in substitution]})
    write(RAW/'observation-witnesses.json',{'by_code':{s:[r for r in clean if s in r['signs_reading_rtl']] for s in selected}})
    write(OUT/'input-manifest.json',{'status':'Exploratory','protocol_sha256':sha(HERE/'PROTOCOL.json'),'code_sha256':sha(Path(__file__)),
        'inputs':[{'path':p,'sha256':sha(ROOT/p)} for p in ['data/normalized/lipi_clean_rtl_singleline.jsonl','data/normalized/lipi_observed_faces.jsonl','experiments/2026-10-08-bonta-extension/run-2026-10-09-v5/candidates.json','experiments/2026-10-08-bonta-review/two-coder-2026-10-09-v1/mapping-first.json','experiments/2026-10-08-bonta-review/two-coder-2026-10-09-v1/mapping-second.json','data/raw/2026-10-08-bonta-review/acquisition-2026-10-08-v1/mw.txt']]})
    # Local contact sheet uses unresolved-rights font witnesses only for review.
    sheet=Image.new('RGB',(1280,((len(selected)+7)//8)*190),'#ffffff');draw=ImageDraw.Draw(sheet)
    try:
        font=ImageFont.truetype('DejaVuSans.ttf',18)
    except OSError:
        font=ImageFont.load_default(size=18)
    for j,s in enumerate(selected):
        x=(j%8)*160;y=(j//8)*190
        im=Image.open(ROOT/by[s]['font_drawing']['path']).convert('RGB');im.thumbnail((135,125));sheet.paste(im,(x+12+(135-im.width)//2,y+8))
        draw.text((x+12,y+135),'W'+s,fill='#111827',font=font)
        draw.text((x+12,y+160),f"n={by[s]['observations']['complete_unique_frame_tokens']}",fill='#475569',font=font)
    sheet.save(RAW/'review-glyph-sheet.png')
    summary={'distinct_sequences':len(unique),'clean_faces':len(clean),'clean_families':len(families),'prior_A_rule':'n >= 10, selected role in six labels, and not inherited. This is a frequency/role rule, not independent evidence.','prior_A_count':sum(r['priority']=='A' for r in candidates),'new_codes':len(new),'new_codes_with_position_q_below_05':sum(int(np.min(q[j])<.05) for j in new),'post_outcome_refinements':lexical}
    write(OUT/'summary.json',summary)
    print(json.dumps({'position_q_codes':summary['new_codes_with_position_q_below_05'],'selected':[{s['code']:s['positions']} for s in stats if s['code'] in ['151','400','142','130','825','540','645']],'lexical':[{r['code']:{'patterns':r['searched_patterns'],'exact_target':r['exact_target_candidate_classes'],'support':r['selected_residual_exact_pattern_support'],'intersection':r['full_exact_intersection']}} for r in lexical]},indent=2))

if __name__=='__main__':main()
