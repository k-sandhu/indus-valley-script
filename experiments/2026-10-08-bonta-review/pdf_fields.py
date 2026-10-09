"""Exploratory canonical-field compatibility and PDF-resolved fish-unit test."""
from pathlib import Path
import argparse, collections, json, random, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pdf_followup import ROOT, OWN, OUT, WORK, read, write, sha

FISH={'220','231','233','235','240','242'}
O1={'803','805','806'}; O2={'193','797','798'}; OAMB={'832'}
MA={'704','705','706','707'}; J={'001','002','060'}; T={'740','520'}

def tokenize(seq):
    units=[];i=0
    while i<len(seq):
        if i+1<len(seq) and seq[i]=='415' and seq[i+1]=='220':units.append(('F','fish-comb',i,i+2));i+=2
        elif i+1<len(seq) and seq[i]=='032' and seq[i+1]=='220':units.append(('F','fish-two-strokes',i,i+2));i+=2
        elif i+1<len(seq) and seq[i] in MA and seq[i+1]=='033':units.append(('MS','measure-pair',i,i+2));i+=2
        elif seq[i] in FISH:units.append(('F',seq[i],i,i+1));i+=1
        elif seq[i] in O1:units.append(('O','oval-tree',i,i+1));i+=1
        elif seq[i] in O2:units.append(('O','oval-pincers',i,i+1));i+=1
        elif seq[i] in OAMB:units.append(('A','oval-internal-stroke',i,i+1));i+=1
        else:units.append(('X',seq[i],i,i+1));i+=1
    return units

def classify(seq):
    """Necessary restrictions on a canonical anchor-led segmentation.

    Field labels remain conditional. Unknown C signs are permitted, while fish
    whose lexical/M use cannot be decided produce an indeterminate result.
    """
    u=tokenize(seq);reasons=[]
    terminal=[i for i,x in enumerate(seq) if x in T]
    juncture=[i for i,x in enumerate(seq) if x in {'002','060'}]
    m=[x for x in u if x[0] in {'O','F','MS'}]
    anchor=any(x[0] in {'O','MS'} for x in u) or any(a[0]==b[0]=='F' for a,b in zip(u,u[1:]))
    if not terminal and not juncture and not anchor:return 'indeterminate',['no discriminating field anchor'],[]
    if terminal and terminal!=[len(seq)-1]:reasons.append('terminal outside final canonical slot')
    if len(juncture)>1:reasons.append('multiple P-exclusive junctures')
    if anchor and m:
        left,right=m[0][2],m[-1][3]
        if juncture and juncture[-1]>=left:reasons.append('P-exclusive juncture after M anchor')
        span=[x for x in u if x[2]>=left and x[3]<=right]
        if any(x[0]=='X' for x in span):reasons.append('interrupted canonical M span')
        types=[x[0] for x in span if x[0]!='A']
        ranks={'O':0,'F':1,'MS':2,'X':3}
        if any(ranks[a]>ranks[b] for a,b in zip(types,types[1:])):reasons.append('M order differs from O-F-MS')
        f=[x[1] for x in span if x[0]=='F'];o=[x[1] for x in span if x[0]=='O']
        if len(f)>3:reasons.append('more than three F units')
        if len(f)!=len(set(f)):reasons.append('repeated F unit')
        if len(o)>2:reasons.append('more than two O units')
        if len(o)!=len(set(o)):reasons.append('repeated O unit')
        if types.count('MS')>1:reasons.append('multiple MS pairs')
    elif m:return 'indeterminate',['fish lexical/measurement role unresolved'],[]
    if reasons:return 'conflict',sorted(set(reasons)),[]
    if any(x[0]=='A' for x in u):return 'indeterminate',['included/excluded oval forms share Wells 832'],[]
    fields=[]
    boundary=juncture[0]+1 if juncture else 0
    if not boundary and anchor and m:
        singles=[i for i,c in enumerate(seq[:m[0][2]]) if c=='001']
        if len(singles)==1:boundary=singles[0]+1
    if boundary:fields.append({'field':'P','start':0,'end':boundary})
    if anchor and m:
        if m[0][2]>boundary:return 'indeterminate',['prefix before M has no certain P boundary'],[]
        fields.append({'field':'M','start':m[0][2],'end':m[-1][3]});boundary=m[-1][3]
    end=len(seq)-1 if terminal else len(seq)
    if end>boundary:fields.append({'field':'C','start':boundary,'end':end})
    if terminal:fields.append({'field':'T','start':end,'end':len(seq)})
    return 'clean',[],fields

def main(output_root=OUT,raw_output_root=WORK):
    output_root=Path(output_root).resolve();raw_output_root=Path(raw_output_root).resolve()
    if not output_root.is_relative_to(OWN) or not raw_output_root.is_relative_to(ROOT/'data/raw/2026-10-08-bonta-review'):raise SystemExit('Outputs must remain in package trees')
    if (output_root/'field-test.json').exists() or (raw_output_root/'corpus-field-annotations.json').exists():raise SystemExit('Endpoint exists')
    output_root.mkdir(parents=True,exist_ok=True);raw_output_root.mkdir(parents=True,exist_ok=True)
    assert sha(OUT/'mapping-v2-frozen.json')==read(OUT/'mapping-freeze-v2.json')['sha256']
    rows=[json.loads(l) for l in (ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl').read_text(encoding='utf-8').splitlines()]
    grouped=collections.defaultdict(list)
    for r in rows:grouped[r['object_family_id']].append(r)
    chosen=[sorted(v,key=lambda r:(-len(r['signs_reading_rtl']),r['record_id']))[0] for v in grouped.values()]
    assert len(chosen)==2469
    annotations=[];counts=collections.Counter();reasons=collections.Counter();sites=collections.defaultdict(collections.Counter)
    adjacency=0; compoundcounts=collections.Counter(); fishunits=0
    for r in chosen:
        seq=r['signs_reading_rtl'];status,why,fields=classify(seq);counts[status]+=1;reasons.update(why)
        site=r.get('metadata',{}).get('site') or r.get('site') or 'unknown';sites[site][status]+=1
        units=tokenize(seq);adjacency+=sum(a[0]==b[0]=='F' for a,b in zip(units,units[1:]));fishunits+=sum(x[0]=='F' for x in units)
        compoundcounts.update(x[1] for x in units if x[1] in ['fish-comb','fish-two-strokes'])
        annotations.append({'record_id':r['record_id'],'object_family_id':r['object_family_id'],'status':status,'reasons':why,'fields':fields})
    rng=random.Random(20261009);null_clean=[];null_fish=[]
    for rep in range(1999):
        clean=0;fish=0
        for r in chosen:
            seq=r['signs_reading_rtl'].copy();rng.shuffle(seq)
            clean+=classify(seq)[0]=='clean';units=tokenize(seq)
            fish+=sum(a[0]==b[0]=='F' for a,b in zip(units,units[1:]))
        null_clean.append(clean);null_fish.append(fish)
    def summary(scores,observed):
        s=sorted(scores);return {'observed':observed,'draws':len(scores),'null_mean':sum(scores)/len(scores),
          'reference_95_percent':[s[int(.025*len(s))],s[int(.975*len(s))]],
          'add_one_tail':(1+sum(x>=observed for x in scores))/(1+len(scores))}
    write(raw_output_root/'corpus-field-annotations.json',annotations)
    write(raw_output_root/'field-and-fish-shuffles.json',{'canonical_clean':null_clean,'fish_adjacent_units':null_fish})
    rules={'reading_order':'RTL','P':'Optional prefix closed by a juncture. Two short strokes or the bent pair are P-exclusive in the source; one short stroke also has numerical uses.',
      'M':'Canonical O-F-MS, optional subfields; O <=2 and F <=3 nonrepeating units. Two fish compounds are (415,220) and (032,220) in RTL order. MS is (704/705/706/707,033).',
      'C':'Residual lexical cluster, permitted to be absent; its signs and boundaries cannot be identified independently for every text.',
      'T':'Canonical final jar/arrow. Non-final predicates and the many extended Table 19 structures require separate annotation.',
      'indeterminate':'Unanchored/complex strings, lexical fish use, uncertain P boundary, or the conflated oval class 832.',
      'source_pages':[17,20,21,234,235,236,237,238,239,240,249,250,251],
      'scope':'Conditional compatibility with the canonical pattern, not an exhaustive grammar of all 19 extended M templates.'}
    write(output_root/'field-rules.json',{'status':'Exploratory','rules':rules,'mapping_sha256':sha(OUT/'mapping-v2-frozen.json')})
    write(output_root/'field-test.json',{'status':'Exploratory','objects':len(chosen),'classification':dict(counts),
       'conflict_or_indeterminate_reasons':dict(reasons),'by_site':{k:dict(v) for k,v in sites.items()},
       'canonical_clean_shuffle':summary(null_clean,counts['clean']),
       'interpretation':'Conflicts concern this explicit canonical operationalization. Source-allowed extended templates, lexical fish, and ambiguous oval classes prevent treating them as failures of the entire proposal.',
       'full_field_boundaries_certified':False,'mapping_sha256':sha(OUT/'mapping-v2-frozen.json')})
    write(output_root/'fish-units.json',{'status':'Exploratory','objects':len(chosen),'fish_units':fishunits,
      'compound_counts':dict(compoundcounts),'adjacency':summary(null_fish,adjacency),
      'comparison':'Earlier six-code token test observed 135 pairs, shuffle mean 54.5505; new compound-aware units are separately labelled.'})
    print(json.dumps({'classification':dict(counts),'field_null':summary(null_clean,counts['clean']),
                     'fish_null':summary(null_fish,adjacency),'compound_counts':dict(compoundcounts)},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-root',default=str(OUT));p.add_argument('--raw-output-root',default=str(WORK));a=p.parse_args();main(a.output_root,a.raw_output_root)
