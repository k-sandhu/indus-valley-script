import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,subprocess,hashlib,datetime,copy
from pyproj import Transformer
OWN=Path(sys.argv[1]);RAW=Path(sys.argv[2]);TOOLS=Path(sys.argv[3]);PKG=OWN.parent
SLUGS=['kalibangan','banawali','rakhigarhi','farmana','bhirrana','kunal','mitathal','karanpura']
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,obj):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')
def rel(p):return str(p).replace('\\','/')
selections={'kalibangan':[(1,1)],'banawali':[(1,3)],'farmana':[(1,1),(2,1),(3,2),(4,3)],'mitathal':[(1,1),(2,1)]}
overrides={('banawali','banawali-01','outer-east-north'):'lower-north-exposure',('banawali','banawali-01','outer-east-middle'):'lower-southeast-exposures',('banawali','banawali-01','outer-east-south'):'lower-southeast-exposures',('banawali','banawali-01','acropolis-opposite-face'):'acropolis-opposite',('farmana','farmana-04','c4-east'):'complex4-east-face'}
rejected={('mitathal','mitathal-02','11-west'):'Wall-face envelope is ambiguous in the final overlay; excluded rather than interpreted as an outer face.',('mitathal','mitathal-02','11-east'):'The pick can follow an internal brick boundary; excluded after overlay review.'}
reasons={
 'rakhigarhi':'No Harappan architectural face can be tied to the inspected 10 m composite. No qualifying north-bearing plan was recovered in the indexed and held sources.',
 'bhirrana':'The 700 m, 1600 m and 4000 m imagery inspections do not identify a plan-matched Harappan wall face. The additional report chapter provides text and tables, without a qualifying architectural plan.',
 'kunal':'The starting coordinate is coarse and we cannot establish which visible patch is the archaeological mound in the 700 m, 1600 m and 4000 m inspections. No qualifying plan is available; visible field and modern transport lines are excluded.',
 'karanpura':'The imagery resolves cultivation and disturbed ground, without a plan-matched ancient wall. Figure 10 locates contours, canals and excavation trenches, not resolved Harappan wall faces.'}
methods={
 'kalibangan':'The paired bright mounds in the 1600 m and 700 m composites correspond in relative arrangement to KLB-1 west of KLB-2 in Fig.3.7. Point is a picked mound-area centre, not an architectural control.',
 'banawali':'The oval bright isolated mound south of the modern village is visible in all four layers at both scales. Point is its approximate centre; the perimeter cannot be identified as a wall face.',
 'rakhigarhi':'Candidate open mound area north of the dense village, beside the ponds, selected in the composite. The exact excavation area and RGR identifier remain unconfirmed.',
 'farmana':'The excavators coordinate in sites-located-v1.json falls in cultivated ground southwest of the modern village. We inspected it at two scales after imagery became available, but did not independently identify the excavation trenches.',
 'bhirrana':'Infrastructure starting coordinate inspected at 700 m, 1600 m and 4000 m. Agriculture, modern settlement and bare patches are visible; no excavation area is securely identified. Coordinate remains a search point.',
 'kunal':'Infrastructure Wikidata starting coordinate, with coarse precision; inspected at three scales. The archaeological mound is not independently located.',
 'mitathal':'Candidate bare mound area south of the canal near the infrastructure point, inspected at two scales. We cannot locate the 1968 MTL-1 and MTL-2 cuttings in 10 m pixels; coordinate remains approximate.',
 'karanpura':'Infrastructure ASI starting point inspected in both-scale composites against the contour/trench layout. The larger disturbed area is visible but individual ancient architecture cannot be identified.'}
notes={
 'kalibangan':'Schematic plan, unresolved book/author identity. Magnetic-symbol interpretation and unknown survey year leave true north unresolved. Longitudinal and transverse walls differ and are kept separate. The singleton lower-city face fails the neighbour rule. No imagery line or registration is admitted.',
 'banawali':'Final v3 measurements follow enlarged overlay checks. Direction groups are split when their measured span exceeds 6 degrees. The rule-selected main may therefore be a singleton; its warning is retained. Two acropolis faces share one wall, have correlated errors and do not establish independent buildings. No imagery line or registration is admitted.',
 'farmana':'Figure 17 prose contains a stated angle on printed p.22; it was encountered incidentally and excluded. Survey year 2008 is the implied end of the 2007-08 season, not an independently documented arrow date. Different figures are separate plan sources. Figure 14 panels retain their layer separation. Its opposite upper-layer wall faces are correlated. Figure 19 complex 4 east face is separated because the original group exceeded 6 degrees. Its main system includes two faces of a common north wall and their errors are correlated. All sigmas and formula SEs are retained exactly. No imagery match or registration is justified.',
 'mitathal':'The newly acquired 1975 report supplies Figs.3 and 4 with internal 1968 labels and scales. Period IIA and Late Harappan IIB faces are labelled separately. Opposite faces of a single wall share survey and drawing errors; formula SE does not remove that correlation. Two ambiguous central Figure 4 picks are excluded after review. Figure 3 north remains unspecified. Figure 4 needle is treated as magnetic and corrected with IGRF-14 for 1968 at the infrastructure coordinate. No imagery architectural line or registration is admitted.'}
all_sources=[];selection_record=[]
for slug in SLUGS:
 snapfile=OWN/'picks'/slug/'infra-snapshot-v2.json'
 if not snapfile.exists():snapfile=snapfile.with_name('infra-snapshot-v1.json')
 snap=read(snapfile);im=snap['imagery'];plans=snap['plans']['plans'];coords=snap['site']['coordinate_used']
 if slug in ['kalibangan','banawali','rakhigarhi']:
  x,y,epsg={'kalibangan':(415550,3260800,32643),'banawali':(537950,3274350,32643),'rakhigarhi':(608150,3241050,32643)}[slug]
  lon,lat=Transformer.from_crs(epsg,4326,always_xy=True).transform(x,y);coords=[lat,lon]
 imagery=dict(id='imagery',kind='imagery',scene_ids=im.get('composite_scene_ids',[]),scene_datetimes=[s['datetime'] for s in im.get('scenes',[]) if s.get('used_in_composite')],manifest_path=rel(snapfile),composite=im.get('composite'),inspection='RGB, brightness, NIR and edge-enhanced brightness at 1600 m and 700 m; 4000 m RGB, NIR and edge brightness also inspected for Bhirrana and Kunal.',measurement_status='not measurable: no plan-matched ancient architectural face resolved')
 sources=[imagery];all_sources.append(dict(town=slug,**imagery,scene_records=im.get('scenes',[]),infrastructure_record=rel(snapfile)))
 for pl in plans:
  all_sources.append(dict(town=slug,id=pl['id'],kind='plan',library_record=pl,used_for='architectural identification and plan measurement' if slug in selections else 'source inspection; no eligible architectural face'))
 town=dict(schema_version=1,slug=slug,measurer='A',authors=[{'model':'GPT-6','harness':'Codex'}],located_point=dict(latitude=coords[0],longitude=coords[1],method=methods[slug]),sources=sources,lines=[],registrations=[],notes=notes.get(slug,reasons.get(slug)),unmeasurable_reason=reasons.get(slug),source_snapshot=rel(snapfile),imagery_unmeasurable_reason=imagery['measurement_status'],calibration_record=rel(PKG/'infra-v1/validation-v1/summary.json'),measurement_selection=[])
 for n,v in selections.get(slug,[]):
  resultpath=OWN/f'picks/{slug}/plan-0{n}-lines-v{v}.json';pickpath=OWN/f'picks/{slug}/plan-0{n}-picks-v{v}.json';r=read(resultpath);sid=r['source_id']
  if slug=='mitathal':
   record=read(RAW/'mitathal/download-v1/record.json')
   pl=dict(id=sid,citation={'author':'Suraj Bhan','year':1975,'title':'Excavation at Mitathal (1968) and Other Explorations in the Sutlej-Yamuna Divide','publisher':'Kurukshetra University'},source={**record,'path':rel(RAW/'mitathal/download-v1/source.pdf')},pdf_page=32 if n==1 else 34,printed_page='unnumbered foldout following printed p.12',figure_or_plate=f'Fig. {3 if n==1 else 4}')
   all_sources.append(dict(town=slug,id=sid,kind='plan',record=pl,used_for='new architectural plan measurement'))
  else:pl=next(p for p in plans if p['id']==sid)
  src=dict(id=sid,kind='plan',citation=pl['citation'],pdf_page=pl['pdf_page'],printed_page=pl['printed_page'],figure=pl['figure_or_plate'],source_record=pl['source'],north_class=r['north']['class'],north_evidence=r['north']['evidence'],survey_year=r['north'].get('survey_year'),north=r['north'],measured_arrow=r['arrow'],measurement_result=rel(resultpath),picks=rel(pickpath),render_sidecar=r['render_sidecar'])
  town['sources'].append(src)
  admission=dict(source_id=sid,picks=rel(pickpath),measurement_result=rel(resultpath),sidecar=r['render_sidecar'],accepted_ids=[],rejected_ids={},system_overrides={})
  for line in r['lines']:
   key=(slug,sid,line['id'])
   if key in rejected:admission['rejected_ids'][line['id']]=rejected[key];continue
   row=copy.deepcopy(line);row['source_id']=sid
   row['source_locator']=dict(pdf_page=pl['pdf_page'],printed_page=pl['printed_page'],figure=pl['figure_or_plate'],source_path=pl['source']['path'],measurement_result=rel(resultpath))
   if key in overrides:
    row['system_from_picks']=row['system'];row['system']=overrides[key];admission['system_overrides'][row['id']]=row['system']
   town['lines'].append(row);admission['accepted_ids'].append(row['id'])
  town['measurement_selection'].append(admission)
  selection_record.append(dict(town=slug,**admission))
 write(OWN/f'picks/{slug}/town-input-v1.json',town)
 subprocess.run([sys.executable,'-I',str(TOOLS/'systems.py'),str(OWN/f'picks/{slug}/town-input-v1.json'),str(OWN/f'towns/{slug}.json'),'--summary',str(OWN/'summary-H.csv')],check=True)
for slug,dir in [('bhirrana','download-v1'),('bhirrana','download-v2'),('mitathal','download-v1')]:
 all_sources.append(dict(town=slug,id=dir,kind='acquisition-attempt',record=read(RAW/slug/dir/'record.json')))
# These held volumes were inspected while looking for additional plans.
for slug,path,url,locator in [
 ('rakhigarhi','data/raw/2026-10-21-town-orientations-verification/infra/plans/rakhigarhi/excavationsatrakhigarhi19972000amarendranath_457_Z/source.pdf','https://archive.org/details/excavationsatrakhigarhi19972000amarendranath_457_Z','searchable plan references in the held 396-page report'),
 ('bhirrana','data/raw/2026-10-21-town-orientations-verification/infra/plans/juni-kuran/report2004/source.pdf','https://ignca.gov.in/Asi_data/87942.pdf','text index checked for Bhirrana; no hits'),
 ('bhirrana',str(RAW/'bhirrana/download-v2/source.pdf'),'https://ignca.gov.in/Asi_data/88233.pdf','contents PDF p.5; chapter PDF pp.74–82/printed pp.60–68; PDF p.70 was a rejected Bator locator')]:
 pp=Path(path);all_sources.append(dict(town=slug,id='inspected-'+pp.parent.name,kind='source-review',path=rel(pp),url=url,bytes=pp.stat().st_size,sha256=hashlib.file_digest(pp.open('rb'),'sha256').hexdigest(),retrieved_utc=None,rights_notice='Held scan or local acquisition record; no independently verified redistribution permission. Local only.',locator=locator))
write(OWN/'sources-H.json',dict(schema_version=1,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources=all_sources,rights_policy='Acquired reports and renders remain local. Scene terms and hashes are retained from the infrastructure records.'))
write(OWN/'selection-H-v1.json',dict(schema_version=1,measurement_selection=selection_record,grouping_note='Explicit overrides split groups wider than six degrees; singleton warnings are retained and never suppress the rule-selected main.'))
