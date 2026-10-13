"""Check witness integrity, lineage, IDs and bounded-census declarations."""
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-11-societal-persistence/literature'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    target=HERE/'source-checks-v1.json'
    if target.exists():
        raise FileExistsError(target)
    sources=json.loads((HERE/'SOURCES.json').read_text('utf-8'))
    observations=json.loads((HERE/'OBSERVATIONS.json').read_text('utf-8'))['observations']
    comparisons=json.loads((HERE/'COMPARISONS.json').read_text('utf-8'))['comparisons']
    checks=[]

    def check(ident, passed, detail):
        checks.append(dict(check_id=ident,passed=bool(passed),detail=detail))

    rows=sources['sources']; index={x['source_id']:x for x in rows}
    check('census-ids',len(rows)==len(index)==28,'28 unique records')
    check('primary-count',sum(x['selected_primary_work'] for x in rows)==25,'25 selected primary works;3 limited leads')
    check('lead-scope',all(not index[x]['selected_primary_work'] for x in ['L14','L15','L25']),'Blocked article, publisher description and unavailable book remain outside primary count')
    check('script-lineage',sources['scope']['script_sha256']==sha(HERE/'build_ledger.py'),'Declared ledger-builder version')
    seen=set(); raw_paths=set()
    for row in rows:
        check(row['source_id']+'-depth',bool(row['inspected_scope']) and bool(row['supporting_loci']),'Reading depth and loci explicitly declared')
        check(row['source_id']+'-primary-support',not row['selected_primary_work'] or any(x['role']!='failed_or_challenge_witness' for x in row['witnesses']),'A selected source has an article witness rather than only a challenge')
        for art in row['witnesses']+row['derivatives']:
            path=ROOT/art['path'];raw_paths.add(art['path'])
            if art['path'] in seen: continue
            seen.add(art['path'])
            check(art['path']+'-hash',path.exists() and sha(path)==art['sha256'] and path.stat().st_size==art['bytes'],'Retained bytes and SHA256')
            check(art['path']+'-rights',art['redistribution']=='local-only','Original publication or mechanical derivative is local-only')
        for attempt in row['acquisition_attempts']:
            p=ROOT/attempt['acquisition_manifest']
            check(row['source_id']+'-'+p.name+'-lineage',sha(p)==attempt['acquisition_manifest_sha256'],'Retained acquisition metadata')
    for row in observations:
        source=index[row['source_id']]
        admissible={x['path'] for x in source['witnesses'] if x['role']!='failed_or_challenge_witness'}
        check(row['observation_id']+'-join',source['selected_primary_work'] and bool(row['locator']) and bool(row['supporting_witness_paths']) and set(row['supporting_witness_paths'])<=admissible,'Source/locus joins exclude failed or challenge-only files')
    obs_ids={x['observation_id'] for x in observations}
    check('observation-ids',len(obs_ids)==len(observations)==45,'45 unique observations')
    for row in comparisons:
        check(row['comparison_id']+'-join',bool(row['source_observations']) and set(row['source_observations'])<=obs_ids,'Proposed comparison links to source observations')
        check(row['comparison_id']+'-falsifier',bool(row['rejects_this_account']) and bool(row['unresolved_when']) and bool(row['rivals']),'Rejection, unresolved outcome and alternatives declared')
    for key in ['L09-smith2021','L10-lawrence2025','L11-pichancourt2025']:
        old=json.loads((RAW/(key+'-xml-extraction-v1.json')).read_text('utf-8'))
        new=json.loads((RAW/(key+'-xml-extraction-v2.json')).read_text('utf-8'))
        check(key+'-metadata-amendment',old['paragraphs']==new['paragraphs'] and len(new['authors'])>0 and new['prior_extraction_sha256']==sha(RAW/(key+'-xml-extraction-v1.json')),'Metadata amendment preserves all paragraphs and links v1')
        parent=ROOT/new['parent_path'];root=ET.parse(parent).getroot()
        title=''.join(root.find('.//article-title').itertext()).strip()
        check(key+'-xml-title',title==new['title'] and sha(parent)==new['parent_sha256'],'Readable primary XML title and parent bytes')
    edition=index['L17']['edition_note']
    check('sraffa-edition','1963' in edition and 'Vora' in edition and 'Bombay' in edition,'Original1960 work and inspected1963 edition distinguished')
    check('ostrom-lecture-identity',index['L23']['title'].endswith('Complex Economic Systems'),'Official2009 lecture identity, separate from2010 article version')
    check('priss-scoped-followup','342' in index['L28']['inspected_scope'] and '345' in index['L28']['inspected_scope'] and 'No complete article' in index['L28']['inspected_scope'],'Follow-up reading remains selected')
    payload=b'\0'.join(x.encode('utf-8') for x in sorted(raw_paths))+b'\0'
    result=subprocess.run(['git','check-ignore','--no-index','-z','--stdin'],input=payload,cwd=ROOT,capture_output=True)
    ignored=set(x.decode('utf-8') for x in result.stdout.split(b'\0') if x)
    check('raw-ignore',result.returncode in [0,1] and raw_paths<=ignored,'Every ledger publication/derivative path is Git-ignored; NUL-delimited path comparison')
    report=dict(status='pass' if all(x['passed'] for x in checks) else 'fail',
        scope='Source integrity, lineage and selected-reading declarations; not independent validation of published data or claims',
        checks=len(checks),passed=sum(x['passed'] for x in checks),
        input_hashes={f:sha(HERE/f) for f in ['SOURCES.json','OBSERVATIONS.json','COMPARISONS.json','QUERY-LOG.json']},
        checker_sha256=sha(Path(__file__)),results=checks)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['status','checks','passed']}))
    if report['status']!='pass':
        print(json.dumps([x for x in checks if not x['passed']],ensure_ascii=False,indent=2))
        raise SystemExit(1)


if __name__=='__main__':main()
