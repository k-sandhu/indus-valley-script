import csv,json,re,hashlib,datetime
from pathlib import Path
import fitz
ROOT=Path('experiments/2026-10-24-object-identity-extension')
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-object-identity-extension')
SRC=Path('data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf')
def dump(p,x): p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
assert not (RAW/'identity-assertions-v1.json').exists(), 'Frozen output exists; choose a new version before rerunning'
rows=list(csv.DictReader(open('experiments/2026-10-21-post-catalogue-finds/objects.csv',encoding='utf-8-sig')))
target=[x for x in rows if x['site_code']=='DHV' and 5<=int(x['row_id'].split('-')[-1])<=32]
doc=fitz.open(SRC)
ctx={};cat={};access=[]
for n in range(264,267):
 p=doc[n-1]; rect=fitz.Rect(30,105 if n==264 else 65,118,600)
 text=p.get_text(clip=rect); (RAW/f'context-p{n}-identity.txt').write_text(text,encoding='utf-8')
 access.append({'pdf_page':n,'printed_page':n-17,'rectangle':list(rect),'content':'serial and accession columns; no images'})
 for a,b in re.findall(r'(\d+)\.\s+(\d+)',text): ctx[int(a)]=(b,n)
# Restrict catalogue text to serial/accession strip; never render image/remarks area.
needed={int(re.search(r'seal catalogue (\d+)',x['other_numbers'])[1]) for x in target}
for n in range(277,330):
 p=doc[n-1]; rect=fitz.Rect(50,100,141,750)
 text=p.get_text(clip=rect)
 pairs=re.findall(r'(\d+)\.\s+(\d+)',text)
 hits=[(int(a),b) for a,b in pairs if int(a) in needed]
 if hits:
  (RAW/f'catalogue-p{n}-identity.txt').write_text(text,encoding='utf-8')
  access.append({'pdf_page':n,'printed_page':n-17,'rectangle':list(rect),'content':'serial and accession columns mechanically extracted; matched rows displayed'})
  for a,b in hits: cat[a]=(b,n)
 if needed.issubset(cat): break
out=[]
for x in target:
 c=int(re.search(r'seal catalogue (\d+)',x['other_numbers'])[1]); t=int(re.search(r'context table (\d+)',x['other_numbers'])[1]); a=ctx.get(t);b=cat.get(c)
 out.append({'row_id':x['row_id'],'source_registration':x['registration'],'context_serial':t,'context_observation':a,'catalogue_serial':c,'catalogue_observation':b,'disposition':'supported_two_table_identity' if a and b and a[0]==b[0]==x['registration'] else 'conflict_or_unresolved','family_disposition':'candidate_preserved','candidate_families':x['local_family_ids'],'physical_merge':False,'assertion_type':'source_catalogue_identity','confirmation_eligibility':False})
dump(RAW/'identity-assertions-v1.json',out)
dump(RAW/'access-log-v1.json',{'participant':'gpt-6.1-sol / Codex collaboration / direction 1','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pages':access,'exceptions':[{'pdf_pages':list(range(268,301)),'content':'first 150 text characters displayed per page during locator search; some motif descriptions and inscription counts; no sign sequences or images'},{'pdf_pages':[277],'content':'header blocks and overly wide x0-180 identity clip displayed partial remarks; no sign sequences or images'}],'freshness_certified':False})
summary={'target_rows':len(out),'supported_two_table_identity':sum(x['disposition']=='supported_two_table_identity' for x in out),'conflict_or_unresolved':sum(x['disposition']!='supported_two_table_identity' for x in out),'candidate_family_status_preserved':len(out),'new_supported_family_links':0,'physical_merges':0,'context_pages':[264,265,266],'catalogue_pages':sorted({x['catalogue_observation'][1] for x in out if x['catalogue_observation']})}
dump(ROOT/'results-v1.json',summary)
manifest=[]
for p in [SRC,ROOT/'PROTOCOL.md',*RAW.glob('*')]:
 b=p.read_bytes();manifest.append({'logical_path':str(p).replace('D:\\projects\\indus_valley_script\\','').replace('\\','/'),'physical_path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'rights':'rights-unverified; local-only' if p!=ROOT/'PROTOCOL.md' else 'own-work'})
dump(ROOT/'source-manifest-v1.json',{'source_id':'bisht-2015-held','title_as_in_inherited_register':'Dholavira Report','access_route':'held local PDF; no new download','url':None,'url_status':'not recorded in inherited source register','review_time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':manifest})
print(json.dumps(summary,indent=2))
print(*[x for x in out if x['disposition']!='supported_two_table_identity'],sep='\n')
print('Identity columns:',[(x['row_id'],x['context_observation'],x['catalogue_observation']) for x in out])
