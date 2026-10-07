"""Snapshot authorized documents, pin all existing files, append the dated amendment."""
from pathlib import Path
import datetime, hashlib, json
ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-06-chronology-region'

def main():
    target=OWN/'review-response-baseline-2026-10-07-v1'
    if target.exists(): raise FileExistsError('Baseline already exists; do not rerun setup.')
    allowed={'README.md','REPORT.md','RETROSPECTIVE.md','registry-entry.json','PROTOCOL.md'}
    files=[]
    for directory in [OWN,RAW]:
        for path in sorted(directory.rglob('*')):
            if not path.is_file(): continue
            files.append({'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'authorized_document_update':path.parent==OWN and path.name in allowed})
    target.mkdir()
    for name in allowed: (target/name).write_bytes((OWN/name).read_bytes())
    (target/'preservation.json').write_text(json.dumps({'origin':'second post-launch amendment',
        'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseline_files':files},indent=2),encoding='utf-8')
    protocol=OWN/'PROTOCOL.md'
    with protocol.open('a',encoding='utf-8') as stream:
        stream.write('\n\n---\n\n'+(OWN/'REVIEW-AMENDMENT-2026-10-07.md').read_text(encoding='utf-8'))
    print(json.dumps({'prior_files_pinned':len(files),'documents_archived':len(allowed),'protocol_amendment_appended':True}))

if __name__=='__main__': main()
