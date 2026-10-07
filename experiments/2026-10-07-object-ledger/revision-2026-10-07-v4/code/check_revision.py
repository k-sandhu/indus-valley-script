"""Reuse all 26 reviewer mutations and test occurrence-qualified imports."""
import argparse
import copy
import json
import sys
from pathlib import Path
sys.dont_write_bytecode=True
from common import OWN, RAW, ROOT, digest, fresh, write
from validate_v2 import validate, scan_directory, sequence_errors
from import_helsinki1979_v2 import import_rows, project_layer, expand_crosswalk, to_package_m, interface_schema
from revise_pilot import LAYER

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-dir',required=True);ap.add_argument('--output-dir',required=True);ap.add_argument('--raw-dir',required=True);a=ap.parse_args()
    run=Path(a.run_dir);out=fresh(a.output_dir,OWN);raw=fresh(a.raw_dir,RAW)
    ledger=json.loads((run/'corrected-original'/LAYER).read_text(encoding='utf-8'))
    reviewer=OWN/'review/negative_tests.py';code=reviewer.read_text(encoding='utf-8').split('full_before, full_out =')[0]
    ns={'__file__':str(reviewer),'__name__':'review_mutations_reused'};exec(compile(code,str(reviewer),'exec'),ns)
    ns['validate']=validate
    before,results=ns['run_mutations'](ledger,'corrected-original')
    write(out/'mutations.json',{'status':'Verified computation','reviewer_script_sha256':digest(reviewer),'baseline_errors':sorted(before),'caught':sum(bool(v.get('caught')) for v in results.values()),'total':len(results),'results':results})
    # Execute the review's original fixture definitions, without its output/deletion code.
    fixture_code=reviewer.read_text(encoding='utf-8').split('fixtures = {',1)[1].split('\nfor name, payload',1)[0]
    fx={'a':'987','b':'988','c':'989'};exec('fixtures = {'+fixture_code,fx);fixtures=fx['fixtures']
    fixture_dir=raw/'sequence-fixtures';fixture_dir.mkdir()
    for name,payload in fixtures.items():write(fixture_dir/name,payload)
    for name,content in [('F11_sequence_in_csv.csv','object,reading\nOL-X,987-988-989\n'),('F12_sequence_in_markdown.md','The reading 987-988-989 appears here.\n'),('F13_sequence_in_jsonl.jsonl',json.dumps({'x':{'sign_sequence':['987','988','989']}})+'\n'),('schema.json',json.dumps({'x':{'sign_sequence':['987','988','989']}})+'\n'),('F15_single_string.json',json.dumps({'reading':'987'})),('F16_single_array.json',json.dumps({'readout':[987]})),('F17_single_prefixed.md','A possible code P987 occurs here.\n')]:
        (fixture_dir/name).write_text(content,encoding='utf-8')
    per_file={p.name:bool(scan_directory(p.parent)[0]) for p in []}
    ee,scanned=scan_directory(fixture_dir)
    per_file={p.name:any(str(p)+':' in e for e in ee) for p in fixture_dir.iterdir()}
    write(out/'sequence-fixtures.json',{'status':'Verified computation','guard':'heuristic','original_review_fixtures':14,'additional_single_sign_fixtures':3,'caught':sum(per_file.values()),'total':len(per_file),'files':per_file,'codes':'invented and absent from source exports; fixtures local-only'})
    # Source hashes show that preservation includes every original endpoint/review file.
    preservation=json.loads((OWN/'preservation-2026-10-07-review-response.json').read_text(encoding='utf-8'))
    changed=[p for p,v in preservation['files'].items() if not (ROOT/p).is_file() or digest(ROOT/p)!=v['sha256']]
    write(out/'preservation.json',{'status':'Failed' if changed else 'Verified computation','checked':len(preservation['files']),'changed':changed})
    mpath=ROOT/'experiments/2026-10-07-helsinki1979-digitization/integration/2026-10-07-v1/ledger-import.jsonl'
    rows=[json.loads(l) for l in mpath.read_text(encoding='utf-8').splitlines() if l]
    accepted,quarantine=import_rows(rows,[],ledger)
    # All test object/surface links are invented interface fixtures, outside archaeology.
    row=copy.deepcopy(next(r for r in rows if isinstance(r['text_number'],str) and any(c.isalpha() for c in r['text_number'])))
    row['synthetic']=True;row['glyph_tokens']=[];row['auxiliary_markers']=[]
    catalog=next(o for o in ledger['objects'] if o['selection_key']=='L-175')
    link={'edition_id':row['edition_id'],'text_number':row['text_number'],'segment_id':row['segment_id'],'concordance_source':'invented interface fixture; no historical object claim','concordance_page':'fixture1',
          'source_access':'opened_primary_concordance','target_identifier':{'scheme':'CISI','value':'L 175'},'surface_id':'S-H79-FIXTURE','surface_review_status':'reviewed_source_surface_alignment',
          'create_surface':True,'source_surface_label':'fixture-face-A','relation':'same_physical_object','status':'confirmed','review_status':'reviewed_object_identity','rights_status':'explicit-license'}
    good,bad=import_rows([row],[link],ledger,True);path=raw/'synthetic-accepted.json';write(path,good)
    projection=project_layer(ledger,good,path,True);write(raw/'synthetic-projection.json',projection)
    # A second segment expands only with explicit occurrence mapping.
    second=copy.deepcopy(row);second['segment_id']=row['segment_id']+'-repeat'
    text_link=copy.deepcopy(link);text_link.pop('segment_id');text_link['occurrence_surfaces']={r['segment_id']:{'surface_id':'S-H79-'+str(i),'create_surface':True,'source_surface_label':'fixture-face-'+str(i),'surface_review_status':'reviewed_source_surface_alignment'} for i,r in enumerate([row,second])}
    expanded=expand_crosswalk([row,second],[text_link]);mapped=expand_crosswalk([row,second],to_package_m(expanded))
    two,twobad=import_rows([row,second],mapped,ledger,True)
    unresolved=copy.deepcopy(text_link);unresolved.pop('occurrence_surfaces');_,unbad=import_rows([row,second],[unresolved],ledger,True)
    _,synthetic_bad=import_rows([row],[link],ledger)
    dup,dupbad=import_rows([row,row],[link],ledger,True)
    mass=copy.deepcopy(ledger);ma=mass['measurements'][0];assertion=next(x for x in mass['assertions'] if x['id']==ma['assertion_id']);ma.update(dimension='mass',value=15,unit='g');assertion['value']={k:ma[k] for k in ['dimension','value','unit']}
    # Update any chosen cell that used the modified measurement.
    for o in mass['objects']:
        if o['fields']['measurement']['value'] is not None and o['fields']['measurement']['assertion_ids'][0]==ma['assertion_id']:o['fields']['measurement']['value']=assertion['value']
    checks={'corrected_baseline_valid':not before,'all26_review_mutations_caught':len(results)==26 and all(v.get('caught') for v in results.values()),'all17_sequence_fixtures_caught':all(per_file.values()),
            'all_original_endpoints_preserved':not changed,'M_empty_crosswalk_zero_accepted':len(accepted)==0 and len(quarantine)==11369,'letter_suffix_and_catalogue_surface_fixture_accepted':len(good)==1 and not bad,
            'projection_has_no_sequence_payload':not sequence_errors(projection),'projection_valid':not validate(projection),'M_crosswalk_round_trip_two_segments':len(two)==2 and not twobad,
            'unreviewed_occurrence_alignment_quarantined':len(unbad)==2,'synthetic_archaeological_import_rejected':len(synthetic_bad)==1,'duplicate_segment_quarantined':len(dup)==1 and len(dupbad)==1,'mass_dimension_15g_valid':not validate(mass)}
    number_counts={'occurrences':len(rows),'null_number':sum(r.get('text_number') is None for r in rows),'letter_suffixed_occurrences':sum(isinstance(r.get('text_number'),str) and any(c.isalpha() for c in r['text_number']) for r in rows)}
    write(out/'helsinki-interface.json',{'status':'Verified computation' if all(checks.values()) else 'Failed','M_payload_sha256':digest(mpath),'number_counts':number_counts,'real_accepted':len(accepted),'real_quarantined':len(quarantine),'fixture_status':'Synthetic; no archaeological joins','checks':checks,'projection_errors':validate(projection),'mass_errors':validate(mass)})
    write(out/'checks.json',{'status':'Verified computation' if all(checks.values()) else 'Failed','passed':sum(checks.values()),'total':len(checks),'checks':checks})
    write(out/'interface-schema-v2.json',interface_schema())
    print(json.dumps({'checks':checks,'mutation_caught':sum(v.get('caught',False) for v in results.values()),'M':number_counts}))
    if not all(checks.values()):raise SystemExit(1)

if __name__=='__main__':main()
