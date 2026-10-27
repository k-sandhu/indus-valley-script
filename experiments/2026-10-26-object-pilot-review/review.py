"""Independent fixed-frame, hash, index and render checks. Run from repo root."""
import csv, hashlib, json
from pathlib import Path
import fitz
from PIL import Image

P = Path('experiments/2026-10-26-object-pilot-review')
R = Path('D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot-review')
IR = Path('D:/projects/indus_valley_script/data/raw/2026-10-26-image-recovery')
REG = Path('D:/projects/indus_valley_script/data/raw/2026-10-26-object-pilot-register')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x): Path(p).write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x,list):
        for v in x: yield from walk(v)

def main():
    reg=read(REG/'pilot-register-v4.json'); objs=reg['objects']
    target={f'PCF-DHV-{i:03d}' for i in range(5,15)}|{'H-1657','H-2587','H-1688','H-1682','H-1692','L-164','L-163','L-167','L-146','L-174'}
    checks={'exact_fixed_membership':len(objs)==20 and {o['record_id'] for o in objs}==target,
            'no_physical_merge':all(not o['accepted_physical_merge'] for o in objs)}
    dh=[o for o in objs if o['site']=='Dholavira']
    checks['candidate_families_62']=len({f for o in dh for f in o['candidate_family_ids']})==62
    checks['candidate_edges_274']=sum(len(o['candidate_family_ids']) for o in dh)==274
    badkeys=[k for d in walk(reg) for k in d if k in {'signs','signs_reading_rtl','sequence','transcription','language','meaning','phonetic'}]
    checks['no_sequence_or_language_payload_keys']=not badkeys
    checks['explicit_missing_per_target']=all(isinstance(o['missing_fields'],list) and o['missing_fields'] for o in objs)
    checks['assertions_source_qualified']=all(a.get('source_refs') and a.get('locator') and a.get('status') for o in objs for a in o['assertions'])
    checks['freshness_not_claimed']=all('previously' in o['exposure_status'] for o in objs)
    byid={o['record_id']:o for o in objs}
    checks['context_pages_not_counted_as_images']=not byid['H-1682']['images'] and not byid['H-1692']['images']
    checks['H1657_pointer_only']=all(not i.get('path') for i in byid['H-1657']['images'])
    hashrows=[]
    manifests=[Path('experiments/2026-10-26-object-pilot-register/source-manifest-v4.json'),Path('experiments/2026-10-26-image-recovery/source-manifest-v2.json'),Path('experiments/2026-10-26-source-conflicts/source-manifest-v2.json'),Path('experiments/2026-10-26-source-conflicts/asset-manifest-v2.json')]
    for m in manifests:
        for d in walk(read(m)):
            path=d.get('physical_path') or d.get('logical_path')
            if path and d.get('sha256'):
                p=Path(path); ok=p.is_file() and sha(p)==d['sha256']
                hashrows.append({'manifest':str(m),'path':str(p),'matches':ok})
    for o in objs:
        for i in o['images']:
            if i.get('path') and i.get('sha256'):
                hashrows.append({'manifest':'register images','path':i['path'],'matches':sha(i['path'])==i['sha256']})
    checks['all_declared_file_hashes_match']=all(r['matches'] for r in hashrows)
    joins=[j for j in read(IR/'image-joins-v2.json') if j['newly_indexed_against_baseline']]
    old=list(csv.DictReader(Path('experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/image-files.csv').open(encoding='utf8')))
    oldby={r['file']:r for r in old}; oldkeys={k for r in old for k in r['keys'].split(';') if k}
    prior=[]
    for j in joins:
        row=oldby[Path(j['image_physical_path']).name]
        prior.append({'join_id':j['join_id'],'target':j['catalogue_target'],'view':j['face_view'],'asset':j['image_logical_path'],'absent_from_asset_prior_keys':j['catalogue_target'] not in row['keys'].split(';'),'target_absent_from_prior_index':j['catalogue_target'] not in oldkeys,'asset_hash_matches':sha(j['image_physical_path'])==j['image_sha256']})
    checks['all_14_new_index_relations']=len(prior)==14 and all(r['absent_from_asset_prior_keys'] and r['asset_hash_matches'] for r in prior)
    sources={1:Path('research/literature/sources/joshi_parpola_1987_cisi1.pdf'),2:Path('data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf')}
    render=[]
    for v,n in sorted({(j['source_page']['volume'],j['source_page']['pdf_page']) for j in joins}):
        doc=fitz.open(sources[v]); pix=doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)); im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        held=Image.open(IR/f'page-v{v}-{n}.png').convert('RGB')
        render.append({'volume':v,'pdf_page':n,'source':str(sources[v]),'source_sha256':sha(sources[v]),'identical_render_pixels':im.size==held.size and im.tobytes()==held.tobytes()})
    checks['all_12_source_page_renders_recreated']=len(render)==12 and all(r['identical_render_pixels'] for r in render)
    # These fresh renders bind the original contradictory source coordinates.
    for label,path,pages in [('rao',Path('data/raw/2026-10-21-town-axes/dating/lothal/rao1985lothal-part2.pdf'),[70,76,454]),('cisi1',sources[1],[409])]:
        doc=fitz.open(path)
        for n in pages: doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(R/f'{label}-pdf{n}.png')
    write(R/'hash-checks-v3.json',hashrows); write(R/'prior-index-checks-v3.json',prior); write(R/'render-checks-v3.json',render)
    summary={'checks':checks,'passed':sum(checks.values()),'failed':sum(not v for v in checks.values()),'hash_bindings_checked':len(hashrows),'new_join_rows':len(joins),'new_unique_assets':len({j['image_sha256'] for j in joins}),'new_unique_catalogue_keys':len({j['catalogue_target'] for j in joins}),'first_index_keys':sorted({r['target'] for r in prior if r['target_absent_from_prior_index']}),'baseline':'13 October image-files.csv catalogue assignments; earlier whole source pages remain available','new_physical_objects':0,'new_primary_files':0,'freshness':False}
    write(P/'validation-v3.json',summary)
    write(P/'source-manifest-v3.json',{'protocol_sha256':sha(P/'PROTOCOL.md'),'inputs':[{'logical_path':str(p),'physical_path':str(p.resolve()),'sha256':sha(p)} for p in [*manifests,REG/'pilot-register-v4.json',IR/'image-joins-v2.json',Path('experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/image-files.csv')]],'local_output_root':str(R),'logical_output_root':'data/raw/2026-10-26-object-pilot-review','rights':'source derivatives local-only; project code Unlicense, prose and aggregates CC0 1.0'})
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()


