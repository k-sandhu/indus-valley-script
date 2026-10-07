"""Audit the completed corrections and preserved, unevaluated repaired sample."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RAW=ROOT/'data/raw/2026-10-07-helsinki1979-digitization'
FOLLOW=HERE/'follow-up/2026-10-07'


def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=FOLLOW/'verification-v1.json')
    ap.add_argument('--manifest-out',type=Path)
    args=ap.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Use a new owned audit file')
    manifest_path=(args.manifest_out or out.with_name(out.stem+'-paths.json')).resolve()
    if not manifest_path.is_relative_to(HERE) or manifest_path.exists() or manifest_path==out:
        raise ValueError('Use a separate new owned path manifest')
    prior=read(FOLLOW/'analysis-v1/preservation-check.json');checks={}
    checks['all_first_endpoint_files_unchanged']=all(sha(HERE/p)==digest for p,digest in prior['frozen_hashes'].items())
    assets=read(FOLLOW/'analysis-v1/portable-input-manifest.json')['assets']
    checks['portable_input_hashes']=all(sha(ROOT/a['path'])==a['sha256'] for a in assets)
    checks['portable_replay_byte_identical']=(FOLLOW/'portable-recompute-v2/metrics.json').read_bytes()==(HERE/'evaluation/2026-10-07-frozen-v1/metrics.json').read_bytes()
    checks['evaluator_supplement_hash']=sha(HERE/'evaluate.py')==read(FOLLOW/'analysis-v1/freeze-supplement.json')['evaluator_sha256']
    q=read(FOLLOW/'analysis-v1/triage-summary.json')
    checks['triage_is_subset']=q['queued_rows']==9584 and q['queued_rows']+q['not_in_triage']==11369
    orient=read(FOLLOW/'analysis-v1/orientation-overlay.json')
    checks['all_inverted_rows_flagged']=orient['affected_rows']==len(orient['rows'])==1223 and len(orient['pages'])==17
    checks['adjudications_separate']=len(read(FOLLOW/'analysis-v1/adjudication-overlay.json')['changes'])==11
    for version in ('v1','v2'):
        run=HERE/f'repair/2026-10-07-{version}';freeze=read(run/'freeze-manifest.json');pred=read(run/'prediction-freeze.json')
        checks[f'repair_{version}_frozen_code_hashes']=all(sha(HERE/p)==digest for p,digest in freeze['code_hashes'].items())
        checks[f'repair_{version}_prediction_hash']=sha(run/'predictions.json')==pred['prediction_sha256']
        checks[f'repair_{version}_selection_hash']=sha(run/'blind/selection.json')==pred['selection_sha256']
    run=HERE/'repair/2026-10-07-v2';selection=read(run/'blind/selection.json')
    checks['new_eighty_unique_indices']=sorted(r['sample_index'] for r in selection['rows'])==list(range(80))
    checks['new_section_quotas']={s:sum(r['section']==s for r in selection['rows']) for s in selection['denominators']}==dict(number_order=28,end_sorted=26,beginning_sorted=26)
    checks['new_source_crop_hashes']=all(sha(run/'blind'/r['source_crop'])==r['source_crop_sha256'] and sha(run/'blind'/r['exact_crop'])==r['exact_crop_sha256'] for r in selection['rows'])
    checks['twenty_one_count_source_pages']=len(selection['count_pages'])==21 and all((run/f'blind/page-count-source/pdf{p}.png').exists() for p in selection['count_pages'])
    checks['count_detections_frozen']=sha(run/'count-page-detections.json')==read(run/'prediction-freeze.json')['count_detections_sha256']
    checks['no_reference_or_repaired_result_claimed']=not any((run/'blind'/p).exists() for p in ['reference-a.json','reference-b.json','adjudicated-reference.json','adjudicated-counts.json'])
    checks['ledger_followup_quarantine']=read(FOLLOW/'ledger-interface-v2.json')['accepted']==0 and read(FOLLOW/'ledger-interface-v2.json')['quarantined']==63
    tracking=set((HERE/'TRACK-EXCEPTIONS.txt').read_text(encoding='utf-8').splitlines())
    checks['tracking_list_has_required_inputs']=all(a['path'] in tracking for a in assets)
    broken=[]
    for path in HERE.rglob('*.md'):
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if re.match(r'^(https?://|#)',target):continue
            local=(path.parent/target.strip('<>').split('#')[0]).resolve()
            if not local.exists():broken.append(dict(document=str(path.relative_to(HERE)),target=target))
    checks['local_markdown_links_exist']=not broken
    # The original manifest identifies pre-follow-up assets and dependency files.
    baseline=[json.loads(line) for line in (HERE/'file-manifest.jsonl').read_text(encoding='utf-8').splitlines()]
    baseline_paths={str(Path(r['path']).resolve()) for r in baseline if r['scope'] in ('owned','local_raw')}
    records=[];new_bytes=0;changed=[]
    for scope,base in [('owned',HERE),('local_raw',RAW)]:
        for path in sorted(base.rglob('*')):
            if not path.is_file() or path==out:continue
            relative=str(path.relative_to(ROOT)).replace('\\','/');size=path.stat().st_size
            if str(path.resolve()) not in baseline_paths:
                new_bytes+=size;records.append(dict(scope=scope,path=relative,bytes=size,sha256=sha(path)))
            elif path.name in {'README.md','REPORT.md','RETROSPECTIVE.md','IMPORT_INTERFACE.md','PROTOCOL.md','registry-entry.json','sources.json','write_docs.py'}:
                changed.append(dict(path=relative,bytes=size,sha256=sha(path)))
    checks['followup_additional_storage_below500MB']=new_bytes<500_000_000
    manifest_path.write_text(json.dumps(dict(created=records,changed=changed,
      unlisted_self=[str(out.relative_to(ROOT)),str(manifest_path.relative_to(ROOT))]),indent=2),encoding='utf-8')
    result=dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,
       broken_links=broken,changed_path_manifest=str(manifest_path.relative_to(ROOT)),
       storage=dict(new_paths_bytes_relative_to_original_manifest=new_bytes,limit_bytes=500_000_000,
                    current_free_bytes=shutil.disk_usage('C:\\').free,new_dependencies_installed=0,
                    scope='Additional follow-up assets; original retained files/dependencies are the prior endpoint, not newly installed again'),
       unfinished=['two independent readers','source-count reference','adjudication','repaired accuracy/recall/calibration','conditional full run and release rule'],
       stop_trigger='917327872 then 256331776 free bytes while helper active; helper finished before interruption')
    out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
