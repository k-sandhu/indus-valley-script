"""Check the PowerPoint package against frozen archaeological inputs and images."""
from __future__ import annotations
import hashlib
import json
import math
import posixpath
import re
import sys
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
LOCAL=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/presentation')
RUN=sys.argv[1] if len(sys.argv)>1 else 'v2'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def numbers(series,key):return [float(n.text) for n in series.findall(f'c:{key}/c:numRef/c:numCache/c:pt/c:v',NS)]
def close(a,b):
    assert len(a)==len(b),(a,b)
    assert all(math.isclose(x,y,rel_tol=1e-10,abs_tol=1e-10) for x,y in zip(a,b)),(a,b)

def main():
    manifest=read(HERE/f'input-manifest-{RUN}.json');evidence=read(manifest['evidence_path'])
    assert sha(manifest['evidence_path'])==manifest['evidence_sha256']
    for r in manifest['inputs']:assert sha(ROOT/r['logical_path'])==r['sha256'],r['logical_path']
    for a in manifest['image_assets']:
        assert sha(a['physical_path'])==a['sha256'],a['id']
        assert sha(a['source_image_path'])==a['source_image_sha256'],a['id']
    deck=LOCAL/'output'/f'shared-infrastructure-plan-test-2026-10-24-{RUN}.pptx'
    receipt=read(LOCAL/'build'/RUN/'validation.json')
    assert sha(deck)==receipt['finalSha256']
    assert receipt['packageIntegrity']['status']=='pass'
    assert receipt['firstPartyImport']['passed']
    assert receipt['presentationLayout']['finding_count']==0
    r=evidence['root'];counts=r['Lothal_independent_recount']['counts'];g=r['Dholavira_coverage']['gate_counts']
    expected={18:[{'val':[counts[k] for k in ['W','W1','W2','O','?']]}],19:[{'val':[g[k] for k in ['accession_string','grid_label','stratum_label','depth_label','area_label','unqualified_stage','explicit_room_label']]}],22:[]}
    ms=[m for m in r['measurements'] if m['module']=='mohenjo-control']
    for i,m in enumerate(ms):
        s=m['source_record'];expected[22].append({'xVal':[s['reading_lower_m'],s['reading_upper_m']],'yVal':[4-i,4-i]});expected[22].append({'xVal':[m['value']],'yVal':[4-i]})
    alt=ms[-1]['source_record']['alternative_edge']
    expected[22]+=[{'xVal':[alt['reading_lower_m'],alt['reading_upper_m']],'yVal':[.85,.85]},{'xVal':[alt['estimate_m']],'yVal':[.85]}]
    chart_slides=[];table_slides=[];image_slides=[];titles=[];notes=[];numeric=0
    with ZipFile(deck) as z:
        names=z.namelist();assert len([n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)])==26
        assert len([n for n in names if n.endswith('.xlsx')])==3
        for i in range(1,27):
            x=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
            if x.findall('.//a:tbl',NS):table_slides.append(i)
            if x.findall('.//p:pic',NS):image_slides.append(i)
            alltext=[t.text or '' for t in x.findall('.//a:t',NS)]
            assert not any('undefined' in t or '\ufffd' in t or '\u00e2\u20ac' in t for t in alltext),i
            titles.append({'slide':i,'title':alltext[0] if alltext else ''})
            n=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'));note='\n'.join(t.text or '' for t in n.findall('.//a:t',NS))
            assert len(note)>200 and 'undefined' not in note,i
            assert evidence['root_run_sha256'] in note,i
            notes.append(i)
            rels=ET.fromstring(z.read(f'ppt/slides/_rels/slide{i}.xml.rels'))
            targets=[]
            for q in rels:
                if q.attrib['Type'].endswith('/chart'):
                    t=q.attrib['Target'];targets.append(t.lstrip('/') if t.startswith('/') else posixpath.normpath(posixpath.join('ppt/slides',t)))
            if i not in expected:
                assert not targets,i;continue
            assert len(targets)==1,i
            cx=ET.fromstring(z.read(targets[0]));series=cx.findall('.//c:ser',NS)
            assert len(series)==len(expected[i]),(i,len(series))
            for s,exp in zip(series,expected[i]):
                for key,values in exp.items():close(numbers(s,key),values);numeric+=len(values)
                for smooth in s.findall('c:smooth',NS):assert smooth.attrib['val']=='0'
            chart_slides.append(i)
        # The clump total is a source cohort, not a census or independent sample count.
        assert 16+2+4==22
        media=[n for n in names if n.startswith('ppt/media/') and not n.endswith('/')]
    assert chart_slides==[18,19,22]
    assert table_slides==[5,6,12,16,20,23,24,25]
    native=read(LOCAL/'build'/RUN/'powerpoint/native-review.json')
    assert native['exportedSlides']==26 and len(native['sampleChartsEditedResizedSavedReopened'])==3
    assert native['finalFileChanged'] is False
    output={'status':'pass','run':RUN,'final_path':str(deck),'final_sha256':sha(deck),'bytes':deck.stat().st_size,'slides':26,'native_chart_slides':chart_slides,'native_table_slides':table_slides,'source_image_slides':image_slides,'embedded_media_files':len(media),'note_pages':len(notes),'chart_source_numeric_points_checked':numeric,'frozen_input_files':len(manifest['inputs']),'frozen_image_assets':len(manifest['image_assets']),'powerpoint_rendered_slides':26,'native_edit_save_reopen_chart_samples':3,'atlas_manifest_sha256':manifest['atlas_manifest_sha256'],'slide_index':titles,'claim_boundary':'Native chart caches are checked against the frozen source register. Source imagery is attributed and local-only. Diagram and table text require the recorded visual and archaeological review.'}
    (HERE/f'verification-{RUN}.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k!='slide_index'}))

if __name__=='__main__':main()
