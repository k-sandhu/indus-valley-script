"""Read-only cross-check of the study, frozen source register and final products."""
from pathlib import Path
from collections import Counter
import argparse
import csv
import hashlib
import json
import math
import zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader

P=Path(__file__).resolve().parent
REPO=P.parents[1]
checks=[]
def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def actual(path):return Path(path.replace('\\\\','\\'))
def check(name,value,detail=None):checks.append(dict(check=name,passed=bool(value),detail=detail))

def main(out):
    if out.exists():raise FileExistsError(out)
    rows=load(P/'run-v3/observations.json');byid={r['id']:r for r in rows}
    summary=load(P/'run-v3/summary.json'); towns=load(P/'run-v3/towns.json')
    source=load(P/'run-v3/sources.json');sid={r['source_id'] for r in source}
    check('287 unique assertions',len(rows)==len(byid)==287)
    check('twelve core towns',len(towns)==12 and len({r['town'] for r in towns})==12)
    check('42 source-use records',len(source)==len(sid)==42)
    check('source references',all(r['source_id'] in sid for r in rows))
    check('core merge validation',load(P/'run-v3/validation.json')['status']=='pass')
    check('five prerequisites per town',len(list(csv.DictReader((P/'run-v3/missing-fields.csv').open(encoding='utf-8-sig'))))==60)
    for item in load(P/'run-v3/input-manifest.json'):
        check('frozen register input: '+item['path'],sha(REPO/item['path'])==item['sha256'])
    hashed=[]
    for s in source:
        if s.get('physical_path') and s.get('sha256'):
            path=actual(s['physical_path']);ok=path.is_file() and sha(path).lower()==s['sha256'].lower()
            hashed.append(s['sha256'].lower());check('held source hash: '+s['source_id'],ok)
    check('38 paths, 36 distinct held hashes',len(hashed)==38 and len(set(hashed))==36)
    unknown=[r for r in rows if r['phase']=='unknown']
    check('13 unknown phases with raw values and reasons',len(unknown)==13 and all(r.get('phase_raw','unexpected') is None and r.get('phase_missing_reason') for r in unknown))
    chrono=load(P/'run-v3/duration-spans.json')
    ravi=next(r for r in chrono if r['observation_id']=='W-HAR-003')
    check('open Ravi start retained',ravi['start_operator']=='>' and ravi['nominal_span_years'] is None)
    check('five eastern numerical chronology payloads retained',sum(r.get('source_chronology') is not None for r in chrono)==5)
    multi=byid['INS-029']
    check('multi-site assertion retained',multi['towns']==['harappa','lahoma-lal-tibba'] and multi['id'] in next(t['observation_ids'] for t in towns if t['town']=='harappa'))
    def indexed(town,domain,oid):return oid in next(t for t in towns if t['town']==town)['domains'][domain]['observation_ids']
    check('dwelling is not a well',not indexed('farmana','water_and_sanitation','EAST-FARMANA-005'))
    check('entrance relocation is not a geographic setting',not indexed('surkotada','location_setting','EAST-SURKOTADA-004'))
    check('chronological extent is not area',not indexed('kanmer','settlement_extent','EAST-KANMER-015'))
    for oid in ['EAST-KALIBANGAN-002','EAST-KALIBANGAN-008','EAST-KALIBANGAN-009']:
        check('Kalibangan extent index: '+oid,indexed('kalibangan','settlement_extent',oid))
    check('Kanmer infill is indexed',indexed('kanmer','incremental_alteration','EAST-KANMER-012'))
    check('Surkotada closure is indexed',indexed('surkotada','layout_and_access','EAST-SURKOTADA-014'))
    quantity=list(csv.DictReader((P/'quantities.csv').open(encoding='utf-8-sig')))
    check('134 lossless quantity rows',len(quantity)==134 and any(r['observation_id']=='W-DHO-005' and r['numeric_field']=='values' for r in quantity))
    shape=load(P/'shape-comparison-v1/results.json')
    check('six exploratory dimension pairs at three towns',len(shape['rows'])==6 and len({r['town'] for r in shape['rows']})==3 and shape['status_class']=='exploratory')
    for r in shape['rows']:
        a,b=r['dimensions_m'];check('dimension ratio: '+r['observation_id'],math.isclose(max(a,b)/min(a,b),r['longer_to_shorter_ratio'],rel_tol=1e-12) and r['ratio_uncertainty'] is None)
    check('synthetic orientation and exact-power controls',load(P/'synthetic-v1/results.json')['passed'])
    bench=load(P/'bench-shots-synthetic-v1.json')
    check('shots guard run is synthetic and passes',bench['synthetic'] and bench['pass'])
    prior=load(P/'modules/inscriptions/prior-results.json')
    check('spent ledger unchanged from source bridge',sha(REPO/'bench/spent.json')==prior['bench_spent_sha256'])
    c=load(P/'modules/inscriptions/context-table-summary.json')
    check('225 source rows and stage denominator',c['rows']==225 and sum(c['stage_raw_counts'].values())==225 and sum(c['stage_raw_counts'][k] for k in ['III A','IV','V','VI'])==162)
    check('139 explicit inscription flags',c['inscription_raw_counts']['Yes']+c['inscription_raw_counts']['Yes,']==139)
    check('no physical-object census gain',c['physical_objects_added']==0 and not c['counts_are_independent_objects'])
    figures=load(P/'modules/visuals/manifest-run-v7.json')
    check('23 final figures',len(figures['figures'])==figures['figure_count']==23)
    for fig in figures['figures']:
        for asset in fig['assets']:
            check('figure asset: '+fig['id']+' '+asset['format'],sha(actual(asset['physical_path']))==asset['sha256'])
    book=load(P/'book-manifest-v4.json');pdf=actual(book['output_physical_path'])
    check('final book hash',sha(pdf)==book['sha256'])
    reader=PdfReader(pdf)
    check('declared pages and 23 landscape figures',len(reader.pages)==book['pages'] and len(reader.pages)>50 and sum(float(p.mediabox.width)>float(p.mediabox.height) for p in reader.pages)==23)
    text='\n'.join(page.extract_text() or '' for page in reader.pages)
    check('no replacement glyphs in PDF',chr(65533) not in text)
    check('all 23 figure captions in PDF',all(f'Figure {i}.' in text for i in range(1,24)))
    for item in book['input_manifest']:
        check('book input: '+Path(item['path']).name,sha(actual(item['path']))==item['sha256'])
    deck_manifest=load(P/'modules/presentation/artifact-manifest.json')
    deck_record=next(r for r in deck_manifest['artifacts'] if r['version']=='v2')
    deck=actual(deck_record['physical_path']);check('final presentation hash',sha(deck)==deck_record['sha256'])
    with zipfile.ZipFile(deck) as z:
        slides=[n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
        notes=[n for n in z.namelist() if n.startswith('ppt/notesSlides/notesSlide') and n.endswith('.xml')]
        check('26 native slides and source notes',len(slides)==len(notes)==26)
        bad=[]
        for name in slides:
            for e in ET.fromstring(z.read(name)).iter():
                if e.tag.endswith('}t') and e.text and any(ord(c) in [0xfffd,0x00c3,0x00e2] for c in e.text):bad.append((name,e.text))
        check('presentation text has no mojibake markers',not bad,bad)
    check('no acquired images embedded in deck',not any(n.startswith('ppt/media/') for n in zipfile.ZipFile(deck).namelist()))
    result=dict(status='pass' if all(c['passed'] for c in checks) else 'fail',checks=len(checks),failed=[c for c in checks if not c['passed']],
                records=checks,scope='Source, computation, population and product integrity; no confirmation score or peer-review acceptance',
                code_sha256=sha(Path(__file__)))
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','checks','failed']},indent=2))
    return 0 if result['status']=='pass' else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True,type=Path)
    raise SystemExit(main(parser.parse_args().out))
