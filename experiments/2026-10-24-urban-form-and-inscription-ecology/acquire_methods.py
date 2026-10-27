"""Acquire a bounded primary-methods library to the checked D: data tree."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/methods')
SOURCES = [
    ('M-SMITH-2007', 'Michael E. Smith', 2007, 'Form and Meaning in the Earliest Cities: A New Approach to Ancient Urban Planning',
     'https://faculty.washington.edu/plape/citiesaut11/readings/Journal%20of%20Planning%20History-2007-Smith-3-47.pdf',
     'https://doi.org/10.1177/1538513206293713', 'smith2007.pdf', 'Published article; rights unresolved, local-only'),
    ('M-GREEN-2018', 'Adam S. Green', 2018, "Mohenjo-daro’s Small Public Structures: Heterarchy, Collective Action, and a Re-visitation of Old Interpretations with GIS and 3D Modelling",
     'https://www.repository.cam.ac.uk/bitstreams/4eb9f594-7cfa-431d-934c-adf6640a2f5c/download',
     'https://doi.org/10.1017/S0959774317000774', 'green2018-accepted.pdf', 'Author accepted manuscript; all rights reserved, local-only'),
    ('M-GREEN-2022', 'Adam S. Green', 2022, 'Of Revenue Without Rulers: Public Goods in the Egalitarian Cities of the Indus Civilization',
     'https://www.frontiersin.org/journals/political-science/articles/10.3389/fpos.2022.823071/pdf',
     'https://doi.org/10.3389/fpos.2022.823071', 'green2022.pdf', 'CC BY; acquired copy retained local-only'),
    ('M-BOEING-2019', 'Geoff Boeing', 2019, 'Urban spatial order: street network orientation, configuration, and entropy',
     'https://arxiv.org/pdf/1808.00600v4', 'https://doi.org/10.1007/s41109-019-0189-1',
     'boeing2019-v4.pdf', 'Author preprint; local-only'),
    ('M-BARTHELEMY-2026', 'Marc Barthelemy and Geoff Boeing', 2026, 'Geometry of Urban Order',
     'https://arxiv.org/pdf/2609.13029v1', 'https://arxiv.org/abs/2609.13029v1',
     'barthelemy-boeing2026-v1.pdf', 'Preprint v1, 11 September 2026; arXiv perpetual non-exclusive license; local-only'),
    ('M-SINGH-2017', 'Ajit Singh and colleagues', 2017, 'Counter-intuitive influence of Himalayan river morphodynamics on Indus Civilisation urban settlements',
     'https://www.nature.com/articles/s41467-017-01643-9.pdf', 'https://doi.org/10.1038/s41467-017-01643-9',
     'singh2017.pdf', 'CC BY 4.0; acquired copy retained local-only'),
]

def acquire(row):
    sid, author, year, title, url, stable, name, rights = row
    path = RAW / name
    record = dict(source_id=sid, author=author, year=year, title=title, url=stable,
                  acquisition_url=url, role='primary-methods-or-original-analysis', rights=rights,
                  retrieved_utc=datetime.now(timezone.utc).isoformat(), local_only=True)
    try:
        if not path.exists():
            request = urllib.request.Request(url, headers={'User-Agent':'IndusResearch/1.0 scholarly source review'})
            with urllib.request.urlopen(request, timeout=55) as response:
                payload = response.read()
            if not payload.startswith(b'%PDF'):
                raise ValueError('Response is not a PDF; source remains unacquired')
            path.write_bytes(payload)
        payload = path.read_bytes()
        import fitz
        doc = fitz.open(path)
        pages = [{'pdf_index':i, 'text':page.get_text()} for i, page in enumerate(doc)]
        text_path = path.with_suffix('.pages.json')
        if not text_path.exists():
            text_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding='utf-8')
        record.update(status='held', physical_path=str(path),
                      logical_path='data/raw/2026-10-24-urban-form-and-inscription-ecology/methods/'+name,
                      sha256=hashlib.sha256(payload).hexdigest(), bytes=len(payload), pages=len(doc),
                      extraction_physical_path=str(text_path))
    except Exception as exc:
        record.update(status='not-acquired', missing_reason=str(exc))
    return record

if __name__ == '__main__':
    if not Path('D:/').is_dir():
        raise RuntimeError('D: is unavailable')
    if not (ROOT.parents[1]/'data/raw').resolve().is_relative_to(Path('D:/projects/indus_valley_script')):
        raise RuntimeError('Historical raw path does not resolve to D:')
    RAW.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(acquire, SOURCES))
    out = ROOT/'methods-sources-v1.json'
    if out.exists():
        raise FileExistsError(out)
    out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps([{k:r.get(k) for k in ('source_id','status','bytes','pages','missing_reason')} for r in records], indent=2))
