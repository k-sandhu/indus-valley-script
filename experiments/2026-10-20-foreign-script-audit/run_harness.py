"""Exercise shared loader using an owned, copied spending ledger."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from bench import shots
ledger=HERE/'private-spent.json'
original=json.loads((ROOT/'bench/spent.json').read_text())
# Explicitly restore the known October12 foreign-statistic exposure omitted by shared ledger.
original['splits']['foreign-sequence-historical-audit']={
 'seed':'2026-10-12-foreign-finds','input_sha256':shots.sha256(ROOT/'data/normalized/lipi_observed_faces.jsonl'),
 'spent_families':['foreign_sequence','object_type','site'], 'historical':True,
 'source':'experiments/2026-10-12-published-claim-tests/foreign-finds/REPORT.md','reads':[]}
with ledger.open('x',encoding='utf-8') as f: json.dump(original,f,indent=2)
split=HERE/'round.json'
shots.create(ROOT/'data/normalized/lipi_observed_faces.jsonl',split,'2026-10-20-foreign-script-audit',ledger)
shots.register(split,'source-audit',HERE/'PREDICTIONS.json',ledger)
shots.freeze(split,'source-audit',[HERE/'PROTOCOL.md',HERE/'frame.json',HERE/'annotations.json',HERE/'audit.py'],ledger)
discovery,de=shots.load_half(split,'discovery','source-audit',ledger,allow_spent=True)
confirmation,ce=shots.load_half(split,'confirmation','source-audit',ledger,allow_spent=True)
with (HERE/'spent-access.json').open('x',encoding='utf-8') as f:
 json.dump({'schema_version':'1.0','task':'shots','synthetic':False,'discovery_faces':len(discovery),'confirmation_faces':len(confirmation),'access':ce,'population_freshness':'spent independently of loader event; October12 analysis examined these objects'},f,indent=2)
print(json.dumps(ce,indent=2))
