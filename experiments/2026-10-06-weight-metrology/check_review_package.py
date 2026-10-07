"""Final integrity, source metadata and local-link checks; no shared writes."""
import argparse
import json
import re
import subprocess
import sys
from parse_catalogue import ROOT, RUN, sha, write_json

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='experiments/2026-10-06-weight-metrology/review-response-final-checks.json');args=ap.parse_args()
    out=ROOT/args.output
    if out.exists():raise FileExistsError(out)
    run=RUN/'runs/2026-10-07-review-response-v4';m=json.loads((run/'manifest.json').read_text());c=json.loads((run/'completion.json').read_text())
    assert m['protocol_sha256']==sha(RUN/'PROTOCOL.md'),'protocol'
    assert all(sha(RUN/n)==h for n,h in m['code_hashes'].items()),'code hashes'
    assert all(sha(run/n)==h for n,h in c['output_hashes'].items()),'output hashes'
    frozen=json.loads((RUN/'history/2026-10-07-before-review-response/frozen-hashes.json').read_text())
    assert all(sha(RUN/'runs/2026-10-06-main'/n)==h for n,h in frozen.items()),'frozen hashes'
    source=json.loads((RUN/'sources.json').read_text(encoding='utf8'));by={r['id']:r for r in source['sources']}
    assert by['lago_cardarelli_ialongo2024']['authors'][1]=='Lorenzo Cardarelli','Cardarelli'
    assert by['ascalone2022']['contributors'][0]['name']=='Jan Tavernier','contribution'
    assert '589–598' in by['hemmy1931']['venue'],'Hemmy pages'
    assert '113/120' in by['hemmy1931']['established'],'Hemmy counts'
    assert '0.89' in by['vahia_yadav2007']['established'],'Vahia base'
    assert by['bibby1970']['title']=='»… EFTER DILMUN NORM«','Bibby title'
    assert all(x in by for x in ['ascalone2018c','ascalone2021a','hemmy1938b','hemmy1943','hendrickx_baudot1972'])
    links=[]
    for name in ['README.md','REPORT.md','RETROSPECTIVE.md','PROTOCOL.md']:
        t=(RUN/name).read_text(encoding='utf8')
        for target in re.findall(r'\]\(([^)]+)\)',t):
            if target.startswith(('https:','http:','#')):continue
            assert (RUN/target.split('#')[0]).exists(),(name,target);links.append((name,target))
    files=[]
    for folder in [run,RUN/'summary-tables-review-response']:
        for f in folder.rglob('*.json'):json.loads(f.read_text(encoding='utf8'));files.append(f)
    for name in ['sources.json','registry-entry.json','parser-validation-review-response.json','review-response-verification.json','review-response-reproduction.json']:
        json.loads((RUN/name).read_text(encoding='utf8'));files.append(RUN/name)
    rows=json.loads((ROOT/m['rows_path']).read_text(encoding='utf8'))
    old=json.loads((ROOT/'data/raw/2026-10-06-weight-metrology/extraction-v6/catalogue-rows.json').read_text(encoding='utf8'))
    assert [r['cat'] for r in rows if r['mass_g']!=old[r['cat']-1]['mass_g']]==[1201,1730]
    assert [r['cat'] for r in rows if r['primary_eligible']]==[r['cat'] for r in old if r['primary_eligible']]
    prose=json.loads(subprocess.run([sys.executable,'tools/review_prose.py','--path',str(RUN.relative_to(ROOT)),'--no-write'],cwd=ROOT,
                                   capture_output=True,text=True,encoding='utf8',check=True).stdout)
    assert not prose['flags'],prose['flags']
    write_json(out,{'status':'Verified computation','status_of_inference':'Exploratory','frozen_files_unchanged':len(frozen),'final_run_hashes_match':True,
      'corrected_mass_ids_only':[1201,1730],'primary_eligibility_flags_unchanged':True,'requested_source_slips_corrected':5,'sources_n':len(source['sources']),
      'required_added_precedents_present':True,'local_markdown_links_checked':len(links),'json_files_parsed':len(files),'prose_review':prose,
      'check_bases':['review-response-verification.json','review-response-frozen-verification.json','review-response-reproduction.json','parser-validation-review-response.json'],
      'still_unverified':['Physical source of low-mass excess','Repeated calibrated measurements and rounding resolution','Printed mass–dimension inconsistencies',
                          'Reconciled contextual/class/identity counts','Restricted precedent originals and complete Gulf assemblages']})
    print(out.read_text(encoding='utf8'))

if __name__=='__main__':main()
