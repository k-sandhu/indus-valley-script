"""Read-only packet checks. Optionally save results to a new endpoint."""
from pathlib import Path
import argparse,hashlib,json,re,datetime
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output');args=parser.parse_args()
checks=[]
def check(name,ok,**details):
    checks.append({'name':name,'pass':bool(ok),**details})
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest=json.loads((OUT/'source-manifest.json').read_text(encoding='utf-8'))
obs=json.loads((OUT/'observations.json').read_text(encoding='utf-8'))
for rec in [*manifest['sources'],*manifest['derivatives']]:
    path=ROOT/rec['path'];check('witness-exists',path.is_file(),path=rec['path'])
    if not path.is_file():continue
    check('witness-sha256',digest(path)==rec['sha256'],path=rec['path'])
    check('witness-bytes',path.stat().st_size==rec['bytes'],path=rec['path'])
    check('local-only-handling',rec['handling']=='local-only',path=rec['path'])
    if 'parent' in rec:
        parent=ROOT/rec['parent'];check('parent-sha256',parent.is_file() and digest(parent)==rec['parent_sha256'],path=rec['path'])
    if 'pdf_page_count' in rec:
        check('pdf-page-count',len(fitz.open(path))==rec['pdf_page_count'],path=rec['path'])
    if 'crop_bounds_xyxy' in rec:
        parent_image=Image.open(ROOT/rec['parent']);w,h=parent_image.size;x0,y0,x1,y1=rec['crop_bounds_xyxy'];check('crop-bounds',0<=x0<x1<=w and 0<=y0<y1<=h,path=rec['path'])
        check('crop-unchanged-pixels',Image.open(path).tobytes()==parent_image.crop((x0,y0,x1,y1)).tobytes(),path=rec['path'])
    if 'pdf_crop_bounds_xyxy' in rec and rec['pdf_crop_bounds_xyxy']:
        doc=fitz.open(ROOT/rec['parent']);bounds=fitz.Rect(rec['pdf_crop_bounds_xyxy']);check('pdf-crop-bounds',doc[rec['pdf_page_1_based']-1].rect.contains(bounds),path=rec['path'])
protocol=manifest['preread_protocol'];check('protocol-preserved',digest(ROOT/protocol['path'])==protocol['sha256'])
g=obs['gonur'];a=obs['altyn_depe']
for name in ['photo_panel','drawing_panel']:
    panel=g[name];check('representation-row-sum',sum(panel['row_counts'])==panel['representation_count']==23,panel=name)
    check('second-model-row-agreement',panel['row_counts']==g['second_model_check']['photo_row_counts' if name=='photo_panel' else 'drawing_row_counts'],panel=name)
check('reported-hoard-count-preserved',g['source_reported_hoard_count']==26)
check('representation-gap',g['source_reported_hoard_count']-g['photo_panel']['representation_count']==g['difference_reported_hoard_minus_each_panel']==3)
check('two-panel-sum-scope',g['two_panel_representation_sum']==46 and g['two_panel_sum_is_physical_object_count'] is False)
check('physical-identity-unresolved',g['photo_panel']['physical_identity_count'] is None and g['panel_to_object_join']=='unresolved at individual level')
check('hoard-context-gaps-preserved',all(g[key] is None for key in ['room_number','layer_or_floor','hoard_inventory_id','hoard_direct_date','hoard_palace_phase','associated_sealings_join']))
check('altyn-item-view-join',a['labelled_item_count']==1 and a['linked_drawing_view_count']==3)
check('altyn-exact-locator',(a['excavation'],a['horizon'],a['room'],a['plate'],a['item'])==(5,11,18,94,2))
check('altyn-count-and-value-unresolved',a['individual_impression_count'] is None and a['quantity_value_or_operation'] is None)
for record in [g,a,obs['later_gonur_source']]:check('observation-source-sha256',digest(ROOT/record['source_pdf'])==record['source_sha256'])
for path in OUT.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
        if target.startswith(('http:','https:','#')):continue
        resolved=(path.parent/target.strip('<>')).resolve();check('local-link',resolved.is_file(),source=path.name,target=target)
failed=[rec for rec in checks if not rec['pass']]
payload={'status':'pass' if not failed else 'fail','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'check_count':len(checks),'failed_check_count':len(failed),'checks':checks,'bounded_result':{'gonur_reported_hoard':26,'gonur_photograph_representations':23,'gonur_drawing_representations':23,'physical_identification':'unresolved','altyn_labelled_item_count':1,'altyn_linked_view_count':3,'altyn_main_bands':2,'altyn_individual_impression_count':None},'scope':'These checks verify file integrity, joins recorded in the packet and count arithmetic. Visual and archaeological assessments remain the source-informed observations.'}
if args.output:
    destination=OUT/args.output
    if destination.exists():raise FileExistsError('Existing result retained. Choose a new output endpoint.')
    destination.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({key:payload[key] for key in ['status','check_count','failed_check_count','bounded_result']},indent=2));
if failed:print(json.dumps(failed,indent=2));raise SystemExit(1)
