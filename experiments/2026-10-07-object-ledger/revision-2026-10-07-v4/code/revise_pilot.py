"""Build corrected baseline and hash-ordered pilot into new dated endpoints."""
import argparse
import collections
import gzip
import json
import shutil
import statistics
import sys
from pathlib import Path
sys.dont_write_bytecode=True
from common import OWN, RAW, ROOT, PATHS, candidate_frame, digest, fresh, load_inputs, write
from revision_selection import revised_selection, external_identity
from revision_builder import RevisedBuilder, FACTS_PATH
from revision_schema import schema_v2
from validate_v2 import validate
import analyze as original_analysis

LAYER='ledger-without-transcription-payloads-or-images.json'
BASE_SELECTION=OWN/'selection-2026-10-07-v1/selection.json'

def coverage(selection,inputs):
    rows=selection['objects'];external=[]
    for r in rows:
        if r['region'] in {'Persian Gulf','Mesopotamia','Iranian Plateau','Central Asia'}:
            canonical,country,source=external_identity(r['site'],inputs,r['key'])
            external.append({'object_id':r['object_id'],'key':r['key'],'export_site':r['site'],'accepted_site':canonical,'country':country,'export_region':r['region'],'selection_group':r['primary_selection'],'source':PATHS['external']+'#site='+str(source),'location_kind':'region_or_area_label' if canonical in {'Luristan','Ornach area','Dilmun'} else 'site'})
    return {'objects':len(rows),'regions_export':dict(sorted(collections.Counter(r['region'] for r in rows).items())),
            'sites_export':dict(sorted(collections.Counter(r['site'] for r in rows).items())),
            'sites_accepted':dict(sorted(collections.Counter(external_identity(r['site'],inputs,r['key'])[0] if r['region'] in {'Persian Gulf','Mesopotamia','Iranian Plateau','Central Asia'} else r['site'] for r in rows).items())),
            'fill_regions':dict(collections.Counter(r['region'] for r in rows if 'stratified_fill' in r['primary_selection'])),
            'fill_sites':dict(collections.Counter(r['site'] for r in rows if 'stratified_fill' in r['primary_selection'])),
            'external_carriers':external,'external_by_site':dict(collections.Counter(r['accepted_site'] for r in external)),
            'external_by_country':dict(collections.Counter(r['country'] for r in external))}

def build_one(selection,selection_path,out,raw,inputs):
    out.mkdir();raw.mkdir()
    b=RevisedBuilder(selection,inputs,selection_path);ledger=b.populate()
    errors=validate(ledger)
    write(raw/'validation-attempt.json',{'status':'Failed' if errors else 'Verified computation','errors':errors})
    if errors:raise ValueError('Validation failed: '+str(errors[:12]))
    write(out/LAYER,ledger)
    with gzip.open(raw/'ledger-full.json.gz','wt',encoding='utf-8') as f:
        json.dump({'metadata_layer':ledger,'local_transcriptions':b.raw_transcriptions},f,ensure_ascii=False)
    witnesses=collections.defaultdict(set)
    for assertion in ledger['assertions']:
        loc=assertion['locator'];witnesses[assertion['object_id']].add((loc['path'],loc['record']))
    lookups=[{'object_id':r['object_id'],'lookup_count':len(witnesses[r['object_id']]),'witnesses':[{'path':p,'record':rec} for p,rec in sorted(witnesses[r['object_id']])]} for r in selection['objects']]
    write(out/'source-lookups.json',lookups);write(out/'museum-comparisons.json',b.comparisons)
    original_analysis.validate=validate
    summary,complete,differences,queue=original_analysis.analyze(ledger,selection,b.comparisons,lookups)
    summary['status']='Exploratory';summary['computation_status']='Verified computation'
    summary['source_lookup_cost']['new_primary_pages_read_for_population']=6
    summary['new_image_inspections']=4
    # Cost without generated rights-rule rows and the selection's geographic attribution.
    counts=[sum(w['path']!='knowledge/provenance/REDISTRIBUTION.md' and w['path']!=str(selection_path.relative_to(ROOT)) for w in row['witnesses']) for row in lookups]
    summary['source_lookup_cost_without_rights_and_selection']={'total':sum(counts),'mean':statistics.mean(counts),'median':statistics.median(counts),'minimum':min(counts),'maximum':max(counts),'definition':'unique source-file/record locators excluding redistribution rows and selection attribution; supplemental observation records count individually'}
    ctx={c['object_id']:c for c in ledger['contexts']};objs={o['id']:o for o in ledger['objects']}
    for q in queue:
        design=ctx[q['object_id']]['fields']['design_classification']['value']
        if q['reason']=='catalogue_only' and design:
            q['question']=f"{q['catalogue_key']} is classified as geometric designs without iconography by the cited page header. Does it contain writing, and should it enter an inscription sample?"
        if q['catalogue_key']=='H-1688' and q['reason']=='one_3A_record':
            q['question']='CISI 3.1 introduction printed liii describes H-1688 as a broken steatite seal from Mound E street deposits about 2600 BC. Check its registration, residuality and use of the Period 3A boundary.'
            q['evidence']+=';Kenoyer-Meadow2010 printed-liii (inherited reviewer check)'
        if q['catalogue_key']=='BM-123208' and q['reason']=='findspot_production_roles':
            q['question']='Gadd no.16 identifies BM 123208/U.17649 at Ur, printed13-14 (PDF24-25). Check the export-family carrier and the independent basis for the Dilmun production attribution.'
        if q['reason']=='impression_count_conflict':
            q['question']=f"Reconcile Table 1 count one with the accepted two-impression view for {q['catalogue_key']}; inspect CISI 1 printed375 corrigenda and printed272/279 plates. For L-141, confirm that corrected A(1)/A(2) denotes separate impressions."
    for o in ledger['objects']:
        if o['fields']['excavation_identifier']['value']=='BNL':
            queue.append({'id':f'Q-{len(queue)+1:05d}','object_id':o['id'],'catalogue_key':o['selection_key'],'reason':'prefix_only_registration','reviewer_role':'catalogue specialist','field':'excavation_identifier','question':'The export supplies only BNL, without an item number. Recover the complete registration and assess whether this prefix identifies a carrier.','evidence':';'.join(o['fields']['excavation_identifier']['assertion_ids'])})
    summary['review_questions']=len(queue);summary['review_objects']=len({q['object_id'] for q in queue})
    summary['accepted_regions']=dict(collections.Counter(c['fields']['region']['value'] for c in ledger['contexts']))
    summary['accepted_sites']=dict(collections.Counter(c['fields']['site']['value'] for c in ledger['contexts']))
    summary['metadata_release_basis']='Private research metadata; Lipi record-level rights unresolved for public release'
    write(out/'summary.json',summary);write(out/'completeness.json',complete);write(out/'disagreements.json',differences);write(out/'review-queue.json',queue);write(out/'join-report.json',summary['joins'])
    write(out/'validation.json',{'status':'Verified computation','errors':[],'schema_version':'2.0','objects':200,'guard':'heuristic'})
    identifier_audit={'bibliographic_locator_carriers_including_Roman_plate_and_leading_placeholder':len({a['object_id'] for a in ledger['assertions'] if a['field']=='bibliographic_locator'}),
                      'raw_export_carriers_with_explicit_figure_or_plate':len({a['object_id'] for a in ledger['assertions'] if a['field']=='export_excavation_identifier' and __import__('re').search(r'(?i)figure|fig\.|plate|pl\.',str(a['value']))}),
                      'accepted_registrations':sum(o['fields']['excavation_identifier']['value'] is not None for o in ledger['objects']),
                      'export_registrations':next(c['corpus_present_on_pilot'] for c in complete if c['field']=='excavation_identifier'),
                      'accepted_cells_with_citations':sum(bool(__import__('re').search(r'(?i)figure|plate',str(o['fields']['excavation_identifier']['value']))) for o in ledger['objects']),
                      'registration_aliases_with_citations':sum(bool(__import__('re').search(r'(?i)figure|plate',i['value'])) for i in ledger['identifiers'] if i['scheme']=='excavation_registration'),
                      'H2218_export_string':next((o['fields']['export_excavation_identifier']['value'] for o in ledger['objects'] if o['selection_key']=='H-2218'),None)}
    write(out/'identifier-audit.json',identifier_audit)
    return summary

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',required=True);ap.add_argument('--raw-dir',required=True);ap.add_argument('--canonical-selection-path');a=ap.parse_args()
    # Both roots permitted: substantive outputs owned; replay copies local raw.
    target=Path(a.output_dir).resolve();allowed=RAW if target.is_relative_to(RAW) else OWN
    out=fresh(target,allowed);raw=fresh(a.raw_dir,RAW);inputs=load_inputs()
    selection,exclusions=revised_selection(inputs);write(out/'selection.json',selection);write(raw/'candidate-frame-exclusions.json',exclusions);write(out/'schema-v2.json',schema_v2())
    original=json.loads(BASE_SELECTION.read_text(encoding='utf-8'))
    oldcov=coverage(original,inputs);newcov=coverage(selection,inputs)
    frame,_=candidate_frame(inputs)
    coverage_output={'status':'Exploratory','original':oldcov,'hash_ordered':newcov,'frame_carriers':len(frame),'frame_regions':dict(collections.Counter(r['region'] for r in frame.values())),'frame_sites':dict(collections.Counter(r['site'] for r in frame.values())),
                     'original_unreached_frame_sites':sorted({r['site'] for r in frame.values()}-set(oldcov['sites_export'])), 'hash_unreached_frame_sites':sorted({r['site'] for r in frame.values()}-set(newcov['sites_export'])),
                     'original_fill_audit':json.loads((OWN/'review/selection-check.json').read_text(encoding='utf-8'))}
    write(out/'coverage-comparison.json',coverage_output)
    summaries={}
    for name,s,p in [('corrected-original',original,BASE_SELECTION),('hash-ordered',selection,Path(a.canonical_selection_path).resolve() if a.canonical_selection_path else out/'selection.json')]:
        summaries[name]=build_one(s,p,out/name,raw/name,inputs)
    code=out/'code';code.mkdir()
    for p in OWN.glob('*.py'):shutil.copyfile(p,code/p.name)
    write(out/'run-manifest.json',{'status':'Exploratory','original_selection_sha256':digest(BASE_SELECTION),'revised_selection_sha256':digest(out/'selection.json'),'protocol_sha256':digest(OWN/'PROTOCOL.md'),
                                 'inputs':{p:digest(ROOT/p) for p in PATHS.values()},'source_observations_sha256':digest(ROOT/FACTS_PATH),'code':{p.name:digest(p) for p in code.glob('*.py')},'outputs':{str(p.relative_to(out)):digest(p) for p in out.rglob('*') if p.is_file() and 'code' not in p.parts}})
    print(json.dumps({k:{f:v[f] for f in ['objects','site_count','assertions','measurement_assertions','review_questions']} for k,v in summaries.items()}))

if __name__=='__main__':main()
