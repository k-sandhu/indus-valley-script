import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import H_work as h
import datetime
slug=sys.argv[1]
m=h.read(h.PKG/'infra-v1/imagery-manifest-v1.json')
l=h.read(h.PKG/'infra-v1/plan-library-v1.json')
im=next((x for x in m['towns'] if x['slug']==slug),None)
if im and im.get('composite'):
 h.images(slug)
else:
 s=next(x for x in h.read(h.PKG/'infra-v1/sites-located-v1.json')['sites'] if x['slug']==slug)
 pl=next(x for x in l['towns'] if x['slug']==slug)
 h.write(h.OWN/'picks'/slug/'infra-snapshot-v1.json',dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),free_bytes=h.space(),site=s,imagery=im,plans=pl))
 print(slug,'NO COMPOSITE;',len(pl['plans']),'indexed plans')
