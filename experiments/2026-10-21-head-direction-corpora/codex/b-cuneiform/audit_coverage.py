"""Audit physical seal and impression coverage without changing corpus records.

Usage: python -I audit_coverage.py --ur3-archive ZIP --oakk-archive ZIP
  --cdli-cat CSV --records-dir DIR --out NEW_JSON
"""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from normalize_cuneiform import safe_archive, oracc_groups, flatten


def main():
    ap=argparse.ArgumentParser()
    for key in ('ur3-archive','oakk-archive','cdli-cat','records-dir','out'):
        ap.add_argument('--'+key,required=True,type=Path)
    a=ap.parse_args(); rows=[]
    for name in ('sux-ur3','akk-sargonic','sux-sargonic','cuneiform-ur3-akkadian','cuneiform-language-unresolved'):
        rows.extend(json.loads(l) for l in (a.records_dir/(name+'.jsonl')).open(encoding='utf-8'))
    represented={r['object_id'] for r in rows}
    physical=[]
    with a.cdli_cat.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            if r['period'].startswith('Old Akkadian') and r['object_type']=='seal (not impression)': physical.append('P'+r['id_text'].zfill(6))
    source_coverage={}
    for source,path in [('sumerian-ur3-v1',a.ur3_archive),('oracc-oakk',a.oakk_archive)]:
        archive=safe_archive(path)
        cat=json.loads(archive.read(next(n for n in archive.namelist() if n.endswith('/catalogue.json'))))['members']
        entries={Path(n).stem:n for n in archive.namelist() if '/corpusjson/' in n and n.endswith('.json')}
        source_ids={r['object_id'] for r in rows if r['source']==source}
        missing=[]; body_sealings=[]
        for identity,info in cat.items():
            kind=info.get('object_type','').lower()
            if 'seal' not in kind or identity not in entries: continue
            if identity not in source_ids:
                data=json.loads(archive.read(entries[identity]))
                words=[n for n in flatten(data.get('cdl',[])) if n.get('node')=='l']
                item=dict(object_id=identity,object_type=kind,word_count=len(words),groups=len(oracc_groups(data,info)))
                if 'not impression' in kind or kind=='cylinder seal': missing.append(item)
                else: body_sealings.append(item)
        source_coverage[source]=dict(missing_physical_seals=missing,body_sealings_without_seal_section=body_sealings)
    identities=Counter(r['object_id'] for r in rows if r['period']=='Old Akkadian')
    both=[identity for identity,n in identities.items() if len({r['source'] for r in rows if r['period']=='Old Akkadian' and r['object_id']==identity})>1]
    result=dict(cdli_old_akkadian_physical_seals=len(physical),cdli_physical_seals_represented=sum(p in represented for p in physical),
        cdli_physical_seals_missing=[p for p in physical if p not in represented],oracc=source_coverage,
        old_akkadian_objects_with_both_editions=both)
    a.out.write_text(json.dumps(result,indent=1)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__': main()
