"""Alternate primary archive routes after preserved challenge/timeout responses."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import capture_sources as base

PLAN = [
 ('L09-smith2021', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8157985/fullTextXML'),
 ('L10-lawrence2025', 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12036995/fullTextXML'),
 ('L11-pichancourt2025', 'https://peerj.com/articles/18938.pdf'),
 ('L15-halstead1989', 'https://assets.cambridge.org/97805216/11923/excerpt/9780521611923_excerpt.pdf'),
 ('L25-tainter1988', 'https://assets.cambridge.org/97805213/86739/excerpt/9780521386739_excerpt.pdf'),
]

if __name__=='__main__':
    out=base.OUT/'capture-v2.json'
    if out.exists(): raise FileExistsError(str(out))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows=list(pool.map(lambda item:base.capture(item,'capture-v2'),PLAN))
    out.write_text(json.dumps(dict(script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), helper_sha256=hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest(), reason='Europe PMC primary-archive XML and PeerJ publisher PDF replace browser challenges; Cambridge requests repeat after transport timeouts.', attempts=rows),ensure_ascii=False,indent=2),encoding='utf-8')
    for row in rows:
        print(row['id'],row.get('status_code'),row.get('format'),row.get('bytes'),row.get('error',''))
