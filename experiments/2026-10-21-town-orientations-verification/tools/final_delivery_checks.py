"""Check the final manifests and complete raw inventory without changing inputs."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,ast,shutil,subprocess
from common import read_json,write_json,sha256,utc,code_hashes
from package_audit import file_records
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('raw');ap.add_argument('infra');a=ap.parse_args();raw=Path(a.raw);infra=Path(a.infra);known={};checked={};failures=[]
    manifests=[infra/'imagery-manifest-v1.json',infra/'plan-library-v1.json',infra/'asset-inventory-v1.json',infra/'source-inventory-v1.json']
    for p in manifests:
        for r in file_records(read_json(p)):
            key=str(Path(r['path']).resolve())
            if key in known and (known[key]['sha256'],known[key]['bytes'])!=(r['sha256'],r['bytes']):failures.append(dict(path=r['path'],reason='Inconsistent inventory records'))
            known[key]=r
    for key,r in known.items():
        p=Path(key);ok=p.exists() and p.stat().st_size==r['bytes'] and sha256(p)==r['sha256'];checked[key]=ok
        if not ok:failures.append(dict(path=r['path'],reason='Final hash or byte count mismatch'))
    all_raw={str(p.resolve()) for p in raw.rglob('*') if p.is_file()};inventory_raw={str(Path(r['path']).resolve()) for r in read_json(infra/'asset-inventory-v1.json')['files']}
    if all_raw!=inventory_raw:failures.append(dict(reason='Raw inventory coverage mismatch'))
    for p in Path(__file__).parent.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    status=subprocess.run(['git','-c','safe.directory='+Path.cwd().resolve().as_posix(),'status','--porcelain'],capture_output=True,text=True,check=True)
    current=code_hashes();test=read_json(infra/'selftest-v1.json');core=['measure_lines.py','register_plan.py','common.py','render_image.py','render_plan.py','systems.py','igrf.py','selftest.py'];core_ok=all(test['provenance']['code_hashes'][k]==current[k] for k in core)
    validation=read_json(infra/'validation-v1/summary.json');runway_ok=current['runway_validation.py']==validation['provenance']['runway_validation.py']
    if not core_ok or not runway_ok:failures.append(dict(reason='Tested measurement-code mismatch'))
    v=read_json(infra/'verification-v1.json');result=dict(schema_version=1,created_utc=utc(),manifest_sha256={p.name:sha256(p) for p in manifests},checked_unique_files=len(known),all_hashes_match=all(checked.values()),raw_inventory_complete=all_raw==inventory_raw,raw_files=len(all_raw),raw_bytes=sum(p.stat().st_size for p in raw.rglob('*') if p.is_file()),full_band_read_record='verification-v1.json',full_band_read_tiffs=len(v['rasters_full_read']),original_pixel_hash_matches=sum(r['original_pixels_match'] is True for r in v['rasters_full_read']),measurement_code_matches_selftest=core_ok,runway_code_matches_validation=runway_ok,code_hashes=current,git_status_read_only=True,git_status_entries=len(status.stdout.splitlines()),failures=failures,overall_pass=not failures,free_bytes=shutil.disk_usage(raw).free)
    write_json(infra/'final-delivery-checks-v1.json',result)
    print({k:v for k,v in result.items() if k not in ['manifest_sha256','code_hashes']})
if __name__=='__main__':main()
