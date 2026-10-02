from pathlib import Path
import fitz,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent/'sources'
QUERIES={
 'bhaskar_2024_anisotropy':['superior','inferior','ICIT'],
 'mukhopadhyay_2019':['functional class','pre-functional','terminal','numeral'],
 'sinha_2011_network':['results','discussion'],
 'yadav_2011_design':['basic signs','modifiers','compounds'],
}
for stem,terms in QUERIES.items():
 path=ROOT/(stem+'.pdf')
 if not path.exists():
  print(stem,'MISSING');continue
 doc=fitz.open(path)
 print('\nSOURCE',stem,len(doc))
 for i,page in enumerate(doc):
  t=page.get_text()
  found=[s for s in terms if s in t.lower()]
  if found:
   print('PDF',i+1,'TERMS',','.join(found),'END',t[-120:].replace('\n',' '))
   if stem.startswith('bhaskar'):
    for line in t.splitlines():
     if any(s in line.lower() for s in terms):print(' ',line)
