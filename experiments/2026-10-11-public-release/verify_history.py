"""Screen the explicitly published histories. Never emit credential values."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
PATTERNS={
 'known_token':rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{35,}|hf_[A-Za-z0-9]{30,})',
 'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'signed_url':rb'[?&](?:X-Amz-(?:Signature|Credential)|X-Goog-(?:Signature|Credential)|sig)=[A-Za-z0-9%_/+-]{12,}'
}
def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    repo=Path(a.repo).resolve();output=HERE/a.output
    if output.exists():raise SystemExit('Preserve previous audits')
    refs=['refs/heads/main','refs/heads/research/2026-10-06-program']
    def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
    raw=git('rev-list','--objects',*refs).decode().splitlines();objects={r.split(' ',1)[0]:r.split(' ',1)[1] if ' ' in r else '' for r in raw}
    excluded={x['path'] for x in json.loads((HERE/'publication-manifest.json').read_text())['excluded_from_public_history']}
    proc=subprocess.Popen(['git','cat-file','--batch'],cwd=repo,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    flagged=[];forbidden=[];oversized=[];count=0;total=0
    for oid,path in objects.items():
        proc.stdin.write((oid+'\n').encode());proc.stdin.flush();head=proc.stdout.readline().decode().split();size=int(head[2]);body=proc.stdout.read(size);proc.stdout.read(1)
        if head[1]!='blob':continue
        count+=1;total+=size
        hits=[name for name,pattern in PATTERNS.items() if re.search(pattern,body,re.I)]
        if hits:flagged.append(dict(object=oid,path=path,patterns=hits))
        if path in excluded or path.startswith('.github/workflows/') or path.startswith('data/') and path!='data/README.md' or path.startswith(('research/literature/sources/','research/literature/primary/')):
            forbidden.append(dict(object=oid,path=path))
        if size>90*1024*1024:oversized.append(dict(object=oid,path=path,bytes=size))
    proc.stdin.close();proc.wait()
    result=dict(status='pass' if not flagged and not forbidden and not oversized else 'fail',refs={r:git('rev-parse',r).decode().strip() for r in refs},blobs=count,bytes_scanned=total,
        credential_or_signed_url_matches=flagged,forbidden_paths=forbidden,oversized_blobs=oversized,
        scope='Reachable blobs of the two selected public branches. Known formats and signed URL markers are bounded screens; source redistribution decisions are separately documented.')
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','blobs','bytes_scanned','credential_or_signed_url_matches','forbidden_paths','oversized_blobs']}))
    raise SystemExit(0 if result['status']=='pass' else 1)
if __name__=='__main__':main()
