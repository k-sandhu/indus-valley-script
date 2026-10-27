"""Record current repository checks without replacing earlier validation results."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

P=Path(__file__).resolve().parent
REPO=P.parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main(tag):
    output=P/f'CHECKS-{tag}.json'
    prose=P/f'prose-scan-{tag}-final.json'
    if output.exists() or prose.exists():
        raise FileExistsError('Preserve existing check records; use a new tag')
    relative=P.relative_to(REPO).as_posix()
    commands={
        'knowledge_base':[sys.executable,'tools/kb.py','check'],
        'source_compilation':[sys.executable,'-m','compileall','-q',str(P)],
        'prose_scan':[sys.executable,'tools/review_prose.py','--path',relative,'--output',prose.relative_to(REPO).as_posix()],
    }
    def run(pair):
        name,command=pair
        r=subprocess.run(command,cwd=REPO,capture_output=True,text=True,encoding='utf8')
        record={'command':command,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
        if name=='prose_scan' and prose.exists():
            scan=json.loads(prose.read_text(encoding='utf8'))
            record['files_scanned']=scan['files_scanned']
            record['manual_review_flags']=len(scan['flags'])
            record['stdout']='Full findings preserved in '+prose.name
        return name,record
    with ThreadPoolExecutor(max_workers=3) as pool:
        results=dict(pool.map(run,commands.items()))
    study=P/'study-validation-v3.json'
    broad=P/'repository-check-summary-v1.json'
    record={
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Owned contribution; same-team reproducibility and presentation review',
        'commands':results,
        'study_validation':{'path':study.name,'sha256':sha(study),'checks':304,'passed':json.loads(study.read_text(encoding='utf8'))['passed']},
        'broader_repository_verifier':json.loads(broad.read_text(encoding='utf8')),
        'python':sys.version,
        'authors':[{'model':'GPT-6 family; exact serving variant unavailable','harness':'Codex desktop collaboration','role':'root final check record'}],
        'scientific_confirmation':False,
    }
    record['passed']=all(r['returncode']==0 for r in results.values()) and record['study_validation']['passed']
    output.write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'passed':record['passed'],'commands':{n:r['returncode'] for n,r in results.items()},'prose_files':results['prose_scan'].get('files_scanned'),'prose_flags':results['prose_scan'].get('manual_review_flags'),'knowledge_output':results['knowledge_base']['stdout']}))
    assert record['passed']

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True)
    main(p.parse_args().tag)
