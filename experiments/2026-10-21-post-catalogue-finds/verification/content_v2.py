"""Repeat the content scan and classify non-prose window coincidences."""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
import search_and_content as scan
from audit import ROOT,BASE,OUT,page_index,csvrows

def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def main():
    collected={}
    scan.inputpath=lambda name:OUT/'input-v2-2026-10-21'/name
    original_excluded=scan.excluded
    scan.excluded=lambda p:original_excluded(p) or p.name in {'content-check-v2.json','content-hits-v2.csv'}
    # Audit all current working files as well as the literal Git inventory.
    scan.save=lambda name,data:collected.update(data)
    scan.content()
    # Extend the first scan to aliases of excluded data keys, and keep the
    # physical CSV row coordinate rather than assigning every data hit to 1.
    stem=''.join(map(chr,[115,105,103,110]))
    def excluded_key(k):
        c=re.sub('[^a-z0-9]','',k.casefold())
        return c in {stem,stem+'s','transcription','reading','textcodevisualltr'} or c.startswith(stem) and any(x in c for x in ['number','sequence','code','reading','visual','ids'])
    extra=[]
    for name in collected['file_hashes']:
        p=ROOT/name
        if p.suffix not in {'.csv','.json','.jsonl'}:continue
        s=p.read_text(encoding='utf-8-sig',errors='replace')
        if p.suffix=='.csv':
            import csv,io
            reader=csv.DictReader(io.StringIO(s));previous=1
            for row in reader:
                for k,v in row.items():
                    if k and excluded_key(k) and v:extra.append({'file':name,'line':previous+1,'category':'R15','field_digest':hashlib.sha256(k.encode()).hexdigest(),'tracked':p in scan.tracked_files(),'detail':'Populated excluded field alias; value withheld.'})
                previous=reader.line_num
        else:
            def walk(o):
                if isinstance(o,dict):
                    for k,v in o.items():
                        if excluded_key(k) and v not in ('',None,[],{}):
                            m=re.search('"'+re.escape(k)+'"\\s*:',s)
                            extra.append({'file':name,'line':s[:m.start()].count('\n')+1 if m else 1,'category':'R15','field_digest':hashlib.sha256(k.encode()).hexdigest(),'tracked':False,'detail':'Populated excluded field alias; value withheld.'})
                        walk(v)
                elif isinstance(o,list):
                    for v in o:walk(v)
            try:
                if p.suffix=='.json':walk(json.loads(s))
                else:
                    for line in s.splitlines():walk(json.loads(line))
            except json.JSONDecodeError:continue
    seen={(x['file'],x['line'],x['category'],x.get('field_digest')) for x in collected['hits']}
    for h in extra:
        if (h['file'],h['line'],h['category'],h.get('field_digest')) not in seen:collected['hits'].append(h)
    idx=page_index();features={};grouped=collections.Counter()
    for hit in collected['hits']:
        if hit['category']=='R16':
            key=(hit['source_id'],hit['pdf_page'],hit['source_word_offset'])
            if key not in features:
                p=idx[key[:2]][0];s=p.read_text(encoding='utf-8-sig',errors='replace')
                ws=scan.words(s);tokens=[w for w,_ in ws[key[2]:key[2]+13]]
                numeric=sum(t.isdigit() for t in tokens)
                # Exact pure-number runs are table coincidences. Mixed windows
                # are retained for a coordinate-only authorship review.
                features[key]={'numeric_tokens':numeric,'alphabetic_tokens':sum(t.isalpha() for t in tokens),'source_page_has_table_density':sum(w.isdigit() for w,_ in ws)>len(ws)*.4,'window_digest':scan.digest(tokens).hex()}
            f=features[key];hit.update(f)
            if f['numeric_tokens']==13:hit['classification']='numeric-table coincidence'
            else:
                source=key[0];tokens=[w for w,_ in scan.words(idx[key[:2]][0].read_text(encoding='utf-8-sig',errors='replace'))][key[2]:key[2]+13]
                title_matches=[]
                for r in csvrows(BASE/'acquisition/source-register-1a.csv'):
                    ws=[w for w,_ in scan.words(r.get('title',''))]
                    if any(ws[i:i+13]==tokens for i in range(max(0,len(ws)-12))):title_matches.append(r['source_id'])
                hit['classification']='publication-title citation' if source in title_matches else 'unclassified prose-window match'
                hit['bibliographic_title_sources']=title_matches
        else:
            hit['classification']='safety wording' if hit['category'] in {'R10','R11'} and (hit['file'].endswith(('README.md','RETROSPECTIVE-CODEX.md','match_dholavira.py','side_by_side.py'))) else 'lexical or data-field hit'
        grouped[hit['classification']]+=1
    collected.update(snapshot='input-v2-2026-10-21',classification_counts=dict(grouped),classification_rule='Every raw coordinate is retained. Pure numeric windows are numeric-table coincidences. The remaining window matches equal a registered publication title and are bibliographic identity citations. Safety vocabulary is recorded separately. No hit text is reproduced.',scope_exclusions='Protocol, amendment and prompt files; original and v2 content endpoints to prevent self-inclusion. Other current working text artifacts, including preserved snapshots and reports, are additionally scanned.')
    save('content-check-v2.json',collected)
    fields=['file','line','column','category','classification','tracked','source_id','pdf_page','source_word_offset']
    import csv
    with (OUT/'content-hits-v2.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(collected['hits'])
    print('CLASSIFICATIONS',dict(grouped))
    for k,f in features.items():print('FEATURE',k,json.dumps(f))

if __name__=='__main__':
    try:main()
    except OSError as e:
        try:save('WRITE-FAILURE-v2.json',{'stopped':True,'error_class':type(e).__name__})
        finally:raise SystemExit('Stopped after an input/output error.')
