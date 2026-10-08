"""Preservation, source-packet and quarantined physical-line transport checks."""
import argparse
import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import numpy as np
import jsonschema
import evaluate_crop_v3 as V

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];RUN=HERE/'repair/2026-10-08-v3'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def finite(x):
    if isinstance(x,float):return math.isfinite(x)
    if isinstance(x,dict):return all(finite(v) for v in x.values())
    if isinstance(x,list):return all(finite(v) for v in x)
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--packet-only',action='store_true');args=ap.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Use a new owned verification path')
    checks={};errors=[]
    a=read(HERE/'follow-up/2026-10-07/analysis-v1/preservation-check.json')['frozen_hashes']
    b=read(HERE/'follow-up/2026-10-07/endpoint-record-v1/preservation-check.json')['hashes']
    checks['first_endpoint_preserved']=all(sha(HERE/p)==h for p,h in a.items())
    checks['v2_and_all_227_witnesses_preserved']=len(b)==227 and all(sha(HERE/p)==h for p,h in b.items())
    f=read(RUN/'freeze-manifest.json');pf=read(RUN/'prediction-freeze.json');s=read(RUN/'blind/selection.json');p=read(RUN/'predictions.json')
    checks['all_twelve_frozen_implementation_inputs_preserved']=len(f['code_hashes'])==12 and all(sha(HERE/n)==h for n,h in f['code_hashes'].items())
    checks['freeze_before_predictions']=f['created_utc']<pf['created_utc']
    checks['predictions_and_selection_hashes_match']=sha(RUN/'predictions.json')==pf['prediction_sha256'] and sha(RUN/'blind/selection.json')==pf['selection_sha256']
    checks['count_detections_hash_matches']=sha(RUN/'count-page-detections.json')==pf['count_detections_sha256']
    checks['all_195_packet_witnesses_match']=len(pf['packet_hashes'])==195 and all(sha(RUN/'blind'/n)==h for n,h in pf['packet_hashes'].items())
    checks['eighty_unique_source_targets']=len(s['rows'])==80 and sorted(r['sample_index'] for r in s['rows'])==list(range(80)) and len({(r['pdf_page'],r['pdf_column'],tuple(r['target_glyph_pdf_box'])) for r in s['rows']})==80
    old=read(HERE/'blind/selection.json')['rows']+read(HERE/'repair/2026-10-07-v2/blind/selection.json')['rows']
    excluded=set(s['excluded_pages']);checks['every_old_evaluation_target_page_excluded']=all(r['pdf_page'] in excluded for r in old) and all(r['pdf_page'] not in excluded for r in s['rows'])
    checks['section_quotas_28_26_26']=Counter(r['section'] for r in s['rows'])==dict(number_order=28,end_sorted=26,beginning_sorted=26)
    checks['eligible_frame_572_2004_2004']=s['denominators']==dict(number_order=572,end_sorted=2004,beginning_sorted=2004)
    checks['new_eighteen_random_count_pages']=len(s['random_count_pages'])==18 and not(set(s['random_count_pages']) & set(read(HERE/'repair/2026-10-07-v2/blind/selection.json')['count_pages']))
    checks['three_stress_pages']=s['stress_pages']==[62,129,130] and len(s['count_pages'])==21
    checks['source_only_locator_fields']=all(not any(re.search(r'prediction|ocr|confidence|candidate|inscription_number|classification_code',k) for k in r) for r in s['rows'])
    checks['packet_predictions_finite']=finite(p)
    checks['no_fresh_reference_or_reader_files']=not list((RUN/'blind').rglob('*reference*')) and not list((RUN/'blind').rglob('adjudicat*')) and not list((RUN/'blind').glob('reader-*'))
    d=read(HERE/'repair/2026-10-08-development-record-v1/diagnosis.json');dev=read(HERE/'repair/2026-10-08-development-v3h/development.json')
    checks['all_eighty_old_rows_disclosed_as_development']=d['all_v2_targets_reused']==80 and d['development_only'] and dev['code_unchanged_during_run'] and dev['code_sha256']==f['code_hashes']['crop_v3.py']
    checks['five_named_unit_window_repairs']=all(r['count_agrees'] and r['top5_whole_row'] for r in d['prior_five_segmentation_underline_failures']) and {r['sample_index'] for r in d['prior_five_segmentation_underline_failures']}=={3,25,50,52,58}
    checks['all_twentyone_old_counts_recovered']=d['development_numbered_recall']['matched']==d['development_numbered_recall']['true_rows']==d['development_numbered_recall']['detected_rows']==1847
    cont=read(HERE/'repair/2026-10-08-development-record-v1/continuation-check.json')
    checks['ten_development_continuations_and_parent_links_match']=cont['continuation_recall']['success']==cont['continuation_precision']['success']==cont['preceding_numbered_parent_agreement']['success']==10
    # Synthetic in-memory fixture exercises separate physical/numbered denominators.
    fixture=[dict(line_kind='numbered',margin_pdf_box=[5,9,9,13],glyph_pdf_box=[10,8,30,16],row_anchor_y_2x=24),
             dict(line_kind='continuation',margin_pdf_box=None,glyph_pdf_box=[10,25,30,35],row_anchor_y_2x=60)]
    truth=dict(pdf_page=1,columns=[dict(x_extent_pdf=[0,40],row_count=1,row_centers_pdf=[12],physical_line_count=2,physical_line_centers_pdf=[12,30])])
    nr=V.recall_page(fixture,truth);pr=V.recall_page(fixture,truth,True)
    checks['synthetic_numbered_physical_denominators_separate']=nr['matched']==nr['true']==nr['detected']==1 and pr['matched']==pr['true']==pr['detected']==2
    scripts=['crop_v3.py','develop_crop_v3.py','inspect_crop_v3.py','prepare_crop_v3.py','evaluate_crop_v3.py','record_crop_v3.py','complete_crop_v3_full.py','check_continuation_v3.py','write_crop_v3_docs.py','verify_crop_v3.py']
    for n in scripts:ast.parse((HERE/n).read_text(encoding='utf-8'))
    checks['new_scripts_parse']=True
    full_counts=None
    if not args.packet_only:
        full=read(RUN/'full-summary.json');payload=ROOT/full['path'];schema=read(HERE/'option-b-schema.json');required=set(schema['required']);validator=jsonschema.Draft202012Validator(schema);keys={};units=rows=invalid=0;sections=Counter();pages=Counter();suffix=0;fail=[]
        with payload.open(encoding='utf-8') as source:
            for line in source:
                r=json.loads(line);rows+=1;units+=len(r['units']);pages[r['pdf_page']]+=1;sections[r['section']]+=1
                if not(required<=set(r)) or not finite(r):fail.append((rows,'fields/nonfinite'))
                for issue in validator.iter_errors(r):fail.append((rows,'schema '+issue.message))
                if r['occurrence_key'] in keys:fail.append((rows,'duplicate'))
                keys[r['occurrence_key']]=r
                if not r['quarantined'] or r['released'] or r['review_status']!='unreviewed':fail.append((rows,'quarantine'))
                box=r['glyph_pdf_box']
                if not(0<=box[0]<box[2]<=595 and 0<=box[1]<box[3]<=841):fail.append((rows,'box'))
                if r['pipeline_freeze_sha256']!=full['freeze_sha256']:fail.append((rows,'freeze'))
                suffix+=bool(r['inscription_number'] and re.fullmatch(r'\d+[A-Z]+',r['inscription_number']))
                for u in r['units']:
                    if u['confidence'] is None:
                        invalid+=1
                        if u['alternatives'] or 'nonfinite_recognition_window' not in r['flags']:fail.append((rows,'unresolved'))
                    elif not 0<=u['confidence']<=1 or not 1<=len(u['alternatives'])<=5:fail.append((rows,'unit'))
        for r in keys.values():
            if r['line_kind']=='continuation':
                parent=keys.get(r['continuation_of'])
                if not parent or parent['line_kind']!='numbered' or parent['pdf_page']!=r['pdf_page'] or parent['pdf_column']!=r['pdf_column']:fail.append((r['occurrence_key'],'parent'))
        checks['full_hash_and_size']=sha(payload)==full['sha256'] and payload.stat().st_size==full['bytes']
        checks['full_pages_22_through180']=set(pages)==set(range(22,181)) and full['pages']==159
        checks['full_rows_units_sections_match_summary']=rows==full['rows'] and units==full['units'] and sections==full['sections']
        checks['all_full_transport_records_valid']=not fail
        checks['nonfinite_windows_explicitly_unresolved']=invalid==full['nonfinite_units_unresolved']
        checks['all_full_page_files_hash_match']=all(sha(ROOT/m['path'])==m['sha256'] for m in full['page_results'])
        checks['transport_helper_hash_preserved']=sha(HERE/'complete_crop_v3_full.py')==read(RUN/'full-transport-manifest.json')['code_sha256']
        checks['host_file_names_large_output']=full['path'] in (HERE/'HOST-FILES.txt').read_text() and full['sha256'] in (HERE/'HOST-FILES.txt').read_text()
        full_counts=dict(rows=rows,units=units,pages=len(pages),nonfinite_unresolved_units=invalid,letter_suffixed_number_proposals=suffix,released=0)
        errors+=fail
        # Exact sample/full matching for unchanged finite proposal values.
        mismatch=[]
        for sample in p['rows']:
            expected=keys[sample['occurrence_key']]
            if sample['units']!=expected['units'] or sample['inscription_number']!=expected['inscription_number'] or sample['classification_code']!=expected['classification_code']:mismatch.append(sample['sample_index'])
        checks['eighty_sample_proposals_match_full']=not mismatch
        errors+=['sample/full '+str(i) for i in mismatch]
        broken=[]
        for md in HERE.rglob('*.md'):
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
                if re.match(r'^(https?://|#)',target):continue
                destination=(md.parent/target.strip('<>').split('#')[0]).resolve()
                planned={out,(HERE/'repair/2026-10-08-record-v1/changed-paths.json').resolve()}
                if not destination.exists() and destination not in planned:broken.append((str(md.relative_to(HERE)),target))
        checks['local_document_links_resolve_or_name_this_check_and_inventory']=not broken;errors+=broken
    result=dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,passed=sum(checks.values()),total=len(checks),errors=errors,
        old_preservation_witness_counts=[len(a),len(b)],fresh_reference_created=False,full_counts=full_counts,packet_files=len(pf['packet_hashes']))
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
    if not all(checks.values()):raise SystemExit(1)
if __name__=='__main__':main()
