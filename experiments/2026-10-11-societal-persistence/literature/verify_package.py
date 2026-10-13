"""Read-only packaging verification; numerical audit remains separately frozen."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest=json.loads((HERE/'changed-paths.json').read_text('utf-8'))
    audit=json.loads((HERE/'source-checks-v1.json').read_text('utf-8'))
    checks=[]

    def check(name,passed):checks.append(dict(name=name,passed=bool(passed)))

    for group in ['authored_artifact_hashes','local_only_raw_paths','ignored_local_generated_helpers','unmodified_collaborator_dependencies']:
        for item in manifest[group]:
            path=ROOT/item['path']
            check(item['path']+' integrity',path.is_file() and sha(path)==item['sha256'] and path.stat().st_size==item['bytes'])
    for file,expected in audit['input_hashes'].items():check(file+' retained audit input',sha(HERE/file)==expected)
    check('retained source audit all pass',audit['status']=='pass' and audit['passed']==audit['checks']==312)
    paths=set(manifest['authored_and_review_output_paths'])
    actual={p.relative_to(ROOT).as_posix() for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    check('authored paths complete',paths==actual and len(paths)==manifest['authored_artifact_count'])
    check('bytecode classified separately',not any('__pycache__' in p or p.endswith('.pyc') for p in paths))
    links=0
    for path in HERE.glob('*.md'):
        for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',path.read_text('utf-8')):
            target=target.strip('<>').split('#')[0]
            if re.match(r'^[a-zA-Z]+://',target):continue
            check(path.name+' link '+target,(path.parent/target).resolve().exists());links+=1
    raw=sorted(x['path'] for x in manifest['local_only_raw_paths']+manifest['ignored_local_generated_helpers'])
    response=subprocess.run(['git','check-ignore','--no-index','-z','--stdin'],input=b'\0'.join(p.encode('utf-8') for p in raw)+b'\0',cwd=ROOT,capture_output=True)
    ignored={p.decode('utf-8') for p in response.stdout.split(b'\0') if p}
    check('owned raw and generated helpers ignored',response.returncode in [0,1] and set(raw)<=ignored)
    failed=[x for x in checks if not x['passed']]
    print(json.dumps(dict(status='pass' if not failed else 'fail',checks=len(checks),passed=len(checks)-len(failed),local_markdown_links=links,authored_artifacts=len(paths),raw_witnesses=len(manifest['local_only_raw_paths']),generated_helpers=len(manifest['ignored_local_generated_helpers']),failed=failed),ensure_ascii=False,indent=2))
    if failed:raise SystemExit(1)


if __name__=='__main__':main()
