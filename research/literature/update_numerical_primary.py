"""Record source adjudication without silently identifying a historical integer ID."""
from pathlib import Path
import json
B=Path(__file__).parent
p=B/'metrology/numerical_source_premises.json'
j=json.loads(p.read_text(encoding='utf-8'))
e=next(x for x in j['premises'] if x['id']=='E2_equal_tablet_faces')
e['historical_object_id']='ICIT3786 in the chapter; candidate H904/current object1786, historical ID join remains unconfirmed'
e['graphic_conflict']='Prose callsW032 three long strokes; current conventionW032 means two tall strokes. Original Vats477 crescent/U face independently shows three long strokes, supporting the prose coefficient in the candidate artifact rather than correction to two.'
e['primary_candidate_adjudication']={
 'physical_artifact':'Vats1940 no.477, excavationJ213, MoundD; matches supplied current H904 metadataJ213(D)477',
 'metadata_source':'Vats1940 text volume, printed349/PDF378, table row477',
 'metadata_url':'https://ignca.gov.in/Asi_data/18220.pdf',
 'metadata_sha256':'022fc5761c16f63c36bb83429a4ecf1cd23ff33b0b13d12f1c0445962f0614ec',
 'table_values':{'plate_no':477,'find_no':'J213','area':'D','material':'white steatite','type':'h','depth_below_surface':'2 feet 0 inches','size_inches':[0.65,0.28]},
 'image_source':'Vats1940 plates volume, PlateXCVI/PDF200, no.477, sixth object row, final column; two faces under one object label',
 'image_url':'https://ignca.gov.in/Asi_data/9842.pdf',
 'image_sha256':'1855dc750a070c570eaecb78c8217dd350ad7e559a65898a57242545fb54a442',
 'observed_counts':{'crescent_U_face_long_strokes':3,'circles_face_long_strokes':2,'circles_face_short_strokes':'unresolved at retained scan resolution'},
 'confidence':'high for coarse long-stroke counts and metadata join; no full glyph transcription',
 'crop':'primary_numeric/vats_h904/477_crop12x.png',
 'metadata_render':'primary_numeric/vats_h904/text_pdf378.png',
 'historical_id_limit':'Author Fig16 has not been visually inspected. Distinctive two-face configuration suggests candidate identity but does not certify historical ICIT3786 equals current1786.',
 'semantic_limit':'Object pairing and visible counts do not establish equal quantities, commensurate units, assigned position multipliers or treatment of the other signs.'
}
p.write_text(json.dumps(j,indent=2,ensure_ascii=False),encoding='utf-8')
p=B/'metrology/numerical_source_audit.md'
s=p.read_text(encoding='utf-8')
s=s.replace('The historical number now points to a different inscription; stable artifact identification requires the author figure or an older register.','The same integer in the current corpus points to a different inscription. A matching physical candidate has now been found: Vats1940 PlateXCVI no.477 (plates PDF200) and printed349/PDF378 table join it to excavationJ213 in MoundD, matching current H904. Its crescent/U face has three long strokes and its opposite overlapping-circle face has two, supporting the prose coefficient3. The short marks on the latter remain less clear. The author figure or historical register is still needed to certify the historical integerID join. [Original plates](https://ignca.gov.in/Asi_data/9842.pdf), [original excavation table](https://ignca.gov.in/Asi_data/18220.pdf).')
p.write_text(s,encoding='utf-8')
p=B/'source_retrieval_log.json'; a=json.loads(p.read_text(encoding='utf-8'))
for x in a:
 if x.get('id')=='franke_govscan_74331':
  x.update({'requested_identity':'Franke1991 via government scan locator','identity_verified':False,'actual_title':'Reports on Field Work Carried out at Mohenjo-Daro: Interim Reports Vol.1, Pakistan1982–83, IsMEO–AachenUniversityMission','actual_editors':['M.Jansen','G.Urban'],'source_inspection':'Original PDF6 title and PDF7 copyright; retained renders/franke/pdf006.png and pdf007.png','correction':'This source is InterimReportsVol1, not Franke1991 or Vidale1987a InterimReportsVol2. Retained acquisition filename is a transport identifier. Do not cite as the sought M1383 excavation chapter.'})
a.append({'id':'fuls2020_figure16_public_asset_attempt','requested_url':'https://www.researchgate.net/profile/Andreas-Fuls/publication/373522958/figure/fig9/AS%3A11431281184893102%401693469477790/Numerical-relationships-between-Sign-700-and-Sign-840-The-bases-of-long-and-stacked.ppm','discovery':'Observed image href in public author-uploaded Fig16 landing; malformed relative/figure prefix repaired to profile path','http_status':403,'content_type':'text/html; charset=UTF-8','status':'Author diagram not acquired; ordinary public request blocked. No access-control bypass.'})
p.write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding='utf-8')
p=B/'source_identity_index.json'; a=json.loads(p.read_text(encoding='utf-8'))
a.append({'id':'franke_govscan_74331','magic':'PDF','requested_url':'https://ignca.gov.in/Asi_data/74331.pdf','actual_title':'Reports on Field Work Carried out at Mohenjo-Daro: Interim Reports Vol.1, Pakistan1982–83','editors':'M.Jansen and G.Urban','identity_correction':'Not Franke1991, not sought Vidale1987a InterimReportsVol2; original title PDF6 inspected.'})
p.write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding='utf-8')
print('Updated numerical source adjudication and source identity provenance.')
