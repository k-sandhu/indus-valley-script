"""Validate the delivered register independently of assembly. Run with python -I."""
import csv
import datetime as dt
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
RAW=ROOT/'data/raw/2026-10-21-town-orientations-verification/dating'
ORDER='mohenjo-daro harappa kalibangan lothal dholavira surkotada banawali rakhigarhi chanhu-daro kanmer shikarpur juni-kuran gola-dhoro desalpur khirsara kuntasi rojdi kot-diji nausharo sutkagen-dor balakot allahdino lakhanjo-daro ganweriwala farmana bhirrana kunal mitathal karanpura rangpur kotada-bhadli pabumath navinal'.split()
errors=[]
checks=Counter()

def require(ok,message):
    checks['assertions']+=1
    if not ok: errors.append(message)

book=json.loads((OUT/'sources.json').read_text(encoding='utf-8'))
sources={s['source_key']:s for s in book['sources']}
towns={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in (OUT/'evidence').glob('*.json')}
require(set(towns)==set(ORDER),'Town inventory differs from assignment')

def citation(c,where):
    require(isinstance(c,dict),where+': locator must be an object')
    if not isinstance(c,dict): return
    k=c.get('source_key');require(k in sources,where+': unknown source '+str(k))
    if k not in sources:return
    s=sources[k]
    for field in ('authors','year','exact_title','page_table_figure'):
        require(bool(c.get(field)),where+': missing citation '+field)
    for field in ('authors','year','exact_title'):
        require(c.get(field)==s.get(field),where+': bibliography mismatch '+field)
    require(c in s['locators'],where+': locator absent from bibliography registry')
    checks['locators']+=1

def walk(x,where):
    if isinstance(x,list):
        for i,v in enumerate(x):walk(v,where+'/'+str(i))
    elif isinstance(x,dict):
        if 'page_table_figure' in x and 'source_key' in x:citation(x,where)
        if 'sigma_D_years' in x and 'level' in x:
            level=x['level']
            r=x.get('start_boundary_95_range_bce') if level==1 else x.get('start_range_bce')
            expected_sigma=abs(r[0]-r[1])/3.92 if level==1 else (abs(r[0]-r[1])/4 if r else 150) if level==2 else 200
            require(math.isclose(x['sigma_D_years'],expected_sigma),where+': candidate/alternative sigma rule')
        for key,v in x.items():
            if key.endswith('_bce') and v is not None:
                out=x.get(key[:-4]+'_astronomical')
                if isinstance(v,(int,float)):require(out==1-v,where+': calendar conversion '+key)
                elif isinstance(v,list) and all(isinstance(a,(int,float)) for a in v):
                    require(out==[1-a for a in v],where+': range calendar conversion '+key)
            walk(v,where+'/'+key)

for slug,t in towns.items():
    walk(t,slug)
    # No measurements of layout direction are permitted in the assembled evidence.
    text=json.dumps(t,ensure_ascii=False)
    require(re.search(r'\b(?:azimuth|bearing)\s*[:=]|\d+(?:\.\d+)?\s*°',text,re.I) is None,slug+': forbidden directional measurement')
    for p in t['parts']:
        cs=sum(p['candidates_by_level'].values(),[])
        for c in cs:
            level=c['level']
            if level==1:
                r=c['start_boundary_95_range_bce'];require(bool(r),'Missing model start range')
                expected=abs(r[0]-r[1])/3.92
            elif level==2:
                r=c['start_range_bce'];expected=abs(r[0]-r[1])/4 if r else 150
            else: require(level==3,'Unknown level');expected=200
            require(math.isclose(c['sigma_D_years'],expected),slug+': sigma rule')
            require(c['astronomical_year']==1-c['year_bce'],slug+': candidate conversion')
            checks['candidate_values']+=1
        prop=p['proposed_candidate']
        require((prop in cs) if prop else not cs,slug+': proposed value absent from candidates')
        if prop:
            require(prop['level']==min(c['level'] for c in cs),slug+': inferior evidence level selected')
            same=[c for c in cs if c['level']==prop['level']]
            recent=max(sources[c['locator']['source_key']]['year'] for c in same)
            require(sources[prop['locator']['source_key']]['year']==recent,slug+': older same-level candidate selected')
        else:require(bool(p['no_candidate_reason']),slug+': missing absence reason')

with (OUT/'candidates.csv').open(encoding='utf-8',newline='') as f: candidates=list(csv.DictReader(f))
with (OUT/'radiocarbon.csv').open(encoding='utf-8',newline='') as f: radiocarbon=list(csv.DictReader(f))
expected={(s,p['part']):p for s,t in towns.items() for p in t['parts']}
require(len(candidates)==len(expected),'Candidate CSV row count differs from parts')
require(len({(r['slug'],r['part']) for r in candidates})==len(candidates),'Duplicate candidate row')
for r in candidates:
    key=(r['slug'],r['part']);require(key in expected,'Unknown candidate part')
    if key not in expected:continue
    c=expected[key]['proposed_candidate']
    ll=json.loads(r['locator']);ll=[ll] if isinstance(ll,dict) else ll
    require(bool(ll),str(key)+': missing CSV locator')
    for x in ll:citation(x,str(key))
    if c:
        require(r['source_key']==c['locator']['source_key'],str(key)+': CSV source differs')
        for field,k in [('candidate_year_bce','year_bce'),('candidate_astronomical_year','astronomical_year'),('sigma_D_years','sigma_D_years'),('level','level')]:
            require(float(r[field])==c[k],str(key)+': CSV value differs '+field)
    else:require(all(not r[k] for k in ('level','candidate_year_bce','candidate_astronomical_year','sigma_D_years','source_key')),str(key)+': undated row has a numerical candidate')
    for field in ('layout_locator','first_occupation_locator'):
        for x in json.loads(r[field]):citation(x,str(key)+'/'+field)

all_rc=[r for t in towns.values() for r in t['radiocarbon_determinations']]
require(len(all_rc)==len(radiocarbon),'Radiocarbon CSV row count differs')
bycode={(r['slug'],r['lab_code']):r for r in all_rc}
require(len(bycode)==len(all_rc),'Duplicate laboratory-code row')
for r in radiocarbon:
    key=(r['slug'],r['lab_code']);require(key in bycode,'Unknown radiocarbon CSV row')
    if key not in bycode:continue
    c=json.loads(r['locator']);citation(c,str(key))
    require(c==bycode[key]['locator'],str(key)+': radiocarbon locator differs')
    require(r['source_key']==c['source_key'],str(key)+': radiocarbon source mismatch')
    require(float(r['conventional_age_bp'])==bycode[key]['conventional_age_bp'],str(key)+': BP age differs')
    e=json.loads(r['error_bp']);require(e==bycode[key]['error_bp'],str(key)+': error differs')
    require(bool(r['context']) and bool(r['material']) and bool(r['phase_label']),str(key)+': missing context/material/phase statement')

for a in book['acquisitions']:
    p=(ROOT/a['path']).resolve();require(p.is_relative_to(RAW.resolve()),'Downloaded path outside ownership')
    b=p.read_bytes()
    require(len(b)==a['byte_count'],a['path']+': size mismatch')
    require(hashlib.sha256(b).hexdigest()==a['sha256'],a['path']+': hash mismatch')
    for field in ('url','retrieved_utc','rights_notice_observed'):require(bool(a.get(field)),a['path']+': missing '+field)
    checks['acquisition_hashes']+=1
for d in book['acquisition_review']['local_derivatives']:
    require(hashlib.sha256((ROOT/d['path']).read_bytes()).hexdigest()==d['sha256'],d['path']+': derivative hash mismatch')

for s in sources.values():
    if s.get('held_copy'):
        b=(ROOT/s['local_path']).read_bytes()
        require(hashlib.sha256(b).hexdigest()==s['held_copy']['sha256'],s['source_key']+': held source hash changed')

status=json.loads((OUT/'final-status.json').read_text(encoding='utf-8'))
prefixes=('experiments/2026-10-21-town-orientations-verification/dating-v1/',
          'data/raw/2026-10-21-town-orientations-verification/dating/')
require(all(any(line[3:].strip('"').replace('\\','/').startswith(prefix) for prefix in prefixes)
            for line in status['owned_status_lines']),'Owned Git status contains a path outside ownership')
owned_files=[p.relative_to(ROOT).as_posix() for base in (OUT,RAW) for p in base.rglob('*') if p.is_file()]
require(all(any(p.startswith(prefix) for prefix in prefixes) for p in owned_files),'Owned file inventory path escaped ownership')
(OUT/'ownership-audit.json').write_text(json.dumps(dict(
    checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),owned_file_paths=sorted(owned_files),
    scoped_paths_pass=True,other_git_status_rows=status['other_status_line_count'],
    note='Raw sources and review images may be ignored by Git. Other contributors have concurrent changes; those paths were not edited by this run. Scope assertion is based on the owned file inventory and performed write operations, not attribution of all workspace changes.'),indent=2)+'\n',encoding='utf-8')

result=dict(checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),passed=not errors,errors=errors,
    checks=dict(checks),towns=len(towns),candidate_rows=len(candidates),proposed_candidates=sum(bool(r['level']) for r in candidates),
    radiocarbon_determinations=len(radiocarbon),bibliography_sources=len(sources),
    no_candidate_towns=[s for s in ORDER if not any(p['proposed_candidate'] for p in towns[s]['parts'])],
    screened_without_construction_phase=[s for s in ORDER if not towns[s]['parts']],
    limits='Structural and arithmetic verification; not an independent archaeological review, a completeness certificate, or primary page-image verification of every transcription.')
(OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
raise SystemExit(bool(errors))
