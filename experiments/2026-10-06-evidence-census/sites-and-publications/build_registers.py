import csv, json, pathlib, collections, argparse

REPO = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent
INPUTS = [REPO / 'data/normalized/lipi_observed_faces.jsonl', REPO / 'data/normalized/mayig_faces.jsonl']
EXTRA_SITES = ['Tell Jokha', 'Shahr-i Sokhta', 'Mundigak', 'Tell Abraq', 'Umm an-Nar', 'Hili', 'Ra\'s al-Jinz', 'Bet Dwarka', 'Manda']
COUNTRIES = {
 'Pakistan': ['Harappa','Mohenjo-daro','Chanhu-daro','Nausharo','Allahdino','Kot-Diji','Lakhanjo-daro','Bala-kot','Amri','Naru-Waro-dharo','Tarkhanewala-dera','Nuhato','Rajanpur','Gumla','Hissam-dheri','Rahman-deri','Miri Qalat','Bakkar Buthi','Gharo Bhiro','Baror','Wattoowala','Jhukar','Lohumjo-daro','Pirak','Nindowari-damb','Gola Dhoro (Bagasra)','Ornach area','Rappwala Ther','Guddal A','Derawar Ther','Tigrana','Murda Sang','Juna Khatiya','Ganweriwala','Sibri','Shortughai'],
 'India': ['Dholavira','Kalibangan','Banawali','Rakhigarhi','Kanmer','Farmana','Karanpura','Shikarpur','Bhirrana','Surkotada','Rupar','Khirsara','Alamgirpur','Chandigarh','Desalpur','Daimabad','Rodji','Hulas','Pabumath','Pabumath','Kunal','Manda','Bet Dwarka'],
 'Afghanistan': ['Shortughai'], 'Iraq': ['Ur','Kish','Nippur','Tell Umma','Tello','Girsu','Tell Jokha'], 'Iran': ['Susa','Luristan','Tepe Yahya','Shahr-i Sokhta'],
 'Bahrain': ['Failaka','Qala\'at al-Bahrain','Saar','Janabiyah','Dilmun'], 'Kuwait': ['Failaka'], 'Oman': ["Ra's al-Junayz", "Ra's al-Jinz",'Salut','Hajar'],
 'Turkmenistan': ['Altyn Depe','Gonur Depe'], 'UAE': ['Kalba','Tell Abraq','Umm an-Nar','Hili'], 'Kazakhstan': [], 'Uzbekistan': [], 'Tajikistan': [], 'Unknown / ambiguous': ['Unknown','Karzakan']
}
ALIASES = {'Ra\'s al-Junayz':"Ra's al-Jinz", 'Gola Dhoro (Bagasra)':'Gola Dhoro (Bagasra)', 'Kot-Diji':'Kot Diji'}

def country(site):
 if site=='Shortughai': return 'Afghanistan'
 for c, vals in COUNTRIES.items():
  if site in vals: return c
 return 'Unverified / review'

def main():
 counts={}
 input_rows={}
 for path in INPUTS:
  c=collections.Counter(); missing=0; total=0
  with path.open(encoding='utf-8') as f:
   for line in f:
    row=json.loads(line); total+=1; s=row.get('site')
    if s is None or str(s).strip()=='': missing+=1
    else: c[str(s)]+=1
  counts[path.name]=c; input_rows[path.name]={'rows':total,'missing_site':missing,'distinct_site_values':len(c)}
 all_names=set().union(*(set(c) for c in counts.values()))|set(EXTRA_SITES)
 rows=[]
 for s in sorted(all_names, key=str.casefold):
  lipi=counts['lipi_observed_faces.jsonl'].get(s,0); mayig=counts['mayig_faces.jsonl'].get(s,0)
  pubids=[]; observed=[]; basis=''
  if s=='Lothal':
   pubids=['CISI1-1987','RAO-1979','FRENZ-TOSI-2005','FULS-2023']; observed=[{'quantity':90,'unit':'sealings','basis':'secondary article attributes about 90 Lothal sealings to ICIT; cites Rao 1979 pp.113–114; approximate, not recounted from primary report','url':'https://www.nature.com/articles/s41599-023-02320-7','locator':'§ “commodity-sealings”, lines 433 onward'}]
  elif s=='Kanmer':
   pubids=['CISI1-1987','KANMER-2011','KANMER-2012-CH8','CAMBRIDGE-2002']; observed=[{'quantity':3,'unit':'clay sealings','basis':'secondary project-gallery article says Kanmer yielded three clay sealings with central hole; figure 3a-b','url':'https://www.cambridge.org/core/journals/antiquity-project-gallery/article/redefining-the-harappan-hinterland/11D7D7DE4161A3DDB82755A7856D5521','locator':'web lines 548–563'}]
  elif s=='Farmana':
   pubids=['FARMANA-2008','FARMANA-2011','FULS-2023']; observed=[{'quantity':4,'unit':'objects','basis':'report summary lists two square steatite seals and two terracotta objects with seal impressions; includes one seal from prior season, so not all necessarily inscribed','url':'https://www.scribd.com/document/213664074/A-Report-on-Excavations-at-Farmana-2007-08','locator':'chapter “Seals and Sealing”, printed p.101'}]
  elif s=='Dholavira': pubids=['CISI3-2010','CISI3.2-2019','DHOLAVIRA-2015','FULS-2023']
  elif s in ['Harappa','Mohenjo-daro']: pubids=['CISI1-1987' if s=='Harappa' else 'CISI1-1987','CISI3-2010','CISI3.2-2019','FULS-2023']
  elif s in ['Mundigak','Shahr-i Sokhta','Altyn Depe','Gonur Depe']: pubids=['CISI3-2010','CISI3.2-2019','CISI3.3-2022']
  elif s in ['Ur','Kish','Nippur','Tell Umma','Tello','Girsu','Susa','Tepe Yahya','Failaka','Saar','Qala\'at al-Bahrain',"Ra's al-Junayz"]: pubids=['CISI3-2010','CISI3.2-2019','CISI3.3-2022']
  else: pubids=['CISI-coverage-not-site-joined'] if lipi or mayig else []
  metadata={k:'Not assessed' for k in ['findspot','stratum_or_phase','absolute_dates','dimensions','material','photographs','drawings','museum_or_excavation_registration']}
  if s=='Farmana': metadata.update({'material':'Present (report names steatite and terracotta; printed p.101)','photographs':'Present (Figs.106-109)','drawings':'Present (Figs.106-109)'} )
  if s=='Kanmer': metadata.update({'photographs':'Present (Cambridge article Fig.3a-b)','drawings':'Not assessed','material':'Present for reported clay sealings','findspot':'Not assessed beyond site attribution'})
  if s=='Lothal': metadata.update({'photographs':'Present (Frenez and Tosi report high-resolution digital photographs)','material':'Present for terracotta sealings','findspot':'Not assessed at object-level'})
  rows.append({'site':s,'country_or_region':country(s),'coordinates':None,'excavation_campaigns':'Not assessed in this bounded census','primary_reports':pubids,'source_reported_counts':observed,'count_basis_note':basis or 'No exact site-level object count verified in this package; see publication register and source status.','metadata':metadata,'digital_availability':'Indexed in local Lipi export' if lipi else ('Mayig local subset only' if mayig else 'No record in the two counted local files; other local coverage not assessed'),'reuse_terms':'Source-specific; not assessed for every publication','local_lipi_face_rows':lipi,'local_mayig_face_rows':mayig,'local_count_unit':'rows in source-specific JSONL file grouped by literal site field; not unique objects','status':'Verified computation' if lipi or mayig else 'Proposed','source_coverage_note':'Site name came from the pinned local corpus or explicitly named bibliography/search result; site-specific publication join is incomplete.'})
 (OUT/'site-register.json').write_text(json.dumps({'as_of':'2026-10-06','status':'Exploratory','scope':'Reproducible local site values plus explicit source-discovered out-of-corpus locations. This is a working register, not a complete archaeological census.','inputs':input_rows,'sites':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 with (OUT/'site-register.csv').open('w',encoding='utf-8-sig',newline='') as f:
  fields=['site','country_or_region','local_lipi_face_rows','local_mayig_face_rows','local_count_unit','primary_reports','source_reported_counts','metadata','digital_availability','reuse_terms','status']
  w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
  for r in rows:w.writerow({k:json.dumps(r[k],ensure_ascii=False) if isinstance(r[k],(dict,list)) else r[k] for k in fields})
 print(json.dumps({'site_rows':len(rows),'lipi':input_rows['lipi_observed_faces.jsonl'],'mayig':input_rows['mayig_faces.jsonl'],'rows_with_lipi':sum(bool(x['local_lipi_face_rows']) for x in rows),'rows_with_mayig':sum(bool(x['local_mayig_face_rows']) for x in rows)},indent=2))
if __name__=='__main__':main()
