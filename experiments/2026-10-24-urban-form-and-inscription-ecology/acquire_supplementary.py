"""Record alternate acquisition routes without changing the first acquisition log."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import urllib.request
import fitz

ROOT = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-urban-form-and-inscription-ecology/methods')
items = [
    dict(source_id='M-SINGH-2017-HARP', author='Ajit Singh and colleagues', year=2017,
         title='Counter-intuitive influence of Himalayan river morphodynamics on Indus Civilisation urban settlements',
         url='https://doi.org/10.1038/s41467-017-01643-9',
         acquisition_url='https://www.harappa.com/sites/default/files/pdf/himalayan-river-influence.pdf',
         filename='singh2017-harappa.pdf', rights='CC BY 4.0; local-only copy',
         note='Alternate author-hosted route after the publisher PDF URL returned non-PDF content'),
    dict(source_id='M-VIDALE-2018', author='Massimo Vidale', year=2018,
         title='Heterarchic Powers in the Ancient Indus Cities',
         url='https://iris.unive.it/retrieve/39773d22-47c4-4b09-85a8-9111b50ccfd1/18-17-PB.pdf',
         acquisition_url='https://iris.unive.it/retrieve/39773d22-47c4-4b09-85a8-9111b50ccfd1/18-17-PB.pdf',
         filename='vidale2018-journal-issue.pdf', rights='Rights unresolved; local-only',
         note='Journal of Asian Civilizations 41(2), printed pp. 1-42; issue dated December 2018, article mentions a January 2019 conversation; whole issue PDF is 196 pages'),
]
records=[]
for source in items:
    record = dict(source, local_only=True, retrieved_utc=datetime.now(timezone.utc).isoformat(), role='primary-original-analysis')
    path=RAW/source['filename']
    try:
        if not path.exists():
            req=urllib.request.Request(source['acquisition_url'], headers={'User-Agent':'Mozilla/5.0 (research source review)'})
            with urllib.request.urlopen(req, timeout=55) as response:
                payload=response.read()
            if not payload.startswith(b'%PDF'):
                raise ValueError('Non-PDF response')
            path.write_bytes(payload)
        data=path.read_bytes()
        doc=fitz.open(path)
        out=path.with_suffix('.pages.json')
        if not out.exists():
            out.write_text(json.dumps([dict(pdf_index=i,text=p.get_text()) for i,p in enumerate(doc)],ensure_ascii=False),encoding='utf-8')
        record.update(status='held',physical_path=str(path),logical_path='data/raw/2026-10-24-urban-form-and-inscription-ecology/methods/'+path.name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),pages=len(doc))
    except Exception as exc:
        record.update(status='not-acquired',missing_reason=str(exc))
    records.append(record)
records.extend([
 dict(source_id='M-LAWRENCE-2025',author='Dan Lawrence and colleagues',year=2025,title='Housing inequality and settlement persistence are associated across the archaeological record',url='https://pmc.ncbi.nlm.nih.gov/articles/PMC12036995/',doi='10.1073/pnas.2400696122',status='web-full-text-inspected',locator='Significance; Settlement Persistence and Material Inequality; Discussion',rights='CC BY 4.0',local_only=True,retrieved_date='2026-10-24'),
 dict(source_id='M-RAMZY-2016',author='Nelly Shafik Ramzy',year=2016,title='Morphological logic in historical settlements: Space syntax analyses of residential districts at Mohenjo-Daro, Kahun and Ur',url='https://doi.org/10.1057/udi.2015.11',status='author-abstract-inspected',locator='Author university publication record, Abstract',access_url='https://bu.edu.eg/staff/nilly.shafiq-publications/46979',rights='Rights unresolved; no source copy redistributed',local_only=True,retrieved_date='2026-10-24',missing_reason='Full article not acquired; methodological comparison restricted to author abstract'),
])
output=ROOT/'methods-sources-supplement-v1.json'
if output.exists():
    raise FileExistsError(output)
output.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([dict(source_id=r['source_id'],status=r['status'],bytes=r.get('bytes')) for r in records],indent=2))
