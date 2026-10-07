"""Independent source-value, identifier, selection and replay comparisons."""
import argparse
import collections
import json
import re
from pathlib import Path
from common import OWN, RAW, ROOT, PATHS, digest, fresh, load_inputs, missing, write, read
from revision_builder import FACTS_PATH
from revise_pilot import LAYER

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-dir',required=True);ap.add_argument('--replay-dir',required=True);ap.add_argument('--output-dir',required=True);a=ap.parse_args()
    run=Path(a.run_dir);replay=Path(a.replay_dir);out=fresh(a.output_dir,OWN);x=load_inputs()
    old=read('experiments/2026-10-07-object-ledger/run-2026-10-07-v4/ledger-public.json')
    citation=lambda v:bool(re.search(r'(?i)figure|fig\.|plate|pl\.',str(v)))
    raw=[a for a in old['assertions'] if a['field']=='excavation_identifier' and a['source_id']=='lipi']
    cells=[o['fields']['excavation_identifier']['value'] for o in old['objects'] if o['fields']['excavation_identifier']['value'] is not None]
    baseline={'original_accepted_excavation_strings':len(cells),'uncontaminated_registration_strings':sum(not citation(v) and not str(v).startswith('-') for v in cells),
              'citation_affected_carriers':len({a['object_id'] for a in raw if citation(a['value'])}),'accepted_cells_with_citations':sum(citation(v) for v in cells),
              'confirmed_export_aliases_with_citations':len({i['value'] for i in old['identifiers'] if i['scheme']=='excavation_registration' and citation(i['value'])}),
              'confirmed_export_alias_rows_with_citations':len([i for i in old['identifiers'] if i['scheme']=='excavation_registration' and citation(i['value'])]),
              'strict_export_uncontaminated_registration_carriers':len({a['object_id'] for a in raw if not citation(a['value']) and not str(a['value']).startswith('-')})}
    family=collections.defaultdict(list)
    for f in x['lipi']:family[f['object_family_id']].append(f)
    full={f:sum(any(not missing(face['metadata'].get(raw)) for face in faces) for faces in family.values()) for f,raw in {'area':'area-section','room_grid':'room-grid','period_label':'time'}.items()}
    endpoints={};audit={}
    for n in ['corrected-original','hash-ordered']:
        p=run/n;summary=json.loads((p/'summary.json').read_text(encoding='utf-8'));complete=json.loads((p/'completeness.json').read_text(encoding='utf-8'));d=json.loads((p/LAYER).read_text(encoding='utf-8'))
        endpoints[n]={'summary':summary,'field_presence':{r['field']:{'corpus':r['corpus_present_on_matched'],'ledger':r['ledger_present_on_matched'],'gain':r['gain_on_matched']} for r in complete},'accepted_site_labels':len(summary['accepted_sites']),
                      'null_reasons':dict(collections.Counter(v['missing_reason'] for t in ['objects','contexts','surfaces','transcriptions'] for r in d[t] for v in r['fields'].values() if v['value'] is None))}
        counts=collections.Counter();mismatches=[]
        keyed={PATHS['lipi']:{f['record_id']:f for f in x['lipi']},PATHS['mayig']:{f['record_id']:f for f in x['mayig']},PATHS['museum']:{f['record_id']:f for f in x['museum']},PATHS['lothal']:{f['object_id']:f for f in x['lothal']},FACTS_PATH:{f['id']:f for f in read(FACTS_PATH)}}
        for assertion in d['assertions']:
            loc=assertion['locator'];rec=loc['record'].split(';')[0];rec=rec.split('=',1)[1] if rec.startswith(('record_id=','object_id=','id=')) else rec
            row=keyed.get(loc['path'],{}).get(rec);field=loc['field'];expected=None;compare=False
            if row and ';' not in field:
                try:
                    value=row
                    for part in field.split('.'):value=value[part]
                    if assertion['field'] in {'export_excavation_identifier'} or assertion['method']=='source_field_extraction' or loc['path']==FACTS_PATH:
                        expected=int(value) if assertion['field']=='impression_count' else value;compare=True
                    elif assertion['field']=='measurement' and loc['path']==PATHS['lipi']:
                        expected={**assertion['value'],'value':float(value)};compare=True
                except (KeyError,TypeError,ValueError):pass
            if compare:
                match=expected==assertion['value'];counts['equal' if match else 'mismatch']+=1
                if not match:mismatches.append({'assertion_id':assertion['id'],'object_id':assertion['object_id'],'field':assertion['field'],'locator':loc})
            else:counts['not_compared']+=1
        audit[n]={'assertions':len(d['assertions']),'counts':dict(counts),'mismatches':mismatches,'scope':'direct scalar source fields, retained raw excavation strings, Lipi numeric dimensions and local source observations; transformations/identity/rights rules not independently compared'}
    result={'status':'Exploratory','original_identifier_restated':baseline,'full_export_families':len(family),'full_export_presence':{f:{'count':v,'denominator':len(family),'percent':round(v/len(family)*100,3)} for f,v in full.items()},'endpoints':endpoints}
    write(out/'comparison.json',result);write(out/'assertion-values.json',{'status':'Verified computation' if all(not r['mismatches'] for r in audit.values()) else 'Failed','endpoints':audit})
    comparisons={}
    for p in run.rglob('*.json'):
        rel=p.relative_to(run)
        if 'code' in rel.parts or p.name=='run-manifest.json':continue
        other=replay/rel;comparisons[str(rel)]={'sha256':digest(p),'replay_sha256':digest(other) if other.exists() else None,'equal':other.exists() and digest(p)==digest(other)}
    write(out/'replay-comparison.json',{'status':'Verified computation' if all(c['equal'] for c in comparisons.values()) else 'Failed','files':comparisons,'equal':sum(c['equal'] for c in comparisons.values()),'total':len(comparisons),'copies_location':str(replay)})
    supplementary=[FACTS_PATH,'experiments/2026-10-02-six-hour/lothal-physical-use/independent-review/source-assertions.json','experiments/2026-10-07-helsinki1979-digitization/integration/2026-10-07-v1/ledger-import.jsonl']
    write(out/'local-inputs.json',{'required_inputs':{p:digest(ROOT/p) for p in PATHS.values()},'supplemental_inputs':{p:digest(ROOT/p) for p in supplementary},'primary_source_inspection_inputs':['research/literature/sources/joshi_parpola_1987_cisi1.pdf','data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/gadd1932.pdf']})
    print(json.dumps({'baseline':baseline,'full_export_presence':result['full_export_presence'],'assertion_counts':{n:r['counts'] for n,r in audit.items()},'replay_equal':sum(c['equal'] for c in comparisons.values()),'replay_total':len(comparisons)}))

if __name__=='__main__':main()
