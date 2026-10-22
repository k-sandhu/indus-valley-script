"""Verify final assets and write coverage, rights, deletion and completion records.

Run once after acquisition and manifest reconciliation. Acquired files are read
with the infrastructure venv in isolated mode. Frozen test outputs are retained.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,csv,io,hashlib,json,shutil,subprocess,copy
from datetime import datetime,timezone
import numpy as np
import rasterio
from common import read_json,write_json,record,sha256,utc,code_hashes,check_space
from package_audit import audit,file_records

def csv_file(path,rows,fields):
    buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    payload=buf.getvalue().encode('utf-8');check_space(path,len(payload))
    with Path(path).open('xb') as f:f.write(payload)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('raw');ap.add_argument('infra');a=ap.parse_args();raw=Path(a.raw);infra=Path(a.infra);repo=Path.cwd().resolve()
    image=read_json(infra/'imagery-manifest-v1.json');plans=read_json(infra/'plan-library-v1.json');sites=read_json(infra/'sites-located-v1.json');test=read_json(infra/'selftest-v1.json');validation=read_json(infra/'validation-v1/summary.json')
    verified=audit([str(infra/'imagery-manifest-v1.json'),str(infra/'plan-library-v1.json')]);baseline={str(Path(x['path']).resolve()):x for x in read_json(infra/'recompression-v1.json')['files']};rasters=[]
    for p in sorted(raw.rglob('*.tif')):
        with rasterio.open(p) as ds:
            arr=ds.read();digest=hashlib.sha256(arr.tobytes()).hexdigest();old=baseline.get(str(p.resolve()))
            row=dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha256(p),shape=list(arr.shape),compression=ds.compression.name,predictor=ds.tags(ns='IMAGE_STRUCTURE').get('PREDICTOR'),all_bands_read=True,finite=bool(np.isfinite(arr).all()),pixel_sha256=digest,original_pixels_match=(digest==old['pixel_sha256']) if old else None)
            if not row['finite'] or row['compression']!='deflate' or row['predictor']!='2' or row['original_pixels_match'] is False:raise ValueError('Raster verification failed '+str(p))
            rasters.append(row)
    checked_old={str(Path(r['path']).resolve()) for r in rasters if r['original_pixels_match'] is not None}
    if set(baseline)-checked_old:raise ValueError('A recompressed first-run survivor is missing')
    current=code_hashes();core=['measure_lines.py','register_plan.py','common.py','render_image.py','render_plan.py','systems.py','igrf.py','selftest.py']
    core_match=all(test['provenance']['code_hashes'][k]==current[k] for k in core)
    runway_code_match=validation['provenance']['runway_validation.py']==current['runway_validation.py']
    proc=subprocess.run(['git','-c','safe.directory='+repo.as_posix(),'status','--porcelain'],capture_output=True,text=True,check=True)
    owned=['experiments/2026-10-21-town-orientations-verification/tools/','experiments/2026-10-21-town-orientations-verification/infra-v1/','data/raw/2026-10-21-town-orientations-verification/infra/','data/raw/2026-10-21-town-orientations-verification/venv-infra/']
    statuses=proc.stdout.splitlines();owned_status=[s for s in statuses if any(s[3:].replace('\\','/').startswith(p) for p in owned)]
    verified.update(rasters_full_read=rasters,all_first_run_survivors_pixel_identical=all(r['original_pixels_match'] is not False for r in rasters),measurement_code_matches_selftest=core_match,runway_code_matches_validation=runway_code_match,git_status_owned=owned_status,git_status_other_contributors_count=len(statuses)-len(owned_status),invariant_deviations=['Early raw JSON inventory diagnostics used system Python without -I. Subsequent acquired-file production processing used the infrastructure venv with -I.'])
    verified['overall_pass']=verified['overall_pass'] and core_match and runway_code_match
    write_json(infra/'verification-v1.json',verified)
    known={}
    for path in list(infra.glob('*.json'))+list(raw.rglob('acquisition-result.json')):
        try:
            for r in file_records(read_json(path)):
                if r.get('url') and r.get('rights_status'):known[str(Path(r['path']).resolve())]=r
        except ValueError:pass
    files=[]
    for p in sorted(raw.rglob('*')):
        if not p.is_file():continue
        old=known.get(str(p.resolve()))
        if old:
            r=copy.deepcopy(old);r.update(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha256(p))
        else:
            own=p.name=='acquisition-result.json' or 'plan-search' in p.parts or any(part.startswith('runways') for part in p.parts)
            spectral=p.suffix=='.tif';url='https://earth-search.aws.element84.com/v1' if spectral or p.name.startswith('stac-search-') else 'local-generated' if own else 'Unresolved acquisition locator; parent source records retained'
            r=record(p,url,'explicit-license' if spectral else 'own-work' if own else 'rights-unverified','Copernicus Sentinel data terms; Contains modified Copernicus Sentinel data 2018–2026' if spectral else 'Project generated derivative; CC0 1.0' if own else 'No explicit licence verified; see source and parent records',retrieved_utc=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),retrieval_time_basis='File modification time; acquisition record not available')
        files.append(r)
    inferred=[r['path'] for r in files if r.get('retrieval_time_basis')]
    write_json(infra/'asset-inventory-v1.json',dict(schema_version=1,created_utc=utc(),file_count=len(files),logical_bytes=sum(r['bytes'] for r in files),records_reconstructed_from_filesystem=inferred,files=files))
    sources={}
    for path in infra.glob('*acquisition*.json'):
        for r in file_records(read_json(path)):
            if r.get('format') in ['pdf','html','csv','txt']:sources[str(Path(r['path']).resolve())]=r
    for r in file_records(plans):
        if r.get('format') in ['pdf','html']:sources[str(Path(r['path']).resolve())]=r
    for r in files:
        if r['format'] in ['pdf','html','csv','txt']:sources[str(Path(r['path']).resolve())]=r
    # Resolve retired duplicate source paths to the byte-identical held copy.
    for row in read_json(infra/'duplicate-cleanup-v1.json')['deletions']:
        old=sources.pop(str(Path(row['path']).resolve()),None)
        if old:
            r=copy.deepcopy(old);r['path']=row['retained_path'];r['bytes']=Path(r['path']).stat().st_size;r['sha256']=sha256(r['path']);sources[str(Path(r['path']).resolve())]=r
    for key in list(sources):
        if not Path(sources[key]['path']).exists():sources.pop(key)
    write_json(infra/'source-inventory-v1.json',dict(schema_version=1,created_utc=utc(),sources=sorted(sources.values(),key=lambda r:r['path'])))
    deletions=[]
    for name in ['storage-verification-v1.json','duplicate-cleanup-v1.json','duplicate-cleanup-v2.json','duplicate-cleanup-v3.json','scratch-cleanup-v1.json','final-scratch-cleanup-v1.json','late-plan-scratch-cleanup-v1.json','final-plan-scratch-cleanup-v1.json']:
        for r in read_json(infra/name)['deletions']:deletions.append(dict(r,ledger=name,count=1))
    # Three synthetic runs each evaluate 1925 twice. TemporaryDirectory removes
    # the same deterministic ASCII serialization; random directory names were
    # not captured by the original wrapper, so keep that limitation explicit.
    text=(raw/'igrf/igrf14coeffs.txt').read_text(encoding='ascii');rows=[]
    for line in text.splitlines():
        v=line.split()
        if not v or v[0] not in ['g','h']:continue
        n,m=int(v[1]),int(v[2]);values=list(map(float,v[3:]));value=values[5]*1+values[6]*0
        rows.append(f'{n} {m if v[0]=="g" else -m} {value:.12g} {value:.12g}')
    size=len(('1 13 2 1 1\n1900.0 2030.0\n'+'\n'.join(rows)+'\n').encode('ascii'))
    deletions.append(dict(path=(raw/'igrf/.igrf14-eval-<random>/converted.shc').as_posix(),bytes=size,count=6,reason='Automatically removed regenerable IGRF conversion scratch; size reconstructed exactly from coefficients; random directory names not logged',ledger='IGRF TemporaryDirectory lifecycle'))
    write_json(infra/'deletions-v1.json',dict(schema_version=1,created_utc=utc(),explicit_files=159,automatic_files=6,files_removed=sum(r['count'] for r in deletions),logical_bytes=sum(r['bytes']*r['count'] for r in deletions),deletions=deletions))
    csv_file(infra/'deletions-v1.csv',deletions,['path','bytes','count','reason','retained_path','ledger'])
    coverage=[]
    for s,t,p in zip(sites['sites'],image['towns'],plans['towns']):
        assert s['slug']==t['slug']==p['slug']
        coverage.append(dict(town=s['slug'],required=s['required'],located=s['located'],flagged=bool(s['flags']),sentinel2_scenes=t['scene_count_in_composite'],composite=bool(t['composite']),landsat_obtained=t['landsat']['obtained'],plans=p['plan_count'],north_meaning_stated=p['north_meaning_stated_count']))
    csv_file(infra/'coverage-v1.csv',coverage,list(coverage[0]))
    missing_images=[r['town'] for r in coverage if not r['composite']];missing_plans=[r['town'] for r in coverage if not r['plans']]
    issues=['No Landsat 8/9 panchromatic product acquired; attempts are recorded','No held imagery for Hisar; official reference is resolved but unmeasured','Lothal and Kalibangan reproductions have incomplete book/author attribution','Some plan scale bars or scale labels are absent or unreadable; see individual plan notes','Four runway references have doubtful coordinate precision; separate precise-reference aggregate retained','Exact random directory names of six automatically removed IGRF scratch files were not logged']
    if inferred:issues.append(f'{len(inferred)} raw file records use filesystem timestamps or reconstructed source locators; see asset-inventory-v1.json')
    result=dict(schema_version=1,created_utc=utc(),authors=[dict(model='GPT-6',harness='Codex API',subagents=False)],located=len(coverage),flagged=sum(r['flagged'] for r in coverage),towns_with_composites=sum(r['composite'] for r in coverage),towns_with_plans=sum(bool(r['plans']) for r in coverage),plans=sum(r['plans'] for r in coverage),coverage=coverage,missing_imagery=missing_images,missing_plans=missing_plans,selftest_pass=test['overall_pass'],runway_validation_pass=validation['overall_pass'],runway_aggregate=validation['aggregate'],raw_bytes=sum(r['bytes'] for r in files),raw_file_count=len(files),deletions_files=sum(r['count'] for r in deletions),deletions_bytes=sum(r['bytes']*r['count'] for r in deletions),verification_pass=verified['overall_pass'],unresolved=issues,invariant_deviations=verified['invariant_deviations'],free_bytes=shutil.disk_usage(raw).free)
    write_json(infra/'completion-v1.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['coverage','runway_aggregate','authors']},indent=2))
if __name__=='__main__':main()
