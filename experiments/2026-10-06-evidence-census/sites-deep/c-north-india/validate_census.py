"""Requested structural, encoding and preservation checks; no network activity."""
import csv, hashlib, json, sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode = True
OUT=Path(__file__).resolve().parent

def main():
    errors=[]
    for p in OUT.iterdir():
        if p.is_file() and p.suffix in ['.json','.csv','.md','.py']:
            try:t=p.read_text(encoding='utf-8')
            except UnicodeDecodeError as e:errors.append(f'{p.name}: {e}');continue
            if '\ufffd' in t or '\u00e2\u20ac\u201c' in t or '\u00e2\u20ac' in t or '\u00c3\u2014' in t:errors.append(p.name+': damaged characters')
            if p.suffix=='.json':
                try:json.loads(t)
                except ValueError as e:errors.append(f'{p.name}: {e}')
    rows=json.loads((OUT/'site-rows.json').read_text(encoding='utf-8'))['rows']
    csv_rows=list(csv.DictReader((OUT/'site-rows.csv').open(encoding='utf-8',newline='')))
    if len(rows)!=25 or len(csv_rows)!=25:errors.append('row count differs from 25')
    qs={q['id']:q for q in json.loads((OUT/'searches.json').read_text(encoding='utf-8'))['searches']}
    ss={s['id']:s for s in json.loads((OUT/'sources.json').read_text(encoding='utf-8'))['sources']}
    def inspect(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if k=='source_id' and v not in ss:errors.append('missing source '+v)
                elif k=='search_ids':
                    errors.extend('missing search '+q for q in v if q not in qs)
                else:inspect(v)
        elif isinstance(o,list):
            for v in o:inspect(v)
    inspect(rows)
    for r,c in zip(rows,csv_rows):
        for k,v in r.items():
            cv=json.loads(c[k]) if isinstance(v,(dict,list)) else c[k]
            if isinstance(v,bool):cv=cv=='True'
            elif isinstance(v,int):cv=int(cv)
            if cv!=v:errors.append(f'JSON/CSV mismatch: {r["canonical_name"]} {k}')
        if len({qs[q]['query'] for q in r['search_ids']})<3:errors.append(r['canonical_name']+': insufficient searches')
        if not ss[r['primary_source_opened']['source_id']]['opened']:errors.append(r['canonical_name']+': no opened source')
        if len(r['counts_by_class'])!=6 or len(r['main_publication_metadata'])!=8:errors.append(r['canonical_name']+': incomplete field structure')
    a=json.loads((OUT/'aggregates.json').read_text(encoding='utf-8'))
    actual_totals={k:sum(r['local_corpus'][k] for r in rows) for k in ['faces','object_families','distinct_cisi_ids']}
    if a['local_totals']!=actual_totals:errors.append('local aggregate totals disagree with rows')
    if a['final_excavation_monograph_count']!=sum(r['final_excavation_monograph_identified'] for r in rows):errors.append('final-report count disagrees with rows')
    if a['post_1987_inscribed_find_count']!=sum(r['post_1987_inscribed_find_documented'] for r in rows):errors.append('later-find count disagrees with rows')
    missing=dict(Counter(k for r in rows for k,v in r['main_publication_metadata'].items() if v['availability']=='no'))
    if a['missing_metadata_fields']!=missing:errors.append('metadata aggregate disagrees with rows')
    if a['cisi1_catalogue_objects']!=sum(r['cisi_coverage'].get('catalogue_objects',0) for r in rows):errors.append('CISI object aggregate disagrees with rows')
    if sum(a['cisi1_class_counts'].values())!=a['cisi1_catalogue_objects']:errors.append('CISI classes do not sum to objects')
    if a['followup_queries']!=sum(not q.get('first_pass',False) for q in qs.values()):errors.append('follow-up query count disagrees with records')
    if a['source_records']!=len(ss):errors.append('source count disagrees with records')
    archive=json.loads((OUT/'first-pass-manifest.json').read_text(encoding='utf-8'))
    for r in archive:
        if hashlib.sha256((OUT/r['path']).read_bytes()).hexdigest()!=r['sha256']:errors.append(r['path']+': archive hash changed')
    result=dict(status='Verified computation' if not errors else 'Failed',sites=len(rows),csv_rows=len(csv_rows),sources=len(ss),search_records=len(qs),archive_files=len(archive),errors=errors,
                limitation='Checks establish record structure, encoding and arithmetic. Archaeological claims need source-page review.')
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2));return int(bool(errors))

if __name__=='__main__':sys.exit(main())
