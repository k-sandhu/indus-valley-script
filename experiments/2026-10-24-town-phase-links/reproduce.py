import json, hashlib
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[2]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-town-phase-links')
PKG=Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--out',default='run-v1'); args=parser.parse_args()
    out=PKG/args.out
    out.mkdir(exist_ok=False)
    sources=json.loads((RAW/'sources.json').read_text(encoding='utf-8'))
    relations=json.loads((RAW/'relations.json').read_text(encoding='utf-8'))
    counts={}
    for source in sources:
        p=Path(source['physical_path']); d=fitz.open(p)
        source['sha256']=sha(p); source['bytes']=p.stat().st_size; source['pdf_pages']=len(d)
        for i in source['pages_read_zero_based']:
            (RAW/f"{source['id']}-{i}-text.txt").write_text(d[i].get_text(),encoding='utf-8')
        counts[source['id']]=len(source['pages_read_zero_based'])
    assert sum(counts.values())==24
    for row in relations:
        assert row['source'] in counts
        s=next(s for s in sources if s['id']==row['source'])
        assert set(row['pages_zero_based'])<=set(s['pages_read_zero_based'])
        assert row['construction_sample_join'] is False
        assert row['required_evidence'] and row['relation'] and row['episode']
    manifest={'sources':sources,'handling':'Source scans, rendered pages, OCR and relation records remain local-only on D:. Existing sources reused without alteration.','new_acquisitions':0}
    (PKG/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    result={'schema_version':'1.0','status':'author-checked','sources':len(sources),'pages_read':counts,'relations':len(relations),'construction_sample_joins':sum(r['construction_sample_join'] for r in relations),'new_radiocarbon_determinations':0,'new_bearings':0,'relations_sha256':sha(RAW/'relations.json'),'sources_sha256':sha(RAW/'sources.json'),'code_sha256':sha(Path(__file__)),'protocol_sha256':sha(PKG/'PROTOCOL.md'),'local_payloads':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(RAW.iterdir()) if p.is_file()]}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='local_payloads'},indent=2))
if __name__=='__main__':main()
