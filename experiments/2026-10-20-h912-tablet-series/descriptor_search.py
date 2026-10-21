"""Post-outcome source worklist search; no new confirmation or p-value."""
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RAW=ROOT/'data/raw/2026-10-20-h912-tablet-series'


def distance(x,y):
    old=list(range(len(y)+1))
    for i,a in enumerate(x,1):
        new=[i]
        for j,b in enumerate(y,1):
            new.append(min(new[-1]+1,old[j]+1,old[j-1]+(a!=b)))
        old=new
    return old[-1]


def main():
    paths=[RAW/run/'faces.jsonl' for run in ('discovery-v1','confirmation-v1')]
    rows=[json.loads(line) for p in paths for line in p.read_text(encoding='utf8').splitlines()]
    core={'H-302','H-912','H-1191','H-1192'}
    targets=[r for r in rows if r['source_cisi'] in core and len(r['signs_reading_rtl'])==5]
    eligible=[r for r in rows if r['clean_rtl_singleline'] and r['source_cisi'] not in core]
    found=[]
    for row in eligible:
        d=min(distance(row['signs_reading_rtl'],target['signs_reading_rtl']) for target in targets)
        if d<=1:found.append({'source_cisi':row['source_cisi'],'record_id':row['record_id'],'object_type':row['object_type'],'distance':d})
    result={'status':'post-outcome source worklist search','method':'Complete fine-code longer faces of the four core entries, searched elsewhere for edit distance at most one; insertion, deletion and substitution each cost one.','eligible_other_faces':len(eligible),'core_target_faces':len(targets),'matches':found,'interpretation':'No additional exact or one-edit carrier is identified by this search. This does not exclude other kinds of relatedness or objects missing from the export.','source_hashes':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with (HERE/'descriptor-search-v1.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'eligible':len(eligible),'matches':len(found)}))


if __name__=='__main__':main()
