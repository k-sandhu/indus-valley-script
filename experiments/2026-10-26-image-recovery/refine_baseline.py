"""Preserve v1 and distinguish crop-index recovery from prior photo availability."""
import hashlib,json
from pathlib import Path
P=Path('experiments/2026-10-26-image-recovery');R=Path('D:/projects/indus_valley_script/data/raw/2026-10-26-image-recovery')
prior=Path('data/raw/2026-10-24-office-seal-pass2/view-ledger-v1.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    assert not p.exists(),p
    p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
x=json.loads((P/'aggregate-v1.json').read_text())
x['version']='v2';x['supersedes_gain_wording_in']='aggregate-v1.json'
x['newly_indexed_catalogue_keys_vs_2026_10_13_image_index']=x.pop('newly_imaged_catalogue_keys')
x['newly_indexed_pilot_catalogue_keys_vs_2026_10_13_image_index']=x.pop('newly_imaged_pilot_keys')
x['newly_indexed_pilot_catalogue_key_count']=x.pop('newly_imaged_pilot_catalogue_objects')
x['newly_indexed_pilot_views']=x.pop('new_pilot_views')
x['newly_available_pilot_photographs']=0;x['previously_unimaged_pilot_physical_objects_established']=0
x['new_photo_availability_for_nonpilot_catalogue_keys']='not established; index absence alone does not audit all earlier source-page availability'
x['L163_prior_availability']={'ledger_logical_path':str(prior),'ledger_sha256':sha(prior),'source':'CISI volume 1','pdf_page':313,'printed_page':277,'panels':['A','C'],'prior_ledger_baseline':'previously inspected October2 and13','additional_prior_source':'Frenez 2005, PDF39 printed101 Figure6 lower left; four views'}
dump(P/'aggregate-v2.json',x)
joins=json.loads((R/'image-joins-v1.json').read_text())
for j in joins:
    j['recovery_baseline']='2026-10-13 image-files.csv asset-to-catalogue assignment'
    j['newly_indexed_against_baseline']=j.pop('newly_recovered')
    j['object_already_indexed_in_2026_10_13_image_files']=j.pop('object_already_imaged_in_prior_index')
    j['new_photograph_availability_established']=False
    if j['catalogue_target']=='L-163':j['prior_source_page_availability']=x['L163_prior_availability']
dump(R/'image-joins-v2.json',joins)
dump(R/'baseline-comparison-v1.json',{'source_ledger_logical_path':str(prior),'source_ledger_physical_path':str(prior.resolve()),'source_ledger_sha256':sha(prior),'conclusion':'L-163 A and C photographs were available and recorded before this run; the new contribution is their explicit association with the held composite crop in the image-file index.','ledger':json.loads(prior.read_text(encoding='utf8'))})
manifest=json.loads((P/'source-manifest-v1.json').read_text())
manifest['version']='v2';manifest['prior_manifest']='experiments/2026-10-26-image-recovery/source-manifest-v1.json'
manifest['baseline_source']={'logical_path':str(prior),'physical_path':str(prior.resolve()),'sha256':sha(prior),'bytes':prior.stat().st_size,'rights':'project metadata; detailed record retained local-only'}
for p in [R/'image-joins-v2.json',R/'baseline-comparison-v1.json']:
    manifest['raw_artifacts'].append({'logical_path':'data/raw/2026-10-26-image-recovery/'+p.name,'physical_path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'rights':'source-derived local-only'})
dump(P/'source-manifest-v2.json',manifest)
