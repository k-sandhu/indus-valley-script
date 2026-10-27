"""Preserve v1 facts and create a reviewed presentation with explicit review scope."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,copy,importlib.util,re,html
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
D=Path('D:/projects/indus_valley_script');V1=D/'data/raw/2026-10-26-object-pilot/integration-v1';V2=D/'data/raw/2026-10-26-object-pilot/integration-v2'
REVIEW=ROOT/'experiments/2026-10-26-object-pilot-review/integration-review-v2.json'
REPORT=ROOT/'experiments/2026-10-26-object-pilot-review/REPORT-v2.md'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf8') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
def physical(x):
    p=Path(x);return p.resolve() if p.is_absolute() else (ROOT/p).resolve()
def render(data):
    renderer=ROOT/'experiments/2026-10-26-object-pilot-register/render_catalogue.py'
    spec=importlib.util.spec_from_file_location('upstream_renderer',renderer);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    view=copy.deepcopy(data)
    for o in view['objects']:
        grouped={};other=[]
        for image in o['images']:
            if not image.get('path'):other.append(image);continue
            key=str(physical(image['path']))
            if key not in grouped:grouped[key]=image
            else:
                old=grouped[key];old['source_refs']=list(dict.fromkeys(old.get('source_refs',[])+image.get('source_refs',[])));old['panel']=', '.join(dict.fromkeys(str(old.get('panel','')).split(', ')+str(image.get('panel','')).split(', ')))
        o['images']=list(grouped.values())+other
    page=m.render(view)
    page=page.replace('<title>Twenty-target object register</title>','<title>Reviewed twenty-target object register</title><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 rx=%276%27 fill=%27%23172522%27/%3E%3Cpath d=%27M9 8h14v16H9z%27 fill=%27%23f2f0e9%27/%3E%3C/svg%3E">')
    notice='<section><h2>Source and integration review complete</h2><p>The independent review structurally checked all 539 inherited assertions and 96 source hash bindings. It directly compared the fourteen new image joins with primary plate and crop pixels. This bounded review did not retranscribe every inherited metadata cell from its original source.</p><p><a href="'+html.escape(REPORT.resolve().as_uri(),quote=True)+'">Read the independent review</a>. Image gains are new crop-to-catalogue index links against the October 13 table; zero newly available pilot photographs are established.</p></section>'
    page=page.replace('<nav>',notice+'<nav>',1)
    for o in data['objects']:
        status='Identity link unresolved' if o['record_id'].startswith('PCF') else 'Catalogue target with source-qualified records'
        old=f'{m.esc(len(o["candidate_family_ids"]))} candidate corpus families' if o['candidate_family_ids'] else m.esc(o.get('identity_status','unspecified'))
        page=page.replace(old+' · Physical merge accepted: False',html.escape(status))
        raw=', '.join(o['missing_fields']);plain=', '.join(s.replace('_',' ') for s in o['missing_fields'])
        page=page.replace('<strong>Missing evidence:</strong> '+html.escape(raw),'<strong>Missing evidence:</strong> '+html.escape(plain))
        if o.get('blocked_assertions'):
            text='<section class="conflict-notice"><h3>Unresolved source identity</h3><p>Safe to display: '+html.escape('; '.join(o['safe_to_display']))+'</p><p><strong>Blocked claims:</strong> '+html.escape('; '.join(o['blocked_assertions']))+'</p></section>'
            marker='<h2>'+html.escape(o['record_id'])+' <span>'+html.escape(o['site'])+'</span></h2>';page=page.replace(marker,marker+text)
    def caption(match):
        content=match[1];first=re.search(r'<pre>(.*?)</pre>',content,re.S)
        coords=json.loads(html.unescape(first[1])) if first else {}
        title=content.split('<pre>',1)[0]
        labels=[]
        for key,label in [('printed_page','Printed page'),('pdf_page','PDF page'),('panel','Panel')]:
            if coords.get(key) is not None:labels.append(label+' '+str(coords[key]))
        if not labels:labels=['See the source coordinates below']
        binding=coords.get('binding_status','')
        status='<p>'+html.escape(binding)+'</p>' if binding else ''
        return '<figcaption>'+title+'<p>'+html.escape(' · '.join(labels))+'</p>'+status+'<details><summary>Source details</summary>'+content+'</details></figcaption>'
    return re.sub(r'<figcaption>(.*?)</figcaption>',caption,page,flags=re.S),renderer
def main():
    assert not V2.exists(),'Preserve frozen endpoints'
    old=read(V1/'pilot-integrated-v1.json');data=copy.deepcopy(old);review=read(REVIEW)
    assert review['failed']==0 and review['passed']==11
    assert review['projection_sha256']==sha(V1/'pilot-integrated-v1.json')
    data['review_status']='source and integration review complete'
    data['review_metadata']={'review_record':str(REVIEW.relative_to(ROOT)).replace('\\','/'),'review_record_physical_path':str(REVIEW),'review_record_sha256':sha(REVIEW),'report':str(REPORT.relative_to(ROOT)).replace('\\','/'),'report_physical_path':str(REPORT),'report_sha256':sha(REPORT),'structurally_checked_inherited_assertions':539,'source_hash_bindings':96,'new_image_joins_primary_reviewed':14,'scope':'Bounded source review and structural integration review; all 539 inherited metadata cells were not retranscribed from primary sources.','maintainer_acceptance':'separate'}
    data['integration']['review_status']='source and integration review complete'
    page,renderer=render(data)
    V2.mkdir(parents=True)
    dump(V2/'pilot-integrated-v2.json',data)
    (V2/'catalogue-integrated-v2.html').write_text(page,encoding='utf8')
    (V2/'missing-evidence-integrated-v2.json').write_bytes((V1/'missing-evidence-integrated-v1.json').read_bytes())
    compare=copy.deepcopy(data);compare.pop('review_metadata');compare['review_status']=old['review_status'];compare['integration'].pop('review_status')
    checks={'json_changes_only_review_metadata':compare==old,'all_objects_exactly_unchanged':data['objects']==old['objects'],'all_base_assertions_unchanged':all(a['assertions']==b['assertions'] for a,b in zip(data['objects'],old['objects'])),'same_twenty_cards':page.count('<article ')==20,'queue_unchanged':sha(V2/'missing-evidence-integrated-v2.json')==sha(V1/'missing-evidence-integrated-v1.json'),'review_hash_matches_input':review['projection_sha256']==sha(V1/'pilot-integrated-v1.json'),'review_passed':review['failed']==0,'inline_favicon':'rel="icon" href="data:image/svg+xml' in page,'no_raw_false_status':'Physical merge accepted: False' not in page,'collapsed_source_details':page.count('<summary>Source details</summary>')==page.count('<figcaption>'),'review_complete_heading':'Source and integration review complete' in page}
    aggregate=read(P/'aggregate-v1.json');aggregate['review_status']=data['review_status'];aggregate['independent_review_checks_passed']=11
    dump(P/'aggregate-v2.json',aggregate);dump(P/'validation-v2.json',{'checks':checks,'passed':all(checks.values()),'review_scope':data['review_metadata']['scope']})
    def rec(p):return {'physical_path':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size}
    dump(P/'manifest-v2.json',{'inputs':[rec(p) for p in [V1/'pilot-integrated-v1.json',V1/'missing-evidence-integrated-v1.json',REVIEW,REPORT,renderer]],'outputs':[rec(p) for p in V2.iterdir()],'code_pins':[rec(Path(__file__)),rec(P/'preview_catalogue.py')],'handling':'Local-only D: records and standalone HTML; temporary preview remains localhost only.','authors':[{'model':'gpt-6.1-sol','harness':'Codex collaboration'}]})
    print(json.dumps({'output':str(V2),'checks':checks},indent=2))
if __name__=='__main__':main()
