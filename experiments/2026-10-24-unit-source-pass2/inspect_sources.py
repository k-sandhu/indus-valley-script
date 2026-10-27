from pathlib import Path
import re,fitz,json
R=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-pass2')
for label in ['cisi31-institution','publisher','cisi32-store']:
 text=(R/(label+'.html')).read_text(encoding='utf-8');print(label,[(a,b) for a,b in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',text,re.S) if any(t in a.lower() for t in ['pdf','tiede','full','document'])][:25]);print(re.sub('<[^>]+>',' ',text)[:100] if label=='cisi32-store' else '')
d=fitz.open('data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf')
p=d[296]; rect=fitz.Rect(45,425,560,562);p.get_pixmap(matrix=fitz.Matrix(3,3),clip=rect).save(R/'20781-entry-candidate.png')
(R/'20781-entry-candidate.txt').write_text(p.get_text(clip=rect),encoding='utf-8')
p=d[265];rect2=fitz.Rect(20,386,595,423);p.get_pixmap(matrix=fitz.Matrix(3,3),clip=rect2).save(R/'20781-context-candidate.png')
h=fitz.open('research/corpus/primary/kenoyer_meadow2010_inscribed_objects.pdf');(R/'KM2010-pdf3.txt').write_text(h[2].get_text(),encoding='utf-8')
print('1999 extracted chars',sum(len(p.get_text()) for p in fitz.open('data/raw/2026-10-12-transmission-hypothesis/material/acquisition-v2/kenoyer1999-harappa.pdf')))
