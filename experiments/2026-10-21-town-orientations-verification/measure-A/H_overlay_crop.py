import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
def read(p):return json.loads(Path(p).read_text())
r=read(sys.argv[1]);old=read(r['render_sidecar']);new=read(sys.argv[2]+'.json');out=Path(sys.argv[3])
if out.exists():raise FileExistsError(out)
m=np.linalg.inv(np.array(new['pixel_to_source']))@np.array(old['pixel_to_source'])
im=Image.open(sys.argv[2]).convert('RGB');d=ImageDraw.Draw(im)
for row in r['lines']:
 p=np.array(row['refined_endpoints_px']);p=(m@np.column_stack([p,np.ones(len(p))]).T).T[:,:2]
 d.line([tuple(x) for x in p],fill='red',width=2);d.text(tuple(p[0]),row['id'],fill='red')
im.save(out)
