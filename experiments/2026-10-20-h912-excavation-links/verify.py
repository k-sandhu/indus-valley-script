"""Author integrity and accounting checks, independent of the result builder."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);args=ap.parse_args()
    out=ROOT/args.out
    if out.exists():raise FileExistsError(out)
    checks=[]
    def check(name,ok):checks.append({"name":name,"pass":bool(ok)})
    def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
    s=json.loads((OWN/'run-v1/summary.json').read_text(encoding='utf-8'))
    p=json.loads((OWN/'run-v1/provenance.json').read_text(encoding='utf-8'))
    j=json.loads((OWN/'run-v1/belcher-plan-joins.json').read_text(encoding='utf-8'))
    rows=list(csv.DictReader((OWN/'run-v1/dispositions.csv').open(encoding='utf-8')))
    check('72 disposition records',len(rows)==s['disposition_rows']==72)
    check('no direct physical content joins',all(x['direct_container_or_fish_lot_join']=='False' for x in rows))
    check('fourteen plan joins',len(j)==14)
    check('fourteen distinct plan registrations',len({x['registration'] for x in j})==14)
    check('fourteen distinct export families',len({x['family'] for x in j})==14)
    check('twenty-one plan faces',sum(x['face_count'] for x in j)==21)
    check('every plan record retains two grades',all(x['object_grade'] and x['location_grade'] for x in j))
    check('no plan object has a fish lot',all(x['fish_unit'] is None for x in j))
    check('depth remains range',s['primary_depth_ft_below_surface']==[4,7] and s['point_measurement_source_found'] is False)
    check('derivative point equals midpoint',s['depth_midpoint_compatibility'] is True and s['export_depth_ft']==-5.5)
    check('stratum conflict retained',s['stratum_conflict']=={'overview':'IV','8650q_specialist_chapter':'III'})
    check('no closed deposit or identity merges',s['closed_deposit_documented'] is False and s['physical_merges_performed']==0)
    check('fourteen suffix records',s['suffix_records']==14)
    check('twelve broader associations',s['broader_registered_associations']==12)
    check('sixteen export prefix families',s['export_prefix_families']==16 and s['export_prefix_faces']==25)
    check('H912 H1191 exact-reference collision',set(s['shared_exact_source_references']['8650c448'])=={'1793','4056'})
    check('no real confirmation read',s['empirical_bench_reads']==0)
    for src in [p['corpus'],*p['sources']]:
        path=ROOT/src['path'];check('hash '+src['path'],path.exists() and sha(path)==src['sha256'])
    check('protocol frozen',sha(OWN/'PROTOCOL.md')==p['protocol_sha256']==(OWN/'PROTOCOL.sha256').read_text().split()[0])
    check('observations unchanged',sha(OWN/'source-observations-v1.json')==p['observations_sha256'])
    check('builder unchanged',sha(OWN/'build.py')==p['code_sha256'])
    for name in ['dispositions.csv','summary.json','belcher-plan-joins.json','provenance.json']:
        check('byte-identical replay '+name,sha(OWN/'run-v1'/name)==sha(OWN/'replay-v1'/name))
    corpus=[json.loads(x) for x in (ROOT/p['corpus']['path']).read_text(encoding='utf-8').splitlines()]
    for item in j:
        pat=re.compile(re.escape(item['registration'])+r'(?:\D|$)')
        found=[x for x in corpus if pat.search(x['metadata']['excavation-idno'])]
        check('independent exact join '+item['registration'],{x['object_family_id'] for x in found}=={item['family']} and {x['source_cisi'] for x in found}=={item['cisi']})
    b=json.loads((OWN/'shots-synthetic-v1.json').read_text())
    check('synthetic bench passed',b['task']=='shots' and b['synthetic'] is True and b['pass'] is True)
    result={'tier':'submitted; author integrity check','checks':checks,'passed':sum(x['pass'] for x in checks),'failed':sum(not x['pass'] for x in checks)}
    with out.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
    print(json.dumps({k:result[k] for k in ['passed','failed','tier']}))
    raise SystemExit(bool(result['failed']))


if __name__=='__main__':main()
