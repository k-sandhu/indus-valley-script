"""Run registered field, source-lexical and reading-coverage sensitivities."""
from pathlib import Path
import argparse, collections, functools, itertools, json, random, shutil
from pdf_followup import ROOT, OWN, RAW, WORK, OUT, read, write, sha
from second_coder_agreement import SCHEMA, well

BASE=OWN/'two-coder-2026-10-09-v1';LOCAL=RAW/'two-coder-2026-10-09-v1'

class Grammar:
    def __init__(self,mapping):
        self.rows={r['sign_id']:r for r in mapping['rows']}
        self.get=lambda s:set(self.rows.get(s,{}).get('wells_candidates',[]))
        self.fish=set().union(*(self.get(s) for s in ['B031','B070','B071','B072','B073']))
        self.oval1=self.get('B066')|self.get('B067');self.oval2=self.get('B068')
        self.oval3=self.get('B069');excluded=self.get('B045')
        self.amboval=(self.oval3&excluded)|(self.oval3&self.oval1)|(self.oval3&self.oval2)
        self.oval1-=self.amboval;self.oval2-=self.amboval;self.oval3-=self.amboval
        self.ma=self.get('B006');self.tra=self.get('B039');self.single=self.get('B079')
        self.terminal=self.get('B055')|self.get('B056')
        self.compound=[]
        for s,label in [('B074','fish-comb'),('B075','fish-two-strokes')]:
            self.compound += [(pattern,label) for pattern in self.patterns(s)]
        self.ms=[tuple(p) for p in itertools.product(self.ma,self.tra)]
        self.junctures=self.patterns('B077')+self.patterns('B078')
        self.ambcode=set()
        categories=[self.fish,self.oval1|self.oval2|self.oval3,self.terminal]
        for a,b in itertools.combinations(categories,2):self.ambcode|=a&b
    def patterns(self,sign):
        row=self.rows.get(sign,{})
        components=row.get('component_sequence_candidates',[])
        if components:
            return sorted({tuple(p) for seq in components for p in itertools.product(*[
                [well(w) for w in SCHEMA[c]['wells_graphemes']] for c in reversed(seq)]) if all(p)})
        return [(c,) for c in sorted(row.get('wells_candidates',[]))]
    def units(self,seq):
        result=[];i=0
        while i<len(seq):
            compound=next(((p,label) for p,label in self.compound if tuple(seq[i:i+len(p)])==p),None)
            if compound:p,label=compound;result.append(('F',label,i,i+len(p)));i+=len(p);continue
            if i+1<len(seq) and (seq[i],seq[i+1]) in self.ms:result.append(('MS','measure-pair',i,i+2));i+=2;continue
            code=seq[i]
            if code in self.ambcode:category,label='A','incompatible field categories'
            elif code in self.fish:category,label='F',code
            elif code in self.oval1:category,label='O','oval-tree'
            elif code in self.oval2:category,label='O','oval-pincers'
            elif code in self.oval3:category,label='O','oval-internal-stroke'
            elif code in self.amboval:category,label='A','oval-role ambiguity'
            else:category,label='X',code
            result.append((category,label,i,i+1));i+=1
        return result
    @functools.lru_cache(maxsize=250000)
    def assess(self,seq):
        units=self.units(seq)
        adjacency=sum(a[0]==b[0]=='F' for a,b in zip(units,units[1:]))
        status,reasons,fields=self.classify(seq,units)
        return status,tuple(reasons),tuple((f['field'],f['start'],f['end']) for f in fields),adjacency
    def classify(self,seq,u):
        reasons=[];terminal=[i for i,c in enumerate(seq) if c in self.terminal]
        js=[];i=0
        while i<len(seq):
            matching=[p for p in self.junctures if tuple(seq[i:i+len(p)])==p]
            if matching:
                p=max(matching,key=len);js.append((i,i+len(p)));i+=len(p)
            else:i+=1
        m=[x for x in u if x[0] in {'O','F','MS'}]
        anchor=any(x[0] in {'O','MS'} for x in u) or any(a[0]==b[0]=='F' for a,b in zip(u,u[1:]))
        if not terminal and not js and not anchor:return 'indeterminate',['no discriminating field anchor'],[]
        if terminal and terminal!=[len(seq)-1]:reasons.append('terminal outside final canonical slot')
        if len(js)>1:reasons.append('multiple P-exclusive junctures')
        if anchor and m:
            left,right=m[0][2],m[-1][3]
            if js and js[-1][0]>=left:reasons.append('P-exclusive juncture after M anchor')
            span=[x for x in u if x[2]>=left and x[3]<=right]
            if any(x[0]=='X' for x in span):reasons.append('interrupted canonical M span')
            types=[x[0] for x in span if x[0]!='A'];ranks={'O':0,'F':1,'MS':2,'X':3}
            if any(ranks[a]>ranks[b] for a,b in zip(types,types[1:])):reasons.append('M order differs from O-F-MS')
            f=[x[1] for x in span if x[0]=='F'];o=[x[1] for x in span if x[0]=='O']
            if len(f)>3:reasons.append('more than three F units')
            if len(f)!=len(set(f)):reasons.append('repeated F unit')
            if len(o)>2:reasons.append('more than two O units')
            if len(o)!=len(set(o)):reasons.append('repeated O unit')
            if types.count('MS')>1:reasons.append('multiple MS pairs')
        elif m:return 'indeterminate',['fish lexical/measurement role unresolved'],[]
        if reasons:return 'conflict',sorted(set(reasons)),[]
        if any(x[0]=='A' for x in u):return 'indeterminate',['mapping categories or oval role ambiguous'],[]
        fields=[];boundary=js[0][1] if js else 0
        if not boundary and anchor and m:
            singles=[i for i,c in enumerate(seq[:m[0][2]]) if c in self.single]
            if len(singles)==1:boundary=singles[0]+1
        if boundary:fields.append({'field':'P','start':0,'end':boundary})
        if anchor and m:
            if m[0][2]>boundary:return 'indeterminate',['prefix before M has no certain P boundary'],[]
            fields.append({'field':'M','start':m[0][2],'end':m[-1][3]});boundary=m[-1][3]
        end=len(seq)-1 if terminal else len(seq)
        if end>boundary:fields.append({'field':'C','start':boundary,'end':end})
        if terminal:fields.append({'field':'T','start':end,'end':len(seq)})
        return 'clean',[],fields
    def category(self,c):
        for name,codes in [('F',self.fish),('O1',self.oval1),('O2',self.oval2),('O3',self.oval3),('OA',self.amboval|self.ambcode),
                           ('MA',self.ma),('J',self.single|{p[0] for p in self.junctures if len(p)==1}),('T',self.terminal),('TRA',self.tra)]:
            if c in codes:return name
        for pattern,label in self.compound:
            if c in pattern:return 'compound component '+label
        return 'X'
    def recipe(self):
        return {'F':sorted(self.fish),'O1':sorted(self.oval1),'O2':sorted(self.oval2),'O3':sorted(self.oval3),
            'ambiguous_ovals':sorted(self.amboval),'MS_patterns':self.ms,'P_exclusive_patterns':self.junctures,
            'single_juncture':sorted(self.single),'T':sorted(self.terminal),'fish_compound_patterns':self.compound,
            'incompatible_codes':sorted(self.ambcode)}

def summary(scores,observed):
    s=sorted(scores);return {'observed':observed,'draws':len(s),'null_mean':sum(s)/len(s),
        'reference_95_percent':[s[int(.025*len(s))],s[int(.975*len(s))]],
        'add_one_tail':(1+sum(v>=observed for v in s))/(1+len(s))}

def prepare(output=BASE,raw=LOCAL):
    output=Path(output).resolve();raw=Path(raw).resolve()
    if not output.is_relative_to(OWN) or not raw.is_relative_to(RAW):raise SystemExit('Package roots required')
    if (output/'operational-registration.json').exists():raise SystemExit('Preparation exists')
    output.mkdir(parents=True,exist_ok=True);raw.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(OWN/'PROTOCOL.md',output/'PROTOCOL-operational.md')
    for label in ['first','second','agreed_only']:
        mp=read(BASE/f'mapping-{label}.json');op=output/label;rp=raw/label
        op.mkdir();rp.mkdir()
        write(op/'field-code-recipe.json',Grammar(mp).recipe())
        selection=read(WORK/'lexical-selection-v2.json')
        keep={r['sign_id'] for r in mp['rows']}
        removed=[]
        if label=='agreed_only':
            removed=[r for r in selection['readings'] if not set(r['signs'])<=keep]
            selection['readings']=[r for r in selection['readings'] if set(r['signs'])<=keep]
        selection['mapping_sha256']=sha(BASE/f'mapping-{label}.json')
        selection['second_coder_gate']='External reference classes do not change manuscript proposed values; agreed-only filters dropped source targets.'
        write(rp/'lexical-selection-v2.json',selection)
        write(op/'lexical-selection-freeze-v2.json',{'selection_sha256':sha(rp/'lexical-selection-v2.json')})
        write(op/'selection-coverage.json',{'status':'Exploratory','mapping':label,'original_identifiable_occurrences':640,
            'retained_occurrences':len(selection['readings']),'removed_occurrences':len(removed),
            'removed_reading_ids':[r['reading_id'] for r in removed],
            'dropped_target_counts':dict(collections.Counter(s for r in removed for s in set(r['signs'])-keep)),
            'source_attempt_denominator':859,'historical_held_out_entries':0})
    pins={'protocol_sha256':sha(output/'PROTOCOL-operational.md'),
        'script_sha256':sha(Path(__file__)),'lexical_code_sha256':sha(OWN/'pdf_lexical.py'),
        'mapping_freeze_sha256':sha(BASE/'mapping-freeze.json'),'dictionary_sha256':sha(RAW/'acquisition-2026-10-08-v1/mw.txt'),
        'reading_inventory_sha256':sha(WORK/'reading-inventory-v4.json')}
    write(output/'operational-registration.json',pins)
    print('Operational source selections frozen before outcomes')

def field(label,output=BASE,raw=LOCAL):
    output=Path(output).resolve()/label;raw=Path(raw).resolve()/label
    if (output/'field-test.json').exists():raise SystemExit('Field endpoint exists')
    mapping=read(BASE/f'mapping-{label}.json');g=Grammar(mapping)
    rows=[json.loads(l) for l in (ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]
    grouped=collections.defaultdict(list)
    for r in rows:grouped[r['object_family_id']].append(r)
    chosen=[sorted(v,key=lambda r:(-len(r['signs_reading_rtl']),r['record_id']))[0] for v in grouped.values()]
    counts=collections.Counter();reasons=collections.Counter();sites=collections.defaultdict(collections.Counter)
    annotations=[];adj=0;fish=0;compounds=collections.Counter()
    for r in chosen:
        seq=tuple(r['signs_reading_rtl']);status,why,fields,a=g.assess(seq);counts[status]+=1;reasons.update(why);adj+=a
        site=r.get('metadata',{}).get('site') or r.get('site') or 'unknown';sites[site][status]+=1
        u=g.units(seq);fish+=sum(x[0]=='F' for x in u);compounds.update(x[1] for x in u if x[1] in ['fish-comb','fish-two-strokes'])
        annotations.append({'record_id':r['record_id'],'object_family_id':r['object_family_id'],'status':status,'reasons':list(why),'fields':fields})
    rng=random.Random(20261009);nullclean=[];nullfish=[]
    for rep in range(1999):
        clean=a=0
        for r in chosen:
            seq=r['signs_reading_rtl'].copy();rng.shuffle(seq);s,_,_,v=g.assess(tuple(seq));clean+=s=='clean';a+=v
        nullclean.append(clean);nullfish.append(a)
        if rep in [499,999,1499]:print(label,'field shuffle',rep+1,flush=True)
    write(raw/'corpus-field-annotations.json',annotations)
    write(raw/'field-and-fish-shuffles.json',{'canonical_clean':nullclean,'fish_adjacent_units':nullfish})
    write(output/'field-test.json',{'status':'Exploratory','coding':'Two AI coding rounds without specialist review; this mapping is '+label,
        'mapping_sha256':sha(BASE/f'mapping-{label}.json'),'objects':len(chosen),'tokens':sum(len(r['signs_reading_rtl']) for r in chosen),
        'classification':dict(counts),'conflict_or_indeterminate_reasons':dict(reasons),'by_site':{k:dict(v) for k,v in sites.items()},
        'canonical_clean_shuffle':summary(nullclean,counts['clean']),'full_field_boundaries_certified':False})
    write(output/'fish-units.json',{'status':'Exploratory','mapping':label,'fish_units':fish,'compound_counts':dict(compounds),'adjacency':summary(nullfish,adj)})
    lines=[json.loads(l) for l in (ROOT/'data/normalized/mayig_lines.jsonl').read_text(encoding='utf-8').splitlines()]
    clear=[r for r in lines if not r['has_unknown_sign'] and r['max_damage']==0 and r['max_uncertainty']==0]
    decisions=[];mc=collections.Counter();ambiguous=0
    for r in clear:
        seq=[];uncertain=False
        for sign in r['signs_reading_rtl']:
            codes=[well(w) for w in SCHEMA[sign]['wells_graphemes']]
            if len({g.category(c) for c in codes})>1:uncertain=True
            seq.append(codes[0] if codes else sign)
        if uncertain:status='indeterminate';why=['candidate codes cross grammar categories'];ambiguous+=1
        else:status,why,_,_=g.assess(tuple(seq))
        mc[status]+=1;decisions.append({'record_id':r['record_id'],'status':status,'reasons':why})
    write(raw/'mayig-field-annotations.json',decisions)
    write(output/'mayig-fields.json',{'status':'Exploratory','mapping':label,'clear_lines':len(clear),'classification':dict(mc),'candidate_category_ambiguous_lines':ambiguous})
    print(label,'field',dict(counts),'fish',summary(nullfish,adj),'Mayig',dict(mc),flush=True)

def lexical(label,output=BASE,raw=LOCAL):
    import pdf_lexical as module
    output=Path(output).resolve()/label;raw=Path(raw).resolve()/label
    module.OUT=output;module.WORK=raw
    module.score(output,raw,False);module.score(output,raw,True)

def joins(label,output=BASE,raw=LOCAL):
    output=Path(output).resolve()/label;raw=Path(raw).resolve()/label
    if (output/'reading-joins.json').exists():raise SystemExit('Join endpoint exists')
    mp={r['sign_id']:r for r in read(BASE/f'mapping-{label}.json')['rows']}
    def supported(sign):
        r=mp.get(sign,{})
        return bool(r.get('mayig_candidates')) or any(all(SCHEMA[c]['wells_graphemes'] for c in seq) for seq in r.get('component_sequence_candidates',[]))
    rows=read(WORK/'reading-inventory-v4.json');attempts=[r for r in rows if r['is_reading_attempt']]
    local=[]
    for r in attempts:
        seq=r['sign_sequence_visual_ltr'];n=sum(supported(s) for s in seq)
        local.append({'reading_id':r['reading_id'],'glyph_count':len(seq),'reference_supported_glyphs':n,
            'fully_reference_supported':bool(seq) and n==len(seq),'alias_joined':bool(r['joined_record_ids']),
            'joined_objects':r['joined_object_family_ids']})
    write(raw/'reading-join-coverage.json',local)
    write(output/'reading-joins.json',{'status':'Exploratory','mapping':label,'attempt_rows':len(attempts),
        'alias_joined_attempt_rows':sum(r['alias_joined'] for r in local),
        'alias_joined_object_families':len({o for r in local for o in r['joined_objects']}),
        'fully_reference_supported_attempts':sum(r['fully_reference_supported'] for r in local),
        'fully_reference_supported_joined_attempts':sum(r['fully_reference_supported'] and r['alias_joined'] for r in local),
        'partially_reference_supported_attempts':sum(0<r['reference_supported_glyphs']<r['glyph_count'] for r in local),
        'no_reference_supported_attempts':sum(r['reference_supported_glyphs']==0 for r in local),
        'meaning':'Object alias joins are independent of glyph coding; reference-supported figures count candidate/component coverage, not transcription agreement.'})
    # Literal source consistency also depends only on the retained manuscript figures.
    retained={r['reading_id'] for r in read(raw/'lexical-selection-v2.json')['readings']}
    old=read(WORK/'reading-consistency-rows.json');items=[r for r in old if r['reading_id'] in retained]
    write(output/'reading-consistency.json',{'status':'Exploratory','mapping':label,'caption_targets_checked':len(items),
        'exact_literal_consistent':sum(r['exact_fixed_variant_consistent'] for r in items),
        'normalized_literal_consistent':sum(r['normalized_fixed_variant_consistent'] for r in items)})
    print(label,'joins',read(output/'reading-joins.json'),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','field','lexical','joins']);p.add_argument('--mapping',choices=['first','second','agreed_only']);
    p.add_argument('--output-root',default=str(BASE));p.add_argument('--raw-output-root',default=str(LOCAL));a=p.parse_args()
    if not Path(a.output_root).resolve().is_relative_to(OWN) or not Path(a.raw_output_root).resolve().is_relative_to(RAW):raise SystemExit('Package roots required')
    if a.stage=='prepare':prepare(a.output_root,a.raw_output_root)
    elif not a.mapping:raise SystemExit('--mapping required')
    else:globals()[a.stage](a.mapping,a.output_root,a.raw_output_root)
