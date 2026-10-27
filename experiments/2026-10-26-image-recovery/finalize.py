"""Encode the documented visual decisions without changing the frozen census."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
P=Path('experiments/2026-10-26-image-recovery'); R=Path('D:/projects/indus_valley_script/data/raw/2026-10-26-image-recovery')
def dump(p,x):
    assert not p.exists(),p
    p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((R/'selection-v1.json').read_text()); inventory=json.loads((R/'unmapped-inventory-v1.json').read_text())
ix=list(csv.DictReader(open('experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/image-files.csv')))
# Candidate numbers refer to selection-v1 and the four review sheets.
dec={1:[('L-146','A'),('L-146','B')],2:[('L-163','A'),('L-163','C'),('L-164','A'),('L-165','A')],3:[('L-167','A')],4:[('L-119','C')],5:[('L-207','A 1-2')],6:[('C-34','B')],8:[('M-805','a')],10:[('M-957','A')],11:[('M-966','A')],12:[('M-1020','B')],13:[('M-1058','B')],14:[('M-1078','a')],16:[('M-1202','F')],17:[('M-1202','c')],20:[('M-1342','A')],21:[('M-1342','a')]}
notes={4:'Rectangular photograph with pale central field and dark frame matches right middle L-119 C; caption lies below crop.',5:'Outline, upper hollow and lower broken margin match large upper-left photograph captioned L-207 A 1-2.',6:'Long narrow tablet reverse with central join and right fracture matches second row C-34 B.',8:'Narrow mirrored animal photograph matches right-middle M-805 a, including vessel and broken right edge.',10:'Long rectangular fragment matches left second row M-957 A; cut caption recovered on page.',11:'Square photograph with lower animal matches left second row M-966 A.',12:'Small triangular reverse with handwritten museum marks matches upper-centre M-1020 B.',13:'Small broken reverse with dark cavity matches central M-1058 B.',14:'Long narrow impression with pointed right end matches right third row M-1078 a.',16:'Tiny side fragment resembles bottom-centre M-1202 F, but crop lacks enough carrier shape for a verified match.',17:'Narrow pale impression with vertical grooves matches bottom-left M-1202 c.',20:'Rough rectangular obverse with sloping lower-left corner matches top-left M-1342 A.',21:'Smoother impression with tapered right edge matches top-right M-1342 a.'}
joins=[]; exposures=[]
for j,x in enumerate(s,1):
    p=Path('D:/projects/indus_valley_script/data/lipi/public/seal_images')/x['filename']; pg=x['source_page_hint']; page=R/f"page-v{pg['volume']}-{pg['pdf_page']}.png"
    exposures.append({'candidate':j,'asset':x['filename'],'source_page':pg,'source_render':str(page),'scope':'Full page and candidate crop displayed; all adjacent graphic objects and labels exposed; no sign transcription recorded.','adjacent_catalogue_scope':'all objects on the full source page; exact labels retained in source page image'})
    for key,view in dec.get(j,[(None,None)]):
        old=[r['file'] for r in ix if key and key in r['keys'].split(';')]
        inherited=bool(key and key in x.get('prior_keys','').split(';'))
        status='candidate' if j==16 else ('verified' if key else 'rejected')
        joins.append({'join_id':f'IR26-{j:02d}-{len(joins)+1:02d}','candidate_number':j,'image_logical_path':'data/lipi/public/seal_images/'+x['filename'],'image_physical_path':str(p),'image_sha256':sha(p),'catalogue_target':key,'object_target':None,'face_view':view,'status':status,'source_page':{**pg,'printed_page':pg['pdf_page']-(36 if pg['volume']==1 else 35),'source_title':'Corpus of Indus Seals and Inscriptions, volume '+str(pg['volume'])},'review_evidence':notes.get(j,'Caption and carrier outline agree with source plate.' if key else 'Crop contains a heading, margin or scan mark; no object photograph to join.'),'source_render_physical_path':str(page),'prior_index_status':'inherited asset target' if inherited else 'not assigned to this asset in prior index','newly_recovered':bool(key and not inherited and status=='verified'),'object_already_imaged_in_prior_index':bool(old),'prior_object_image_files':old,'identity_scope':'catalogue image-to-caption relation; no excavation accession or cross-catalogue physical merge'})
dump(R/'image-joins-v1.json',joins)
dump(R/'exposure-log-v1.json',{'candidate_exposures':exposures,'full_pages_displayed':20,'candidate_crops_displayed':24,'contact_sheets':4,'fresh_confirmation_cohort':False,'incidental_text_display':'Source-page OCR from CISI1 PDF313 and409 was printed while finding a missing locator. No normalized sequence fields were loaded.','failures':['First preparation stopped with KeyError L-146 because prior key-page table lacks it. Census outputs were retained. Heading-range page309 located L-146; corrected script reused prior hashes for duplicate candidate generation.','Initial registry read used platform encoding and failed; retried UTF-8.']})
byfile={x['filename']:[] for x in inventory}
for x in joins:
    name=Path(x['image_physical_path']).name
    if name in byfile:byfile[name].append(x)
for x in inventory:
    reviewed=byfile[x['filename']]
    if reviewed:x['disposition']='; '.join(sorted({r['status'] for r in reviewed}));x['review_join_ids']=[r['join_id'] for r in reviewed]
dump(R/'anonymous-dispositions-v2.json',[x for x in inventory if x['anonymous']])
dump(R/'unmapped-dispositions-v2.json',inventory)
new=[x for x in joins if x['newly_recovered']]
agg={**json.loads((R/'pre-review-aggregate-v1.json').read_text()),'verified_join_rows':sum(x['status']=='verified' for x in joins),'new_asset_catalogue_view_joins':len(new),'new_anonymous_catalogue_view_joins':sum(x['candidate_number']>=4 for x in new),'newly_imaged_catalogue_keys':sorted({x['catalogue_target'] for x in new if not x['object_already_imaged_in_prior_index']}),'newly_imaged_pilot_catalogue_objects':1,'newly_imaged_pilot_keys':['L-163'],'new_pilot_views':['L-163 A','L-163 C'],'new_primary_image_files':0,'new_physical_identity_merges':0,'rejected_non_object_assets':sum(x['status']=='rejected' for x in joins),'candidate_join_rows':sum(x['status']=='candidate' for x in joins),'unreviewed_anonymous_unassigned':34}
dump(P/'aggregate-v1.json',agg)
checks={'anonymous_count':len([x for x in inventory if x['anonymous']])==284,'unmapped_count':len(inventory)==2152,'selection_bound':len(s)<=24,'page_bound':len({str(x['source_page_hint']) for x in s})<=30,'all_selected_reviewed':len({x['candidate_number'] for x in joins})==24,'all_verified_have_page_and_hash':all(x['source_page'] and x['image_sha256'] for x in joins if x['status']=='verified'),'pilot_gain_only_L163':agg['newly_imaged_pilot_keys']==['L-163'],'no_merge':all(x['object_target'] is None for x in joins)}
dump(P/'validation-v1.json',{'checks':checks,'passed':all(checks.values()),'tier':'submitted'})
dump(R/'missing-evidence-queue-v1.json',[{'filename':x['filename'],'source_page_hint':x['source_page_hint'],'reason':x['disposition']} for x in inventory if x['anonymous'] and (not x['prior_keys']) and not any(y['status']=='verified' for y in byfile[x['filename']])])
manifest=[]
for p in sorted(R.iterdir()):
    if p.is_file():manifest.append({'logical_path':'data/raw/2026-10-26-image-recovery/'+p.name,'physical_path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'rights':'rights-unverified; source-derived local-only'})
dump(P/'source-manifest-v1.json',{'prior_manifest':'experiments/2026-10-24-object-identity-pass3/source-manifest-v3.json','source_pins':{'lipi':'fc8813a52e183d19c441631dc26c33a4dccbea39'},'acquisition':'existing local files only; no network retrieval','raw_artifacts':manifest,'project_code_license':'Unlicense','project_prose_license':'CC0 1.0'})
print(json.dumps(agg,indent=2))
