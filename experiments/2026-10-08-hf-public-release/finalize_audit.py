"""Expand the audit to individual exclusions and staged outputs; no external calls."""
from pathlib import Path
import argparse
import shutil
from build_release import HERE,ROOT,read,sha,dump

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--release',type=Path,default=HERE/'release');args=parser.parse_args()
    release=args.release.resolve()
    if not release.is_relative_to(HERE):raise ValueError('Use a Package O build.')
    audit=read(release/'provenance/rights-audit.json')
    manifest=read(ROOT/'experiments/2026-10-06-research-program/hf-hosting-manifest.json')
    known={r['path'] for r in audit['files']}
    for row in manifest['files']+manifest['backed_up_files_kept_locally']:
        if row['path'] in known:continue
        licensed=row['set'].startswith('helsinki1979')
        audit['files'].append(dict(path=row['path'],bytes=row['bytes'],sha256=row['sha256'],
            rights_status='explicit-license' if licensed else 'rights-unverified',decision='exclude',
            basis='CC BY 4.0 source but provisional/quarantined transcription or frame; no release.' if licensed else 'Lipi-derived predictions, fitted model or training register; source licence absent. Existing private backup retained.',
            hash_basis='Preserved hosting manifest; remote backup not queried in Package O.'))
    audit['staged_assets']=[]
    for path in sorted(release.rglob('*')):
        if not path.is_file():continue
        rel=path.relative_to(release).as_posix()
        if rel in ['provenance/rights-audit.json','provenance/file-manifest.json']:continue
        derived=rel.startswith(('images/','benchmark/')) or rel in ['data/chart_reference.parquet','data/benchmark_rows_v1.parquet','data/benchmark_rows_v2.parquet','data/benchmark_readings.parquet','data/benchmark_chart_cards.parquet','data/benchmark_count_pages.parquet','data/benchmark_count_readings.parquet','data/image_assets.parquet']
        audit['staged_assets'].append(dict(path=rel,sha256=sha(path),bytes=path.stat().st_size,
            rights_status='explicit-license' if derived else 'own-work',
            decision='stage-for-review',source_basis='Koskenniemi and Parpola 1979 CC BY 4.0' if derived else 'Project-authored compilation, code, documentation or factual bibliography',
            project_contribution_license='MIT proposed' if rel.startswith('code/') else 'CC BY 4.0 proposed',
            owner_confirmation_pending=True))
    dump(release/'provenance/rights-audit.json',audit)
    if release==HERE/'release':shutil.copyfile(release/'provenance/rights-audit.json',HERE/'rights-audit.json')

if __name__=='__main__':main()
