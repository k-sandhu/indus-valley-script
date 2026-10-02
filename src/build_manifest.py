"""Record reproducibility metadata without copying restricted source corpora."""
from __future__ import annotations
import hashlib,json,platform,sys,importlib.metadata
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    packages={}
    for name in ['numpy','scipy','pandas','scikit-learn','Pillow','PyMuPDF','opencv-python','reportlab','pypdf','requests']:
        try:packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:packages[name]=None
    vendor=ROOT/'.vendor'
    vendor_packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=[str(vendor)])}
    environment={'generated_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,
                 'python_executable':sys.executable,'platform':platform.platform(),
                 'packages':packages,'local_vendor_packages':vendor_packages,
                 'note':'Plotting appends .vendor to the search path, preserving the global numerical packages.'}
    OUT.mkdir(exist_ok=True)
    (OUT/'environment.json').write_text(json.dumps(environment,indent=2),encoding='utf-8')
    paths=set()
    for folder in ['src','research','results']:
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix.lower() in ['.py','.md','.json','.jsonl','.csv'] and '__pycache__' not in p.parts)
    for name in ['README.md','PLAN.md','output/report_build.json','output/environment.json','output/pdf/indus_script_research_report.pdf']:
        p=ROOT/name
        if p.exists():paths.add(p)
    paths.update((ROOT/'output/figures').glob('*.png'))
    for folder in ['output/chart_atlas','output/playwright']:
        paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file())
    paths.update((ROOT/'output').glob('verification*'))
    for name in ['research_summary.json','report_visual_qa.json']:
        p=OUT/name
        if p.exists():paths.add(p)
    paths.update((ROOT/'data/normalized').glob('*'))
    entries=[]
    for p in sorted(paths):
        if not p.is_file():continue
        stat=p.stat();entries.append({'path':p.relative_to(ROOT).as_posix(),'bytes':stat.st_size,'sha256':sha(p),
             'modified_utc':datetime.fromtimestamp(stat.st_mtime,timezone.utc).isoformat()})
    manifest={'generated_utc':datetime.now(timezone.utc).isoformat(),'research_started_utc':'2026-10-01T23:07:54+00:00',
        'minimum_four_hours_ends_utc':'2026-10-02T03:07:54+00:00',
        'claim':'Research tools and structural constraints; no authenticated semantic or phonetic decipherment.',
        'edition':json.loads((OUT/'report_build.json').read_text())['edition'],
        'source_rights':{'Lipi':'No repository license found; bulk local-only research input.',
                        'Mayig':'MIT, Michael Carlson2024.',
                        'Koskenniemi_Parpola1979':'Official Helsinki CC BY4.0; chart/text image attribution retained.',
                        'Other_primary_sources':'Acquisition and hash metadata retained; do not infer redistribution rights.'},
        'source_pins':{'Lipi':'fc8813a52e183d19c441631dc26c33a4dccbea39','Mayig':'ad2f1e218a34b8c33c57de0d6cb8d99272765bbb'},
        'source_pdf_hash_location':'research/corpus/primary/*_provenance.json and research/literature/source_retrieval_log.json; per-experiment source hashes retained.',
        'files':entries,
        'limits':'Hashes document local state, not archaeological authentication or scientific peer review. File mtime is not by itself a preregistration proof.'}
    (OUT/'evidence_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'files':len(entries),'edition':manifest['edition'],'path':'output/evidence_manifest.json'}))

if __name__=='__main__':main()
