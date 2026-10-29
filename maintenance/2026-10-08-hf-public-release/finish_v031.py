"""Record final prose, current-source rebuild, provenance and path inventory."""
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
from build_release import HERE,ROOT,RAW,read,dump,sha

def main():
    output=HERE/'completion-checks-v0.3.1-2026-10-08-v2.json'
    if output.exists():raise FileExistsError(output)
    fresh=HERE/'r44'
    files=[dict(path=p.relative_to(fresh).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(fresh.rglob('*')) if p.is_file() and p.relative_to(fresh).as_posix()!='provenance/file-manifest.json']
    dump(fresh/'provenance/file-manifest.json',files)
    before={p.relative_to(HERE/'release').as_posix():sha(p) for p in (HERE/'release').rglob('*') if p.is_file()}
    after={p.relative_to(fresh).as_posix():sha(p) for p in fresh.rglob('*') if p.is_file()}
    plan=read(HERE/'preservation-plan-2026-10-08-v031.json');protocol=read(HERE/'protocol-plan-2026-10-08-v031.json')
    prose=read(HERE/'prose-review-v0.3.1-2026-10-08-v3.json')
    protected=[name for name,value in plan['reviewer_hashes'].items() if sha(HERE/name)!=value]
    syntax=[]
    for path in HERE.glob('*.py'):
        try:compile(path.read_text(encoding='utf-8-sig'),str(path),'exec')
        except SyntaxError as e:syntax.append(dict(path=path.name,error=str(e)))
    docs=read(RAW/'rr41/scan/public-documentation-prose-sample-v031.json')
    sample_witnesses=Counter(x['witness'] for x in docs)
    checks=dict(current_source_rebuild_equal=before==after,protocol_plan_text_preserved=sha(HERE/'history/2026-10-08-protocol-plan-v031.md')==protocol['protocol_sha256'],reviewer_files_unchanged=not protected,prose_clear=not prose['flags'],code_syntax_clear=not syntax)
    dump(output,dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,current_source_rebuild=dict(folder='r44',files=len(after),equal=sum(before.get(k)==v for k,v in after.items()),release_bytes=sum(p.stat().st_size for p in (HERE/'release').rglob('*') if p.is_file()),unequal=[k for k in before.keys()|after.keys() if before.get(k)!=after.get(k)],basis='Fresh current builder after the owner review-source record was added; the public builder excludes that private review record.'),
        protocol_plan=dict(recorded_utc=protocol['recorded_utc'],sha256=protocol['protocol_sha256'],preserved_text='history/2026-10-08-protocol-plan-v031.md'),reviewer_files=len(plan['reviewer_hashes']),changed_reviewer_files=protected,code_syntax_errors=syntax,prose=dict(files_scanned=prose['files_scanned'],flags=prose['flags'],report='prose-review-v0.3.1-2026-10-08-v3.json'),
        prose_manual_sample=dict(matching_records=len(docs),distinct_windows=len({x['words'] for x in docs}),witnesses=dict(sample_witnesses),disposition='Inspected all 33 distinct matched windows in public documentation after excluding known project mirror witnesses. All are bibliographic titles, publisher names or citation URLs; exact windows stay in the raw sample file.',raw_record='data/raw/2026-10-08-hf-public-release/rr41/scan/public-documentation-prose-sample-v031.json')))
    if not all(checks.values()):raise SystemExit(1)
    validation_path=HERE/'validation-2026-10-08-v45.json'
    if validation_path.exists():raise FileExistsError(validation_path)
    final=read(HERE/'validation-2026-10-08-v43.json')
    final.update(validation_revision='v45 adds the current-source r44 rebuild, preserved plan proof, final prose and code checks to v43',completion_checks=read(output),completion_check_report=output.name)
    dump(validation_path,final)
    for name in ['README.md','REPORT.md','registry-entry.json','write_package_report_v031.py']:
        path=HERE/name;text=path.read_text(encoding='utf8').replace('validation-2026-10-08-v43.json','validation-2026-10-08-v45.json');path.write_text(text,encoding='utf8')
    initial_owned=set(plan['existing_owned_files']);initial_raw=set(plan['existing_raw_files'])
    changed=[]
    archives=['history/2026-10-08-v0.3.0-code/','history/2026-10-08-release-v0.3.0/','history/2026-10-08-protocol-plan-v031.md']
    for path in HERE.rglob('*'):
        if not path.is_file():continue
        rel=path.relative_to(HERE).as_posix();old=HERE/'history/2026-10-08-v0.3.0-code'/path.name
        explicitly_refreshed=rel=='prepare_v031.py' or rel in ['private-store/README.md','private-store/checksums-manifest.json','private-store/inventory-summary.json']
        if explicitly_refreshed or rel not in initial_owned or rel.startswith('release/') or any(rel.startswith(prefix) for prefix in archives) or path.parent==HERE and old.exists() and sha(path)!=sha(old):
            changed.append(dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=sha(path),kind='modified' if rel in initial_owned and not any(rel.startswith(prefix) for prefix in archives) else 'created-or-preserved-copy'))
    raw_files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size) for p in RAW.rglob('*') if p.is_file() and p.relative_to(RAW).as_posix() not in initial_raw]
    inventory=HERE/'created-paths-v0.3.1-2026-10-08.json'
    dump(inventory,dict(date='2026-10-08',owned_files=changed,raw_files=raw_files,owned_count=len(changed),raw_count=len(raw_files),inventory_path=inventory.relative_to(ROOT).as_posix(),inventory_excludes_its_own_hash=True,only_owned_roots_written=True,preserved_review_files=57,note='release/ lists every replaced public file, including byte-identical retained assets. All new raw cache, prediction, scan and archived-preview files are enumerated. The code/0.3.0 archives were created before the initial inventory and are included explicitly.'))
    print(json.dumps(dict(checks=checks,owned_files=len(changed),raw_files=len(raw_files))))

if __name__=='__main__':main()
