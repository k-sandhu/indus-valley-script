from pathlib import Path
import fitz,subprocess
out=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-office-seal-evidence')
for key,path,pages in [('rao1985','data/raw/2026-10-21-town-axes/dating/lothal/rao1985lothal-part2.pdf',[71,72,73,74]),('rao1979','data/raw/2026-10-21-town-axes/dating/lothal/rao1979lothal-part1.pdf',[122,123,124,125])]:
 d=fitz.open(path)
 for n in pages:
  img=out/f'{key}-pdf{n}.png'; d[n-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(img)
  result=subprocess.run(['tesseract',str(img),str(img.with_suffix(''))],capture_output=True,text=True)
  print(key,n,img.with_suffix('.txt').read_text(encoding='utf8')[:12000])

