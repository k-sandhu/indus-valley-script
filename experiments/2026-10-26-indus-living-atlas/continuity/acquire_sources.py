"""Preserve primary witnesses locally; never overwrite a previous endpoint."""
from __future__ import annotations
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/continuity')
JOBS = [
    ('G2012', 'giosan2012.xml', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3387054/fullTextXML', 'xml'),
    ('S2021', 'suryanarayan2021.xml', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7829615/fullTextXML', 'xml'),
    ('N2020', 'neogi2020-accepted.pdf', 'https://api.repository.cam.ac.uk/server/api/core/bitstreams/8239b10a-1dd9-4e78-91b5-d27e5da823b6/content', 'pdf'),
    ('K2010', 'kenoyer2010.pdf', 'https://www.harappa.com/sites/default/files/pdf/Kenoyer%202010%20Measuring%20the%20Harappan%20World.pdf', 'pdf'),
    ('KM2004', 'kenoyer-meadow2004.pdf', 'https://www.harappa.com/sites/default/files/pdf/Kenoyer2004_Fifty-five%20years%20of%20Archaeological%20Research%20in%20P.pdf', 'pdf'),
    ('SP2013', 'singh2013.html', 'https://www.researchgate.net/publication/283348204_Recent_Excavations_at_Alamgirpur_Meerut_District_A_Preliminary_Report', 'html'),
]
REUSED = [
    ('B2015', 'data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf'),
    ('MK1997', 'data/raw/2026-10-11-societal-persistence/evidence/acquisition-v1/meadow-kenoyer1997.pdf'),
    ('GP2018', 'data/raw/2026-10-11-societal-persistence/evidence/acquisition-v4/green-petrie2018-full.xml'),
    ('PB2017', 'data/raw/2026-10-25-crop-continuity/petrie-bates-2017.pdf'),
    ('M1943', 'research/literature/sources/mackay_1943_chandaro.pdf'),
]

def facts(path: Path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'physical_path': str(path.resolve()),
            'logical_path': str(path.resolve().relative_to(Path('D:/projects/indus_valley_script'))).replace('\\', '/')}

def acquire(job):
    sid, name, url, kind = job
    path = RAW / name
    row = {'source_id': sid, 'url': url, 'retrieved_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
           'handling': 'local-only', 'rights_status': 'rights-unverified'}
    if path.exists():
        raise FileExistsError(path)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'IndusResearchSourceReview/1.0'})
        with urllib.request.urlopen(req, timeout=45) as response:
            data = response.read()
            row.update(http_status=response.status, content_type=response.headers.get('Content-Type'), final_url=response.url)
        path.write_bytes(data)
        row.update(facts(path))
        valid = data.startswith(b'%PDF') if kind == 'pdf' else (b'<article' in data if kind == 'xml' else b'<html' in data.lower())
        row['status'] = 'acquired' if valid else 'rejected-format'
    except Exception as e:
        row.update(status='failed', error=f'{type(e).__name__}: {e}')
    return row

def main():
    if not RAW.parents[2].is_dir() or (ROOT / 'data/raw').resolve() != RAW.parents[1]:
        raise RuntimeError('D: storage or data/raw junction does not match')
    RAW.mkdir(parents=True, exist_ok=True)
    output = HERE / 'acquisition-v1.json'
    if output.exists():
        raise FileExistsError(output)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(acquire, JOBS))
    for sid, logical in REUSED:
        p = ROOT / logical
        rows.append({'source_id': sid, 'status': 'reused-existing-witness', 'handling': 'local-only',
                     'rights_status': 'rights-unverified', **facts(p)})
    payload = {'schema_version': '1.0', 'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'raw_logical_root': 'data/raw/2026-10-26-indus-living-atlas/continuity/',
               'raw_physical_root': str(RAW), 'acquisitions': rows}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps([{'source_id': r['source_id'], 'status': r['status'], 'bytes': r.get('bytes')} for r in rows], indent=2))

if __name__ == '__main__':
    main()
