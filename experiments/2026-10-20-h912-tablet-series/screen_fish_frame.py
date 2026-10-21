"""Post-outcome eligibility screen of the separately sourced Belcher plan frame."""
from pathlib import Path
from collections import defaultdict
import csv,json,hashlib,re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RAW=ROOT/'data/raw/2026-10-20-h912-tablet-series'
SOURCE=ROOT/'experiments/2026-10-20-h912-excavation-links/source-observations-v1.json'


def main():
    obs=json.loads(SOURCE.read_text(encoding='utf8'))
    fs=[]
    for run in ('discovery-v1','confirmation-v1'):
        fs.extend(json.loads(l) for l in (RAW/run/'faces.jsonl').read_text(encoding='utf8').splitlines())
    with (ROOT/'experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv').open(encoding='utf8') as f:
        table={r['code']:r for r in csv.DictReader(f,delimiter='\t')}
    output=[];local=[]
    for item in obs['plan_objects']:
        number=item['registration'].split('-')[-1]
        pattern=re.compile(r'(?<![A-Za-z0-9])H90[- /]?'+re.escape(number)+r'(?!\d)')
        found=[r for r in fs if pattern.search(r.get('metadata',{}).get('excavation-idno',''))]
        families={r['object_family_id'] for r in found}
        signs={str(s).zfill(3) for r in found for s in r['signs_reading_rtl']}
        entry={'registration':item['registration'],'source_context_key':item['context_key'],
               'source_object_grade':item['object_grade'],'source_location_grade':item['location_grade'],
               'matched_families':sorted(families),'cisi':sorted({r['source_cisi'] for r in found}),
               'recorded_faces':len(found),'has_plain_fish': '220' in signs,
               'has_fish_family':any(table.get(s,{}).get('base')=='B220' for s in signs),
               'has_plain_v':'700' in signs,'has_v_family':any(table.get(s,{}).get('base')=='B700' for s in signs),
               'exact_four_v_fish_face':any([str(s).zfill(3) for s in r['signs_reading_rtl']] in [['004','700','220'],['004','220','700']] for r in found),
               'physical_fish_lot_link':False}
        output.append(entry)
        local.extend({'source_registration':item['registration'],'row':r} for r in found)
    dest=RAW/'fish-frame-v1';dest.mkdir(exist_ok=False)
    with (dest/'faces.jsonl').open('x',encoding='utf8') as f:
        for r in local:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    result={'status':'post-outcome source worklist; no inferential test',
       'source_objects':len(output),'uniquely_joined_objects':sum(len(r['matched_families'])==1 for r in output),
       'recorded_faces':len(local),'objects_with_fish_family':sum(r['has_fish_family'] for r in output),
       'objects_with_plain_v':sum(r['has_plain_v'] for r in output),
       'objects_with_exact_four_v_fish':sum(r['exact_four_v_fish_face'] for r in output),
       'objects':output,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
       'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
       'scope':'Plan position supplies a same-area source association. Neither fish-sign presence nor absence identifies a fish deposit or translates a sign. No physical fish-lot link was provided by the source.'}
    with (HERE/'fish-frame-screen-v1.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('objects','source_sha256','code_sha256','scope')}))
    for r in output:print(r['registration'],r['cisi'],'fish',r['has_fish_family'],'V',r['has_plain_v'])


if __name__=='__main__':main()
