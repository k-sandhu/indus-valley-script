import fitz,re,json,pathlib
p=pathlib.Path('data/raw/2026-10-20-fresh-test-collection');d=fitz.open(p/'farmana.pdf')
ids=[59,116,143,151,161,200,243,246,279,287,288,335,420,459,502,515,516,518,519,520,588,646,685,691,859,860,918,971,984,993]
out=[]
for n in ids:
 hits=[]
 for i in range(267,382):
  t=d[i].get_text();lines=t.splitlines()
  if any(re.fullmatch(str(n)+r'(?: \(GW\))?',l.strip()) for l in lines):
   captions=[l for l in lines if l.startswith('Figure')]
   hits.append({'pdf_page':i+1,'printed_page':i-13,'captions':captions})
 out.append({'specimen':n,'locations':hits})
(p/'pottery-locators.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=1))
