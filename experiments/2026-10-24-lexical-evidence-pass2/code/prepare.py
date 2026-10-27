from collections import defaultdict
from datetime import datetime, timezone
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PKG=Path(__file__).resolve().parents[1]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-lexical-evidence-pass2')
OLD=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-lexical-extraction-extension')
SEED='lexical-evidence-pass2-2026-10-24-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def rows(p):
 with p.open(encoding='utf8') as f:return [json.loads(l) for l in f]
def save(p,x):
 with p.open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
 source=OLD/'run-v1/winslow-entries.jsonl';records=rows(source);index={r['entry_id']:r for r in records}
 audit=read(OLD/'increment-audit-v1/candidate-audit.json')
 folded={r['entry_id'] for r in audit if any(c['folding_dependent'] for c in r['candidates'])}
 known=[r for r in records if (r['translit_plain'],r['page']) in [('murukkampū',883),('murukkañcettal',501)]]
 excluded=folded|{r['entry_id'] for r in known}
 rank=lambda r:hashlib.sha256((SEED+'|'+r['entry_id']).encode()).hexdigest()
 exact=sorted([r for r in records if r['entry_id'] not in excluded and r['increment_candidates']],key=rank)[:6]
 conflicts=sorted([r for r in records if r['boundary_review_status']=='conflicting_cross_source_boundaries'],key=rank)[:6]
 selected=[('folding_dependent',index[k]) for k in sorted(folded)]+[('exact_candidate',r) for r in exact]+[('boundary_conflict',r) for r in conflicts]+[('known_increment',r) for r in known]
 assert len(selected)==len({r['entry_id'] for _,r in selected})==16
 payload=[dict(case_id=f'L{i:02d}',stratum=s,entry=r) for i,(s,r) in enumerate(selected,1)]
 save(RAW/'case-selection-v1.json',payload)
 save(PKG/'FREEZE-v1.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),seed=SEED,
  protocol_sha256=sha(PKG/'PROTOCOL.md'),selector_sha256=sha(Path(__file__)),
  input_sha256=sha(source),audit_sha256=sha(OLD/'increment-audit-v1/candidate-audit.json'),
  selection_sha256=sha(RAW/'case-selection-v1.json'),selected=[dict(case_id=x['case_id'],stratum=x['stratum'],entry_id=x['entry']['entry_id'],winslow_page=x['entry']['page']) for x in payload]))
 print(json.dumps([dict(case_id=x['case_id'],stratum=x['stratum'],form=x['entry']['translit_plain'],root=x['entry'].get('root'),members=x['entry']['members'],candidates=x['entry']['increment_candidates']) for x in payload],ensure_ascii=False))
if __name__=='__main__':main()
