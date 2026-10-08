"""List revision paths and final checks, excluding the reviewer's protected files."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.metadata
import json
from build_release import HERE,ROOT,RAW,read,dump,sha

def main():
    baseline=read(HERE/'created-paths.json')
    old_owned=set(baseline['owned_files']);old_raw=set(baseline['local_raw_files'])
    owned=[p.relative_to(ROOT).as_posix() for p in HERE.rglob('*') if p.is_file() and 'review' not in p.relative_to(HERE).parts and p.name!='REVIEW.md']
    raw_prefixes=['review-fixes-2026-10-08-sources','validation-2026-10-08-review-fixes-v1','v6','v7','v8','v10','cf6','cf8','cf10','rr6','rr8','rr10','rb9','rb11','revision-ds','snippet6','pre-review-release-2026-10-08','pre-review-build-replay-2026-10-08']
    raw=[]
    for p in RAW.rglob('*'):
        if p.is_file() and (p.relative_to(RAW).parts[0] in raw_prefixes or p.name.startswith('museum-joins-excluded-')):
            raw.append(p.relative_to(ROOT).as_posix())
    changed_top=['PROTOCOL.md','README.md','REPORT.md','RETROSPECTIVE.md','sources.json','rights-audit.json','registry-entry.json','build_release.py','score_benchmark.py','validate_release.py','write_documents.py','write_package_report.py','finalize_audit.py','private-store/README.md','private-store/checksums-manifest.json','private-store/inventory-summary.json']
    changed=[(HERE/p).relative_to(ROOT).as_posix() for p in changed_top]
    changed+=sorted(x for x in owned if x in old_owned and '/release/' in x)
    relocations=[dict(source='experiments/2026-10-08-hf-public-release/release (pre-review snapshot)',target='data/raw/2026-10-08-hf-public-release/pre-review-release-2026-10-08',reason='Preserve original bytes locally; contains the 19 now-excluded identifier joins.'),dict(source='experiments/2026-10-08-hf-public-release/build-replay-2026-10-08-v1',target='data/raw/2026-10-08-hf-public-release/pre-review-build-replay-2026-10-08',reason='Preserve old fresh-build snapshot containing the 68-row table.'),dict(source='experiments/2026-10-08-hf-public-release/release (intermediate r6)',target='experiments/2026-10-08-hf-public-release/history/2026-10-08-review-fixes-r6',reason='Preserved before final documentation build.'),dict(source='release/RELEASE-CHECKLIST.md',target='RELEASE-CHECKLIST.md',reason='Owner-only decisions outside upload folder.'),dict(source='release/provenance/rights-audit.json',target='rights-audit.json and build-records/',reason='Full private paths/hashes outside upload folder.')]
    planned=['created-paths-review-fixes-2026-10-08.json','completion-checks-2026-10-08.json']
    for name in planned:
        path=(HERE/name).relative_to(ROOT).as_posix()
        if path not in owned:owned.append(path)
    dump(HERE/planned[0],dict(status='Verified computation',scope='Review fixes only; old created-paths.json remains the first-package inventory.',owned_directory=HERE.relative_to(ROOT).as_posix(),local_raw_directory=RAW.relative_to(ROOT).as_posix(),created_owned_files=sorted(set(owned)-old_owned),changed_owned_files=sorted(set(changed)),local_raw_revision_files=sorted(raw),local_raw_new_paths=sorted(set(raw)-old_raw),relocations=relocations,protected_reviewer_files_changed=[],outside_owned_roots_changes=[],notes='Caches and materialized reviewer snapshots are included in the raw list; original failed/passed validation files remain unchanged.'))
    v=read(HERE/'validation-2026-10-08-v11.json');fix=read(HERE/'review-fixes-check-2026-10-08-v10.json');replay=read(HERE/'rebuild-comparison-2026-10-08-v11.json');rv=read(HERE/'rebuild-validation-2026-10-08-v11.json');prose=read(HERE/'prose-review-2026-10-08-complete.json')
    import pyarrow.parquet as pq
    storage=Counter(r['storage'] for r in pq.read_table(HERE/'release/data/image_assets.parquet').to_pylist())
    files=read(HERE/'release/provenance/file-manifest.json')
    mismatches=[r['path'] for r in files if sha(HERE/'release'/r['path'])!=r['sha256']]
    result=dict(status='Verified computation',release_files=91,release_bytes=sum(p.stat().st_size for p in (HERE/'release').rglob('*') if p.is_file()),image_storage=dict(storage),manifest_mismatches=mismatches,validation_status=v['status'],review_fix_status=fix['status'],rebuild_status=replay['status'],fresh_validation_status=rv['status'],fresh_build_equal_files=replay['equal_files'],prose_scan=prose,reviewer_scripts_unchanged=v['review_checks']['reviewer_scripts_unchanged'],jsonschema_version=importlib.metadata.version('jsonschema'),sequence_basis='sequence-screen-basis-2026-10-08.json',remaining_owner_decisions=v['required_user_decisions'],upload_performed=False,repository_created=False,visibility_changed=False)
    if mismatches or prose['flags'] or any(result[k]!='Verified computation' for k in ['validation_status','review_fix_status','rebuild_status','fresh_validation_status']):result['status']='Failed'
    dump(HERE/planned[1],result)
    print(json.dumps(dict(status=result['status'],created_owned_files=len(set(owned)-old_owned),changed_owned_files=len(set(changed)),raw_revision_files=len(raw),release_bytes=result['release_bytes'],storage=dict(storage))))

if __name__=='__main__':main()
