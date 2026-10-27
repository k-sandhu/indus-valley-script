"""Independent author checks on version 1 outputs; no model scores."""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent;D=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-extension/run-v2')
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 r=load(P/'results-v2.json');a=load(D/'face-annotations.json');routes=load(D/'missing-face-routes.json');panels=load(D/'panels.json');images=load(D/'image-annotations.json');recovery=load(D/'recovered-divided-face.json')
 checks={'all_output_hashes':all(sha(Path(x['physical_path']))==x['sha256'] for x in r['local_outputs']),'all_input_hashes':all(sha(Path(x['physical_path']))==x['sha256'] for x in r['inputs']),'eight_bridges':len([x for x in a if x['accepted_side_bridge']])==8,'four_bridged_objects':len({x['face_id'].split('.')[0] for x in a if x['accepted_side_bridge']})==4,'ten_faces':len(a)==10,'all_43_routes':len(routes)==43,'31_CISI3_routes':sum(x['route'].startswith('CISI3') for x in routes)==31,'seven_nonCISI_locators':sum(x['route'] in ['HARP-object-and-figure','Dholavira-excavation-number'] for x in routes)==7,'one_recovered':sum(x['crop_recovered'] for x in routes)==1,'22_crops':len(list((D/'crops').glob('*.png')))==22,'H1001_preserved':all(x['source_side'] is None for x in a if x['catalogue_key']=='H-1001'),'image_links_13':sum(x['accepted_for_face_side'] for x in images)==13}
 for panel in panels:
  with Image.open(panel['crop_path']) as im:
   box=panel['bbox_pixels'];assert im.size==(box[2]-box[0],box[3]-box[1])
 checks['crop_dimensions_match_coordinates']=True
 with (P/'verification-v2.json').open('x',encoding='utf8') as f:json.dump({'tier':'author checks, submitted','checks':checks,'passed':all(checks.values())},f,indent=2)
 assert all(checks.values());print(json.dumps(checks,indent=2))
if __name__=='__main__':main()
