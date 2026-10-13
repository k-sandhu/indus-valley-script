"""Check coordinator source identities, witness pins, derivatives and disposition."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=HERE/'source-checks-v1.json'
    if out.exists():raise SystemExit('Source checks exist; no overwrite.')
    source_path=HERE/'sources-v2.json';obs_path=HERE/'observations-v2.json'
    sources=json.loads(source_path.read_text('utf-8'))['sources']
    observations=json.loads(obs_path.read_text('utf-8'))['observations']
    checks=[];witnesses=set()

    def check(name,condition):checks.append({'check':name,'passed':bool(condition)})

    check('Three distinct primary controls',len(sources)==len({s['source_id'] for s in sources})==3)
    check('Eight distinct observations',len(observations)==len({o['observation_id'] for o in observations})==8)
    source_ids={s['source_id'] for s in sources}
    for o in observations:
        check(o['observation_id']+' source and scope',o['source_id'] in source_ids and bool(o['locus']) and bool(o['inference_limit']))
    for source in sources:
        check(source['source_id']+' recorded reading and rights',bool(source['reading_scope']) and source['redistribution']=='local-only' and bool(source['rights_status']))
        for row in source['witnesses']+source.get('derivatives',[]):
            path=ROOT/row['path'];witnesses.add(row['path'])
            check('Witness pin '+row['path'],path.is_file() and path.stat().st_size==row['bytes'] and sha(path)==row['sha256'])
            if 'parent_sha256' in row:
                parent=ROOT/row['parent_path'] if 'parent_path' in row else ROOT/'data/raw/2026-10-12-transmission-hypothesis/coordinator/population-v1/narasimhan2019-author.pdf'
                check('Derivative parent '+row['path'],sha(parent)==row['parent_sha256'])
    population_pdf=ROOT/'data/raw/2026-10-12-transmission-hypothesis/coordinator/population-v1/narasimhan2019-author.pdf'
    check('Population witness is actual PDF',population_pdf.read_bytes().startswith(b'%PDF'))
    excluded=sources[0]['failed_or_excluded_routes'][0]
    challenge=ROOT/excluded['path'];witnesses.add(excluded['path'])
    check('PMC challenge excluded and pinned',excluded['challenge_detected'] and sha(challenge)==excluded['sha256'])
    body=(ROOT/'data/raw/2026-10-12-transmission-hypothesis/coordinator/method-v1/diachenko2023-body-v1.txt').read_text('utf-8')
    check('Method work identity in normal HTML',all(s in body for s in ['Convergent Evolution','Diachenko','Creative Commons']))
    text=(ROOT/'data/raw/2026-10-12-transmission-hypothesis/coordinator/method-v1/shennan2020-metadata.html').read_text('utf-8')
    check('Shennan institutional identity and year',all(s in text for s in ['Shennan','2020','978-3-030-46126-3_15']))
    response=subprocess.run(['git','check-ignore','--no-index','-z','--stdin'],cwd=ROOT,
                            input=b'\0'.join(p.encode('utf-8') for p in sorted(witnesses))+b'\0',capture_output=True)
    ignored={p.decode('utf-8').replace('\\','/') for p in response.stdout.split(b'\0') if p}
    check('All source witnesses and derivatives ignored',response.returncode==0 and ignored==witnesses)
    value={'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Source identity, recorded reading scope and exact-byte disposition. No genetic or archaeological reanalysis.',
           'input_sha256':{'sources-v2.json':sha(source_path),'observations-v2.json':sha(obs_path),'check_sources.py':sha(Path(__file__))},
           'checks_passed':sum(row['passed'] for row in checks),'checks_failed':sum(not row['passed'] for row in checks),'checks':checks}
    with out.open('x',encoding='utf-8') as stream:json.dump(value,stream,indent=2);stream.write('\n')
    print(json.dumps({'checks_passed':value['checks_passed'],'checks_failed':value['checks_failed'],'witness_paths':len(witnesses)}))
    if value['checks_failed']:raise SystemExit(1)


if __name__=='__main__':main()
