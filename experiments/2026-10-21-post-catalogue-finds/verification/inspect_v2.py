"""Show approved identities and closed-vocabulary source evidence only."""
import collections
import json
import re
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
from audit import BASE,OUT,ROOT,csvrows,families,safe,page_index
P=OUT/'input-v2-2026-10-21'
obj=csvrows(P/'objects.csv')
mode=sys.argv[2]
if mode=='joins':
    fam=families()
    print('statuses',collections.Counter((r['local_match'],r['match_basis']) for r in obj))
    for r in obj:
        if r['local_match']=='matched' or r['match_basis']=='catalogue-containment':
            fields=['row_id','site','local_site_label','registration','other_numbers','primary_publication','page','pdf_page','plate_or_figure','object_type','catalogue_status','cisi_in_baseline','local_match','local_family_ids','match_basis','match_note','context_join_family']
            print(json.dumps({k:safe(r[k]) for k in fields}))
            for fid in re.split('[|;]',r['local_family_ids']):
                for f in fam.get(fid,[]):
                    m=f['metadata']
                    print(json.dumps({'family':fid,'site':f['site'],'cisi':f.get('source_cisi'),'registration':safe(m.get('excavation-idno')),'type':m.get('type'),'area':safe(m.get('area-section')),'block':safe(m.get('block-house'))}))
elif mode=='sources':
    wanted={'chanhu-surface2017-held','iar-2013-14','iar-2003-04-asi','iar-1997-98-archive','puratattva-33','puratattva-35-held'}
    for file in ['matching/source-register.csv','acquisition/source-register-1a.csv','acquisition-web/source-candidates-1b.csv']:
        for r in csvrows(BASE/file):
            if r['source_id'] in wanted or 'cisi' in r['source_id'].lower():
                print(file,json.dumps({k:safe(v) for k,v in r.items() if k in {'source_id','title','year','publication_year','local_path','held_path','path','site_codes','site','notes','status'}}))
elif mode=='omission':
    targets={('iar-2013-14',106),('chanhu-surface2017-held',155),('chanhu-surface2017-held',195),('chanhu-surface2017-held',187),('chanhu-surface2017-held',203),('iar-2003-04-asi',62),('iar-1997-98-archive',329),('puratattva-33',188),('puratattva-35-held',85)}
    idx=page_index();records=[]
    # All displayed words belong to identity, publication or qualification fields.
    terms=r'\b(?:inscribed|uninscribed|inscription|inscriptions|script|Indus|Harappan|Harappa|Mohenjo-daro|Chanhu-daro|Dholavira|Surkotada|Surkotda|Desalpar|Desalpur|Farmana|Kanmer|Karanpura|Rakhigarhi|Rojdi|Kalibangan|Khirsara|Bhirrana|Binjor|Banawali|Lothal|seals?|sealings?|tablets?|potsherds?|sherds?|pottery|graffiti|marks?|reported|found|discovered|recovered|excavated|excavation|excavations|exploration|explorations|surface|collection|museum|references|bibliography|contents|figure|fig|plate|pl|caption|uncertain|possibly|probably|letters?|characters?|legend|legends|published|unpublished|illustrated|illustration|drawing|photograph)\b'
    for sid,pg in sorted(targets):
        p=idx[sid,pg][0];s=p.read_text(encoding='utf-8-sig',errors='replace')
        print('PAGE',sid,pg,'bytes',p.stat().st_size)
        for i,l in enumerate(s.splitlines(),1):
            cues=[m.group() for m in re.finditer(terms,l,re.I)]
            if cues:print(i,' | '.join(cues))
        records.append({'source_id':sid,'pdf_page':pg,'path':str(p.relative_to(ROOT)),'access':'Closed identity and qualification vocabulary only; no page image.'})
    (OUT/'omission-revisit-access-v2.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
elif mode=='conflicts':
    a=json.loads((OUT/'coordinator-join-check-v2.json').read_text(encoding='utf-8'));fam=families();rows={r['row_id']:r for r in obj}
    print('conflict categories',collections.Counter(x for r in a['candidate_assessments'] for f in r['conflicts'] for x in f['reasons']))
    wanted={'PCF-DHV-006','PCF-DHV-011','PCF-DHV-017','PCF-GNW-001','PCF-KNM-001','PCF-RGR-003'}
    for r in a['candidate_assessments']:
        if r['row_id'] not in wanted:continue
        row=rows[r['row_id']]
        print(json.dumps({k:safe(row[k]) for k in ['row_id','registration','findspot','period_or_phase','object_type','material']}))
        for f in r['conflicts'][:8]:
            v=fam[f['family']][0];m=v['metadata']
            print(json.dumps({'family':f['family'],'reasons':f['reasons'],'registration':safe(m.get('excavation-idno')),'area':safe(m.get('area-section')),'block':safe(m.get('block-house')),'room':safe(m.get('room-grid')),'period':safe(m.get('period')),'phase':safe(m.get('phase')),'material':safe(m.get('material')),'type':safe(m.get('type'))}))
elif mode=='windows':
    from search_and_content import words,digest
    a=json.loads((OUT/'content-check-v2.json').read_text(encoding='utf-8'));idx=page_index()
    seen=set()
    for h in a['hits']:
        if h['category']!='R16' or h['classification']=='numeric-table coincidence':continue
        key=(h['source_id'],h['pdf_page'],h['source_word_offset'])
        if key in seen:continue
        seen.add(key);s=idx[key[:2]][0].read_text(encoding='utf-8-sig',errors='replace');tokens=[w for w,_ in words(s)][key[2]:key[2]+13]
        matches=[]
        for r in csvrows(BASE/'acquisition/source-register-1a.csv'):
            for field,value in r.items():
                ws=[w for w,_ in words(value)]
                if any(ws[i:i+13]==tokens for i in range(max(0,len(ws)-12))):
                    matches.append({'source_id':r['source_id'],'field':field,'value':safe(value) if field in {'notes','bibliography_basis','bibliography_status','title'} else '[metadata withheld]'})
        print('WINDOW',key,json.dumps(matches))
elif mode=='bhr':
    for r in obj:
        if r['site_code'] in {'BHR','BRR'}:
            print(json.dumps({k:safe(r[k]) for k in ['row_id','site','season','object_type','object_subtype','material','primary_publication','pdf_page','other_publications','row_basis','inscription_status']}))
elif mode=='basic':
    # Reuse the selective basic-data identity parser without running its endpoint.
    from audit import skip_value
    decoder=json.JSONDecoder()
    def proj(s,start=0):
        i=start+1;out={}
        while True:
            while s[i].isspace() or s[i]==',':i+=1
            if s[i]=='}':return out,i+1
            k,i=decoder.raw_decode(s,i)
            while s[i].isspace() or s[i]==':':i+=1
            if k in {'cisi','printed_page','pdf_page','col3_excavation'}:out[k],i=decoder.raw_decode(s,i)
            else:i=skip_value(s,i)
    p=ROOT/'data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi1-basic-data.jsonl'
    with p.open(encoding='utf-8-sig') as f:
        for l in f:
            d,_=proj(l)
            if re.match(r'^(Dlp|Sktd)-',d.get('cisi','')):print(json.dumps({k:safe(v) for k,v in d.items()}))
elif mode=='chanhu':
    from search_and_content import candidate_map
    sid='chanhu-surface2017-held';cm=candidate_map();idx=page_index()
    for pg in [155,187,195,203]:
        s=idx[sid,pg][0].read_text(encoding='utf-8-sig',errors='replace')
        sites=[]
        for r in csvrows(BASE/'selection/sites-seed.csv'):
            for alias in [r['site'],*re.split('[;|]',r.get('aliases',''))]:
                if len(alias)>3 and re.search(r'\b'+re.escape(alias)+r'\b',s,re.I):sites.append(r['site'])
        print(json.dumps({'source_id':sid,'pdf_page':pg,'candidate_site_codes':[k for k,v in cm.items() if (sid,str(pg)) in v],'site_mentions':sorted(set(sites)),'eligible_word_present':bool(re.search(r'\b(?:inscribed|inscription|script|seals?|sealings?|tablets?)\b',s,re.I)),'replacement_character_present':'\ufffd' in s,'mostly_latin':sum(c.isascii() and c.isalpha() for c in s)>sum(c.isalpha() for c in s)*.9}))
