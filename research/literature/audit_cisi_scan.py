"""Audit repeated page images without treating photographed objects as new finds."""
from pathlib import Path
import fitz,hashlib,json,collections
ROOT=Path(__file__).resolve().parent
doc=fitz.open(ROOT/'sources'/'joshi_parpola_1987_cisi1.pdf')
data=[]
cache={}
for i,page in enumerate(doc):
    hashes=[]
    for im in page.get_images(full=True):
        x=im[0]
        if x not in cache:
            cache[x]=hashlib.sha256(doc.extract_image(x)['image']).hexdigest()
        hashes.append(cache[x])
    data.append({'pdf_page':i+1,'images':hashes,'text_chars':len(page.get_text())})
groups=collections.defaultdict(list)
for row in data:
    groups[tuple(row['images'])].append(row['pdf_page'])
duplicate=[v for k,v in groups.items() if k and len(v)>1]
(ROOT/'cisi1_page_image_audit.json').write_text(json.dumps({'pages':data,'duplicate_groups':duplicate},indent=2),encoding='utf-8')
print('pages',len(doc),'duplicate groups',len(duplicate))
print(duplicate[:12])
print('offsets',collections.Counter(v[1]-v[0] for v in duplicate).most_common(10))
