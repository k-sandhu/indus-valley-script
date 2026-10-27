"""Build a checked local-only delivery archive from explicit final products."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

P=Path(__file__).resolve().parent
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test')

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as s:
        for b in iter(lambda:s.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def main(pdf,pptx,html,figures,tag):
    out=RAW/f'delivery-{tag}'
    out.mkdir(exist_ok=False)
    archive=out/'shared-infrastructure-study-2026-10-24.zip'
    products=[('shared-infrastructure-report.pdf',pdf),
              ('shared-infrastructure-presentation.pptx',pptx),
              ('shared-infrastructure-explorer.html',html),
              ('source-linked-figures.zip',figures)]
    items=[{'archive_path':n,'physical_path':str(f),'sha256':sha(f),'bytes':f.stat().st_size,
            'class':'final local product'} for n,f in products]
    # Only authored project records and code from this contribution enter the archive.
    # Raw source books, image acquisitions, OCR and detailed catalogue rows stay out.
    for f in sorted(P.rglob('*')):
        if not f.is_file() or '__pycache__' in f.parts:continue
        if f.suffix.lower() not in {'.md','.py','.json','.mjs','.js','.ps1','.txt'}:continue
        if f.name.startswith('artifact-manifest-'):continue
        items.append({'archive_path':'research/'+f.relative_to(P).as_posix(),
                      'physical_path':str(f),'sha256':sha(f),'bytes':f.stat().st_size,
                      'class':'authored code, metadata, prose or review record'})
    assert len({x['archive_path'] for x in items})==len(items)
    for r in items:
        path=Path(r['physical_path']).resolve()
        assert path.is_relative_to(P.resolve()) or path.is_relative_to(RAW.resolve())
        assert not r['archive_path'].startswith('/') and '..' not in Path(r['archive_path']).parts
    metadata={'title':'Shared infrastructure against excavation evidence','date':'2026-10-24',
              'local_only':True,'source_terms':'Illustrated products contain attributed third-party source excerpts with unresolved redistribution rights. Keep this archive local.',
              'included':'Final report, PowerPoint, self-contained offline explorer, figure archive, authored study records and code.',
              'excluded':'Acquired full source publications, raw corpora, OCR, detailed source-row derivatives and raw endpoint coordinates.',
              'scientific_status':'Exploratory measurement and eligibility pilot; no fresh confirmation score.',
              'files':items}
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for r in items:z.write(r['physical_path'],r['archive_path'])
        z.writestr('DELIVERY-MANIFEST.json',json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for r in items:
            assert hashlib.sha256(z.read(r['archive_path'])).hexdigest()==r['sha256']
        entry_count=len(z.namelist())
    result={'output_physical_path':str(archive),'output_logical_path':'data/raw/2026-10-24-shared-infrastructure-plan-test/'+archive.relative_to(RAW).as_posix(),
            'sha256':sha(archive),'bytes':archive.stat().st_size,'archive_entries':entry_count,
            'all_entry_hashes_checked':True,'local_only':True,'source_terms':metadata['source_terms'],
            'products':items[:4],'authored_record_count':len(items)-4,'code_sha256':sha(Path(__file__))}
    (P/f'artifact-manifest-{tag}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('output_physical_path','bytes','archive_entries','sha256','all_entry_hashes_checked')}))

if __name__=='__main__':
    a=argparse.ArgumentParser()
    for n in ('pdf','pptx','html','figures'):a.add_argument('--'+n,type=Path,required=True)
    a.add_argument('--tag',required=True)
    v=a.parse_args();main(v.pdf,v.pptx,v.html,v.figures,v.tag)
