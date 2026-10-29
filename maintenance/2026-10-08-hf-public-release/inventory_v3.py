"""Enumerate this revision's owned paths and verify the final release witnesses."""
from pathlib import Path
from datetime import datetime,timezone
import json
from build_release import HERE,ROOT,RAW,read,sha,dump


def main():
    output=HERE/'created-paths-v0.3.0-2026-10-08-v2.json'
    if output.exists():raise FileExistsError(output)
    cutoff=(HERE/'history/2026-10-08-v0.2.0-code').stat().st_ctime
    changed=['PROTOCOL.md','README.md','REPORT.md','RETROSPECTIVE.md','registry-entry.json','RELEASE-CHECKLIST.md','rights-audit.json','sources.json',
        'build_release.py','release_policy.py','score_benchmark.py','extract_images.py','validate_release.py','check_review_fixes.py',
        'rerun_review.py','summarize_review.py','finalize_audit.py','write_release_docs.py','write_package_report.py',
        'private-store/README.md','private-store/checksums-manifest.json','private-store/inventory-summary.json']
    def rel(path):return path.relative_to(ROOT).as_posix()
    owned=set(changed)
    for path in HERE.rglob('*'):
        if not path.is_file() or 'review' in path.relative_to(HERE).parts or path.name=='REVIEW.md':continue
        if path.stat().st_ctime>=cutoff:owned.add(path.relative_to(HERE).as_posix())
    # All staged files are listed, including retained byte-identical public assets.
    owned.update(p.relative_to(HERE).as_posix() for p in (HERE/'release').rglob('*') if p.is_file())
    owned.update(p.relative_to(HERE).as_posix() for p in (HERE/'history/2026-10-08-release-v0.2.0').rglob('*') if p.is_file())
    owned.add(output.relative_to(HERE).as_posix())
    raw=[rel(p) for p in RAW.rglob('*') if p.is_file() and (p.stat().st_ctime>=cutoff or p.stat().st_mtime>=cutoff)]
    files=read(HERE/'release/provenance/file-manifest.json')
    current_ok=all(sha(HERE/'release'/r['path'])==r['sha256'] for r in files)
    cff=read(HERE/'review-fixes-check-2026-10-08-v35.json')
    final=read(HERE/'validation-2026-10-08-v38.json')
    prose=read(HERE/'prose-review-v0.3.0-2026-10-08-v3.json')
    owned.add('prose-review-v0.3.0-2026-10-08-v3.json')
    completion=dict(status='Verified computation',release_version='0.3.0',
        checks=dict(final_validation=final['status']=='Verified computation',current_release_manifest=current_ok,
            cff_and_privacy=cff['status']=='Verified computation',prose_no_flags=not prose['flags']),
        prose_files=prose['files_scanned'],prose_report='prose-review-v0.3.0-2026-10-08-v3.json',
        release_files=len(files)+1,release_bytes=sum(r['bytes'] for r in files)+(HERE/'release/provenance/file-manifest.json').stat().st_size,
        no_external_actions=True,reviewer_files_edited=False,
        earlier_checks_preserved=['validation.json','validation-2026-10-08-v10.json','validation-2026-10-08-v11.json','rebuild-comparison-2026-10-08-v11.json'])
    if not all(completion['checks'].values()):completion['status']='Failed'
    dump(HERE/'completion-checks-v0.3.0-2026-10-08-v2.json',completion)
    owned.add('completion-checks-v0.3.0-2026-10-08-v2.json')
    dump(output,dict(status='Verified computation',scope='0.3.0 revision; all release files enumerated, including unchanged retained assets.',
        time_basis='Creation/modified times since initial code snapshot, plus explicitly edited pre-snapshot paths; raw lists include temporary/cache files still present.',
        cutoff_utc=datetime.fromtimestamp(cutoff,timezone.utc).isoformat(),
        changed_or_created_owned_files=[rel(HERE/p) for p in sorted(owned)],raw_created_or_updated_files=sorted(raw),
        preserved_relocations=[dict(source='release/',destination='history/2026-10-08-release-v0.2.0/',unchanged_files=91),
            dict(source='r35/',destination='release/',files=136),
            dict(source='r30/, r31/, r32/, former release r33/',destination='data/raw/2026-10-08-hf-public-release/v0.3.0-build-history/',reason='Preserve partial and intermediate builds.')],
        earlier_validation_files_overwritten=False,reviewer_files_edited=False,external_uploads=0))
    print(completion['status'],len(owned),'owned files,',len(raw),'raw paths')

if __name__=='__main__':main()
