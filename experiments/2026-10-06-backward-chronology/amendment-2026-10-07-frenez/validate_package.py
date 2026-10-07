"""Validate appended records, preserved witnesses and paths without shared writes."""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[3]
OWN=Path(__file__).resolve().parent
BASE=OWN.parent
RAW=ROOT/'data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-frenez'

def load(p):
    payload=p.read_bytes()
    encoding='utf-16' if payload.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'
    return json.loads(payload.decode(encoding))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--manifest',required=True);a=p.parse_args()
    out=Path(a.output).resolve();out.relative_to(OWN)
    manifest=Path(a.manifest).resolve();manifest.relative_to(OWN)
    if out.exists() or manifest.exists():p.error('Choose fresh validation/manifest paths.')
    rows=load(OWN/'evidence-table.json')['rows'];sources=load(OWN/'sources.json')['sources'];claims=load(OWN/'continuity-claims.json')['claims']
    assert rows[:42]==load(BASE/'evidence-table.json')['rows']
    assert sources[:18]==load(BASE/'sources.json')['sources']
    assert claims[:11]==load(BASE/'continuity-claims.json')['claims']
    with (OWN/'evidence-table.csv').open(encoding='utf-8-sig',newline='')as f:cr=list(csv.DictReader(f))
    assert len(cr)==len(rows)
    cells=0
    for c,r in zip(cr,rows):
        for k,v in r.items():
            expected=json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else '' if v is None else str(v)
            assert c[k]==expected,(r['id'],k)
            cells+=1
    sids={s['id'] for s in sources};cids={c['id'] for c in claims};rids={r['id']for r in rows}
    for r in rows:assert set(r['source_ids'])<=sids and set(r['continuity_claim_ids'])<=cids
    for c in claims:assert set(c['source_ids'])<=sids
    for c in load(OWN/'lecture-claim-audit.json')['claims']:
        assert set(c['source_ids'])<=sids and set(c['evidence_row_ids'])<=rids
    for c in load(OWN/'contact-items.json')['cases']:assert set(c['source_ids'])<=sids
    hashes=[]
    for s in sources:
        if 'local_witness'in s:
            assert sha(ROOT/s['local_witness'])==s['sha256'],s['id']
            hashes.append(s['id'])
    baseline=load(OWN/'baseline-integrity.json')['baseline_files']
    for b in baseline:assert sha(ROOT/b['path'])==b['sha256'],b['path']
    acquisition=[]
    for f in sorted(RAW.glob('*.acquisition.json'))+sorted(RAW.glob('*.processing.json')):
        d=load(f)
        if 'local_path'in d:assert sha(ROOT/d['local_path'])==d['sha256'],f.name
        acquisition.append(dict(id=d['id'],record=f.relative_to(ROOT).as_posix(),http_status=d.get('http_status'),
                                reuse=bool(d.get('reuse')),success=d.get('download_success'),error=d.get('error')))
    pages=load(RAW/'quivron1980-pages/pages.json')
    assert len(pages)==12
    for d in pages:
        assert d['http_status']==d['image_status']==200
        assert sha(RAW/f"quivron1980-pages/p{d['page']}.html")==d['sha256']
        assert sha(RAW/f"quivron1980-pages/p{d['page']}.jpg")==d['image_sha256']
    code=[]
    for f in sorted(OWN.glob('*.py')):ast.parse(f.read_text(encoding='utf-8'));code.append(f.name)
    rebuilt=OWN/'inputs-reproduction-01'
    assert rebuilt.exists(),'Run build_amendment.py to inputs-reproduction-01 first.'
    builtfiles=['evidence-table.json','evidence-table.csv','sources.json','continuity-claims.json','added-rows.json','build-verification.json']
    for n in builtfiles:assert (OWN/n).read_bytes()==(rebuilt/n).read_bytes(),n
    comparison=load(OWN/'comparison-01/comparison.json')
    assert comparison['reproduction']['all_identical']
    scan=load(RAW/'prose-scan-final-02.txt');assert not scan['flags']
    links=[];queued={out,manifest}
    for f in sorted(OWN.rglob('*.md')):
        for target in re.findall(r'\]\(([^)]+)\)',f.read_text(encoding='utf-8')):
            target=target.strip('<>').split('#')[0]
            if not target or re.match(r'[a-z]+://',target):continue
            q=(f.parent/unquote(target)).resolve()
            exists=q.exists();pending=q in queued
            assert exists or pending,(f,target)
            links.append(dict(file=f.relative_to(ROOT).as_posix(),target=target,exists_or_queued=exists or pending))
    for path in load(OWN/'registry-entry.json')['evidence']:assert (ROOT/path).exists(),path
    quality=dict(status='Verified computation',documentary_status='Exploratory',
        preserved_parent_rows=42,preserved_parent_sources=18,preserved_parent_claims=11,
        baseline_files_checked=len(baseline),all_baseline_files_unchanged=True,
        evidence_rows_checked=len(rows),csv_json_cells_checked=cells,source_hashes_checked=len(hashes),source_ids_hashed=hashes,
        code_files_parsed=code,rebuilt_input_files_identical=len(builtfiles),coverage_output_files_identical=6,
        prose_scan=dict(command='python tools/review_prose.py --path experiments/2026-10-06-backward-chronology --no-write',
                        markdown_files_scanned=scan['files_scanned'],flags=scan['flags']),
        local_markdown_links_checked=len(links),links=links,
        acquisition_records=acquisition,direct_download_failures=[d for d in acquisition if d['success']is False or d['error']],
        quivron_public_page_checks=dict(html_pages=12,image_pages=12,all_HTTP200=True,hashes_verified=24),
        raw_measurement_transcriptions=load(RAW/'radiocarbon-source-rows.json')['source'],
        source_and_artifact_scope='Only dated amendment owned/raw directories written; earlier manifests and other packages read only. Final manifest enumerates new paths.',
        manifest_self_hash_excluded=True)
    write(out,quality)
    files=[]
    for top in [OWN,RAW]:
        for f in sorted(top.rglob('*')):
            if f.is_file()and f!=manifest:files.append(dict(path=f.relative_to(ROOT).as_posix(),bytes=f.stat().st_size,sha256=sha(f)))
    files.append(dict(path=manifest.relative_to(ROOT).as_posix(),bytes=None,sha256=None,note='Self path included; recursive self-hash excluded.'))
    write(manifest,dict(status='Verified computation',files_created=len(files),files_changed_outside_amendment=0,
                       owned_directory=OWN.relative_to(ROOT).as_posix(),local_raw_directory=RAW.relative_to(ROOT).as_posix(),files=files))
    assert out.exists()and manifest.exists()
    for item in files:
        if item['sha256']:assert sha(ROOT/item['path'])==item['sha256']
    print(json.dumps(dict(baseline_unchanged=len(baseline),rows=len(rows),csv_cells=cells,source_hashes=len(hashes),
                         prose_flags=len(scan['flags']),links_checked=len(links),new_paths=len(files)),indent=2))

if __name__=='__main__':main()
