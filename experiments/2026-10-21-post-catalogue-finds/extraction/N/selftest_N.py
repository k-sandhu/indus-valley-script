"""Validate run 2N tables, locators, coverage and restricted output vocabulary."""
import collections
import csv
import hashlib
import json
import re
import runpy
from pathlib import Path
M=runpy.run_path(str(Path(__file__).with_name('extract_N.py')))
OUT=M['OUT']; errors=[]; checks={}
COLS='row_id site_code site site_as_published country baseline_volume baseline_year excavation season registration other_numbers findspot depth_or_layer period_or_phase object_type object_subtype material primary_publication publication_year page pdf_page plate_or_figure photo_published drawing_published transcription_published other_publications row_basis inscription_status catalogue_status excavated_before_baseline possible_duplicate_of extraction_note extracted_by'.split()
def read_csv(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:
        r=csv.DictReader(f); data=list(r)
        if None in r.fieldnames or any(None in x or any(v is None for v in x.values()) for x in data):errors.append(dict(check='CSV completeness',file=name))
        return r.fieldnames,data
header,objects=read_csv('objects-N.csv')
if header!=COLS:errors.append(dict(check='exact object columns'))
_,notes=read_csv('site-notes-N.csv');_,pages=read_csv('pages-read-N.csv');_,merges=read_csv('merge-log-N.csv');_,exposure=read_csv('exposure-log-N.csv')
registered={r['source_id'] for r in M['registers']()}
ids={r['row_id'] for r in objects}
if len(ids)!=len(objects):errors.append(dict(check='unique row IDs'))
allowed=dict(object_type=set('seal sealing tablet tag inscribed-pottery inscribed-tool other uncertain'.split()),row_basis={'individual','enumerated-count'},inscription_status={'stated','uncertain'},catalogue_status={'post-catalogue','possibly-in-cisi3','in-baseline-catalogue'},excavated_before_baseline={'yes','no','unknown'})
for k in ['photo_published','drawing_published','transcription_published']:allowed[k]={'yes','no','unknown'}
page_set={(r['source_id'],r['pdf_page']) for r in pages}
for r in objects:
    rid=r['row_id']
    for k,vals in allowed.items():
        if r[k] not in vals:errors.append(dict(check='controlled value',row=rid,field=k))
    if r['primary_publication'] not in registered:errors.append(dict(check='source registration',row=rid))
    if not r['primary_publication'] or not r['pdf_page'] or not r['pdf_page'].isdigit():errors.append(dict(check='nonempty locator',row=rid));continue
    f=M['path_for'](r['primary_publication'])/f"p{int(r['pdf_page']):04}.txt"
    if not f.is_file() or not f.read_text(encoding='utf-8').strip():errors.append(dict(check='page text exists and nonempty',row=rid))
    if (r['primary_publication'],r['pdf_page']) not in page_set:errors.append(dict(check='primary page review logged',row=rid))
    if r['extracted_by']!=M['AGENT']:errors.append(dict(check='extractor label',row=rid))
    if r['possible_duplicate_of'] and r['possible_duplicate_of'] not in ids:errors.append(dict(check='duplicate link',row=rid))
    for entry in filter(None,r['other_publications'].split('; ')):
        if ':' not in entry or entry.split(':',1)[0] not in registered:errors.append(dict(check='secondary source registration',row=rid))
    if not re.fullmatch(r'XN-[A-Z]{3}-\d{3}',rid):errors.append(dict(check='row ID format',row=rid))
by_site={}
for n in notes:
    rr=[r for r in objects if r['site_code']==n['site_code']]
    counts={ 'rows_individual':sum(r['row_basis']=='individual' for r in rr),'rows_enumerated':sum(r['row_basis']=='enumerated-count' for r in rr),'rows_uncertain_status':sum(r['inscription_status']=='uncertain' for r in rr),'rows_possibly_in_cisi3':sum(r['catalogue_status']=='possibly-in-cisi3' for r in rr)}
    for k,v in counts.items():
        if str(v)!=n[k]:errors.append(dict(check='site count',site=n['site_code'],field=k))
    by_site[n['site_code']]={**counts,'total':len(rr),'stated':sum(r['inscription_status']=='stated' for r in rr),'catalogue_status':dict(collections.Counter(r['catalogue_status'] for r in rr))}
seed_codes={r['site_code'] for r in M['rows'](M['BASE']/'selection/sites-seed.csv')}
for c in ['ATR','LLQ','GNS','IDN']:
    if c in seed_codes:errors.append(dict(check='new site code collision',site=c))
for r in merges:
    if r['kept_row_id'] not in ids or r['merged_source'] not in registered or not r['basis']:errors.append(dict(check='merge record'))
protocol=M['BASE']/'PROTOCOL.md'
expected=(M['BASE']/'PROTOCOL.sha256').read_text(encoding='utf-8').split()[0]
if hashlib.sha256(protocol.read_bytes()).hexdigest()!=expected:errors.append(dict(check='protocol freeze'))
for f in OUT.glob('*.json'):
    try:json.loads(f.read_text(encoding='utf-8'))
    except (ValueError,UnicodeError):errors.append(dict(check='complete JSON',file=f.name))
terms=['uni'+'corn','bu'+'ll','rhino'+'ceros','ele'+'phant','ti'+'ger','buff'+'alo','ze'+'bu','go'+'at','ante'+'lope','mo'+'tif','ani'+'mal','sign'+' sequence','reads'+' as']
bad=re.compile(r'\b(?:'+'|'.join(map(re.escape,terms))+r')\b',re.I)
measure=re.compile(r'\b\d+(?:\.\d+)?\s*(?:mm|cm)\b',re.I)
files=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='selftest-N.json']
wordpat=re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")
wanted=collections.defaultdict(set)
for f in files:
    t=f.read_text(encoding='utf-8')
    if bad.search(t):errors.append(dict(check='restricted vocabulary',file=f.name))
    if measure.search(t):errors.append(dict(check='restricted measurement',file=f.name))
    words=[w.lower() for w in wordpat.findall(t)]
    for i in range(len(words)-12):wanted[tuple(words[i:i+13])].add(f.name)
overlaps=set(); compared=0
for sid,n in sorted(page_set):
    f=M['path_for'](sid)/f'p{int(n):04}.txt'
    if not f.exists():errors.append(dict(check='reviewed page exists',source=sid,pdf_page=n));continue
    words=[w.lower() for w in wordpat.findall(f.read_text(encoding='utf-8'))]
    compared+=1
    for i in range(len(words)-12):
        match=wanted.get(tuple(words[i:i+13]))
        if match:
            for fn in match:overlaps.add((fn,sid,n))
if overlaps:errors.extend(dict(check='source prose overlap over twelve words',file=fn,source=sid,pdf_page=n) for fn,sid,n in sorted(overlaps))
audit=json.loads((OUT/'text-audit-N.json').read_text(encoding='utf-8'))
if not audit['pass_']:errors.append(dict(check='text completeness audit'))
checks.update(exact_columns=True,controlled_values=True,registered_publications=True,primary_locator_files=True,site_count_reconciliation=True,nonempty_locators=True,new_site_codes=True,protocol_hash=True,csv_and_json_complete=True,restricted_vocabulary=True,source_prose_overlap=True)
for e in errors:
    key=e['check']
    if key in checks:checks[key]=False
report=dict(passed=not errors,rows=len(objects),sites=len(notes),row_basis=dict(collections.Counter(r['row_basis'] for r in objects)),inscription_status=dict(collections.Counter(r['inscription_status'] for r in objects)),catalogue_status=dict(collections.Counter(r['catalogue_status'] for r in objects)),possible_duplicates=sum(bool(r['possible_duplicate_of']) for r in objects),by_site=by_site,checks=checks,files_scanned=len(files),source_pages_compared=compared,overlap_method='Case-insensitive sequences of thirteen alphabetic words, including across line breaks; source bodies stay local.',errors=errors)
(OUT/'selftest-N.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['passed','rows','sites','row_basis','inscription_status','catalogue_status','possible_duplicates','files_scanned','source_pages_compared','errors']}))
raise SystemExit(0 if report['passed'] else 1)
