"""Fresh picks after the overlay revealed a western frontage fit inside the house."""
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);obj=json.loads(p.read_text(encoding='utf-8'))
line=next(r for r in obj['lines'] if r['id']=='west-street-lower')
line.update(endpoints_px=[[202,615],[212,868]],corridor_half_width_px=3)
obj['revision_note']='The v1 overlay placed west-street-lower inside houses 10 and 11. The new corridor follows their actual street frontage, about 10-15 pixels farther west. All other picks are unchanged.'
with Path(sys.argv[2]).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2)
