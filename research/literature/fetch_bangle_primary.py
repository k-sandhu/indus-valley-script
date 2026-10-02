import json
from concurrent.futures import ThreadPoolExecutor
from fetch_sources import ROOT,retrieve
items=[
 ('franke_govscan_74331','identity pending','Government-hosted primary catalogue/craft report; inspect title before use','https://ignca.gov.in/Asi_data/74331.pdf'),
 ('blackman_vidale1992_bangles','1992','Smithsonian author repository primary material study','https://repository.si.edu/bitstreams/64271be1-5d78-4196-8a87-f1ea1669c777/download'),
 ('kenoyer2020_origin','2020','Excavation-author primary chapter; inspected pagination required','https://www.harappa.com/sites/default/files/pdf/Kenoyer2020%20Origin%20of%20Indus%20Script-2.pdf'),
]
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(retrieve,items))
p=ROOT/'source_retrieval_log.json';old=json.loads(p.read_text(encoding='utf-8'))
p.write_text(json.dumps(old+rows,indent=2),encoding='utf-8')
for r in rows:print(json.dumps(r))
