"""Schema/semantic validation and a heuristic short-sequence disclosure guard."""
import argparse
import copy
import csv
import functools
import json
import math
import re
from pathlib import Path
import jsonschema
from common import OWN, ROOT, PATHS, read, write
from revision_schema import schema_v2, OBJECT_EXTRA, CONTEXT_EXTRA
from validate import validate as legacy_validate, SEQUENCE_KEYS

CODE = r'(?:[PW]?\d{3})'
SAFE_NUMERIC_FIELDS = {'export_family_identifier', 'source_text_number', 'excavation_unit', 'excavation_item', 'excavation_identifier', 'export_excavation_identifier', 'museum_accession', 'field_identifier', 'identity_join', 'candidate_identity_join'}

def sequence_errors(value, location='$'):
    """Heuristic, not a guarantee: bibliographic numerals need context."""
    errors=[]
    if isinstance(value,dict):
        for k,v in value.items():
            if k.casefold() in SEQUENCE_KEYS or k.casefold() in {'signs','inscription','reading','readout','marks'}:
                errors.append(location+'.'+k+': possible transcription payload key')
            # Source-qualified family IDs and numeric bibliographic identifiers are metadata.
            if k=='value' and (value.get('field') in SAFE_NUMERIC_FIELDS or 'scheme' in value or any('.fields.'+f+'.' in location+'.' for f in SAFE_NUMERIC_FIELDS)):
                continue
            if k in {'record','page_or_url','url','locator','path','version','source_version','sha256','selection_sha256','protocol_sha256','title','venue','authors'}:
                continue
            errors += sequence_errors(v,location+'.'+k)
    elif isinstance(value,list):
        if value and all((isinstance(v,str) and re.fullmatch(CODE,v)) or (type(v)==int and 100<=v<=999) for v in value):
            errors.append(location+': possible one-or-more-sign code array')
        if value and all(isinstance(v,dict) and re.fullmatch(CODE,str(v.get('id',''))) for v in value):
            errors.append(location+': possible grapheme dictionary array')
        for i,v in enumerate(value):errors += sequence_errors(v,f'{location}[{i}]')
    elif isinstance(value,str):
        if re.fullmatch(r'\+?'+CODE+r'\+?',value) or re.search(r'(?<![A-Za-z0-9])(?:[PW]\d{3})(?![A-Za-z0-9])',value):
            errors.append(location+': possible single-sign code string')
        if re.search(r'(?<![A-Za-z0-9])\+?'+CODE+r'(?:[-, +]+'+CODE+r')+\+?(?![A-Za-z0-9])',value):
            # Printed page pairs are frequent; retain obvious source-coordinate prose.
            if not re.search(r'(?i)\b(?:pp\.?|pages?|printed|PDF|book|author|reprint|volume|Figure|CISI1|L124)',value):
                errors.append(location+': possible short code sequence string')
    return errors

@functools.lru_cache(maxsize=128)
def source_data(path):
    p=ROOT/path
    if p.suffix in {'.json','.jsonl','.csv'}:return read(path)
    return p.read_text(encoding='utf-8-sig') if p.suffix in {'.md','.txt'} else None

def dictionaries(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from dictionaries(v)
    elif isinstance(x,list):
        for v in x:yield from dictionaries(v)

@functools.lru_cache(maxsize=20000)
def locator_exists(path,record):
    p=ROOT/path
    if not p.is_file():return False
    x=source_data(path)
    if x is None:return False
    r=record.split(';',1)[0]
    if isinstance(x,str):
        if r.startswith('heading='):return bool(re.search(r'^#+ '+re.escape(r[8:])+r'\s*$',x,re.M))
        return r in x
    if re.fullmatch(r'description_assertions\[\d+\]',r):
        n=int(re.search(r'\d+',r)[0]);return isinstance(x,dict) and n<len(x.get('description_assertions',[]))
    m=re.fullmatch(r'(?:physical_objects\[|assertions\[)?([\w_-]+)=(.*?)(?:\])?',r)
    if m:
        key,val=m.groups()
        key='object_family_id' if key=='family' else key
        return any(str(d.get(key,''))==val for d in dictionaries(x))
    return any(str(d.get('record_id',''))==r or str(d.get('object_id',''))==r or str(d.get('id',''))==r for d in dictionaries(x))

def measurement_errors(v,label):
    if not isinstance(v,dict) or set(v)!={'dimension','value','unit'}:return [label+': malformed measurement cell/assertion']
    dim,n,u=v['dimension'],v['value'],v['unit'];errors=[]
    if type(n) not in (int,float) or not math.isfinite(n) or n<=0:return [label+': nonpositive or nonfinite measurement']
    if dim=='mass':
        if u not in {'g','kg'}:errors.append(label+': mass requires g or kg')
        elif n*(1000 if u=='kg' else 1)>100000:errors.append(label+': mass exceeds pilot plausibility bound 100 kg')
    else:
        if u not in {'mm','cm'}:errors.append(label+': length requires mm or cm')
        elif n*(10 if u=='cm' else 1)>1000:errors.append(label+': length exceeds pilot plausibility bound 1000 mm')
    return errors

def validate(ledger):
    errors=[str(e.json_path)+': '+e.message for e in jsonschema.Draft202012Validator(schema_v2()).iter_errors(ledger)]
    projection=copy.deepcopy(ledger);projection['schema_version']='1.0'
    for o in projection.get('objects',[]):
        for f in OBJECT_EXTRA:o['fields'].pop(f,None)
    for c in projection.get('contexts',[]):
        for f in CONTEXT_EXTRA:c['fields'].pop(f,None)
    for s in projection.get('sources',[]):s.pop('creator_role',None)
    for a in projection.get('assertions',[]):
        if a['confidence']=='derived':a['confidence']='source-reported'
    # Version 1 checks still apply; the new mass/diameter types are handled below.
    projection['measurements']=[m for m in projection.get('measurements',[]) if m['dimension'] not in {'mass','diameter'}]
    errors += legacy_validate(projection)
    errors += sequence_errors(ledger)
    amap={a['id']:a for a in ledger.get('assertions',[])}
    contexts={c['object_id']:c for c in ledger.get('contexts',[])}
    counts={oid:sum(c['object_id']==oid for c in ledger['contexts']) for oid in {o['id'] for o in ledger['objects']}}
    if any(n!=1 for n in counts.values()):errors.append('Contexts must cover each object exactly once')
    for table in ['measurements','identifiers','relationships']:
        for r in ledger.get(table,[]):
            a=amap.get(r['assertion_id'],{})
            expected={k:r[k] for k in ['dimension','value','unit']} if table=='measurements' else r.get('value') if table=='identifiers' else r.get('external_record')
            if table!='relationships' and a.get('value')!=expected:errors.append(r['id']+': row value/unit differs from assertion')
            if table=='relationships' and r['status']=='confirmed' and a.get('confidence')=='candidate':errors.append(r['id']+': confirmed relationship backed by candidate assertion')
            if table=='measurements':errors+=measurement_errors(expected,r['id'])
    for o in ledger['objects']:
        v=o['fields']['measurement']['value']
        if v is not None:errors+=measurement_errors(v,o['id']+'.measurement')
    periods={p['label']:p for p in read(PATHS['periods'])}
    for a in ledger['assertions']:
        loc=a['locator']
        if not locator_exists(loc['path'],loc['record']):errors.append(a['id']+': locator record absent from source')
        if loc['path'].endswith('source-observations.json'):
            f=next((f for f in source_data(loc['path']) if 'id='+f['id']==loc['record']),None)
            if f and (f['source_id']!=a['source_id'] or not (ROOT/f['primary_path']).is_file()):errors.append(a['id']+': observation source attribution invalid')
        if a['field']=='measurement':errors+=measurement_errors(a['value'],a['id'])
        if a['field']=='calendar_interval':
            v=a['value']
            if isinstance(v,dict) and all(type(n) in (int,float) for n in v.values()):
                if any(n<1000 or n>4000 for n in v.values()):errors.append(a['id']+': date outside pilot plausibility range 4000-1000 BCE')
            if a['source_id']=='harappa2010' or a['method'].startswith('attributed_period_conversion'):
                ctx=contexts.get(a['object_id'],{}).get('fields',{})
                if ctx.get('site',{}).get('value')!='Harappa' or loc['path']!=PATHS['periods'] or not loc['record'].startswith('label='):
                    errors.append(a['id']+': HARP conversion lacks Harappa label-table provenance')
    for oid,c in contexts.items():
        fs=c['fields'];label=fs['period_label']['value'];interval=fs['calendar_interval']['value']
        if fs['site']['value']=='Harappa' and isinstance(label,str) and isinstance(interval,dict):
            p=periods.get(label.replace('late ',''))
            if p and p['bce_oldest'] is not None and all(type(n) in (int,float) for n in interval.values()):
                if interval.get('bce_oldest',0)>p['bce_oldest'] or interval.get('bce_youngest',9999)<p['bce_youngest']:
                    errors.append(oid+': accepted interval exceeds period-label range')
    return sorted(set(errors))

def scan_directory(directory):
    errors=[];scanned=[]
    for p in sorted(Path(directory).rglob('*')):
        if p.suffix.lower() not in {'.json','.jsonl','.csv','.md'}:continue
        text=p.read_text(encoding='utf-8-sig');scanned.append(str(p))
        try:
            if p.suffix=='.json':
                x=json.loads(text)
                # Recognize real schema documents by content, never just by filename.
                if isinstance(x,dict) and '$schema' in x and ('$defs' in x or 'properties' in x):continue
                ee=sequence_errors(x)
            elif p.suffix=='.jsonl':ee=[e for line in text.splitlines() if line.strip() for e in sequence_errors(json.loads(line))]
            elif p.suffix=='.csv':ee=[e for row in csv.DictReader(text.splitlines()) for e in sequence_errors(row)]
            else:ee=sequence_errors(text)
        except (ValueError,TypeError) as e:ee=['scan parse error: '+str(e)]
        errors += [str(p)+': '+e for e in ee]
    return errors,scanned

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ledger',required=True);ap.add_argument('--scan-dir');ap.add_argument('--output');a=ap.parse_args()
    ledger=json.loads(Path(a.ledger).read_text(encoding='utf-8'));errors=validate(ledger);scanned=[]
    if a.scan_dir:
        ee,scanned=scan_directory(a.scan_dir);errors+=ee
    result={'status':'Failed' if errors else 'Verified computation','guard':'heuristic; bibliographic numeral contexts and metadata exclusions documented','errors':errors,'scanned_files':scanned}
    if a.output:
        p=Path(a.output).resolve()
        if not p.is_relative_to(OWN) or p.exists():raise ValueError('Output must be new and owned')
        write(p,result)
    print(json.dumps(result,ensure_ascii=True))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
