"""Assemble the retrieved catalogue fields into an explicit star record."""
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
from records import *

def prepare(output):
    p=RAW/'simbad-basic-v1.json'; raw=json.loads(p.read_text())
    keys=[x['name'] for x in raw['metadata']]
    names=['alcyone','aldebaran','procyon','thuban']
    # Match the returned identifiers rather than depending on service row order.
    identifiers={'* eta Tau':'alcyone','* alf Tau':'aldebaran','* alf CMi':'procyon','* alf Dra':'thuban'}
    ss={}
    for row in raw['data']:
        s=dict(zip(keys,row));ss[identifiers[s['main_id']]]=s
    pm=next(x for x in json.loads((RAW/'simbad-thuban-pm-v1.json').read_text())['data'] if x[-1]=='2007A&A...474..653V')
    plx=next(x for x in json.loads((RAW/'simbad-thuban-plx-v1.json').read_text())['data'] if x[0]=='2007A&A...474..653V')
    ss['thuban'].update(pmra=pm[1],pmdec=pm[2],pm_bibcode=pm[3],plx_value=plx[2],plx_bibcode=plx[0])
    for name,hip,mag in zip(names,[17702,21421,37279,68756],[2.87,.86,.34,None]):
        ss[name].update(hip=hip,V=mag,position_epoch='J2000.0 ICRS',pmra_convention='mu_alpha_cos_delta')
    for name in names[:3]:
        if any(ss[name][k]!='2007A&A...474..653V' for k in ('coo_bibcode','pm_bibcode','plx_bibcode')):
            raise ValueError('catalogue preference changed: '+name)
    return write_json(output,'independent-star-retrieval',
      dict(stars=ss,thuban_coordinate_exception='SIMBAD retains Hipparcos 2007 proper motion and parallax as measurements but exposes only Gaia J2000 ICRS coordinates. Thuban is validation-only; those Gaia coordinates are explicitly retained, with Hipparcos 2007 motion and parallax. Prediction stars use Hipparcos 2007 in every astrometric field.'),
      inputs=[p,RAW/'simbad-thuban-pm-v1.json',RAW/'simbad-thuban-plx-v1.json'],
      codes=[__file__,Path(__file__).with_name('acquire.py')])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    prepare(a.output)
