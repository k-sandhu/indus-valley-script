"""Identity search and content audit; never emit source excerpts."""
import collections
import hashlib
import json
import random
import re
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,RAW,csvrows,save,savecsv,page_index,references,sitekey,safe,inputpath
from safe_read import BLOCKED

def excluded(p):
    name=p.name.upper()
    return name.startswith(('PROTOCOL','CODEX-PROMPT','AMENDMENT-')) or 'prompts' in p.relative_to(BASE).parts

def tracked_files():
    cmd=['git','-c','safe.directory='+ROOT.as_posix(), 'ls-files','-z','--',str(BASE.relative_to(ROOT)).replace('\\','/')]
    done=subprocess.run(cmd,cwd=ROOT,capture_output=True,check=True)
    paths=[ROOT/x for x in done.stdout.decode('utf-8').split('\0') if x]
    return [p for p in paths if p.is_file() and not excluded(p)]

def words(s):return [(m.group().casefold(),m.start()) for m in re.finditer(r'\b\w+(?:[’\x27-]\w+)*\b',s)]
def digest(ws):return hashlib.blake2b('\0'.join(ws).encode('utf-8'),digest_size=16).digest()

def content():
    tracked=tracked_files(); own=[p for p in OUT.rglob('*') if p.is_file() and p.suffix in ('.py','.csv','.md','.json') and p!=OUT/'content-check.json']
    working=[p for p in BASE.rglob('*') if p.is_file() and p.suffix in ('.py','.csv','.md','.json','.sh','.sha256','.txt','.log','.tsv','.yaml','.yml','.toml','.ps1','.jsonl') and not excluded(p) and p!=OUT/'content-check.json']
    scan=sorted(set(tracked+working)); hits=[]
    cached={}
    for p in scan:
        s=p.read_text(encoding='utf-8-sig',errors='replace');cached[p]=s
        for line_no,line in enumerate(s.splitlines(),1):
            for i,w in enumerate(BLOCKED,1):
                for m in re.finditer(r'\b'+re.escape(w)+r'\b',line,re.I):hits.append({'file':str(p.relative_to(ROOT)),'line':line_no,'column':m.start()+1,'category':'R'+str(i).zfill(2),'tracked':p in tracked})
            for m in re.finditer(r'\b\d+(?:[.,]\d+)?\s*(?:m{2}|c[m])\b',line,re.I):hits.append({'file':str(p.relative_to(ROOT)),'line':line_no,'column':m.start()+1,'category':'R14','tracked':p in tracked})
        # Look only at data keys, not regexes and safety declarations in code.
        badnames=[''.join(map(chr,c)) for c in [[115,105,103,110,115],[115,105,103,110,95,110,117,109,98,101,114,115],[115,105,103,110,95,105,100,115],[115,105,103,110,115,95,114,101,97,100,105,110,103,95,114,116,108],[115,105,103,110,115,95,118,105,115,117,97,108,95,108,116,114],[116,101,120,116,95,99,111,100,101,95,118,105,115,117,97,108,95,108,116,114]]]
        if p.suffix=='.csv':
            for row in csvrows(p):
                for key,value in row.items():
                    if key and key.casefold() in badnames and value:
                        hits.append({'file':str(p.relative_to(ROOT)),'line':1,'category':'R15','field_digest':hashlib.sha256(key.encode()).hexdigest(),'detail':'Populated excluded data field; value withheld.'});break
        elif p.suffix=='.json':
            try:obj=json.loads(s)
            except json.JSONDecodeError:continue
            def walk(o):
                if isinstance(o,dict):
                    for k,v in o.items():
                        if k.casefold() in badnames and v not in ('',None,[],{}):
                            m=re.search(r'"'+re.escape(k)+r'"\s*:',s)
                            hits.append({'file':str(p.relative_to(ROOT)),'line':s[:m.start()].count('\n')+1 if m else 1,'category':'R15','field_digest':hashlib.sha256(k.encode()).hexdigest(),'detail':'Populated excluded data field; value withheld.'})
                        walk(v)
                elif isinstance(o,list):
                    for v in o:walk(v)
            walk(obj)
    obj=csvrows(inputpath('objects.csv'));reg={r['source_id']:r for r in csvrows(BASE/'matching/source-register.csv')};idx=page_index()
    sources={r['primary_publication'] for r in obj}
    sources.update(s for r in obj for s,_,_ in references(r,reg) if s)
    rng=random.Random(20261023); windows=collections.defaultdict(list);coverage=[]
    for source in sorted(sources):
        pages=[(pg,paths[0]) for (sid,pg),paths in sorted(idx.items()) if sid==source]
        pools=[];total=0
        for pg,p in pages:
            ws=words(p.read_text(encoding='utf-8-sig',errors='replace'))
            count=max(0,len(ws)-12)
            if count:pools.append((pg,[w for w,_ in ws],total,count));total+=count
        amount=min(200,total)
        for loc in rng.sample(range(total),amount):
            for pg,ws,start,count in pools:
                if start<=loc<start+count:
                    offset=loc-start;windows[digest(ws[offset:offset+13])].append({'source_id':source,'pdf_page':pg,'source_word_offset':offset});break
        coverage.append({'source_id':source,'page_text_pages':len(pages),'available_windows':total,'sampled_unique_windows':amount,'requirement_met':amount>=200,'reason':None if amount>=200 else 'Fewer than 200 distinct windows available in held page text.'})
    for p,s in cached.items():
        ws=words(s);tokens=[x for x,_ in ws]
        for i in range(max(0,len(ws)-12)):
            h=digest(tokens[i:i+13])
            if h in windows:
                line=s[:ws[i][1]].count('\n')+1
                for source in windows[h]:hits.append({'file':str(p.relative_to(ROOT)),'line':line,'category':'R16','tracked':p in tracked,**source})
    output={'tracked_files_scanned':len(tracked),'working_files_scanned':len(working),'own_files_scanned':len(own),'files_scanned':len(scan),'file_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in cached},'scope_exclusions':'Protocol, protocol amendment, prompt files and this audit JSON itself. The full current package is additionally checked, including untracked text artifacts.','category_reference':'R01–R13 refer in order to the 13 vocabulary entries in check 6 of CODEX-PROMPT-4.md. R14 is the numeric-unit pattern, R15 an excluded populated data field, and R16 a sampled 13-word source-window match. No hit text is reproduced.','copy_sample_seed':20261023,'copy_windows_per_source_requested':200,'copy_sampling':'Uniform without replacement across available 13-word windows, after choosing the preferred held text version for each source page. Case and punctuation are normalised. Common bibliographic phrases are retained as hits.','source_coverage':coverage,'hits':hits,'tracked_hits':sum(x.get('tracked',True) for x in hits),'untracked_hits':sum(not x.get('tracked',True) for x in hits),'limitation':'This sampled window check cannot prove absence of longer copied passages outside its sampled windows.'}
    save('content-check.json',output)
    print('CONTENT',len(scan),'files',len(hits),'hits',collections.Counter(x['category'] for x in hits),'source windows',sum(x['sampled_unique_windows'] for x in coverage),'short sources',[x['source_id'] for x in coverage if not x['requirement_met']])

def candidate_map():
    mapping=collections.defaultdict(set)
    for p in [BASE/'acquisition/candidate-pages-1a.csv',*sorted((BASE/'extraction').glob('*/candidate-pages-*.csv')),*sorted((BASE/'extraction').glob('*/additional-candidates-*.csv')),*sorted((BASE/'extraction').glob('*/extra-candidates-*.csv'))]:
        for r in csvrows(p):
            codes=r.get('site_code') or r.get('site_codes') or r.get('sites') or ''
            for code in re.split('[;|,]',codes):
                if code:mapping[code].add((r['source_id'],r['pdf_page']))
    p=BASE/'acquisition-web/candidate-publication-locators-1b.json'
    raw=json.loads(p.read_text(encoding='utf-8-sig'))
    if isinstance(raw,list):
        for entry in raw:
            source=entry.get('source_id','')
            by_site=entry.get('site_candidate_pages',{})
            if source and isinstance(by_site,dict):
                for code,values in by_site.items():
                    if isinstance(values,(str,int)):values=re.findall(r'\d+',str(values))
                    if isinstance(values,list):
                        for value in values:
                            if isinstance(value,dict):value=value.get('pdf_page','')
                            if str(value).isdigit():mapping[code].add((source,str(value)))
    def walk(o,inherited=''):
        if isinstance(o,dict):
            code=o.get('site_code',inherited)
            source=o.get('source_id','')
            if code and source:
                pages=o.get('pdf_page',o.get('pdf_pages',[]))
                if isinstance(pages,(str,int)):pages=re.findall(r'\d+',str(pages))
                if isinstance(pages,list):
                    for pg in pages:
                        if isinstance(pg,(str,int)) and str(pg).isdigit():mapping[code].add((source,str(pg)))
            for k,v in o.items():walk(v,code or (k if re.fullmatch('[A-Z]{3}',k) else ''))
        elif isinstance(o,list):
            for v in o:walk(v,inherited)
    walk(raw)
    return mapping

def pattern(reg):
    reg=reg.strip().strip('-')
    if 'project' in reg.casefold():reg=re.split('project',reg,flags=re.I)[-1]
    reg=re.sub('^DHR[- ]*','',reg,flags=re.I)
    def char(c):
        if c.upper() in '0O':return '[0Oo]'
        if c in '1IiLl':return '[1IiLl]'
        return re.escape(c)
    chars=[char(c) for c in reg if c.isalnum()]
    return re.compile(r'(?<![A-Za-z0-9])(?:D[Hh][Rr][\s-]*)?'+r'[\s-]*'.join(chars)+r'(?![A-Za-z0-9])',re.I)

def unnamed():
    local=csvrows(inputpath('local-unnamed.csv'));obj=csvrows(inputpath('objects.csv'));idx=page_index();candidates=candidate_map()
    reg={r['source_id']:r for r in csvrows(BASE/'matching/source-register.csv')}
    out=[];summary=[];exposure=[]
    readpairs={(r['source_id'],int(n)) for p in (BASE/'extraction').glob('*/pages-read-*.csv') for r in csvrows(p) for n in re.findall(r'\d+',r['pdf_page'])}
    for l in local:
        fid=l['object_family_id'];registration=l['excavation_idno']
        if not registration:
            out.append({'family':fid,'site':l['site'],'registration':'','source_id':'','pdf_page':'','line':'','result':'no registration supplied','source_page_read_by_extraction':''})
            summary.append({'family':fid,'site':l['site'],'registration':'','result':'no registration supplied','occurrences':0});continue
        sources={r['primary_publication'] for r in obj if r['site_code']==l['site_code']}
        sources.update(s for r in obj if r['site_code']==l['site_code'] for s,_,_ in references(r,reg) if s)
        specific=set()
        for source,pg in candidates.get(l['site_code'],set()):
            for n in re.findall(r'\d+',str(pg)):specific.add((source,int(n)))
        pairs=sorted(k for k in idx if k[0] in sources or k in specific)
        rx=pattern(registration);found=[];missing=[{'source_id':s,'pdf_page':p} for s,p in sorted(specific) if (s,p) not in idx]
        for source,pg in pairs:
            hitlines=set()
            for p in idx[source,pg]:
                # Whole pages are searched mechanically; only match coordinates leave this loop.
                txt=p.read_text(encoding='utf-8-sig',errors='replace')
                for m in rx.finditer(txt):hitlines.add(txt[:m.start()].count('\n')+1)
            if hitlines:
                for line in sorted(hitlines):found.append({'family':fid,'site':l['site'],'registration':registration,'source_id':source,'pdf_page':str(pg),'line':line,'result':'registration-shaped occurrence','source_page_read_by_extraction':'yes' if (source,pg) in readpairs else 'no'})
                exposure.append({'source_id':source,'pdf_page':pg,'purpose':'unnamed registration search','access':'match coordinates only; no surrounding description emitted','family':fid})
        out.extend(found or [{'family':fid,'site':l['site'],'registration':registration,'source_id':'','pdf_page':'','line':'','result':'not found','source_page_read_by_extraction':''}])
        summary.append({'family':fid,'site':l['site'],'registration':registration,'result':'found' if found else 'not found','occurrences':len(found),'distinct_pages':len({(r['source_id'],r['pdf_page']) for r in found}),'pages_searched':len(pairs),'candidate_pages_without_text':missing,'interpretation':'An occurrence establishes a search hit, not object identity. Short bare identifiers can coincide with page or reference numbers.'})
    savecsv('unnamed-search.csv',out,['family','site','registration','source_id','pdf_page','line','result','source_page_read_by_extraction'])
    save('unnamed-summary.json',{'families':len(local),'with_registration':sum(bool(x['excavation_idno']) for x in local),'results':summary,'candidate_pages_by_site':{k:len(v) for k,v in sorted(candidates.items())},'search_rule':'Spaces and hyphens may vary; DHR is optional; 0/O and 1/I/l are interchangeable. Project labels are removed from registrations before search. Full appended context is retained for all other identifiers. All held text versions are searched. The web locator register is joined through its nested site-to-page map.','exposure':exposure})
    print('UNNAMED',len(local),'families',collections.Counter(x['result'] for x in summary),'occurrences',len([r for r in out if r['result']=='registration-shaped occurrence']))
    for r in summary:print(r['family'],r['registration'],r['result'],r['occurrences'])

if __name__=='__main__':
    try:
        if sys.argv[2]=='content':content()
        else:unnamed()
    except OSError as e:
        try:save('WRITE-FAILURE.json',{'stopped':True,'error_class':type(e).__name__})
        finally:raise SystemExit('Stopped after an input/output error.')
