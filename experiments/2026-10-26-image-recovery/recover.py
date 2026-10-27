"""Census held images and prepare the prospectively bounded review; run at repo root."""
import csv, json, hashlib, re
from pathlib import Path
from collections import Counter, defaultdict
from PIL import Image, ImageOps, ImageDraw
import fitz

P=Path('experiments/2026-10-26-image-recovery')
R=Path('D:/projects/indus_valley_script/data/raw/2026-10-26-image-recovery')
I=Path('D:/projects/indus_valley_script/data/lipi/public/seal_images')
OLD=Path('experiments/2026-10-13-image-index-and-units')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,x):
    p=R/name
    assert not p.exists(),p
    p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def main():
    a=json.loads(Path('data/raw/2026-10-24-object-identity-pass3/asset-inventory-v1.json').read_text())
    index={x['file']:x for x in csv.DictReader((OLD/'run-2026-10-13/images/image-files.csv').open())}
    pages={x['key']:x for x in csv.DictReader((OLD/'run-2026-10-13/pages/key-pages.csv').open())}
    groups=defaultdict(list)
    for n in a['all_names']: groups[index[n]['sha256']].append(n)
    inv=[]
    for n in a['unmapped_files']:
        p=I/n; im=Image.open(p); prior=index.get(n,{})
        m=re.match(r'vol([12])_page_(\d+)',n)
        inv.append({'image_logical_path':'data/lipi/public/seal_images/'+n,'image_physical_path':str(p),'filename':n,'sha256':sha(p),'bytes':p.stat().st_size,'width':im.width,'height':im.height,'anonymous':bool(m),'source_page_hint':{'volume':int(m[1]),'pdf_page':int(m[2])} if m else None,'prior_keys':prior.get('keys',''),'prior_views':prior.get('views',''),'prior_note':prior.get('note',''),'prior_index_status':'catalogue-indexed' if prior.get('keys') else 'unresolved','exact_duplicate_names':groups[sha(p)],'disposition':'inherited catalogue assignment' if prior.get('keys') else 'unresolved; source-page review needed'})
    if not (R/'unmapped-inventory-v1.json').exists(): dump('unmapped-inventory-v1.json',inv)
    anon=[x for x in inv if x['anonymous']]
    if not (R/'anonymous-dispositions-v1.json').exists(): dump('anonymous-dispositions-v1.json',anon)
    pilot=['L-146_A_L-146_B.jpg','L-164_A_L-165_A.jpg','L-167_A.jpg']
    chosen=[]
    for n in pilot:
        prior=index[n]; key=prior['keys'].split(';')[0]; pg=pages.get(key,{'volume':'1','pdf_page':'309'})
        chosen.append({'filename':n,'source_page_hint':{'volume':int(pg['volume']),'pdf_page':int(pg['pdf_page'])},'prior_keys':prior['keys'],'prior_views':prior['views'],'selection':'pilot held asset'})
    chosen += [{**x,'selection':'anonymous unresolved lexical order'} for x in anon if not x['prior_keys']][:24-len(chosen)]
    dump('selection-v1.json',chosen)
    sources={1:Path('research/literature/sources/joshi_parpola_1987_cisi1.pdf'),2:Path('data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf')}
    docs={v:fitz.open(p) for v,p in sources.items()}
    rendered=set()
    for j,x in enumerate(chosen,1):
        v=x['source_page_hint']['volume']; pn=x['source_page_hint']['pdf_page']; out=R/f'page-v{v}-{pn}.png'
        if (v,pn) not in rendered:
            docs[v][pn-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(out); rendered.add((v,pn))
        im=Image.open(I/x['filename']).convert('RGB'); im.thumbnail((540,460))
        tile=Image.new('RGB',(600,520),'white'); tile.paste(im,((600-im.width)//2,30)); ImageDraw.Draw(tile).text((5,5),f'{j}: '+x['filename'],fill='black'); tile.save(R/f'candidate-{j:02d}.png')
    for s in range(0,len(chosen),6):
        sheet=Image.new('RGB',(1800,1040),'white')
        for k in range(s,min(s+6,len(chosen))):sheet.paste(Image.open(R/f'candidate-{k+1:02d}.png'),((k-s)%3*600,(k-s)//3*520))
        sheet.save(R/f'sheet-{s//6+1}.png')
    dump('pre-review-aggregate-v1.json',{'all_assets':a['all_count'],'application_mapped_filenames':a['mapped_files'],'application_unmapped':len(inv),'unmapped_already_catalogue_indexed':sum(bool(x['prior_keys']) for x in inv),'anonymous':len(anon),'anonymous_inherited_indexed':sum(bool(x['prior_keys']) for x in anon),'anonymous_unresolved':sum(not x['prior_keys'] for x in anon),'selected_candidates':len(chosen),'selected_source_pages':len(rendered),'hash_duplicate_anonymous':sum(len(x['exact_duplicate_names'])>1 for x in anon),'protocol_sha256':sha(P/'PROTOCOL.md')})
    dump('input-manifest-v1.json',[{'logical_path':str(p),'physical_path':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size} for p in [P/'PROTOCOL.md',Path('data/raw/2026-10-24-object-identity-pass3/asset-inventory-v1.json'),OLD/'run-2026-10-13/images/image-files.csv',OLD/'volpage-readings.tsv',*sources.values()]])
    print((R/'pre-review-aggregate-v1.json').read_text())
if __name__=='__main__':main()
