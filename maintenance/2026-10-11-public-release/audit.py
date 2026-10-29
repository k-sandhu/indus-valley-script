"""Audit proposed public files and reachable Git history without exposing secrets."""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, re, subprocess, zipfile

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-11-public-release'
TOKEN=re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{35,}|hf_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)

def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='audit-initial.json');p.add_argument('--backup',action='store_true');a=p.parse_args()
    out=HERE/a.output
    if out.exists():raise SystemExit('Refusing to overwrite audit')
    selected=sorted(set(git('ls-files','--cached','--others','--exclude-standard','-z').decode().split('\0'))-{''})
    tracked=set(git('ls-files','-z').decode().split('\0'))-{''}
    if a.backup:
        RAW.mkdir(parents=True,exist_ok=True)
        bundle=RAW/'private-history-before.bundle'
        if bundle.exists():raise SystemExit('Backup already exists')
        subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=ROOT,check=True)
        snapshot=RAW/'working-tree-before.zip'
        with zipfile.ZipFile(snapshot,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for name in selected:
                f=(ROOT/name).resolve()
                assert f.is_relative_to(ROOT)
                if f.is_file():z.write(f,name)
        write(RAW/'backup-manifest.json',{'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'working_snapshot_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),'files':len(selected),'refs':git('show-ref').decode().splitlines()})
    files=[];secrets=[];source_suspects=[]
    for name in selected:
        f=ROOT/name
        if not f.is_file():continue
        b=f.read_bytes()
        files.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'tracked_before':name in tracked})
        if TOKEN.search(b):secrets.append(name)
        fields=[]
        if f.suffix in {'.json','.jsonl','.html','.csv','.md'}:
            for k in [b'"signs_reading_rtl"',b'"signs_visual_ltr"',b'"sequence"',b'"target_code"',b'"source_text"',b'"caption"',b'"excerpt"',b'<LEND>',b'"translation"']:
                n=b.count(k)
                if n>=15:fields.append({'field':k.decode(),'count':n})
        if fields:source_suspects.append({'path':name,'bytes':len(b),'fields':fields})
    objs=git('rev-list','--objects','--all').decode().splitlines()
    names={line.split(' ',1)[0]:line.split(' ',1)[1] if ' ' in line else '' for line in objs}
    proc=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    history_secrets=[];history_forbidden=[];history_source=[];blobs=0
    for oid,name in names.items():
        proc.stdin.write((oid+'\n').encode());proc.stdin.flush()
        header=proc.stdout.readline().decode().split();size=int(header[2]);b=proc.stdout.read(size);proc.stdout.read(1)
        if header[1]!='blob':continue
        blobs+=1
        if TOKEN.search(b):history_secrets.append({'object':oid,'path':name})
        if (name.startswith('data/') and name!='data/README.md') or name.startswith('research/literature/sources/') or name.startswith('research/literature/primary/') or name.startswith('.github/workflows/'):
            history_forbidden.append({'object':oid,'path':name,'bytes':size})
        if b.count(b'"signs_reading_rtl"')>=15 or b.count(b'"signs_visual_ltr"')>=15 or b.count(b'<LEND>')>=15:
            history_source.append({'object':oid,'path':name,'bytes':size})
    proc.stdin.close();proc.wait()
    write(out,{'selected_files':len(files),'selected_bytes':sum(f['bytes'] for f in files),'known_credential_pattern_paths':secrets,'source_payload_review_queue':source_suspects,'history_blob_count':blobs,'history_credential_pattern_objects':history_secrets,'history_forbidden_paths':history_forbidden,'history_bulk_corpus_signatures':history_source,'file_types':dict(Counter(Path(f['path']).suffix or '(extensionless)' for f in files)),'largest_files':sorted(files,key=lambda f:-f['bytes'])[:20],'scope':'All selected files and all reachable Git blobs; credential signatures and source-field screens are bounded, with asset review recorded separately.'})
    write(RAW/(a.output.replace('.json','-files.json')),files)
    print(json.dumps({'selected_files':len(files),'bytes':sum(f['bytes'] for f in files),'history_blobs':blobs,'secret_paths':len(secrets),'history_secrets':len(history_secrets),'history_forbidden':len(history_forbidden),'history_bulk_corpus':len(history_source),'source_review_queue':len(source_suspects),'largest':[(f['path'],f['bytes']) for f in sorted(files,key=lambda f:-f['bytes'])[:5]]},indent=2))

if __name__=='__main__':main()
