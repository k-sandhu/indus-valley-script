"""Finalize the full owner-only audit outside the upload folder."""
import argparse
from pathlib import Path
from build_release import HERE,ROOT,read,sha,dump

def finalize(release,records,update_owner=False):
    audit=read(records/'rights-audit.json')
    hosting=read(ROOT/'experiments/2026-10-06-research-program/hf-hosting-manifest.json')
    known={r['path'] for r in audit['files']}
    for row in hosting['files']+hosting['backed_up_files_kept_locally']:
        if row['path'] in known:continue
        licensed=row['set'].startswith('helsinki1979')
        audit['files'].append(dict(path=row['path'],bytes=row['bytes'],sha256=row['sha256'],rights_status='explicit-license' if licensed else 'rights-unverified',decision='exclude',basis='Provisional/quarantined Helsinki transcription or frame.' if licensed else 'Lipi-derived record-level output; no redistribution licence.',hash_basis='Hosting manifest; coordinator reports 1038/1038 remote matches on 8 October 2026; not rerun by Package O.'))
    audit['staged_assets']=[]
    mixed={'chart_reference','benchmark_rows_v1','benchmark_rows_v2','benchmark_readings','benchmark_chart_cards','benchmark_count_pages','benchmark_count_readings','image_assets'}
    for path in sorted(release.rglob('*')):
        if not path.is_file() or path.name=='file-manifest.json':continue
        rel=path.relative_to(release).as_posix();edition=rel.startswith(('images/','benchmark/')) or path.stem in mixed or path.stem.startswith('benchmark_') or rel=='provenance/chart-changes.json'
        legal_text=rel.startswith('LICENSES/')
        audit['staged_assets'].append(dict(path=rel,bytes=path.stat().st_size,sha256=sha(path),rights_status='permission-recorded' if legal_text else ('explicit-license' if edition else 'own-work'),decision='include',basis='Official licence text, reproduced from the issuer; URLs and access record in sources.json.' if legal_text else 'Edition derivative or project-authored compilation/code/documentation.',edition_content_license='CC BY 4.0' if edition else None,project_contribution_license=None if legal_text else ('Unlicense' if rel.startswith('code/') else 'CC0 1.0'),owner_confirmation_pending=False))
    audit['decision_record']='Owner and coordinator follow-up, 8 October 2026; museum fact extracts include 49 and exclude 19.'
    dump(records/'rights-audit.json',audit)
    if update_owner:dump(HERE/'rights-audit.json',audit)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--release',type=Path,required=True);p.add_argument('--records',type=Path,required=True);a=p.parse_args()
    if not a.release.resolve().is_relative_to(HERE) or not a.records.resolve().is_relative_to(HERE):raise ValueError('Owned paths required')
    finalize(a.release,a.records)
