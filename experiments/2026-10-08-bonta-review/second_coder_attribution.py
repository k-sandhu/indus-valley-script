"""Post-outcome descriptive attribution to disputed field targets."""
import collections, copy, json
from pdf_followup import ROOT, OWN, RAW, WORK, read, write, sha
from second_coder_sensitivity import BASE, LOCAL, Grammar

if __name__=='__main__':
    if (BASE/'target-attribution.json').exists():raise SystemExit('Attribution exists')
    first=read(BASE/'mapping-first.json');second={r['sign_id']:r for r in read(BASE/'mapping-second.json')['rows']}
    agreed={r['sign_id'] for r in read(BASE/'mapping-agreed_only.json')['rows']}
    rows=[json.loads(l) for l in (ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]
    grouped=collections.defaultdict(list)
    for r in rows:grouped[r['object_family_id']].append(r)
    chosen=[sorted(v,key=lambda r:(-len(r['signs_reading_rtl']),r['record_id']))[0] for v in grouped.values()]
    old=Grammar(first);baseline=[old.assess(tuple(r['signs_reading_rtl']))[0] for r in chosen]
    results=[];local=[]
    for mode in ['second replacement','agreed omission']:
        for target in ['B069','B074','B075','B078']:
            if mode=='agreed omission' and target in agreed:continue
            mp=copy.deepcopy(first)
            mp['rows']=[second[r['sign_id']] if mode=='second replacement' and r['sign_id']==target else r for r in mp['rows']]
            if mode=='agreed omission':mp['rows']=[r for r in mp['rows'] if r['sign_id']!=target]
            g=Grammar(mp);cnt=collections.Counter();adj=0;changed=[]
            for r,oldstatus in zip(chosen,baseline):
                status,_,_,a=g.assess(tuple(r['signs_reading_rtl']));cnt[status]+=1;adj+=a
                if status!=oldstatus:changed.append(r['record_id'])
            results.append({'mode':mode,'target':target,'classification':dict(cnt),'fish_adjacent_pairs':adj,'changed_classifications':len(changed)})
            local.append({'mode':mode,'target':target,'changed_record_ids':changed})
    sel=read(WORK/'lexical-selection-v2.json');clean={int(k) for k,v in sel['derivation_classes'].items() if v['dictionary_context_search_excluded_with_confidence']}
    subset=[r for r in sel['readings'] if r['basis'].startswith('explicit caption') and set(r['roles'])<=clean and len(r['roles'])>=2]
    removed=[r for r in subset if not set(r['signs'])<=agreed]
    clean_dropped={'source_multi_role_occurrences':len(subset),'removed_multi_role_occurrences':len(removed),
        'source_types':len({tuple(r['roles']) for r in subset}),
        'retained_types':len({tuple(r['roles']) for r in subset if set(r['signs'])<=agreed}),
        'dropped_target_occurrences':dict(collections.Counter(s for r in removed for s in set(r['signs'])-agreed)),
        'affected_reading_ids':[r['reading_id'] for r in removed]}
    write(LOCAL/'target-attribution-rows.json',local)
    write(BASE/'target-attribution.json',{'status':'Exploratory','post_outcome':True,'protocol_sha256':sha(OWN/'PROTOCOL.md'),
        'diagnostic_results':results,'clear_origin_restriction':clean_dropped,
        'adjudication':'All disputed targets remain unresolved; these are replacement/omission sensitivities.'})
    print(results);print(clean_dropped)
