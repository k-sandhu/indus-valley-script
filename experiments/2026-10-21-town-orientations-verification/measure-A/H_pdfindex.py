import sys
sys.dont_write_bytecode=True
import fitz,re,json
sys.stdout.reconfigure(encoding='utf-8')
doc=fitz.open(sys.argv[1]);term=sys.argv[2]
print('pages',len(doc))
for i,p in enumerate(doc):
 t=p.get_text()
 if re.search(term,t,re.I):
  lines=t.splitlines()
  # List page locators and caption-like text only; never reproduce numeric directions.
  hits=[s.strip() for s in lines if re.search(r'fig|plate|plan|'+term,s,re.I) and not re.search(r'orient|degree|\d\s*°',s,re.I)]
  print(json.dumps(dict(pdf_page=i+1,hits=hits[:5]),ensure_ascii=False))
