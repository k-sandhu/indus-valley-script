"""Record the completed run's hashes, owned files, prose review and Git status.

Usage: python -I record_run.py --root REPOSITORY --code-dir DIR --raw-root DIR
  --records-dir DIR --protocol MD --schema MD --prose-tool PY
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def digest(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()


def write(path,value):
    with path.open('x',encoding='utf-8') as f: f.write(json.dumps(value,ensure_ascii=False,indent=1)+'\n')


def main():
    ap=argparse.ArgumentParser()
    for key in ('root','code-dir','raw-root','records-dir','protocol','schema','prose-tool'):
        ap.add_argument('--'+key,required=True,type=Path)
    a=ap.parse_args(); root=a.root.resolve(); code=a.code_dir.resolve(); raw=a.raw_root.resolve()
    relative=lambda p:p.resolve().relative_to(root).as_posix()
    assert code.is_relative_to(root) and raw.is_relative_to(root)
    immutable={'CODEX-PROMPT.md','TASK.md'}
    review=subprocess.run([sys.executable,'-I',str(a.prose_tool),'--path',str(a.code_dir),'--no-write'],capture_output=True,text=True,encoding='utf-8',check=True)
    prose=json.loads(review.stdout)
    authored=[f for f in prose['flags'] if Path(f['file']).name not in immutable]
    prose['authored_file_flags']=authored
    write(code/'prose-review.json',prose)
    assert not authored, authored
    status=subprocess.run(['git','-c','safe.directory='+root.as_posix(),'status','--porcelain','--untracked-files=all'],cwd=root,capture_output=True,text=True,encoding='utf-8',check=True).stdout
    (raw/'codex-b/git-status-final.txt').write_text(status,encoding='utf-8')
    code_prefix=relative(code)+'/'
    acq_prefix='experiments/2026-10-21-head-direction-corpora/acquisition/'
    owned=[]; unowned=[]
    for line in status.splitlines():
        path=line[3:].strip('"')
        is_owned=path.startswith(code_prefix) or (path.startswith(acq_prefix) and Path(path).name.startswith(('oracc-oakk-','cdli-data-')))
        if is_owned and Path(path).name not in immutable: owned.append(path)
        elif not is_owned: unowned.append(path)
    audit=dict(owned_status_paths=owned,unowned_status_entries=len(unowned),
        repository_already_dirty=True,unowned_changes='pre-existing or concurrent contributions; left untouched',
        git_mutation_commands_used=False,raw_and_normalised_files='ignored by Git',
        final_status_local_path=relative(raw/'codex-b/git-status-final.txt'))
    write(code/'PATH-AUDIT-CODEX.json',audit)
    ignored=subprocess.run(['git','-c','safe.directory='+root.as_posix(),'check-ignore',relative(a.records_dir/'sux-ur3.jsonl'),relative(a.records_dir/'akk-sargonic.jsonl'),relative(a.records_dir/'sux-sargonic.jsonl')],cwd=root,capture_output=True,text=True,encoding='utf-8',check=True)
    assert len(ignored.stdout.splitlines())==3
    now=datetime.datetime.now(datetime.timezone.utc)
    started=datetime.datetime.fromtimestamp((code/'PLAN-CODEX.md').stat().st_birthtime,datetime.timezone.utc)
    timing=dict(started_utc=started.isoformat(),finished_utc=now.isoformat(),elapsed_seconds=round((now-started).total_seconds(),3),
        start_basis='creation of PLAN-CODEX.md, the first owned write; preceding orientation is not timed')
    write(code/'RUN-TIMING-CODEX.json',timing)
    counts=json.loads((code/'counts.json').read_text(encoding='utf-8'))
    for c in counts['corpora'].values(): assert c['records']>=0
    inputs={relative(p):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in (a.protocol,a.schema,code/'normalize_cuneiform.py',code/'lexicon-cuneiform.tsv')}
    outputs={relative(p):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(a.records_dir.iterdir()) if p.is_file() and p.name.startswith(('sux-ur3.','akk-sargonic.','sux-sargonic.','cuneiform-'))}
    write(code/'ARTIFACTS-CODEX.json',dict(inputs=inputs,normalised_outputs=outputs,source_checks=counts['acquisitions'],held_archive=counts['held_archive'],
        final_normalisation_record=relative(raw/'codex-b/run-v6/run.json'),
        validation=relative(code/'validation-v6.json'),coverage=relative(code/'coverage-v6.json'),
        review=relative(code/'review-summary.json'),manual_checks=relative(code/'hand-checks.json')))
    files=[]
    for p in code.rglob('*'):
        if p.is_file() and p.name not in immutable: files.append(relative(p))
    acq=root/acq_prefix
    for pattern in ('oracc-oakk-*.json','cdli-data-*.json'):
        files.extend(relative(p) for p in acq.glob(pattern))
    directories=[]
    for pattern in ('src-oracc-oakk-*','src-cdli-data-*','codex-b'):
        for d in raw.glob(pattern):
            if not d.is_dir(): continue
            directories.append(relative(d))
            for p in d.rglob('*'):
                if p.is_file(): files.append(relative(p))
                elif p.is_dir(): directories.append(relative(p))
    files.extend(outputs)
    files.append(relative(code/'FILES-CODEX.json'))
    storage=json.loads((code/'storage-repair.json').read_text(encoding='utf-8'))
    removed=[]
    for item in storage['duplicates']:
        name=Path(item['retained']).name
        removed.extend(relative(raw/'codex-b'/run/name) for run in item['removed_from_runs'])
    write(code/'FILES-CODEX.json',dict(created_files=sorted(set(files)),created_source_and_scratch_directories=sorted(set(directories)),
        removed_verified_duplicate_extracts=sorted(removed),unchanged_supplied_files=sorted(immutable)))
    print(json.dumps(dict(created_files=len(set(files)),local_directories=len(set(directories)),authored_prose_flags=len(authored),
        unowned_preexisting_or_concurrent_status_entries=len(unowned),elapsed_seconds=timing['elapsed_seconds'])))


if __name__=='__main__': main()
