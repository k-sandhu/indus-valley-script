import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import H_work as h
slug=sys.argv[1];snap=h.read(h.OWN/'picks'/slug/'infra-snapshot-v2.json')
for layer,edge in [('RGB',False),('brightness',True),('NIR',False)]:
 h.space();h.render(snap['imagery']['composite']['path'],h.RAW/slug/f'4000-{layer}{"-edge" if edge else ""}-v1.png',snap['site']['coordinate_used'],4000,layer,2,500,edge)
