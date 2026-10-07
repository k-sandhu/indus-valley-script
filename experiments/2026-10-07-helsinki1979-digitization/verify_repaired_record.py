"""Verify preservation, recorded diagnosis and small-file inventory."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RECORD=HERE/'follow-up/2026-10-07/endpoint-record-v1'
RUN=HERE/'repair/2026-10-07-v2'


def read(p):return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=RECORD/'verification-v1.json');ap.add_argument('--manifest-out',type=Path)
    args=ap.parse_args();out=args.out.resolve();manifest=(args.manifest_out or RECORD/'changed-paths-v1.json').resolve()
    if any(not p.is_relative_to(HERE) or p.exists() for p in (out,manifest)) or out==manifest:raise ValueError('Use new owned audit and manifest files')
    checks={}
    prior=read(HERE/'follow-up/2026-10-07/analysis-v1/preservation-check.json')['frozen_hashes']
    new=read(RECORD/'preservation-check.json')['hashes']
    checks['first_frozen_endpoint_unchanged']=all(sha(HERE/p)==h for p,h in prior.items())
    checks['repaired_inputs_and_all_source_witnesses_unchanged']=all(sha(HERE/p)==h for p,h in new.items())
    source=RUN/'evaluation-2026-10-07-adjudicated/metrics.json';replay=RECORD/'evaluator-replay-v1/metrics.json'
    checks['frozen_evaluator_replay_byte_identical']=source.read_bytes()==replay.read_bytes()
    d=read(RECORD/'diagnosis.json');u=read(RECORD/'unit-window-audit.json');w=read(RECORD/'review-workload.json');m=read(source)
    checks['four_failed_criteria']=sum(not v for v in m['negative_result_criteria'].values())==4
    checks['zero_occurrences_released']=d['quarantine']==dict(all_original_occurrences=11369,released_occurrences=0,global_rule_passes=False)
    checks['top5_partition_covers_exact_failed_rows']=d['incompatible_whole_row_partitions']['strict_top5']['counts']==dict(crop=34,unit_count=3,unit_candidates_count_consistent_proxy=3)
    checks['top1_partition_covers_exact_failed_rows']=d['incompatible_whole_row_partitions']['strict_top1']['counts']==dict(crop=35,unit_count=3,unit_candidates_count_consistent_proxy=22)
    checks['unit_inspection_covers_all_proxy_top5_misses']=len(u['units'])==5 and {r['sample_index'] for r in u['units']}=={25,58,72}
    checks['source_inspection_hashes_match']=all(sha(HERE/r['exact_source'])==r['source_sha256'] for r in u['units']) and all(sha(HERE/r['source'])==r['source_sha256'] for r in u['count_failure_rows'])
    checks['refined_top5_partition_sums_to40']=sum(u['refined_top5_incompatible_rows'][k] for k in ['crop','unit_count_segmentation','unit_underline_window_association','graphic_proposal_classification'])==40
    checks['all_row_fields_agree']=sum(d['readers']['row_field_agreement'].values())==320
    checks['strict_unit_agreement333of352']=d['readers']['strict_unit_set_agreement']==333 and d['readers']['strict_units_total']==352
    checks['fifteen_disagreement_rows_nineteen_units']=len(d['readers']['strict_disagreement_rows'])==15 and len(d['readers']['strict_disagreement_units'])==19
    checks['count_misses_only66and112']=[(p['pdf_page'],p['missing']) for p in d['count_page_failures']]==[(66,5),(112,39)]
    checks['readings_workload22738']=w['minimum_row_readings']==22738
    checks['reader_elapsed16037_seconds']=w['reader_summed_elapsed_seconds']==16037 and w['row_reader_summed_elapsed_seconds']==13810 and w['count_reader_summed_elapsed_seconds']==2227
    checks['unobserved_costs_are_null']=all(w[k] is None for k in ['adjudicator_time_seconds','billed_usd','billed_tokens'])
    entry=read(HERE/'registry-entry.json');checks['registry_records_failed_endpoint']=entry['status']=='Failed' and '1242/1286' in entry['outcome']
    checks['protocol_records_completed_evaluation']='recording the coordinator' in (HERE/'PROTOCOL.md').read_text(encoding='utf-8')
    broken=[]
    for p in HERE.rglob('*.md'):
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if re.match(r'^(https?://|#)',target):continue
            if not (p.parent/target.strip('<>').split('#')[0]).resolve().exists():broken.append(dict(document=str(p.relative_to(HERE)),target=target))
    checks['local_markdown_links_exist']=not broken
    scripts=['record_repaired_endpoint.py','audit_repaired_unit_windows.py','write_repaired_endpoint_docs.py','verify_repaired_record.py']
    for name in scripts:ast.parse((HERE/name).read_text(encoding='utf-8'))
    checks['new_scripts_parse']=True
    prose=read(RECORD/'prose-review-v2.json')
    checks['prose_scan_zero_flags']=not prose['flags']
    checks['prose_scan_matches_current_documents']=all(sha(HERE/p)==h for p,h in prose['markdown_sha256'].items())
    changed=['PROTOCOL.md','README.md','REPORT.md','RETROSPECTIVE.md','IMPORT_INTERFACE.md','sources.json','registry-entry.json','write_followup_docs.py','verify_followup.py']
    created=[HERE/p for p in scripts]+[p for p in RECORD.rglob('*') if p.is_file() and p not in (out,manifest)]
    paths=lambda ps:[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(ps)]
    records=dict(created=paths(created),changed=paths([HERE/p for p in changed]),
        listed_self=[str(out.relative_to(ROOT)).replace('\\','/'),str(manifest.relative_to(ROOT)).replace('\\','/')],
        coordinator_supplied_inputs_are_preserved_and_not_counted_as_created=True,raw_paths_written=[])
    new_bytes=sum(p.stat().st_size for p in created)
    checks['new_record_storage_below5MB']=new_bytes<5_000_000
    manifest.write_text(json.dumps(records,indent=2),encoding='utf-8')
    result=dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,broken_links=broken,
        preserved_current_source_files=len(new),first_preserved_files=len(prior),repaired_metric_sha256=sha(source),
        new_created_bytes_excluding_audit_and_manifest=new_bytes,current_free_bytes=shutil.disk_usage('C:\\').free,
        changed_path_manifest=str(manifest.relative_to(HERE)).replace('\\','/'),
        limitations=['Diagnosis is post-outcome; equal counts are a segmentation proxy outside inspected residual cases.',
            'Projected human times are assumptions; billed dollars and adjudicator time are unavailable.',
            'No automatic or reviewed release rule has passed; all occurrences remain quarantined.'])
    out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
