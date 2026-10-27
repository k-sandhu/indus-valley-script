"""Freeze the twenty-target register plus explicit image and conflict overlays."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,importlib.util,copy,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
D=Path('D:/projects/indus_valley_script');R=D/'data/raw/2026-10-26-object-pilot/integration-v1'
BASE=D/'data/raw/2026-10-26-object-pilot-register/pilot-register-v4.json'
JOIN=D/'data/raw/2026-10-26-image-recovery/image-joins-v2.json'
CONFLICT=D/'data/raw/2026-10-26-source-conflicts/conflicts-v2.json'
QUEUE=D/'data/raw/2026-10-26-object-pilot-register/missing-evidence-v4.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf8') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
def physical(p):
    p=Path(p);return p.resolve() if p.is_absolute() else (ROOT/p).resolve()
def main():
    assert not R.exists(),'Frozen endpoint already exists'
    data=read(BASE);base=copy.deepcopy(data);joins=read(JOIN);conf=read(CONFLICT)['conflicts'];queue=read(QUEUE)
    targets={o['record_id']:o for o in data['objects']};catalog={s['source_ref']:s for s in data['source_catalogue']}
    def source(p,title):
        p=physical(p);key=str(p)
        if key not in catalog:catalog[key]={'source_ref':key,'logical_path':str(p.relative_to(D)).replace('\\','/') if p.is_relative_to(D) else str(p.relative_to(ROOT)).replace('\\','/'),'physical_path':str(p),'exists':p.exists(),'bytes':p.stat().st_size,'sha256':sha(p),'title':title,'rights':'source-derived local-only'}
        return key
    jr=source(JOIN,'Image recovery joins v2');cr=source(CONFLICT,'Source conflicts v2')
    for o in data['objects']:o['integration_image_joins']=[];o['safe_to_display']=[];o['blocked_assertions']=[]
    for j in joins:
        t=j['catalogue_target']
        if j['status']!='verified' or t not in targets:continue
        o=targets[t];o['integration_image_joins'].append(j)
        path=physical(j['image_physical_path']);ir=source(path,'Held crop: '+path.name);pr=source(j['source_render_physical_path'],'CISI source page for '+t)
        existing=next((im for im in o['images'] if im.get('path') and physical(im['path'])==path),None)
        if existing is None:
            existing={'path':str(path),'sha256':sha(path),'kind':'caption-verified held crop','source_refs':[],'coverage_class':'verified-catalogue-crop-index-overlay','binding_status':'caption and carrier outline verified against primary page; physical identity merge not adjudicated','image_scope':'composite may include adjacent catalogue objects; only this card target is assigned'};o['images'].append(existing)
        existing.setdefault('verified_target_views',[]).append(j['face_view']);existing['panel']=', '.join(existing['verified_target_views']);existing['pdf_page']=j['source_page']['pdf_page'];existing['printed_page']=j['source_page']['printed_page'];existing['locator']=j['source_page'];existing['binding_status']='verified image-to-catalogue caption relation; no physical identity merge';existing['index_gain_baseline']='October 13 image-files.csv';existing['new_photo_availability_established']=False
        existing['source_refs']=list(dict.fromkeys(existing.get('source_refs',[])+[jr,ir,pr]))
    for c in conf:
        for t in c['target_ids']:
            o=targets[t];o['conflicts'].append(c);o['safe_to_display']+=c['safe_to_display'];o['blocked_assertions']+=c['blocked_assertions']
            o['assertions'].append({'assertion_id':'INTEGRATION-'+c['conflict_id'],'field':'source_conflict_review','value':{'disposition':c['disposition'],'safe_to_display':c['safe_to_display'],'blocked_assertions':c['blocked_assertions']},'status':'conflicting','source_refs':[cr],'locator':{'conflict_id':c['conflict_id']},'safe_to_display':True})
            for a in o['assertions']:
                if not a['assertion_id'].startswith('INTEGRATION-'):a['integration_conflict_review']={'conflict_id':c['conflict_id'],'rule':'Keep this source-qualified assertion; any canonical or transferred identity claim must satisfy the explicit blocked-assertion rules on this card.'}
            for image in o['images']:
                if t=='L-164' and ('CLXI' in str(image) or '491' in str(image)):
                    image['binding_status']='BLOCKED as confirmed L-164 photograph: Plate CLXI F identity unresolved between excavation 1864 and 1830';image['confirmed_target_join']=False;image['coverage_class']='unresolved-candidate-source-page'
    data['source_catalogue']=list(catalog.values());data['review_status']='pending integrated review';data['integration']={'base_version':'v4','base_assertions_retained':sum(len(o['assertions']) for o in base['objects']),'image_index_gain_baseline':'2026-10-13 image-files.csv','new_index_links_all_targets_and_nonpilot':14,'newly_available_pilot_photographs':0,'physical_merges':0,'conflicts':len(conf)}
    tops=[]
    for c in conf:
        for record in c['exact_resolving_record']:
            tops.append({'record_ids':c['target_ids'],'priority':0,'reason':record['rank_reason'],'required_evidence':record['record'],'conflict_id':c['conflict_id'],'original_conflict_rank':record['rank'],'integration_priority_reason':'This record decides a named unresolved identity and prevents transfer of disputed context or image metadata.'})
    tops.append({'record_ids':[t for t in targets if t.startswith('PCF')],'priority':0,'reason':'Ten source targets retain candidate corpus families without a qualifying identity bridge.','required_evidence':'Source-qualified accession-to-CISI concordance or registered photographs tying each accession carrier to a catalogue record.','integration_priority_reason':'The bridge decides physical identity before candidate metadata can become target facts.'})
    combined={'denominator':20,'top_priorities':tops,'rows':queue['rows'],'original_rank_reasons_preserved':True}
    # Use the compatible upstream renderer on this projection; overlay notices are visible per card.
    spec=importlib.util.spec_from_file_location('pilot_render',ROOT/'experiments/2026-10-26-object-pilot-register/render_catalogue.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    view=copy.deepcopy(data)
    for o in view['objects']:
        grouped={};rest=[]
        for im in o['images']:
            if not im.get('path'):rest.append(im);continue
            key=str(physical(im['path']))
            if key not in grouped:grouped[key]=im
            else:
                g=grouped[key];g['source_refs']=list(dict.fromkeys(g.get('source_refs',[])+im.get('source_refs',[])));g['panel']=', '.join(dict.fromkeys(str(g.get('panel','')).split(', ')+str(im.get('panel','')).split(', ')))
        o['images']=list(grouped.values())+rest
    page=mod.render(view)
    notice='<p><strong>Integrated review pending.</strong> Image gains are new crop-to-catalogue index links against the October 13 table. This pass establishes zero newly available pilot photographs. The original assertions and unresolved identity conflicts remain source-qualified.</p>'
    page=page.replace('<nav>',notice+'<nav>',1)
    for o in data['objects']:
        if o['blocked_assertions']:
            notice='<section class="conflict-notice"><h3>Unresolved source identity</h3><p>Safe to display: '+html.escape('; '.join(o['safe_to_display']))+'</p><p><strong>Blocked claims:</strong> '+html.escape('; '.join(o['blocked_assertions']))+'</p></section>'
            marker='<h2>'+html.escape(o['record_id'])+' <span>'+html.escape(o['site'])+'</span></h2>';page=page.replace(marker,marker+notice)
    R.mkdir(parents=True)
    dump(R/'pilot-integrated-v1.json',data);dump(R/'missing-evidence-integrated-v1.json',combined)
    with (R/'catalogue-integrated-v1.html').open('x',encoding='utf8') as f:f.write(page)
    unchanged=all([a for a in targets[o['record_id']]['assertions'] if not a['assertion_id'].startswith('INTEGRATION-')][i]['value']==a['value'] for o in base['objects'] for i,a in enumerate(o['assertions']))
    localrefs=[s for s in data['source_catalogue'] if s.get('physical_path') and s.get('sha256')]
    checks={'fixed_twenty':len(targets)==20,'same_target_set':set(targets)=={o['record_id'] for o in base['objects']},'base_values_retained':unchanged,'candidate_sets_unchanged':all(targets[o['record_id']]['candidate_family_ids']==o['candidate_family_ids'] for o in base['objects']),'source_hashes':all(physical(s['physical_path']).is_file() and sha(physical(s['physical_path']))==s['sha256'] for s in localrefs),'two_conflicts_attached':sum(bool(o['blocked_assertions']) for o in data['objects'])==2,'L163_composite_once':sum(Path(im.get('path','')).name=='L-164_A_L-165_A.jpg' for im in next(o for o in view['objects'] if o['record_id']=='L-163')['images'])==1,'no_accepted_merges':not any(o['accepted_physical_merge'] for o in data['objects']),'twenty_html_cards':page.count('<article ')==20,'original_queue_preserved':combined['rows']==queue['rows']}
    agg={'targets':20,'base_assertions':data['integration']['base_assertions_retained'],'integrated_assertions':sum(len(o['assertions']) for o in data['objects']),'conflicts':2,'candidate_edges':sum(len(o['candidate_family_ids']) for o in data['objects']),'pilot_verified_overlay_join_rows':sum(len(o['integration_image_joins']) for o in data['objects']),'index_links_gain_across_full_image_pass':14,'newly_available_pilot_photographs':0,'review_status':data['review_status']}
    dump(P/'aggregate-v1.json',agg);dump(P/'validation-v1.json',{'checks':checks,'passed':all(checks.values()),'tier':'author checks; integrated independent review pending'})
    def rec(p):return {'physical_path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
    dump(P/'manifest-v1.json',{'inputs':[rec(p) for p in [BASE,JOIN,CONFLICT,QUEUE,Path(mod.__file__)]],'outputs':[rec(p) for p in R.iterdir()],'handling':'Detailed JSON and standalone file-URI HTML remain local-only on D:. Preview binds only to127.0.0.1 and publishes no external site.','authors':[{'model':'gpt-6.1-sol','harness':'Codex collaboration'}]})
    print(json.dumps({'output':str(R),'aggregate':agg,'checks':checks},indent=2))
if __name__=='__main__':main()
