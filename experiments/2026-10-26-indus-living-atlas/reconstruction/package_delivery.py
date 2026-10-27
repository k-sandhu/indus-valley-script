"""Record original project payload and local visual-QA hashes without embedding witnesses."""
from pathlib import Path
import hashlib
import json
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/reconstruction')


def digest(p):
    return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def main():
    target=HERE/'delivery-v1.json'
    if target.exists():raise FileExistsError(target)
    registry=ROOT/'knowledge/registry/attempts/INDUS-CITY-3D-2026-10-26.json'
    files=sorted(p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths=[p.relative_to(ROOT).as_posix() for p in files]+[registry.relative_to(ROOT).as_posix()]
    hashes=[]
    for p in files+[registry]:
        record=digest(p);record['path']=p.relative_to(ROOT).as_posix();hashes.append(record)
    screenshots=sorted(RAW.glob('*-v5.png'))
    local=[digest(p) for p in screenshots]
    local += [digest(RAW/n) for n in ['browser-great-bath-v5.obj','browser-great-bath-v5.json']]
    checks=json.loads((HERE/'verification-v5.json').read_text(encoding='utf-8'))
    browser=json.loads((HERE/'browser-verification-v5.json').read_text(encoding='utf-8'))
    repository=json.loads((HERE/'repository-verification-v1.json').read_text(encoding='utf-8'))
    own_errors=[x for x in repository['errors'] if '2026-10-26-indus-living-atlas/reconstruction' in str(x)]
    ignored=subprocess.run(['git','check-ignore',*paths],cwd=ROOT,capture_output=True,text=True).stdout.splitlines()
    result=dict(schema_version='1.0',endpoint='run-v5',entry='index.html',files=hashes,
                local_visual_review=local,geometry_checks=len(checks['checks']),browser_checks=len(browser['checks']),
                passed=checks['passed'] and browser['passed'] and not own_errors and not ignored,
                counts=checks['counts'],repo_verifier=dict(total_errors=len(repository['errors']),owned_errors=own_errors),
                unexpected_ignored_project_paths=ignored,
                rights=dict(project_code='Unlicense',project_geometry_and_prose='CC0 1.0',
                            raw_sources='rights-unverified; local-only; no third-party images or plans embedded'),
                publication='No publication, deployment, push or visibility change performed.',
                authors='GPT-6 family through Codex desktop collaboration; exact variant unavailable')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (HERE/'CHANGED-PATHS.json').write_text(json.dumps(dict(paths=paths+[target.relative_to(ROOT).as_posix(),(HERE/'CHANGED-PATHS.json').relative_to(ROOT).as_posix()],
                    owned_roots=[HERE.relative_to(ROOT).as_posix(),registry.relative_to(ROOT).as_posix()],raw_root=RAW.as_posix()),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'],project_files=len(paths),screenshots=len(screenshots),ignored=ignored,
                          checks=len(checks['checks']),browser_checks=len(browser['checks']),outside_repo_errors=len(repository['errors']))))


if __name__=='__main__':main()
