"""Full identifiable-reading lexical audit; fixed dictionary and value bundles.

Selection is written and hashed separately before scoring. Exact Table 18
variants are primary. No semantic acceptance or arbitrary substring matching.
"""
from pathlib import Path
import argparse, collections, functools, hashlib, itertools, json, random, re, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pdf_followup import ROOT, OWN, OUT, RAW, WORK, read, write, sha

def roman(s):
    table={'ā':'A','ī':'I','ū':'U','ṛ':'f','ṝ':'F','ḷ':'x','ṅ':'N','ñ':'Y','ṭ':'w','ḍ':'q','ṇ':'R','ś':'S','ṣ':'z','ṃ':'M','ṁ':'M','ḥ':'H'}
    for x,y in [('kh','K'),('gh','G'),('ch','C'),('jh','J'),('ṭh','W'),('ḍh','Q'),('th','T'),('dh','D'),('ph','P'),('bh','B')]:s=s.replace(x,y)
    return ''.join(table.get(c,c) for c in s)

ALIASES={1:['ka'],2:['dhu'],3:['ni'],4:['pa'],5:['pu'],6:['ma','maha'],7:['ja'],8:['sa'],9:['su'],10:['su'],11:['ra'],12:['vi'],13:['hu'],
 14:['ana'],15:['eka','eka','ka'],16:['ati'],17:['pala'],18:['dana','dhana'],19:['dana','dhana'],20:['para','pra'],21:['jaya','jya'],
 22:['vara','var','vara'],23:['mana','man'],24:['sara','sar'],25:['suri','sri'],26:['taya','tya'],27:['saha','sava'],28:['nata','natha'],
 29:['mina','min'],30:['vasu'],31:['caru','car'],32:['mana','mani'],33:['kara','kar','kra'],34:['kara','kar'],35:['pra'],36:['tra','tri'],
 37:['rashtra','rastra'],38:['laksh','laksha','laksa'],39:['sena'],40:['arya'],41:['dara','dhara'],42:['sam'],43:['raksha','raksh','raksa'],
 44:['raja','rajan'],45:['dhanya'],46:['deva','devi'],47:['pati'],48:['ashva','asva'],49:['go'],50:['as'],51:['ish','is'],52:['asti'],
 53:['sripati','suripati'],54:['sripatideva','sridevapati','devasripati'],55:['paka'],56:['sripala'],57:['aryaka'],58:['karapala']}

def key(s):return re.sub('[^a-z]','',s.lower())

def select():
    p=WORK/'lexical-selection-v2.json'
    if p.exists():raise SystemExit('Selection exists')
    inventory=read(WORK/'reading-inventory-v3.json');catalog=read(WORK/'sign-catalogue-v2.json')
    idrole={r['sign_id']:r['table_entry'] for r in catalog if r['table_entry']}
    rolevals={}
    initial_only={}
    for r in read(ROOT/'research/literature/2026-10-08-bonta-sign-inventory/inventory.json')['rows'][:58]:
        variants=r['readings']
        if r['entry']==53:variants='śrīpati, sūripati'
        if r['entry']==54:variants='śrīpatideva, śrīdevapati, devaśrīpati'
        if r['entry']==56:variants='śrīpāla'
        if r['entry']==6:
            vals=['ma','mā','maha','mahā'];initial_only[6]=['maha','mahā']
        elif r['entry']==50:vals=['as']
        elif r['entry']==51:vals=['iṣ','īś']
        elif r['entry']==52:vals=['asti']
        else:vals=re.split(r'[,;/]|; alternatively |; alternatively',variants)
        vals=[v.strip().replace('alternatively ','') for v in vals]
        vals=[v for v in vals if re.fullmatch('[a-zāīūṛṝḷṅñṭḍṇśṣṃḥ]+',v)]
        rolevals[str(r['entry'])]=sorted({roman(v) for v in vals})
        assert rolevals[str(r['entry'])],r
    reverse=collections.defaultdict(set)
    for role,aliases in ALIASES.items():
        for alias in aliases:reverse[alias].add(role)
    selections=[];unmatched=[];unknown_votes=collections.defaultdict(list)
    initial_votes=read(WORK/'lexical-selection.json')['caption_variant_votes']
    caption_roles={s:next(iter({v['role'] for v in votes})) for s,votes in initial_votes.items() if len({v['role'] for v in votes})==1}
    caption_roles.pop('U149',None)  # Visually kara, while these captions retain sava.
    for r in inventory:
        if not r['is_reading_attempt']:continue
        sequence=r['sign_sequence_assumed_rtl']; prefix=r['proposed_reading']
        aligned=[]
        if prefix:
            tokens=[t for t in re.split(r'[-\s;]+',prefix.strip(' -.*')) if t]
            expected=[reverse.get(key(t),set()) for t in tokens]
            if expected and all(expected):
                for start in range(len(sequence)-len(expected)+1):
                    window=sequence[start:start+len(expected)]
                    if all((idrole[s] in choices if s in idrole else caption_roles[s] in choices if s in caption_roles else True) for s,choices in zip(window,expected)):
                        # At least one fixed Table 18 drawing must anchor a caption alignment.
                        if any(s in idrole for s in window):aligned.append((window,expected,start))
        if len(aligned)==1:
            window,expected,start=aligned[0]; roles=[]; valid=True
            for s,choices in zip(window,expected):
                if s in idrole:roles.append(idrole[s])
                elif s in caption_roles and caption_roles[s] in choices:
                    roles.append(caption_roles[s]);unknown_votes[s].append({'role':roles[-1],'reading_id':r['reading_id'],'page':r['source_page']})
                elif len(choices)==1:
                    roles.append(next(iter(choices)));unknown_votes[s].append({'role':roles[-1],'reading_id':r['reading_id'],'page':r['source_page']})
                else:valid=False;break
            if valid:selections.append({'reading_id':r['reading_id'],'primary_label':r['primary_label'],'page':r['source_page'],
                'signs':window,'roles':roles,'basis':'explicit caption aligned to its contiguous drawing','start':start,
                'table18_only':all(s in idrole for s in window),'source_kind':r['source_kind'],
                'unclear_or_unattested':r['unclear_or_unattested_flag']})
            else:unmatched.append({'reading_id':r['reading_id'],'reason':'ambiguous source-caption role in an additional form'})
        elif r['complete_table18_sequence']:
            # Complete identified drawings remain eligible even when the caption defers to an earlier entry.
            selections.append({'reading_id':r['reading_id'],'primary_label':r['primary_label'],'page':r['source_page'],
              'signs':sequence,'roles':[idrole[s] for s in sequence],
              'basis':'entire primary drawing consists of Table 18 forms','start':0,'table18_only':True,
              'source_kind':r['source_kind'],'unclear_or_unattested':r['unclear_or_unattested_flag']})
        else:unmatched.append({'reading_id':r['reading_id'],'reason':'unresolved caption/drawing alignment or unvalued glyphs','alignment_candidates':len(aligned)})
    # Conflicting additional drawings stay outside the extended endpoint.
    conflicts={s for s,v in unknown_votes.items() if len({a['role'] for a in v})>1}|{'U149'}
    excluded=[r for r in selections if set(r['signs'])&conflicts]
    selections=[r for r in selections if not set(r['signs'])&conflicts]
    provenance={}
    anchors={6:(53,'metrology or M field'),17:(51,'metrology or M field'),18:(68,'pictorial'),19:(68,'pictorial'),36:(43,'metrology or M field')}
    pictorial={48:216,49:217}
    explicitdict={5:[70,71],47:[74,75,76]}
    for role in range(1,59):
        if role in anchors:
            page,kind=anchors[role]; basis='Initial anchor derived from metrological context or bow rebus; later dictionary refinements still occur.';certain=True
        elif role in pictorial:page=pictorial[role];kind='pictorial';basis='Animal form interpreted with reading examples; no independent sound value evidence.';certain=True
        elif role in explicitdict:page=explicitdict[role];kind='dictionary search against contexts';basis='Explicit cross-context dictionary search in the entering-wedge derivation.';certain=True
        else:page=[77,79,80,81,82];kind='later extension';basis='Later trial-and-error cross-checking against previously proposed values; narrative does not separate lexical search from subsequent confirmation.';certain=False
        provenance[str(role)]={'category':kind,'source_pages':page,'dictionary_context_search_excluded_with_confidence':certain and role in anchors|pictorial,
                              'basis':basis,'maha_extension_dictionary_fitted':role==6}
    data={'status':'Exploratory','dictionary':{'path':'data/raw/2026-10-08-bonta-review/acquisition-2026-10-08-v1/mw.txt',
              'sha256':sha(RAW/'acquisition-2026-10-08-v1/mw.txt'),'commit':'55e8addbd96e8d9001b8789026b026763f4049c1'},
          'table18_role_variants_slp1':rolevals,'initial_only_slp1':{str(k):[roman(s) for s in v] for k,v in initial_only.items()},
          'derivation_classes':provenance,'readings':selections,'excluded':unmatched,
          'caption_variant_votes':dict(unknown_votes),'conflicting_variant_ids':sorted(conflicts),
          'excluded_conflicting_variant_readings':[r['reading_id'] for r in excluded],
          'mapping_sha256':sha(OUT/'mapping-v1-frozen.json'),'inventory_sha256':sha(WORK/'reading-inventory-v3.json'),
          'protocol_sha256':sha(OWN/'PROTOCOL.md'),
          'selection_rule':'All complete Table 18 figures plus unambiguous anchored source-caption alignments. No dictionary hit used for selection.',
          'held_out_rule':'No individual entries explicitly identify membership in the historical post-fixed-value batch; ICIT-first remains a proxy only.'}
    write(p,data)
    write(OUT/'lexical-selection-freeze-v2.json',{'selection_sha256':sha(p),'reading_occurrences':len(selections),
       'table18_only_occurrences':sum(r['table18_only'] for r in selections),
       'additional_caption_variant_ids':len(unknown_votes),'conflicting_variant_ids':sorted(conflicts),
       'excluded_reading_rows':len(unmatched)+len(excluded),'provenance_unknown_later_extension_roles':49,
       'status':'Exploratory','protocol_sha256':data['protocol_sha256']})
    # Only our provenance annotations and source locations are tracked.
    write(OUT/'value-derivations-v2.json',{'status':'Exploratory','rows':[{'table18_entry':int(k),**v} for k,v in provenance.items()]})
    print(json.dumps(read(OUT/'lexical-selection-freeze-v2.json'),indent=2))

def score(output_root=OUT, raw_output_root=WORK, caption_only=False):
    selection=read(WORK/'lexical-selection-v2.json');assert sha(WORK/'lexical-selection-v2.json')==read(OUT/'lexical-selection-freeze-v2.json')['selection_sha256']
    output_root=Path(output_root).resolve();raw_output_root=Path(raw_output_root).resolve()
    if not output_root.is_relative_to(OWN) or not raw_output_root.is_relative_to(RAW):raise SystemExit('Outputs must remain in package trees')
    output_name='lexical-caption-sensitivity.json' if caption_only else 'lexical-test.json'
    raw_name='lexical-caption-predictions.json' if caption_only else 'lexical-predictions.json'
    if (output_root/output_name).exists() or (raw_output_root/raw_name).exists():raise SystemExit('Refusing existing score endpoint')
    output_root.mkdir(parents=True,exist_ok=True);raw_output_root.mkdir(parents=True,exist_ok=True)
    heads=set()
    with (RAW/'acquisition-2026-10-08-v1/mw.txt').open(encoding='utf-8') as f:
        for line in f:
            i=line.find('<k1>')
            if i>=0:
                h=line[i+4:line.find('<',i+4)]
                if re.fullmatch('[A-Za-z]+',h):heads.add(h)
    bundles={int(k):v for k,v in selection['table18_role_variants_slp1'].items()}
    # The dictionary-context-free endpoint omits the fitted initial maha extension.
    clean={int(k) for k,v in selection['derivation_classes'].items() if v['dictionary_context_search_excluded_with_confidence']}
    sets={}; population=[r for r in selection['readings'] if not caption_only or r['basis'].startswith('explicit caption')]
    for label,panel in [('table18_only',[r for r in population if r['table18_only']]),
                        ('caption_extended',population),
                        ('only_clear_nondictionary_origins',[r for r in population if set(r['roles'])<=clean])]:
        # One-sign items are counted separately; selected strings remain type-deduplicated.
        sequences=sorted({tuple(r['roles']) for r in panel if len(r['roles'])>=2})
        sets[label]=(panel,sequences)
    groups=['aA','iI','uU','fF','xX','kKgG','cCjJ','wWqQ','tTdD','pPbB','sSz','nR']
    cmap={c:g[0] for g in groups for c in g}; norm=lambda s:''.join(cmap.get(c,c) for c in s)
    results={};predictions=[]; rng=random.Random(20261009)
    for label,(panel,sequences) in sets.items():
        involved=sorted({r for seq in sequences for r in seq})
        count=__import__('math').factorial(len(involved))
        assignments=list(itertools.permutations(involved)) if count<=40320 else [tuple(rng.sample(involved,len(involved))) for _ in range(1999)]
        vals={k:([v for v in bundles[k] if v not in ('maha','mahA')] if label=='only_clear_nondictionary_origins' and k==6 else [v for v in bundles[k] if v!='bala'] if label=='only_clear_nondictionary_origins' and k==17 else bundles[k]) for k in involved}
        initial=selection['initial_only_slp1']
        @functools.lru_cache(maxsize=200000)
        def matches(values_tuple,endpoint):
            choices=[]
            for index,r in enumerate(values_tuple):
                v=vals[r]
                if index:v=[s for s in v if s not in initial.get(str(r),[])]
                choices.append(v)
            lex=heads if endpoint=='exact' else normalized
            for words in itertools.product(*choices):
                word=''.join(words)
                if (word if endpoint=='exact' else norm(word)) in lex:return True
            return False
        normalized={norm(h) for h in heads}
        endpoints={}
        for endpoint in ['exact','normalized']:
            observed=sum(matches(seq,endpoint) for seq in sequences)
            scores=[]
            for a in assignments:
                mp=dict(zip(involved,a));scores.append(sum(matches(tuple(mp[r] for r in seq),endpoint) for seq in sequences))
            tail=sum(s>=observed for s in scores)
            exactenum=count<=40320
            endpoints[endpoint]={'observed_matches':observed,'distinct_sequences':len(sequences),
              'null_assignments':len(assignments),'null_mean':sum(scores)/len(scores) if scores else None,
              'histogram':dict(sorted(collections.Counter(scores).items())),
              'assignments_at_least_observed':tail,'tail_fraction':tail/len(scores) if exactenum and scores else (tail+1)/(len(scores)+1),
              'exhaustive':exactenum,'tail_rule':'exact enumeration' if exactenum else 'add-one Monte Carlo'}
            predictions.append({'panel':label,'endpoint':endpoint,'scores':scores,
                  'observed_readings':[{'roles':list(s),'matched':matches(s,endpoint)} for s in sequences]})
        results[label]={'eligible_reading_occurrences':len(panel),'one_sign_occurrences':sum(len(r['roles'])==1 for r in panel),
          'roles_permuted':involved,'strings_containing_PU_or_PATI':sum(bool(set(seq)&{5,47}) for seq in sequences),
          'only_clear_nondictionary_origin_types':sum(set(seq)<=clean for seq in sequences),'endpoints':endpoints}
        print(label,{k:(v['observed_matches'],v['distinct_sequences'],v['null_mean'],v['tail_fraction']) for k,v in endpoints.items()},flush=True)
    write(raw_output_root/raw_name,predictions)
    write(output_root/output_name,{'status':'Exploratory','dictionary_alphabetic_heads':len(heads),
        'explicit_caption_only':caption_only,
        'selection_sha256':sha(WORK/'lexical-selection-v2.json'),'mapping_sha256':selection['mapping_sha256'],
        'matching_rule':'Exact whole-headword from fixed Table 18 variants, with initial-only maha restriction; normalized secondary retains the old broader equivalences (no su/so transform).',
        'panels':results,'historical_held_out_identifiable_entries':0,'historical_held_out_score':None,
        'interpretation':'Later extension values generally lack a separable dictionary-training history. The clear-origin subset removes explicit PU/PATI context searches and fitted maha; it is still a source-selected anchor test.'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['select','score']);p.add_argument('--output-root',default=str(OUT));p.add_argument('--raw-output-root',default=str(WORK));p.add_argument('--caption-only',action='store_true');a=p.parse_args()
    select() if a.stage=='select' else score(a.output_root,a.raw_output_root,a.caption_only)
