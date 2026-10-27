"""Apply final display-only labels to a new HTML, preserving the reviewed v2 file."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parent
R=Path('D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot/integration-v2')
src=R/'catalogue-integrated-v2.html';out=R/'catalogue-integrated-v2-polished.html'
assert not out.exists()
page=src.read_text(encoding='utf8')
page=page.replace("n+' targets'","n+(n===1?' target':' targets')")
# Shared page paths keep their reviewed catalogue labels; only the displayed link text changes.
page=page.replace('CISI source page for L-163','CISI volume 1, PDF 313 / printed 277')
page=page.replace('CISI source page for L-164','CISI volume 1, PDF 313 / printed 277')
page=page.replace('CISI source page for L-167','CISI volume 1, PDF 313 / printed 277')
page=page.replace('CISI source page for L-146','CISI volume 1, PDF 309 / printed 273')
out.write_text(page,encoding='utf8')
def rec(p):return {'physical_path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
checks={'singular_count':"n===1?' target':' targets'" in page,'generic_shared_page_titles':'CISI source page for L-163' not in page,'twenty_cards':page.count('<article ')==20,'same_image_sources':re.findall(r'<img[^>]+src="([^"]+)"',src.read_text(encoding='utf8'))==re.findall(r'<img[^>]+src="([^"]+)"',page),'inline_favicon':'rel="icon" href="data:image/svg+xml' in page}
with (P/'polish-manifest-v1.json').open('x',encoding='utf8') as f:json.dump({'input':rec(src),'output':rec(out),'code':rec(Path(__file__)),'checks':checks,'passed':all(checks.values()),'facts_changed':False},f,indent=2);f.write('\n')
print(json.dumps(checks))
